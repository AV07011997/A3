import json
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .decorators import unauthenticated_users
from django.db.models import Q
from pan.models import Pan
from aadhaar.models import Aadhaar
from itrv.models import Itrv
from form16.models import Info
from form26as.models import AsseseeDetails
from bank.models import Bank, Bank_master
from salary.models import Salary
from datetime import datetime, timedelta
from .models import Los_details, Customer_details, Customer_address, Processed_document_details, Unprocessed_document_details, Document_type_master, District_master, State_master
from common.scripts import normalize_date
from .models import Uploaded_itrv_form16_form26as_details, Uploaded_bank_statements_details
import numpy as np
import mysql.connector
import pandas as pd
from django.db import connection

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    all_data = []
    for row in cursor.fetchall():
        data_row = dict(zip(columns, row))
        # data_row["Disbursal_date"] = data_row["Disbursal_date"].strftime('%d/%m/%Y')
        # data_row["Date_reported"] = data_row["Date_reported"].strftime('%d/%m/%Y')
        # data_row["bank_name"] = data_row["bank_name"]
        # data_row["deal_id"] = data_row["deal_id"]
        all_data.append(data_row)

    return all_data

@unauthenticated_users
def login_page(request):
    if request.method == "POST":
        uname = request.POST.get("username")
        upwd = request.POST.get("password")

        user = authenticate(request, username=uname, password=upwd)

        if user is not None:
            login(request, user)
            return redirect("search")
        else:
            messages.info(request, "Invalid Credentials!")

    payload = {"login_page": True}
    return render(request, "login.html", payload)


@login_required
def home_page(request):
    return redirect("search")
    


