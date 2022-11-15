from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
from .data_extraction.pancard import get_pancard_data
from .models import Pan
from common.scripts import convert_to_binary_data, normalize_date
from django.urls import reverse
import time
import json
from mysite.models import Unprocessed_document_details


@login_required
def home(request):
    status = {}
    payload = {}

    if "deal_id" not in request.session or "customer_id" not in request.session:
        status["type"] = "deal"
        status["message"] = "Please select a deal first to procceed further!"

    if request.method == 'POST' and not status:
        if 'file_upload' not in request.FILES:
            status["type"] = "other"
            status["message"] = "Field name is missing, can not procceed further!"

        if not status:
            upload_file = request.FILES['file_upload']

            file_name = request.session["customer_id"] + "_" + str(time.time())
            file_name_type = file_name + '.' + upload_file.name.split('.')[-1]
            
            fs = FileSystemStorage()
            fs.save('pan/' + file_name_type, upload_file)

            media_root = settings.MEDIA_ROOT
            file_dir = os.path.join(media_root, 'pan')
            file_path = os.path.join(file_dir, file_name_type)
            try:
                data, image_path = get_pancard_data(file_path)
            except Exception as e:
                print(e)
                status["type"] = "fail"
                status["message"] = "We are unable to process the uploaded document. Do you want to process it manually through knowlvers?"
                
            try:
                if data['pan_number'].values[0] == None or data['pan_number'].values[0] == '':
                    status["type"] = "fail"
                    status["message"] = "We are unable to process the uploaded document. Do you want to process it manually through knowlvers?"
            except Exception as e:
                print(e)
                status["type"] = "fail"
                status["message"] = "We are unable to process the uploaded document. Do you want to process it manually through knowlvers?"
            
            if not status:
                status["type"] = "success"
                status["message"] = "File upload successful!"

            if status["type"] == "success":
                try:
                    image_binary_data = convert_to_binary_data(image_path)
                    db_data = Pan.objects.create(name=data['name'].values[0] if 'name' in data else '', 
                                                relative_name=data['relative_name'].values[0] if 'relative_name' in data else '', 
                                                dob=normalize_date(data['dob'].values[0]) if 'dob' in data else '', 
                                                pan_number=data['pan_number'].values[0] if 'pan_number' in data else '',
                                                deal_id=request.session["deal_id"],
                                                customer_id=request.session["customer_id"],
                                                image_data=image_binary_data,
                                                image_name=file_name_type,
                                                created_by=request.user)
                except Exception as e:
                    print(e)
                    status["type"] = "other"
                    status["message"] = "Something went wrong! please try again!"

                # return redirect(reverse('upload', kwargs={"doc_type": "aadhaar"}))
    
    payload = json.dumps({"upload_page": True, "page_heading": "PAN", "status": status})
    return HttpResponse(payload)
