from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import time
import json
from django.urls import reverse
from .data_extraction.aadhaarcard import get_aadhaarcard_data
from .models import Aadhaar
from common.scripts import convert_to_binary_data, normalize_date


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
			fs.save('aadhaar/' + file_name_type, upload_file)
			
			media_root = settings.MEDIA_ROOT
			file_dir = os.path.join(media_root, 'aadhaar')
			file_path = os.path.join(file_dir, file_name_type)
			try:
				data, image_path = get_aadhaarcard_data(file_path)
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
					db_data = Aadhaar.objects.create(name= data['name'].values[0] if 'name' in data else '', 
													gender=data['gender'].values[0] if 'gender' in data else '', 
													yob=data['yob'].values[0] if 'yob' in data else '',
													gname = data['gname'].values[0] if 'gname' in data else '',
													house=data['house'].values[0] if 'house' in data else '',
													street=data['street'].values[0] if 'street' in data else '',
													lm=data['lm'].values[0] if 'lm' in data else '',
													vtc=data['vtc'].values[0] if 'vtc' in data else '',
													po=data['po'].values[0] if 'po' in data else '',
													dist=data['dist'].values[0] if 'dist' in data else '',
													subdist=data['subdist'].values[0] if 'subdist' in data else '',
													state=data['state'].values[0] if 'state' in data else '',
													pc=data['pc'].values[0] if 'pc' in data else '',
													dob=normalize_date(data['dob'].values[0]) if 'dob' in data else '',
													uid=data['uid'].values[0] if 'uid' in data else '',
													image_data=image_binary_data,
													deal_id=request.session["deal_id"],
													customer_id=request.session["customer_id"],
													image_name=file_name_type,
									created_by=request.user)
					# return redirect(reverse('upload_form'))
				except Exception as e:
					print(e)
					status["type"] = "other"
					status["message"] = "Something went wrong! please try again!"

	payload = json.dumps({"upload_page": True, "page_heading": "AADHAAR", "status": status})
	return HttpResponse(payload)