@login_required
def search_page(request):
    
     
    import boto3
    import mysql.connector

    bucket = 'digitizedfiles'
    s3 = boto3.resource('s3')
    objects_files = s3.Bucket(bucket).objects.all()
    print(objects_files)

    mydb = mysql.connector.connect(
            host="localhost",
            user="root",                        ###connect to database
            password="Knowlvers@555",
            database="a3_kit"
        )

    mycursor = mydb.cursor()  

    def status_all():

        sql = "delete from digitized_file_status;"
        mycursor.execute(sql)
        
        for obj in objects_files:
            file_name = obj.key
            lid = obj.key.split('_')[0]
            if obj.key.split('_')[-1] == 'b.csv':
                file_type = 'bank'
            if obj.key.split('_')[-1] == 'i.csv':
                file_type = 'itr'

            if obj.key.split('_')[-1] != 'i.csv' and obj.key.split('_')[-1] != 'b.csv':
                file_type = 'others'


            sql = "INSERT INTO digitized_file_status (file_name, lead_id, type) VALUES (%s, %s, %s);"

            val = (file_name,lid, file_type)

            mycursor.execute(sql, val)
        mydb.commit()

    status_all()

    text = request.GET.get("search")
    request.session["stext"] = text
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT lead_id, COUNT(file_name) as bank_uploaded FROM upload_file_details WHERE type='bank' group by lead_id;")
            bank_lead=dictfetchall(cursor)
            bank_lead = pd.DataFrame(bank_lead)
    except:pass

    try:
      

        with connection.cursor() as cursor:
            cursor.execute("SELECT lead_id, COUNT(file_name) as itr_uploaded FROM upload_file_details WHERE type='itr' group by lead_id;")
            itr_lead=dictfetchall(cursor)
            itr_lead = pd.DataFrame(itr_lead)
     
    except:pass

    try:

        with connection.cursor() as cursor:
            cursor.execute("SELECT lead_id,count(file_name) as itr_download FROM downloaded_file_details where substring(file_name,-5,1)='i' group by lead_id;")
            itr_download=dictfetchall(cursor)
            itr_download = pd.DataFrame(itr_download)
         
    except:pass

    try:

        with connection.cursor() as cursor:
            cursor.execute("SELECT lead_id,count(file_name) as bank_download FROM downloaded_file_details where substring(file_name,-5,1)='b' group by lead_id;")
            bank_download=dictfetchall(cursor)
            bank_download = pd.DataFrame(bank_download)
          
            
    except:pass
    with connection.cursor() as cursor:
        cursor.execute("SELECT lead_id,deal_id, customer_id , name FROM los_did_cid_generation;")
        customer_detail=dictfetchall(cursor)
        customer_detail = pd.DataFrame(customer_detail)
        
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT lead_id, creation_time FROM los_did_cid_generation group by lead_id;")
            creation_time=dictfetchall(cursor)
            creation_time = pd.DataFrame(creation_time)
            # creation_time['creation_time'] = creation_time['creation_time'].astype('str')


    except:pass

    try:

        with connection.cursor() as cursor:
            cursor.execute("SELECT lead_id, count(file_name) as itr_download_ready FROM digitized_file_status where type = 'itr' group by lead_id;")
            itr_download_ready=dictfetchall(cursor)
            itr_download_ready = pd.DataFrame(itr_download_ready)
    except:pass

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT lead_id, count(file_name) as bank_download_ready FROM digitized_file_status where type = 'bank' group by lead_id;")
            bank_download_ready=dictfetchall(cursor)
            bank_download_ready = pd.DataFrame(bank_download_ready)
    except:pass
    try:
            
        with connection.cursor() as cursor:
            cursor.execute("SELECT lead_id, customer_id,creation_time as bureau_creation_time   FROM a3_kit.los_did_cid_generation group by lead_id ;")
            bureau_updated=dictfetchall(cursor)
            bureau_updated = pd.DataFrame(bureau_updated)
            
            
            bureau_updated['bureau_creation_time'] = bureau_updated['bureau_creation_time'].dt.strftime('%d-%b-%Y, %I:%M %p')


            

    except:pass
    try:
            
        with connection.cursor() as cursor:
            cursor.execute("SELECT customer_id FROM bureau group by customer_id ;")
            bureau_updated_data=dictfetchall(cursor)
            bureau_updated_data = pd.DataFrame(bureau_updated_data)
            
           

            

    except:pass

    try:
        customer_detail['lead_id'] = customer_detail['lead_id'].astype('int64')
        customer_detail['customer_id'] = customer_detail['customer_id'].astype('int64')
        bureau_updated['lead_id'] = bureau_updated['lead_id'].astype('int64')
        bureau_updated['customer_id'] = bureau_updated['customer_id'].astype('int64')

    except:pass
    
    try:
        customer_detail = customer_detail.merge(bank_lead, on="lead_id", how="left")
        customer_detail = customer_detail.merge(itr_lead, on="lead_id", how="left")
        customer_detail = customer_detail.merge(itr_download, on="lead_id", how="left")
        customer_detail = customer_detail.merge(bank_download, on="lead_id", how="left")
        customer_detail = customer_detail.merge(creation_time, on="lead_id", how="left")
        try:
            customer_detail = customer_detail.merge(itr_download_ready, on="lead_id", how="left")
        except:pass
        try:
            customer_detail = customer_detail.merge(bank_download_ready, on="lead_id", how="left")
        except:pass
        bureau_updated = bureau_updated.sort_values('lead_id', ascending=False)

        customer_detail = customer_detail.merge(bureau_updated, on=['customer_id','lead_id'], how='left')
       

        customer_detail['bureau_updated'] = customer_detail['bureau_updated'].fillna('No')

        customer_detail = customer_detail.fillna(0)
        customer_detail['bank_uploaded'] = customer_detail['bank_uploaded'].astype('int64')
        customer_detail['bank_download'] = customer_detail['bank_download'].astype('int64')
        customer_detail['itr_uploaded'] = customer_detail['itr_uploaded'].astype('int64')
        customer_detail['itr_download'] = customer_detail['itr_download'].astype('int64')
        try:
            customer_detail['itr_download_ready'] = customer_detail['itr_download_ready'].astype('int64')
        except:pass
        try:
            customer_detail['bank_download_ready'] = customer_detail['bank_download_ready'].astype('int64')
        except:pass
    except Exception as e:
        print(e)


    customer_detail = customer_detail.drop_duplicates().reset_index(drop=True)
    
    customer_detail = customer_detail.sort_values('lead_id')

    if 'itr_download_ready' not in customer_detail:
        customer_detail['itr_download_ready'] = 0

    if 'bank_download_ready' not in customer_detail:
        customer_detail['bank_download_ready'] = 0
        
    customer_detail['bank_download_ready'] = customer_detail['bank_download_ready'].apply(lambda x: int(x) if pd.notnull(x) else 0)
    customer_detail['bank_uploaded'] = customer_detail['bank_uploaded'].apply(lambda x: int(x) if pd.notnull(x) else 0)
    customer_detail['bank_download'] = customer_detail['bank_download'].apply(lambda x: int(x) if pd.notnull(x) else 0)
    
    customer_detail = customer_detail.sort_values(['creation_time'], ascending=[False])
    customer_detail['bureau_updated']=''
    i=0
    for x in bureau_updated_data['customer_id']:
        
        for i in range(len(customer_detail)):
            if x==customer_detail['customer_id'][i]:
                customer_detail['bureau_updated'][i]="Yes"
                
            
        
        
    
    
    #########Adding to get correct time#######
    customer_detail['creation_time']=customer_detail['creation_time']+timedelta(hours=5,minutes=30)
    customer_detail['creation_time'] = customer_detail['creation_time'].dt.strftime('%d-%b-%Y,  %H:%M')


    json_records = customer_detail.to_json(orient ='records') 
    customer_detail = json.loads(json_records)
    
    payload = {'customer_detail': customer_detail}
    return render(request, "search.html", payload)

