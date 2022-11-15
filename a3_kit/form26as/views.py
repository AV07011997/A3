from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
from django.http import HttpResponse
import json
import time
from .data_extraction.form26as import get_form26as_data
from .models import AsseseeDetails
from .models import PartA
from .models import PartB
from .models import PartC
from .models import PartD
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
			document_type = request.POST['document_type']
			year = request.POST['year']
			upload_file = request.FILES['file_upload']
			file_name = request.session["customer_id"] + "_" + str(time.time())
			file_name_type = file_name + '.' + upload_file.name.split('.')[-1]
			fs = FileSystemStorage()
			fs.save('form26as/'+file_name_type, upload_file)

			media_root = settings.MEDIA_ROOT
			file_dir = os.path.join(media_root, 'form26as')
			file_path = os.path.join(file_dir, file_name_type)

			try:
				all_data1, all_data3, all_data8, all_data5, all_data4, all_part_g = get_form26as_data(file_path)
			except Exception as e:
				status["type"] = "fail"
				status["message"] = "We are unable to process the uploaded document. Do you want to process it manually through knowlvers?"
			
			if not status:
				status["type"] = "success"
				status["message"] = "File upload successful!"

			if status["type"] == "success":
				try:
					if not all_data1.empty:
						part_assesee_details_all_data = []
						for index, data1 in all_data1.iterrows():
							assesee_details_db_data = AsseseeDetails.objects.create(
								pan = data1['PAN'],
								financial_year = data1['Financial_Year'],
								assessment_year = data1['Assessment_Year'],
								current_pan_status = data1['Current_pan_status'],
								name_of_assessee = data1['Name_of_Assessee'],
								address_of_assessee = data1['Address_of_Assessee'],
								created_by=request.user,
								deal_id=request.session["deal_id"],
								customer_id=request.session["customer_id"],
								image_name=file_name_type
							)

					if not all_data3.empty:
						for index, data3 in all_data3.iterrows():
							part_a_db_data = PartA.objects.create(
								sr_no = data3['Sr_No.'],
								section_1 = data3['Section_1'],
								tan_of_deductor = data3['TAN_of_Deductor'],
								amount_paid_credited = data3['Amount_Paid_Credited'],
								tax_deducted = data3['Tax_Deducted'],
								tds_deposited = data3['TDS_Deposited'],
								remarks	= data3['Remarks'],
								transaction_date = data3['Transaction_Date'],
								status_of_booking = data3['Status_of_Booking'],
								date_of_booking	= data3['Date_of_Booking'],
								name_of_deductor = data3['Name_of_Deductor'],
								total_amount_paid_credited = data3['Total_Amount_Paid_Credited'],
								total_tax_deducted = data3['Total_Tax_Deducted'],
								total_tds_deposited = data3['Total_TDS_Deposited'],
								pan	= data3['PAN'],
								name_of_assessee = data3['Name_of_Assessee'],
								assessment_year = data3['Assessment_Year'],
								created_by=request.user,
								deal_id=request.session["deal_id"],
								customer_id=request.session["customer_id"]
							)

					if not all_data8.empty:
						for index, data8 in all_data8.iterrows():
							part_b_db_data = PartB.objects.create(
								sr_no = data8['Sr_No.'],
								section_1 = data8['Section_1'],
								tan_of_collector = data8['TAN_of_Collector'],
								amount_paid_debited = data8['Amount_Paid_Debited'],
								tax_collected = data8['Tax_Collected'],
								tcs_deposited = data8['TCS_Deposited'],
								remarks	= data8['Remarks'],
								transaction_date = data8['Transaction_Date'],
								status_of_booking = data8['Status_of_Booking'],
								date_of_booking	= data8['Date_of_Booking'],
								name_of_collector = data8['Name_of_Collector'],
								total_amount_paid_debited = data8['Total_Amount_Paid_Debited'],
								total_tax_collected = data8['Total_Tax_Collected'],
								total_tcs_deposited = data8['Total_TCS_Deposited'],
								pan	= data8['PAN'],
								name_of_assessee = data8['Name_of_Assessee'],
								assessment_year = data8['Assessment_Year'],
								created_by=request.user,
								deal_id=request.session["deal_id"],
								customer_id=request.session["customer_id"]
							)

					if not all_data5.empty:
						for index, data5 in all_data5.iterrows():
							part_c_db_data = PartC.objects.create(
								sr = data5['Sr.'],
								major_head = data5['Major Head'],
								minor_head = data5['Minor Head'],
								tax = data5['Tax'],
								surcharge = data5['Surcharge'],
								education_cess = data5['Education Cess'],
								others = data5['Others'],
								total_tax = data5['Total Tax'],
								bsr_code = data5['BSR Code'],	
								date_of_deposit = data5['Date of Deposit'],
								challan_serial_number = data5['Challan Serial Number'],
								remarks = data5['Remarks**'],
								pan	= data5['PAN'],
								name_of_assessee = data5['Name_of_Assessee'],
								assessment_year = data5['Assessment_Year'],
								created_by=request.user,
								deal_id=request.session["deal_id"],
								customer_id=request.session["customer_id"]
							)

					if not all_data4.empty:
						for index, data4 in all_data4.iterrows():
							part_d_db_data = PartD.objects.create(
								sr = data4['Sr.'],
								assessment_year_refund = data4['Assessment_Year_Refund'],
								mode = data4['Mode'],
								refund_issued = data4['Refund Issued'],
								nature_of_refund = data4['Nature of Refund'],
								amount_of_refund = data4['Amount of Refund'],
								interest = data4['Interest'],
								date_of_payment = data4['Date of Payment'],
								remarks = data4['Remarks'],
								pan	= data4['PAN'],
								name_of_assessee = data4['Name_of_Assessee'],
								assessment_year = data4['Assessment_Year'],
								created_by=request.user,
								deal_id=request.session["deal_id"],
								customer_id=request.session["customer_id"]
							)

					if not all_part_g.empty:
						for index, part_g in all_part_g.iterrows():
							part_g_db_data = PartD.objects.create(
								sr = data4['Sr. No.'],
								financial_year = part_g['Financial Year'],
								short_payment = data4['Short Payment'],
								short_deduction = data4['Short Deduction'],
								interest_on_tds = data4['Interest on TDS'],
								interest_on_tds_1 = data4['Interest on TDS.1'],
								late_filing_fee_us = data4['Late Filing Fee u/s'],
								interest_us = data4['Interest u/s 220(2)'],
								total_default = part_g['Total Default'],
								pan	= part_g['PAN'],
								name_of_assessee = part_g['Name_of_Assessee'],
								assessment_year = part_g['Assessment_Year'],
								created_by=request.user,
								deal_id=request.session["deal_id"],
								customer_id=request.session["customer_id"]
							)

					Uploaded_itrv_form16_form26as_details.objects.create(
                                deal_id=request.session["deal_id"],
                                customer_id=request.session["customer_id"],
                                year=year,
                                document_type = document_type,
                                file_name = file_name_type,
                                created_by=request.user
                        )
				except Exception as e:
					print(e)
					status["type"] = "other"
					status["message"] = "Something went wrong! please try again!"

	# return JsonResponse({"status": status})
	payload = json.dumps({"upload_form_page": True, "status": status})
	return HttpResponse(payload)
