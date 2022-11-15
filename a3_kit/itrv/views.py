from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
from django.http import HttpResponse
import json
import time
from .data_extraction.itrv import get_itrv_data
from .models import Itrv
from django.http import JsonResponse
from mysite.models import Uploaded_itrv_form16_form26as_details


@login_required
def home(request):
	status = {}
	
	if "deal_id" not in request.session or "customer_id" not in request.session:
		status["type"] = "other"
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
			fs.save('itrv/'+file_name_type, upload_file)
			# print("itrv uploaded file", request.FILES['file_upload'][0])
			# upload_file = request.FILES['pdf']
			# upload_file = request.POST['file_data'][0]
			print("itvr views clicked")
			document_type = request.POST['document_type']
			year = request.POST['year']
			print("itrv views document type: ",document_type)
			print("itrv views year: ",year)

			media_root = settings.MEDIA_ROOT
			file_dir = os.path.join(media_root, 'itrv')
			file_path = os.path.join(file_dir, file_name_type)

			try:
				data = get_itrv_data(file_path)
			except Exception as e:
				print(e)
				status["type"] = "fail"
				status["message"] = "We are unable to process the uploaded document. Do you want to process it manually through knowlvers?"
			
			if not status:
				status["type"] = "success"
				status["message"] = "File upload successful!"

			if status["type"] == "success" and data is not None:
				try:
					Itrv.objects.create(assessment_year=data.iloc[0,1],
										name=data.iloc[1,1],
										pan=data.iloc[2,1],
										town_city_district_state=data.iloc[3,1],
										pin_code=data.iloc[4,1],
										efiling_acknowledgement_number=data.iloc[5,1],
										form_no=data.iloc[6,1],
										date_of_itr_filed=data.iloc[7,1],
										gross_total_income=data.iloc[8,1],
										deductions_under_chapter_vi_a=data.iloc[9,1],
										total_income=data.iloc[10,1],
										total_income_deemed_total_income_under_amt_mat=data.iloc[11,1],
										total_income_current_year_loss=data.iloc[12,1],
										net_tax_payable=data.iloc[13,1],
										interest_and_fee_payable=data.iloc[14,1],
										total_tax_interest_and_fee_payable=data.iloc[15,1],
										taxes_paid_advance_tax=data.iloc[16,1],
										taxes_paid_tds=data.iloc[17,1],
										taxes_paid_tcs=data.iloc[18,1],
										taxes_paid_self_assessment_tax=data.iloc[19,1],
										taxes_paid_total_taxes_paid=data.iloc[20,1],
										tax_payable=data.iloc[21,1],
										refund=data.iloc[22,1],
										created_by=request.user,
										deal_id=request.session["deal_id"],
										customer_id=request.session["customer_id"],
										image_name=file_name_type)

					Uploaded_itrv_form16_form26as_details.objects.create(
										deal_id=request.session["deal_id"],
										customer_id=request.session["customer_id"],
										year=year,
										document_type = document_type,
										file_name = file_name_type,
										created_by=request.user)
										
				except Exception as e:
					print(e)
					status["type"] = "other"
					status["message"] = "Something went wrong! please try again!"
	
	# return JsonResponse({"status": status})
	payload = json.dumps({"upload_form_page": True, "status": status})
	return HttpResponse(payload)