def searchsession(request,text):
    request.session["lead_session"] = text
    try:
        del request.session['customer_id']
        del request.session['deal_id']
        del request.session['name']

    except:
        pass
    return redirect("customer_id1234")
    return JsonResponse({"result":text})

def customer_id1234(request):
    print("suhaib")
    lead_id=request.session["lead_session"]
    with connection.cursor() as cursor:
        cursor.execute("SELECT distinct(customer_id) ,lead_id,deal_id, name,bank,account_number FROM los_did_cid_generation where lead_id = " + lead_id + ";")
        customer_detail=dictfetchall(cursor)
        print(customer_detail)
    
    return render(request, "customer_id.html",{'data' :customer_detail})

def customer_session(request,text,text1):
    request.session["customer_id"] = text
    request.session["deal_id"] = text1
    name=""
    with connection.cursor() as cursor:
        cursor.execute("SELECT distinct(cid),name FROM customer_allocation where cid = " + text + ";")
        name=dictfetchall(cursor)
        print(name[0]['name'])
        
        request.session["name"] = name[0]['name']
    return JsonResponse({"result":text})
    
    
@login_required
def search_result(request, text):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest'() and request.method == "GET":
        request.session["stext"] = text
        result = Customer_details.objects.filter(Q(los_details__deal_id__icontains = str(text)) | Q(customer_name__icontains = str(text))| Q(customer_address__primary_phone__icontains = str(text)))

        los_data = []
        result_query = []
        for i in result:
            los_data.append(Los_details.objects.filter(customer_id=i.customer_id).values_list("id", "deal_id", "customer_id"))

        for i, j in enumerate(los_data):
            for k in j:
                documents_list = ''
                if Pan.objects.filter(customer_id=k[2]).count() > 0:
                    documents_list += "," + "1"
                
                if Aadhaar.objects.filter(customer_id=k[2]).count() > 0:
                    documents_list += "," + "2"

                if Itrv.objects.filter(customer_id=k[2]).count() > 0:
                    documents_list += "," + "3"

                if Info.objects.filter(customer_id=k[2]).count() > 0:
                    documents_list += "," + "4"

                if AsseseeDetails.objects.filter(customer_id=k[2]).count() > 0:
                    documents_list += "," + "5"

                if Bank.objects.filter(customer_id=k[2]).count() > 0:
                    documents_list += "," + "6"

                if Salary.objects.filter(customer_id=k[2]).count() > 0:
                        documents_list += "," + "7"

                result_query.append({"documents_list": documents_list, "sresult": result[i].customer_name + " (Deal Id: " + k[1] + ", Phone Number: " + result[i].customer_address.primary_phone + ")", "deal_id":k[1], "los_id": k[0], "customer_id": result[i].customer_id})
        print("search result (selected) query: ",result_query)
        if not len(los_data):
            result_query.append({"sresult": "No results found!"})

        return JsonResponse({"result": result_query})


