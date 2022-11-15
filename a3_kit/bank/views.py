from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import time
from .data_extraction.bob import bob_digitization
from .data_extraction.cbi import cbi_digitization
from .data_extraction.hdfc import hdfc_digitization
from .data_extraction.idfc import idfc_digitization
from .data_extraction.obc import obc_digitization
from .data_extraction.kotak import kotak_digitization
from .data_extraction.axis import axis_digitization
from .data_extraction.sbi import sbi_digitization
from .data_extraction.standardchartered import standard_chartered_digitization
from .data_extraction.corporation import corporation_digitization
from .data_extraction.indusind import indusind_digitization
from .data_extraction.union import union_digitization

from .models import Bank
from mysite.models import Uploaded_bank_statements_details
from common.scripts import normalize_date
from django.http import JsonResponse


@login_required
def home(request):
	status = {}

	if "deal_id" not in request.session or "customer_id" not in request.session:
		status["type"] = "other"
		status["message"] = "Please select a deal first to procceed further!"
	
	if request.method == 'POST' and not status:
		if 'file_upload' not in request.FILES or 'bank_name' not in request.POST or 'file_pass' not in request.POST:
			status["type"] = "other"
			status["message"] = "Field name is missing, can not procceed further!"
		
		if not status:
			action_type = request.POST['action_type']
			bank_index = request.POST['bank_index']
			bank_id = request.POST['bank_id']
			bank_name = request.POST['bank_name']
			pdf_password = request.POST['file_pass']
			upload_file = request.FILES['file_upload']
			file_name = request.session["customer_id"] + "_" + str(time.time())
			file_name_type = file_name + '.' + upload_file.name.split('.')[-1]
			bank_file_name_type = bank_name.lower() + "/" + file_name_type

			fs = FileSystemStorage()
			fs.save('bank/'+bank_file_name_type, upload_file)

			media_root = settings.MEDIA_ROOT
			file_dir = os.path.join(media_root, 'bank')
			file_path = os.path.join(file_dir, bank_file_name_type)
			
			try:
				if bank_name == "BOB":
					data = bob_digitization(file_path, pdf_password)
				elif bank_name == "CBI":
					data = cbi_digitization(file_path, pdf_password)
				elif bank_name == "HDFC":
					data = hdfc_digitization(file_path, pdf_password)
				elif bank_name == "IDFC":
					data = idfc_digitization(file_path, pdf_password)
				elif bank_name == "OBC":
					data = obc_digitization(file_path, pdf_password)
				elif bank_name == "KOTAK":
					data = kotak_digitization(file_path)
					# change column name
					data = data.rename(columns={'Narration': 'Description'})
				elif bank_name == "AXIS":
					data = axis_digitization(file_path, pdf_password)
				elif bank_name == "SBI":
					data = sbi_digitization(file_path, pdf_password)
				elif bank_name == "STANDARD CHARTERED":
					data = standard_chartered_digitization(file_path, pdf_password)
				elif bank_name == "CORPORATION":
					data = corporation_digitization(file_path, pdf_password)
				elif bank_name == "INDUSIND":
					data = indusind_digitization(file_path, pdf_password)
				elif bank_name == "UNION":
					data = union_digitization(file_path, pdf_password)
				
				else:
					status["type"] = "other"
					status["message"] = "Currently we don't process this Bank statement!"
			except Exception as e:
				print(e)
				status["type"] = "fail"
				status["message"] = "We are unable to process the uploaded document. Do you want to process it manually through knowlvers?"
				data = None
		
		if not status:
			status["type"] = "success"
			status["message"] = "File upload successful!"
		
		print(data)
		
		if status["type"] == "success" and data is not None:
			try:
				for index, row in data.iterrows():
					Bank.objects.create(bank_name=bank_name, 
					txn_date=normalize_date(row['Txn Date']),
					description=row['Description'],
					cheque_number=row['Cheque Number'],
					debit=row['Debit'],
					credit=row['Credit'],
					balance=row['Balance'],
					account_name=row['Account Name'],
					account_number=row['Account Number'],
					created_by=request.user,
					deal_id=request.session["deal_id"],
					customer_id=request.session["customer_id"],
					mode=row["mode"],
					sub_mode=row["sub_mode"],
					entity=row["entity"],
					entity_bank=row["entity_bank"],
					source_of_trans=row["source_of_trans"],
					transaction_type=row['Transaction_Type'],
					image_name=bank_file_name_type)
				
				Uploaded_bank_statements_details.objects.create(
					deal_id = request.session["deal_id"],
					customer_id = request.session["customer_id"],
					action_type = action_type,
					bank_index =  bank_index,
					bank_name = bank_name,
					bank_id = bank_id,
					file_name = bank_file_name_type,
					created_by = request.user)

			except Exception as e:
				print(e)
				status["type"] = "other"
				status["message"] = "Something went wrong! please try again!"
	
	return JsonResponse({"upload_bank_page": True, "status": status})