@login_required
def doclist_page(request, ptype):
    if ptype == "unpro":
        page_heading = "UNPROCESSED DOCUMENT LIST"
        processed_page = False
        unprocessed_page = True
    elif ptype == "pro":
        page_heading = "PROCESSED DOCUMENT LIST"
        processed_page = True
        unprocessed_page = False
    else:
        raise Http404
    
    pdd = Processed_document_details.objects.all()
    unpdd = Unprocessed_document_details.objects.all()

    loan_yeaterday = Processed_document_details.objects.filter(creation_time__lte=datetime.today()-timedelta(days=1), creation_time__gt=datetime.today()-timedelta(days=2)).count()
    loan_last_7_days = Processed_document_details.objects.filter(creation_time__lte=datetime.today(), creation_time__gt=datetime.today()-timedelta(days=7)).count()
    pending_loan = Unprocessed_document_details.objects.count()

    data = []
    if processed_page:
        current = pdd
    elif unprocessed_page:
        current = unpdd
    
    for i in current:
        customer_name = Customer_details.objects.get(customer_id=i.customer_id).customer_name
        document_name = Document_type_master.objects.get(document_id=i.document_id).document_name

        data.append({"id": i.id, "deal_id": i.deal_id, "customer_id": i.customer_id, "customer_name": customer_name, "document_name": document_name, "document_path": i.uploaded_document_path})

    payload = {"doclist_page": True, "pddc": pdd.count(), "unpddc": unpdd.count(), "page_heading": page_heading, "processed_page": processed_page, "unprocessed_page": unprocessed_page, "data": data, "loan_yeaterday": loan_yeaterday, "loan_last_7_days": loan_last_7_days, "pending_loan": pending_loan}
    return render(request, "doclist.html", payload)


@login_required
def delete_doclist_data(request, xid):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest'() and request.method == "POST":
        try:
            delete_ddata = Unprocessed_document_details.objects.get(id=xid)
            delete_ddata.delete()
            return JsonResponse({"status": "success"})
        except Exception as e:
            print(e)
    
    return JsonResponse({"status": "failed"})


@login_required
def loan_page(request, deal_id):
    los_data = Los_details.objects.filter(deal_id=deal_id)
    result_query = []
    
    for i in los_data:
        customer_data = Customer_details.objects.get(customer_id=i.customer_id)

        customer_documents = Processed_document_details.objects.filter(customer_id=i.customer_id)

        # documents_list = ''
        # for customer_document in customer_documents:
        #     documents_list += "," + customer_document.document.document_id
        documents_list = ''
        if Pan.objects.filter(customer_id=i.customer_id).count() > 0:
            documents_list += "," + "1"
        
        if Aadhaar.objects.filter(customer_id=i.customer_id).count() > 0:
            documents_list += "," + "2"

        if Itrv.objects.filter(customer_id=i.customer_id).count() > 0:
            documents_list += "," + "3"

        if Info.objects.filter(customer_id=i.customer_id).count() > 0:
            documents_list += "," + "4"

        if AsseseeDetails.objects.filter(customer_id=i.customer_id).count() > 0:
            documents_list += "," + "5"

        if Bank.objects.filter(customer_id=i.customer_id).count() > 0:
            documents_list += "," + "6"

        if Salary.objects.filter(customer_id=i.customer_id).count() > 0:
            documents_list += "," + "7"


        result_query.append({"los_id": i.id, "deal_id": i.deal_id, "customer_id": i.customer_id, "customer_name": customer_data.customer_name, "customer_dob": customer_data.customer_dob.strftime('%d/%m/%Y'), "customer_aadhaar": customer_data.customer_uid, "customer_district": customer_data.customer_address.district, "customer_state": customer_data.customer_address.state, "customer_pin": customer_data.customer_address.pin_code, "customer_bank": i.bank_name, "customer_account": i.account_no, "documents_list": documents_list})

    payload = {"loan_page": True, "data": result_query}
    return render(request, "loan.html", payload)


@login_required
def upload_page(request, doc_type):
    status = {}
    if doc_type == "aadhaar":
        page_heading = "Aadhaar"
    elif doc_type == "pan":
        page_heading = "PAN"
    else:
        raise Http404
    
    # if "deal_id" not in request.session or "customer_id" not in request.session:
    #     status["type"] = "deal"
    #     status["message"] = "Please select a deal first!"

    payload = {"upload_page": True, "page_heading": page_heading, "status": status}
    return render(request, "upload.html", payload)


@login_required
def set_session(request):
    session_data = request.POST
    deal_id = session_data["lead_id"]
    customer_id = session_data["customer_id"]
    # customer_name = Customer_details.objects.get(customer_id=customer_id).customer_name
    # print("session_data: ", session_data)
    request.session["lead"] = lead_id
    request.session["customer_id"] = customer_id
    # request.session["customer_name"] = customer_name
    print('session')
    return HttpResponse("true")
    

@login_required
def get_pan_image(request):
    if "deal_id" not in request.session or "customer_id" not in request.session:
        return HttpResponse("No images")
    
    deal_id = request.session["deal_id"]
    customer_id = request.session["customer_id"]
    print("deal_id", deal_id)
    print("customer_id", customer_id)

    try:
        pan = Pan.objects.filter(deal_id=deal_id, customer_id=customer_id)[0]
        return HttpResponse(pan.image_name,status=200)
    except:
        # return HttpResponse(status=400)
        return HttpResponse("No images")


@login_required
def remove_pan_image(request):
    file_name = request.POST["file_name"]
    deal_id = request.session["deal_id"]
    customer_id = request.session["customer_id"]
    print("deal_id", deal_id)
    print("customer_id", customer_id)
    print("Deleting Pan image: ", file_name)

    try:        
        Pan.objects.filter(deal_id=deal_id, customer_id=customer_id, image_name=file_name).delete()
        return HttpResponse("success")
    except:
        # return HttpResponse(status=400)
        return HttpResponse("error")


@login_required
def get_aadhaar_image(request):
    if "deal_id" not in request.session or "customer_id" not in request.session:
        return HttpResponse("No images")

    deal_id = request.session["deal_id"]
    customer_id = request.session["customer_id"]
    print("deal_id", deal_id)
    print("customer_id", customer_id)

    try:
        aadhaar = Aadhaar.objects.filter(deal_id=deal_id, customer_id=customer_id)[0]
        return HttpResponse(aadhaar.image_name,status=200)
    except:
        return HttpResponse(status=400)


@login_required
def remove_aadhaar_image(request):
    print("in to remove aadhaar image")
    file_name = request.POST["file_name"]
    deal_id = request.session["deal_id"]
    customer_id = request.session["customer_id"]
    print("deal_id", deal_id)
    print("customer_id", customer_id)
    print("Deleting Aadhaar image: ", file_name)

    try:        
        Aadhaar.objects.filter(deal_id=deal_id, customer_id=customer_id, image_name=file_name).delete()
        return HttpResponse("success")
    except:
        # return HttpResponse(status=400)
        return HttpResponse("error")


@login_required
def get_itrv_form16_form26as_files(request):
    deal_id = request.session["deal_id"]
    customer_id = request.session["customer_id"]
    try:
        uploaded_itrv_form16_form26as_details = Uploaded_itrv_form16_form26as_details.objects.filter(deal_id=deal_id, customer_id=customer_id)
        data_list = []
        for item in uploaded_itrv_form16_form26as_details:
            data = {}
            data['year'] = item.year
            data['document_type'] = item.document_type
            data['file_name'] = item.file_name
            data_list.append(data)

        print("get_itrv_form16_form26as_files data: ", data_list)
        return HttpResponse(json.dumps(data_list))
    except:
        return HttpResponse("error")


@login_required
def remove_itrv_image(request):
    print("in to remove itrv image")
    file_name = request.POST["file_name"]
    deal_id = request.session["deal_id"]
    customer_id = request.session["customer_id"]
    print("deal_id", deal_id)
    print("customer_id", customer_id)
    print("Deleting itrv image: ", file_name)

    try:        
        Itrv.objects.filter(deal_id=deal_id, customer_id=customer_id, image_name=file_name).delete()
        Uploaded_itrv_form16_form26as_details.objects.filter(deal_id=deal_id, customer_id=customer_id, file_name=file_name).delete()

        return HttpResponse("success")
    except:
        # return HttpResponse(status=400)
        return HttpResponse("error")


@login_required
def remove_form16_image(request):
    print("in to remove form16 image")
    file_name = request.POST["file_name"]
    deal_id = request.session["deal_id"]
    customer_id = request.session["customer_id"]
    print("deal_id", deal_id)
    print("customer_id", customer_id)
    print("Deleting form16 image: ", file_name)

    try:        
        Info.objects.filter(deal_id=deal_id, customer_id=customer_id, image_name=file_name).delete()
        Uploaded_itrv_form16_form26as_details.objects.filter(deal_id=deal_id, customer_id=customer_id, file_name=file_name).delete()

        return HttpResponse("success")
    except:
        # return HttpResponse(status=400)
        return HttpResponse("error")


@login_required
def remove_form26as_image(request):
    print("in to remove form26as image")
    file_name = request.POST["file_name"]
    deal_id = request.session["deal_id"]
    customer_id = request.session["customer_id"]
    print("deal_id", deal_id)
    print("customer_id", customer_id)
    print("form26as itrv image: ", file_name)

    try:        
        AsseseeDetails.objects.filter(deal_id=deal_id, customer_id=customer_id, image_name=file_name).delete()
        Uploaded_itrv_form16_form26as_details.objects.filter(deal_id=deal_id, customer_id=customer_id, file_name=file_name).delete()

        return HttpResponse("success")
    except:
        # return HttpResponse(status=400)
        return HttpResponse("error")


@login_required
def get_bank_statement_files(request):
    deal_id = request.session["deal_id"]
    customer_id = request.session["customer_id"]
    try:
        uploaded_bank_statements_details = Uploaded_bank_statements_details.objects.filter(deal_id=deal_id, customer_id=customer_id)
        data_list = []
        for item in uploaded_bank_statements_details:
            data = {}
            data['action_type'] = item.action_type
            data['bank_index'] = item.bank_index
            data['bank_name'] = item.bank_name
            data['bank_id'] = item.bank_id
            data['file_name'] = item.file_name
            data_list.append(data)

        print("get_uploaded_bank_statements_details data: ", data_list)
        return HttpResponse(json.dumps(data_list))
    except:
        return HttpResponse("error")


@login_required
def remove_bank_statements(request):
    print("in to remove bank statements image")
    file_name = request.POST["file_name"]
    deal_id = request.session["deal_id"]
    customer_id = request.session["customer_id"]
    print("deal_id", deal_id)
    print("customer_id", customer_id)
    print("form26as itrv image: ", file_name)

    try:        
        Bank.objects.filter(deal_id=deal_id, customer_id=customer_id, image_name=file_name).delete()
        Uploaded_bank_statements_details.objects.filter(deal_id=deal_id, customer_id=customer_id, file_name=file_name).delete()

        return HttpResponse("success")
    except:
        # return HttpResponse(status=400)
        return HttpResponse("error")


@login_required
def add_user_details(request):
    data = request.POST
    # print(data)
    deal_id = data['deal_id']
    customer_id = data['customer_id']
    name = data['name']
    dob = data['dob']
    aadhaar = data['aadhaar']
    district_info = data['dist']
    dist_id = district_info.split(',')[0]
    state_info = data['state']
    state_id = state_info.split(',')[0]
    pin_code = data['pin_code']
    bank_info = data['bank']
    bank_id = bank_info.split(',')[0]
    account_no = data['account_no']

    request.session["deal_id"] = deal_id
    request.session["customer_id"] = customer_id

    # status = Los_details.objects.get(customer_id=customer_id, deal_id=deal_id)
    # print("Status: ", status)

    customer_details = Customer_details.objects.create(customer_id = customer_id,
                                            customer_name = name,
                                            customer_dob = normalize_date(dob),
                                            customer_uid = aadhaar,
    )

    state_master = State_master.objects.get(state_id = state_id)

    district_master = District_master.objects.get(district_id = dist_id)
    
    Customer_address.objects.create(customer = customer_details,
                                            state = state_master,
                                            district = district_master,
                                            pin_code = pin_code,
    )

    bank_master = Bank_master.objects.get(bank_id = bank_id)

    Los_details.objects.create(deal_id = deal_id,
                                            bank_name = bank_master,
                                            account_no = account_no,
                                            customer = customer_details,
    )

    return HttpResponse("true")


@login_required
def upload_form_page(request):
    payload = {"upload_form_page": True}
    return render(request, "upload_form.html", payload)


@login_required
def upload_bank_statement_page(request):
    bdata = Bank.objects.all()
    banks = bdata.filter(customer_id=request.session["customer_id"]).values('bank_name', 'account_number').distinct()
    try:
        bank1 = banks[0]['bank_name'] if banks[0]['bank_name'] else "NA"
    except:
        bank1 = '-'
    try:
        bank2 = banks[1]['bank_name'] if banks[1]['bank_name'] else "NA"
    except:
        bank2 = '-'
    try:
        bank3 = banks[2]['bank_name'] if banks[2]['bank_name'] else "NA"
    except:
        bank3 = '-'
    try:
        acc1 = banks[0]['account_number'] if banks[0]['account_number'] else "NA"
    except:
        acc1 = '-'
    try:
        acc2 = banks[1]['account_number'] if banks[1]['account_number'] else "NA"
    except:
        acc2 = '-'
    try:
        acc3 = banks[2]['account_number'] if banks[2]['account_number'] else "NA"
    except:
        acc3 = '-'
   
    count1 = bdata.filter(customer_id=request.session["customer_id"], bank_name=bank1, account_number=acc1).values('image_name').distinct().count()
    count2 = bdata.filter(customer_id=request.session["customer_id"], bank_name=bank2, account_number=acc2).values('image_name').distinct().count()
    count3 = bdata.filter(customer_id=request.session["customer_id"], bank_name=bank3, account_number=acc3).values('image_name').distinct().count()
    count1 = np.where(count1==0, '-', count1)
    count2 = np.where(count2==0, '-', count2)
    count3 = np.where(count3==0, '-', count3)

    query1 = bdata.filter(customer_id=request.session["customer_id"], bank_name=bank1, account_number=acc1)
    if query1.exists():
        start1 = getattr(query1.earliest('txn_date'), 'txn_date')
        end1 = getattr(query1.latest('txn_date'), 'txn_date')
    else:
        start1 = '-'
        end1 = '-'
    
    query2 = bdata.filter(customer_id=request.session["customer_id"], bank_name=bank2, account_number=acc2)
    if query2.exists():
        start2 = getattr(query2.earliest('txn_date'), 'txn_date')
        end2 = getattr(query2.latest('txn_date'), 'txn_date')
    else:
        start2 = '-'
        end2 = '-'
    
    query3 = bdata.filter(customer_id=request.session["customer_id"], bank_name=bank3, account_number=acc3)
    if query3.exists():
        start3 = getattr(query3.earliest('txn_date'), 'txn_date')
        end3 = getattr(query3.latest('txn_date'), 'txn_date')
    else:
        start3 = '-'
        end3 = '-'
    
    payload = {"upload_bank_statement_page": True, "bank1": bank1, "bank2":bank2, "bank3": bank3, "acc1": acc1, "acc2": acc2, "acc3": acc3, "count1": count1, "count2": count2, "count3": count3, "start1": start1, "end1": end1, "start2": start2, "end2": end2, "start3": start3, "end3": end3}
    return render(request, "upload_bank_statement.html", payload)



@login_required
def table_page(request):
    payload = {"table_page": True}
    return render(request, "table.html", payload)

@login_required
def analyze_page(request):
    payload = {"analyze_page": True}
    return render(request, "summary.html", payload)

@login_required
def bank_customer_month_kpi(request):
    payload = {"bank_customer_month_kpi": True, 'data':data}
    return render(request, "bcmk.html", payload)

@login_required
def bank_customer_kpi(request):
    payload = {"bank_customer_kpi": True, 'data':data}
    return render(request, "bck.html", payload)



def leadsearch(request,text):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest'() and request.method == "GET":
        print(text)
        with connection.cursor() as cursor:
            sql_query = "SELECT tld.lead_id,tld.name FROM a3_kit.los_did_cid_generation as tld where tld.lead_id LIKE " + "'" + text + "%'" + "or" + " tld.name LIKE " + "'" + text + "%'" + ";"
            cursor.execute(sql_query)
            data = dictfetchall(cursor)
            print(data)
            if not len(data):
                messages.info(request, "No results found!")
            else :
                return JsonResponse({"result":data})


@login_required

def upload_statments(request):

    payload = {"upload_statments": True, 'data':data}
    return render(request, 'upload_files.html', payload)


@login_required
def statement(request):
    payload = {"statement": True, 'data':data}
    return render(request, "statement.html", payload)
