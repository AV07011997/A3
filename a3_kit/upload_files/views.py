import os
import time
import boto3
import tabula
import datetime
# import schedule
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.db import connection
from django.contrib import messages


# Create your views here.
from django.shortcuts import HttpResponse


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


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


@login_required
def upload_statments(request):
    # print(request.session["lead_session"])

    if "lead_session" not in request.session:
        print("no")

    data = ""
    data1 = ""
    data2=""
    if "lead_session" in request.session:
        lead_id = request.session["lead_session"]
        print(lead_id)
        with connection.cursor() as cursor:
            sql_query = "SELECT SUM(case when type=" + "'" + "bank" + "'" + " THEN 1 ELSE 0 END) AS bank_count,name,lead_id,SUM(case when type=" + "'" + "itr" + "'" + " THEN 1 ELSE 0 END) AS itr_count FROM a3_kit.upload_file_details as tld where tld.lead_id LIKE " + "'%" + lead_id + "%'" + ";"
            cursor.execute(sql_query)
            data = dictfetchall(cursor)
            print(data)
        with connection.cursor() as cursor:
            # sql_query = "SELECT tld.lead_id,tld.name,SUM(case when type="+"'"+"bank"+"'"+ " THEN 1 ELSE 0 END) AS bank_count,SUM(case when type="+ "'" +"itr"+"'"+" THEN 1 ELSE 0 END) AS itr_count FROM a3_kit.test_leaddetails as tld Left join a3_kit.bank_statment_of_lead as bsl ON tld.lead_id=bsl.lead_id where tld.lead_id LIKE " + "'" + text + "%'" + "or" + " tld.name LIKE " + "'" + text + "%'" + ";"
            sql_query = "SELECT tld.lead_id,tld.name FROM a3_kit.los_lid_generation as tld where tld.lead_id LIKE " + "'%" + lead_id + "%'" + ";"
            cursor.execute(sql_query)
            data1 = dictfetchall(cursor)
            print(data1)

        with connection.cursor() as cursor:
            cursor.execute("select file_name, date from upload_file_details where lead_id = " + lead_id + ";")
            data2 = dictfetchall(cursor)

    return render(request, 'upload_files.html', {'data': data, 'data1': data1, 'data2': data2})


@login_required
def search_by_lead_name(request, text):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "GET":
        text = text
        print(text)
        with connection.cursor() as cursor:
            # sql_query = "SELECT tld.lead_id,tld.name,SUM(case when type="+"'"+"bank"+"'"+ " THEN 1 ELSE 0 END) AS bank_count,SUM(case when type="+ "'" +"itr"+"'"+" THEN 1 ELSE 0 END) AS itr_count FROM a3_kit.test_leaddetails as tld Left join a3_kit.bank_statment_of_lead as bsl ON tld.lead_id=bsl.lead_id where tld.lead_id LIKE " + "'" + text + "%'" + "or" + " tld.name LIKE " + "'" + text + "%'" + ";"
            sql_query = "SELECT tld.lead_id,tld.name FROM a3_kit.los_lid_generation as tld where tld.lead_id LIKE " + "'" + text + "%'" + "or" + " tld.name LIKE " + "'" + text + "%'" + ";"
            cursor.execute(sql_query)
            data = dictfetchall(cursor)
            print(data)
            if not len(data):
                messages.info(request, "No results found!")
            else:
                return JsonResponse({"result": data})


@login_required
def get_count_by_lead_id_name(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        lead_id = request.POST.get('id')
        lead_name = request.POST.get('name')
        request.session["lead_session"] = lead_id
        with connection.cursor() as cursor:
            sql_query = "SELECT SUM(case when type=" + "'" + "bank" + "'" + " THEN 1 ELSE 0 END) AS bank_count,SUM(case when type=" + "'" + "itr" + "'" + " THEN 1 ELSE 0 END) AS itr_count FROM a3_kit.upload_file_details as tld where tld.lead_id LIKE " + "'" + lead_id + "%'" + "and" + " tld.name LIKE " + "'" + lead_name + "%'" + ";"
            cursor.execute(sql_query)
            data = dictfetchall(cursor)
            data[0]["lead_id"] = lead_id
            data[0]["name"] = lead_name
            if not len(data):
                messages.info(request, "No results found!")
            else:
                return JsonResponse({"result": data})


@login_required
def find_files(filename, search_path):
    file = search_path + "" + filename
    for root, dir, files in os.walk(search_path):
        if filename in files:
            os.remove(file)
        else:
            time.sleep(30)
            os.remove(file)


def cutFile(f):
    file_name = str(f.name)
    try:
        print('hello1')
        with open(file_name, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        destination.close()
    except Exception as e:
        print(e);
        if e:
            file_name = e

    return file_name


@login_required
def uploadBankStatments(request):
    lead_id = request.POST.get('id')
    lead_name = request.POST.get('name')
    bank_count = request.POST.get('bank_count')
    deleted_files = request.POST.get('deleted_file')
    if str(bank_count) == 'null' or str(bank_count) == 'None':
        bank_count = 0
    result = ''
    result_count = ''
    deleted_file = deleted_files.split(',')
    if (len(request.FILES) > 0):
        uploaded_file = ''
        next_count = int(bank_count) + 1
        for item in range(len(request.FILES)):
            uploaded_file = request.FILES['upload[' + str(item) + ']']
            print('uploaded_file=', uploaded_file)
            key = cutFile(uploaded_file)
            print('key =', key)
            if key in deleted_file:
                continue;
            else:
                try:
                    s3_client = boto3.client('s3')
                    bucket = 'a3bank'
                    key = cutFile(uploaded_file)

                    s3_client.upload_file(key, bucket, lead_id + '_' + str(next_count) + '_' + key)
                    result = 'Bank File successfully uploaded.'
                    next_count += 1
                    file_name = key

                    with connection.cursor() as cursor:
                        sql_query = "INSERT INTO a3_kit.upload_file_details(lead_id, name, date, file_name,type ) VALUES(" + lead_id + ",'" + lead_name + "'" + ", now() ," + "'" + file_name + "','" + "bank" + "'" + ");"
                        cursor.execute(sql_query)
                    try:
                        file_path = "D:/prudhvi/Dev/a3-kit/a3_kit/"
                        find_files(file_name, file_path)
                    except Exception as e:
                        pass
                    with connection.cursor() as cursor:
                        sql_query = "SELECT SUM(case when type=" + "'" + "bank" + "'" + " THEN 1 ELSE 0 END) AS bank_count,SUM(case when type=" + "'" + "itr" + "'" + " THEN 1 ELSE 0 END) AS itr_count FROM a3_kit.upload_file_details as tld where tld.lead_id LIKE " + "'" + lead_id + "%'" + "and" + " tld.name LIKE " + "'" + lead_name + "%'" + ";"
                        cursor.execute(sql_query)
                        result_count = dictfetchall(cursor)
                except Exception as e:
                    result = e
                    print(result)
    return JsonResponse({"result": result, "count": result_count})


@login_required
def uploadITRStatments(request):
    lead_id = request.POST.get('id')
    lead_name = request.POST.get('name')
    itr_count = request.POST.get('itr_count')
    deleted_files = request.POST.get('deleted_file')
    print(str(itr_count))
    if str(itr_count) == 'None' or str(itr_count) == 'null':
        itr_count = 0
    result = ''
    result_count = ''
    deleted_file = deleted_files.split(',')
    if (len(request.FILES) > 0):
        next_count = int(itr_count) + 1
        for item in range(len(request.FILES)):
            uploaded_file = request.FILES['upload[' + str(item) + ']']
            key = cutFile(uploaded_file)
            if key in deleted_file:
                continue;
            else:
                try:
                    s3_client = boto3.client('s3')
                    bucket = 'a3itr'
                    key = cutFile(uploaded_file)
                    s3_client.upload_file(key, bucket, lead_id + '_' + str(next_count) + '_' + key)
                    result = 'ITR File successfully uploaded.'
                    next_count += 1
                    file_name = key
                    with connection.cursor() as cursor:
                        sql_query = "INSERT INTO a3_kit.upload_file_details(lead_id, name, date, file_name,type ) VALUES(" + lead_id + ",'" + lead_name + "'" + ", now() ," + "'" + file_name + "','" + "itr" + "'" + ");"
                        cursor.execute(sql_query)
                    try:
                        file_path = r"D:\prudhvi\Dev\a3-kit\a3_kit\\"
                        find_files(file_name, file_path)
                    except Exception as e:
                        pass
                    with connection.cursor() as cursor:
                        sql_query = "SELECT SUM(case when type=" + "'" + "bank" + "'" + " THEN 1 ELSE 0 END) AS bank_count,SUM(case when type=" + "'" + "itr" + "'" + " THEN 1 ELSE 0 END) AS itr_count FROM a3_kit.upload_file_details as tld where tld.lead_id LIKE " + "'" + lead_id + "%'" + "and" + " tld.name LIKE " + "'" + lead_name + "%'" + ";"
                        cursor.execute(sql_query)
                        result_count = dictfetchall(cursor)
                except Exception as e:
                    result = e
                    print(result)
    return JsonResponse({"result": result, "count": result_count})


@login_required
def download_statments(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(file_name) as bank_upload , COUNT(distinct(lead_id)) as lead_id FROM upload_file_details WHERE type='bank';")
        count_bank = cursor.fetchall()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(file_name) as bank_upload , COUNT(distinct(lead_id)) as lead_id FROM upload_file_details WHERE type='itr';")
        count_itr = cursor.fetchall()
    # with connection.cursor() as cursor:
    #     cursor.execute("SELECT COUNT(file_name) as bank_upload FROM bank_statment_of_lead;")
    #     count_total=cursor.fetchall()
    count_total = int(count_bank[0][0]) + int(count_itr[0][0])
    print(count_total)
    print(count_bank[0][0])
    if (count_bank[0][1] > count_itr[0][1]):
        max1 = count_bank[0][1]
    if (count_bank[0][1] < count_itr[0][1]):
        max1 = count_itr[0][1]
    if (count_bank[0][1] == count_itr[0][1]):
        max1 = count_itr[0][1]
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT count(file_name) as download,count(distinct(lead_id))   FROM downloaded_file_details where substring(file_name,-5,1)='b' ;")
        count_bank1 = cursor.fetchall()
        print(count_bank1)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT count(file_name) as download,count(distinct(lead_id))   FROM downloaded_file_details where substring(file_name,-5,1)='i' ;")
        count_itr1 = cursor.fetchall()
    if (count_bank1[0][1] > count_itr1[0][1]):
        max2 = count_bank1[0][1]
    if (count_bank1[0][1] < count_itr1[0][1]):
        max2 = count_itr1[0][1]
    if (count_bank1[0][1] == count_itr1[0][1]):
        max2 = count_itr1[0][1]

    count_total1 = int(count_bank1[0][0]) + int(count_itr1[0][0])
    if "lead_session" in request.session:
        lead_id = request.session["lead_session"]
        print(lead_id)
        print("xxx")
        with connection.cursor() as cursor:
            sql_query = "SELECT distinct(customer_id) ,lead_id,deal_id, name,bank,account_number FROM a3_kit.los_did_cid_generation  where lead_id=" + lead_id + ";"
            cursor.execute(sql_query)
            data = dictfetchall(cursor)
            print((data))
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT distinct(cid),lid,did,name FROM a3_kit.customer_allocation where lid = " + lead_id + ";")
            customer_detail1 = dictfetchall(cursor)
            print(customer_detail1)

            if not len(data):
                messages.info(request, "No results found!")
            else:
                with connection.cursor() as cursor:
                    sql_query = "SELECT COUNT(lead_id) AS count FROM a3_kit.downloaded_file_details  where lead_id=" + "'" + lead_id + "'" + ";"
                    cursor.execute(sql_query)
                    result_count = dictfetchall(cursor)
                    print(result_count)

                    return render(request, 'download_file.html',
                                  {'count_bank': count_bank, 'count_itr': count_itr, 'max1': max1,
                                   'count_total': count_total, 'count_bank1': count_bank1, 'count_itr1': count_itr1,
                                   'max2': max2, 'count_total1': count_total1, "result": data, "count": result_count,
                                   'data': customer_detail1})

    return render(request, 'download_file.html',
                  {'count_bank': count_bank, 'count_itr': count_itr, 'max1': max1, 'count_total': count_total,
                   'count_bank1': count_bank1, 'count_itr1': count_itr1, 'max2': max2, 'count_total1': count_total1})


@login_required
def search_by_lead_name_for_download(request, text):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "GET":
        text = text
        with connection.cursor() as cursor:
            sql_query = "SELECT tld.lead_id,tld.name FROM a3_kit.los_did_cid_generation as tld where tld.lead_id LIKE " + "'" + text + "%'" + "or" + " tld.name LIKE " + "'" + text + "%'" + ";"
            cursor.execute(sql_query)
            data = dictfetchall(cursor)
            if not len(data):
                messages.info(request, "No results found!")
            else:
                return JsonResponse({"result": data})


@login_required
def get_about_lead_id(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        lead_id = request.POST.get('id')
        print(lead_id)
        print("YYY")
        request.session["lead_session"] = lead_id
        # lead_name = request.POST.get('name')
        with connection.cursor() as cursor:
            sql_query = "SELECT distinct(customer_id) ,lead_id,deal_id, name,bank,account_number FROM a3_kit.los_did_cid_generation  where lead_id=" + lead_id + ";"
            cursor.execute(sql_query)
            data = dictfetchall(cursor)
            if not len(data):
                messages.info(request, "No results found!")
            else:
                with connection.cursor() as cursor:
                    sql_query = "SELECT COUNT(lead_id) AS count FROM a3_kit.downloaded_file_details  where lead_id=" + "'" + lead_id + "'" + ";"
                    cursor.execute(sql_query)
                    result_count = dictfetchall(cursor)

                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT dbs.lead_id, dbs.name,dbs.customer_id FROM a3_kit.los_did_cid_generation as dbs where dbs.lead_id=" + lead_id + ";")
                    cust_details = dictfetchall(cursor)

                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT bank_name as sub_type,account_name as name,account_number as identifier from a3_kit.bank_bank as bk where deal_id=" + deal_id + " group by account_number;")
                    bank_updated_result = dictfetchall(cursor)

                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT name,pan as identifier FROM a3_kit.itrv_itrv  where deal_id=" + deal_id + " group by pan ;")
                    itr_updated_result = dictfetchall(cursor)
                    print(itr_updated_result)

                list1 = []
                if len(bank_updated_result) > 0:
                    for obj in bank_updated_result:
                        obj["doc_type"] = "BANK"
                        list1.append(obj)
                if len(itr_updated_result) > 0:
                    for obj in itr_updated_result:
                        obj["doc_type"] = "ITR"
                        obj["sub_type"] = "ITR V"
                        list1.append(obj)
                # if len(form16_challans_updated_result)>0:
                #     for obj in form16_challans_updated_result:
                #         list1.append(obj)
                print(list1)

                return_data = list1

                return JsonResponse(
                    {"result": data, "count": result_count, "afterdownload": return_data, "cust_details": cust_details})


@login_required
def download_files_by_lead(request):
    print("Hello1")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        print("Hello2")
        lead_id = request.POST.get('id')
        bucket = 'digitizedfiles'
        s3 = boto3.resource('s3')
        objects_bank = s3.Bucket(bucket).objects.filter(Prefix=lead_id)
        result = ''
        for obj in objects_bank:
            try:
                # file = r'd:\bank\{}'.format(obj.key)
                file_name = obj.key
                #s3.Bucket(bucket).download_file(obj.key, r'D:\digitizedfiles\{}'.format(obj.key))  ###download file to bank folder
                s3.Bucket(bucket).download_file(obj.key, '/Users/hardikbhardwaj/Desktop/digitised/{}'.format(obj.key))

                s3.Object(bucket, obj.key).delete()  ### delete downloaded file from AWS
                result = 'Successfuly download files!'
                with connection.cursor() as cursor:
                     sql_query = "INSERT INTO a3_kit.downloaded_file_details(lead_id, file_name, date) VALUES(" + lead_id + ",'" + file_name + "'" + ", now() " + ");"
                     cursor.execute(sql_query)
            except Exception as e:
                result = e

        # else:
        #     result = 'No Found, Please try again!'
        with connection.cursor() as cursor:
            sql_query = "SELECT COUNT(lead_id) AS count FROM a3_kit.downloaded_file_details  where lead_id=" + "'" + lead_id + "'" + ";"
            cursor.execute(sql_query)
            result_count = dictfetchall(cursor)

        return_data = addindatabasefromcsv(request)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT dbs.lead_id, dbs.name,dbs.customer_id FROM a3_kit.los_did_cid_generation as dbs where dbs.lead_id=" + lead_id + ";")
            cust_details = dictfetchall(cursor)

    return JsonResponse(
        {"result": result, "count": result_count, "afterdownload": return_data, "cust_details": cust_details})


import pandas as pd
import glob
import numpy as np


@login_required
def addindatabasefromcsv(request):
    lid = request.POST.get('id')
    #files = glob.glob(r'D:\digitizedfiles\\*')
    files = glob.glob('/Users/hardikbhardwaj/Desktop/digitised/*')
    list1 = []
    bank_updated_result = ''
    itr_updated_result = ''
    form16_challans_updated_result = ''
    form16_info_updated_result = ''
    form16_partb_updated_result = ''
    form16_quarters_updated_result = ''
    form26as_asseseedetails_updated_result = ''
    form26as_parta_updated_result = ''
    form26as_partb_updated_result = ''
    form26as_partc_updated_result = ''
    form26as_partd_updated_result = ''
    form26as_partg_updated_result = ''
    # print(files)
    for file in files:
        file2 = str(file).split('_')
        file1 = file2[len(file2) - 1][:1]

        if file1 == "b":
            reader = pd.read_csv(file)
            reader['Txn Date'] = pd.to_datetime(reader['Txn Date'], format="%d/%m/%Y")
            reader['Txn Date'] = reader['Txn Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
            reader = reader.replace(np.nan, 'NA')
            reader['creation_time'] = datetime.datetime.now()

            reader['last_modification_time'] = datetime.datetime.now()
            reader['image_name'] = "asmfbejhb"
            reader['customer_id'] = 0
            reader['created_by_id'] = 1

            for i in range(len(reader)):
                row = reader.iloc[i]
                with connection.cursor() as cursor:
                    cursor.execute(
                        "insert into bank_bank(txn_date,description,cheque_number,debit,credit,balance,account_name,account_number,mode,entity,source_of_trans,sub_mode,transaction_type,bank_name,deal_id,creation_time,last_modification_time,image_name,customer_id,created_by_id) values(%s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s,%s, %s,%s)",
                        row)
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT bank_name as sub_type,account_name as name,account_number as identifier from a3_kit.bank_bank as bk where deal_id=" + lid + " group by account_number;")
                bank_updated_result = dictfetchall(cursor)
            os.remove(file)
            continue;

        if file1 == "i":
            file3 = file2[1]
            file4 = file2[2]
            if file3 == "form16":
                if file4 == "challans":
                    reader = pd.read_csv(file)
                    reader['tax_deposited_date'] = pd.to_datetime(reader['tax_deposited_date'])
                    reader['tax_deposited_date'] = reader['tax_deposited_date'].apply(lambda x: x.strftime('%Y-%m-%d'))
                    reader['tax_deposited_date'] = reader['tax_deposited_date'].astype('str')
                    reader = reader.replace(np.nan, 'NA')
                    reader['creation_time'] = datetime.datetime.now()
                    reader['creation_time'] = reader['creation_time'].astype('str')
                    reader['last_modification_time'] = datetime.datetime.now()
                    reader['last_modification_time'] = reader['last_modification_time'].astype('str')
                    for i in range(len(reader)):
                        row = reader.iloc[i]
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "insert into form16_challans(tax_deposited,bsr_code,tax_deposited_date,challan_serial_no,status_match_oltas,assessment_year,pan_of_the_employee,lid,creation_time,last_modification_time) values(%s, %s, %s,%s, %s, %s,%s, %s, %s,%s)",
                                row)
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "SELECT pan_of_the_employee as identifier FROM a3_kit.form16_challans  where lid=" + lid + " group by pan_of_the_employee ;")
                            form16_challans_updated_result = dictfetchall(cursor)
                    os.remove(file)
                    continue;

                if file4 == "info":
                    reader = pd.read_csv(file)
                    reader = reader.replace(np.nan, 'NA')
                    reader['creation_time'] = datetime.datetime.now()
                    reader['last_modification_time'] = datetime.datetime.now()

                    for i in range(len(reader)):
                        row = reader.iloc[i]
                        with connection.cursor() as cursor:
                            # cursor.execute("insert into form16_info(certification_no,last_updated_on,pan_of_the_deductor,tan_of_the_deductor,pan_of_the_employee,assessment_year,period_with_the_employer_from,period_with_the_employer_to,employer_name,employer_address,employee_name,employee_address,image_name,lid,creation_time,last_modification_time) values(%s, %s, %s,%s, %s, %s,%s, %s, %s,%s,%s, %s,%s, %s, %s, %s)",row)
                            cursor.execute("insert into form16_info(assessment_year,certification_no,employee_address,employee_name,employer_address,employer_name,last_updated_on,pan_of_the_deductor,pan_of_the_employee,period_with_the_employer_from,period_with_the_employer_to,tan_of_the_deductor,image_name,lid,creation_time,last_modification_time) values(%s, %s, %s,%s, %s, %s,%s, %s, %s,%s,%s, %s,%s, %s, %s, %s)",row)
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "SELECT employee_name as name,pan_of_the_employee as identifier FROM a3_kit.form16_info  where lid=" + lid + " group by pan_of_the_employee ;")
                            form16_info_updated_result = dictfetchall(cursor)
                    os.remove(file)
                    continue;
                if file4 == "partb":
                    reader = pd.read_csv(file)
                    reader = reader.replace(np.nan, 'NA')
                    reader['creation_time'] = datetime.datetime.now()
                    reader['last_modification_time'] = datetime.datetime.now()

                    for i in range(len(reader)):
                        row = reader.iloc[i]
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "insert into form16_partb(gross_salary_salary_as_per_provisions_contained_in_section_17_1,gross_salary_value_of_perquisites_under_section_17_2,gross_salary_profits_in_lieu_of_salary_under_section_17_3,gross_salary_total,gr_sal_rprtd_total_amount_of_sal_received_from_other_employers,less_allowance_to_the_extent_exempt_under_section_10,travel_concession_or_assistance_under_section_10_5,death_cum_retirement_gratuity_under_section_10_10,commuted_value_of_pension_under_section_10_10a,cash_equivalent_of_leave_salary_encashment_under_section_10_10aa,house_rent_allowance_under_section_10_13a,amount_of_any_other_exemption_under_section_10,total_amount_of_any_other_exemption_under_section_10,total_amount_of_exemption_claimed_under_section_10,total_amount_of_sal_received_from_current_employer_1d_minus_2h,standard_deduction_under_section_16_ia,entertainment_allowance_under_section_16_ii,tax_on_employment_under_section_16_iii,total_amount_of_deductions_under_section_16_4a_plus_4b_plus_4c,income_chargeable_under_the_head_salaries_3_plus_1e_minus_5,incm_or_admsble_los_frm_house_prprty_rprtd_by_empyee_ofr_for_tds,income_under_the_head_other_sources_offered_for_tds,total_amount_of_other_income_reported_by_the_employee_7a_plus_7b,gross_total_income_6_plus_8,ductn_in_rspct_of_lfe_inc_prmia_cntrbn_2_pf_undr_sec_80c_gr_amnt,ductn_in_rspct_of_ctrbtn_2_crtn_pnsn_fnds_undr_sec_80ccc_gr_amnt,dctn_in_rsp_of_cntbn_by_txpr_2_pnsn_scm_undr_sec_80ccd_1_gr_amnt,total_deduction_under_section_80c_80ccc_and_80ccd_1_gross_amount,dtn_in_rsp_of_amnt_pd_dpt_2_ntfd_pnsn_scm_ndr_sc_80ccd_1b_gr_amt,dtn_in_rsp_of_cntrbtn_by_empyr_2_pnsn_scm_ndr_sc_80ccd_2_gr_amt,dtn_in_rsp_of_hlt_insrnc_premia_ndr_sc_80d_gr_amt,dtn_in_rsp_of_intst_on_ln_tkn_for_hghr_edu_ndr_sec_80e_gr_amt,ttl_dtn_in_rsp_of_dntn_2_crtn_fnds_crtbl_ins_ndr_sc_80g_gr_amt,dctn_in_rsp_of_inrst_on_dpst_in_svng_acnt_ndr_sec_80tta_gr_amt,amt_deductible_under_any_other_provisions_of_cptr_vi_a_gr_amt,ttl_of_amt_deductible_under_any_other_provisions_of_chapter_vi_a,aggregate_of_deductible_amount_under_chapter_vi_a,total_taxable_income_9_minus_11,tax_on_total_income,rebate_under_section_87a_if_applicable,surcharge_wherever_applicable,health_and_education_cess,tax_payable_13_plus_15_plus_16_minus_14,relief_under_section_89,net_tax_payable_17_minus_18,assessment_year,pan_of_the_employee,lid,creation_time,last_modification_time) values(%s, %s, %s,%s, %s, %s,%s,%s,%s, %s,%s, %s, %s,%s,%s,%s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s,%s,%s, %s,%s, %s, %s,%s,%s,%s,%s,%s,%s,%s, %s,%s, %s, %s,%s,%s,%s,%s,%s,%s,%s)",
                                row)
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "SELECT pan_of_the_employee as identifier FROM a3_kit.form16_partb  where lid=" + lid + " group by pan_of_the_employee ;")
                            form16_partb_updated_result = dictfetchall(cursor)
                    os.remove(file)
                    continue;
                if file4 == "quarters":
                    reader = pd.read_csv(file)
                    reader = reader.replace(np.nan, 'NA')
                    reader['creation_time'] = datetime.datetime.now()
                    reader['last_modification_time'] = datetime.datetime.now()

                    for i in range(len(reader)):
                        row = reader.iloc[i]
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "insert into form16_quarters(quarter,reciept_number,amount_credited,tax_deducted,tax_remitted,assessment_year,pan_of_the_employee,lid,creation_time,last_modification_time) values(%s, %s,%s, %s,%s, %s, %s,%s, %s,%s)",
                                row)
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "SELECT pan_of_the_employee as identifier FROM a3_kit.form16_quarters  where lid=" + lid + " group by pan_of_the_employee ;")
                            form16_quarters_updated_result = dictfetchall(cursor)
                    os.remove(file)
                    continue;
            if file3 == "form26as":
                if file4 == "asseseedetails":
                    reader = pd.read_csv(file)
                    reader = reader.replace(np.nan, 'NA')
                    reader['creation_time'] = datetime.datetime.now()
                    reader['last_modification_time'] = datetime.datetime.now()

                    for i in range(len(reader)):
                        row = reader.iloc[i]
                        with connection.cursor() as cursor:
                            # cursor.execute("insert into form26as_asseseedetails(pan,financial_year,assessment_year,current_pan_status,name_of_assessee,address_of_assessee,deal_id,image_name,lid,creation_time,last_modification_time) values(%s, %s, %s,%s, %s, %s,%s,%s, %s,%s, %s)",row)
                            cursor.execute(
                                "insert into form26as_asseseedetails(pan,financial_year,assessment_year,current_pan_status,name_of_assessee,address_of_assessee,image_name,lid,creation_time,last_modification_time) values(%s, %s, %s,%s, %s, %s,%s,%s, %s, %s)",
                                row)
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "SELECT name_of_assessee as name,pan as identifier FROM a3_kit.form26as_asseseedetails  where lid=" + lid + " group by pan ;")
                            form26as_asseseedetails_updated_result = dictfetchall(cursor)
                    os.remove(file)
                    continue;
                if file4 == "parta":
                    reader = pd.read_csv(file)
                    reader = reader.replace(np.nan, 'NA')
                    reader['creation_time'] = datetime.datetime.now()
                    reader['last_modification_time'] = datetime.datetime.now()

                    for i in range(len(reader)):
                        row = reader.iloc[i]
                        with connection.cursor() as cursor:
                            # cursor.execute("insert into form26as_parta(sr_no,section_1,tan_of_deductor,amount_paid_credited,tax_deducted,tds_deposited,remarks,transaction_date,status_of_booking,date_of_booking,name_of_deductor,total_amount_paid_credited,total_tax_deducted,total_tds_deposited,pan,name_of_assessee,assessment_year,deal_id,lid,creation_time,last_modification_time) values(%s, %s, %s,%s, %s, %s,%s, %s, %s,%s,%s, %s, %s,%s, %s, %s,%s, %s,%s, %s,%s)",row)
                            cursor.execute(
                                "insert into form26as_parta(sr_no,section_1,tan_of_deductor,amount_paid_credited,tax_deducted,tds_deposited,remarks,transaction_date,status_of_booking,date_of_booking,name_of_deductor,total_amount_paid_credited,total_tax_deducted,total_tds_deposited,pan,name_of_assessee,assessment_year,lid,creation_time,last_modification_time) values(%s, %s, %s,%s, %s, %s, %s, %s,%s,%s, %s, %s,%s, %s, %s,%s, %s,%s, %s,%s)",
                                row)
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "SELECT name_of_assessee as name,pan as identifier FROM a3_kit.form26as_parta  where lid=" + lid + " group by pan ;")
                            form26as_parta_updated_result = dictfetchall(cursor)
                    os.remove(file)
                    continue;
                if file4 == "partb":
                    reader = pd.read_csv(file)
                    reader = reader.replace(np.nan, 'NA')
                    reader['creation_time'] = datetime.datetime.now()
                    reader['last_modification_time'] = datetime.datetime.now()

                    for i in range(len(reader)):
                        row = reader.iloc[i]
                        with connection.cursor() as cursor:
                            # cursor.execute("insert into form26as_partb(sr_no,section_1,tan_of_collector,amount_paid_debited,tax_collected,tcs_deposited,remarks,transaction_date,status_of_booking,date_of_booking,name_of_collector,total_amount_paid_debited,total_tax_collected,total_tcs_deposited,pan,name_of_assessee,assessment_year,deal_id,lid,creation_time,last_modification_time) values(%s, %s, %s,%s, %s, %s,%s, %s, %s,%s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s,%s)",row)
                            cursor.execute(
                                "insert into form26as_partb(sr_no,section_1,tan_of_collector,amount_paid_debited,tax_collected,tcs_deposited,remarks,transaction_date,status_of_booking,date_of_booking,name_of_collector,total_amount_paid_debited,total_tax_collected,total_tcs_deposited,pan,name_of_assessee,assessment_year,lid,creation_time,last_modification_time) values(%s, %s, %s,%s, %s, %s,%s, %s, %s,%s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s)",
                                row)
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "SELECT name_of_assessee as name,pan as identifier FROM a3_kit.form26as_partb  where lid=" + lid + " group by pan ;")
                            form26as_partb_updated_result = dictfetchall(cursor)
                    os.remove(file)
                    continue;

                if file4 == "partc":
                    reader = pd.read_csv(file)
                    reader = reader.replace(np.nan, 'NA')
                    reader['creation_time'] = datetime.datetime.now()
                    reader['last_modification_time'] = datetime.datetime.now()

                    for i in range(len(reader)):
                        row = reader.iloc[i]
                        with connection.cursor() as cursor:
                            # cursor.execute("insert into form26as_partc(sr,major_head,minor_head,tax,surcharge,education_cess,others,total_tax,bsr_code,date_of_deposit,challan_serial_number,remarks,pan,name_of_assessee,assessment_year,deal_id,lid,creation_time,last_modification_time) values( %s,%s,%s, %s, %s,%s, %s, %s,%s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s)",row)
                            cursor.execute(
                                "insert into form26as_partc(sr,major_head,minor_head,tax,surcharge,education_cess,others,total_tax,bsr_code,date_of_deposit,challan_serial_number,remarks,pan,name_of_assessee,assessment_year,lid,creation_time,last_modification_time) values( %s,%s,%s, %s, %s,%s, %s, %s,%s,%s, %s, %s,%s, %s, %s,%s, %s, %s)",
                                row)
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "SELECT name_of_assessee as name,pan as identifier FROM a3_kit.form26as_partc  where lid=" + lid + " group by pan ;")
                            form26as_partc_updated_result = dictfetchall(cursor)
                    os.remove(file)
                    continue;
                if file4 == "partd":
                    reader = pd.read_csv(file)
                    reader = reader.replace(np.nan, 'NA')
                    reader['creation_time'] = datetime.datetime.now()
                    reader['last_modification_time'] = datetime.datetime.now()

                    for i in range(len(reader)):
                        row = reader.iloc[i]
                        with connection.cursor() as cursor:
                            # cursor.execute("insert into form26as_partd(sr,assessment_year_refund,mode,refund_issued,nature_of_refund,amount_of_refund,interest,date_of_payment,remarks,pan,name_of_assessee,assessment_year,deal_id,lid,creation_time,last_modification_time) values(%s, %s,%s, %s,%s, %s, %s,%s, %s, %s,%s,%s, %s, %s,%s, %s)",row)
                            cursor.execute(
                                "insert into form26as_partd(sr,assessment_year_refund,mode,refund_issued,nature_of_refund,amount_of_refund,interest,date_of_payment,remarks,pan,name_of_assessee,assessment_year,lid,creation_time,last_modification_time) values(%s, %s,%s, %s, %s, %s,%s, %s, %s,%s,%s, %s, %s,%s, %s)",
                                row)
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "SELECT name_of_assessee as name,pan as identifier FROM a3_kit.form26as_partd  where lid=" + lid + " group by pan ;")
                            form26as_partd_updated_result = dictfetchall(cursor)
                    os.remove(file)
                    continue;
                if file4 == "partg":
                    reader = pd.read_csv(file)
                    reader = reader.replace(np.nan, 'NA')
                    reader['creation_time'] = datetime.datetime.now()
                    reader['last_modification_time'] = datetime.datetime.now()

                    for i in range(len(reader)):
                        row = reader.iloc[i]
                        with connection.cursor() as cursor:
                            # cursor.execute("insert into form26as_partg(sr,financial_year,short_payment,short_deduction,interest_on_tds,interest_on_tds_1,late_filing_fee_us,interest_us,total_default,pan,name_of_assessee,assessment_year,deal_id,lid,creation_time,last_modification_time) values(%s, %s, %s,%s, %s, %s,%s, %s, %s,%s,%s, %s,%s, %s,%s, %s)",row)
                            cursor.execute(
                                "insert into form26as_partg(sr,financial_year,short_payment,short_deduction,interest_on_tds,interest_on_tds_1,late_filing_fee_us,interest_us,total_default,pan,name_of_assessee,assessment_year,lid,creation_time,last_modification_time) values(%s, %s, %s,%s, %s, %s, %s, %s,%s,%s, %s,%s, %s,%s, %s)",
                                row)
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "SELECT name_of_assessee as name,pan as identifier FROM a3_kit.form26as_partg  where lid=" + lid + " group by pan ;")
                            form26as_partg_updated_result = dictfetchall(cursor)
                    os.remove(file)
                    continue;
            if file3 == "itr":
                reader = pd.read_csv(file)
                reader = reader.replace(np.nan, 'NA')
                reader['creation_time'] = datetime.datetime.now()
                reader['last_modification_time'] = datetime.datetime.now()

                for i in range(len(reader)):
                    row = reader.iloc[i]
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "insert into a3_kit.itrv_itrv(assessment_year,name,pan,town_city_district_state,pin_code,efiling_acknowledgement_number,form_no,date_of_itr_filed,gross_total_income,deductions_under_chapter_vi_a,total_income,total_income_deemed_total_income_under_amt_mat,total_income_current_year_loss,net_tax_payable,interest_and_fee_payable,total_tax_interest_and_fee_payable,taxes_paid_advance_tax,taxes_paid_tds,taxes_paid_tcs,taxes_paid_self_assessment_tax,taxes_paid_total_taxes_paid,tax_payable,refund,deal_id,customer_id,image_name,creation_time,last_modification_time) values(%s, %s, %s,%s, %s, %s,%s, %s, %s,%s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s,%s, %s, %s,%s, %s, %s,%s, %s)",
                            row)
                os.remove(file)
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT name,pan as identifier FROM a3_kit.itrv_itrv  where deal_id=" + lid + " group by pan ;")
                    itr_updated_result = dictfetchall(cursor)
                continue;

    if len(bank_updated_result) > 0:
        for obj in bank_updated_result:
            obj["doc_type"] = "BANK"
            list1.append(obj)
    if len(itr_updated_result) > 0:
        for obj in itr_updated_result:
            obj["doc_type"] = "ITR"
            obj["sub_type"] = "ITRV"
            list1.append(obj)

    if len(form16_challans_updated_result) > 0:
        for obj in form16_challans_updated_result:
            obj["doc_type"] = "ITR"
            obj["sub_type"] = "form16_challans"
            obj["name"] = "-"
            list1.append(obj)
    if len(form16_info_updated_result) > 0:
        for obj in form16_info_updated_result:
            obj["doc_type"] = "ITR"
            obj["sub_type"] = "form16_info"
            list1.append(obj)

    if len(form16_partb_updated_result) > 0:
        for obj in form16_partb_updated_result:
            obj["doc_type"] = "ITR"
            obj["sub_type"] = "form16_partb"
            obj["name"] = "-"
            list1.append(obj)

    if len(form16_quarters_updated_result) > 0:
        for obj in form16_quarters_updated_result:
            obj["doc_type"] = "ITR"
            obj["sub_type"] = "form16_quarters"
            obj["name"] = "-"
            list1.append(obj)

    if len(form26as_asseseedetails_updated_result) > 0:
        for obj in form26as_asseseedetails_updated_result:
            obj["doc_type"] = "ITR"
            obj["sub_type"] = "form26as_asseseedetails"
            # obj["name"] = "-"
            list1.append(obj)

    if len(form26as_parta_updated_result) > 0:
        for obj in form26as_parta_updated_result:
            obj["doc_type"] = "ITR"
            obj["sub_type"] = "form26as_parta"
            list1.append(obj)

    if len(form26as_partb_updated_result) > 0:
        for obj in form26as_partb_updated_result:
            obj["doc_type"] = "ITR"
            obj["sub_type"] = "form26as_partb"
            list1.append(obj)

    if len(form26as_partc_updated_result) > 0:
        for obj in form26as_partc_updated_result:
            obj["doc_type"] = "ITR"
            obj["sub_type"] = "form26as_partc"
            list1.append(obj)

    if len(form26as_partd_updated_result) > 0:
        for obj in form26as_partd_updated_result:
            obj["doc_type"] = "ITR"
            obj["sub_type"] = "form26as_partd"
            list1.append(obj)

    if len(form26as_partg_updated_result) > 0:
        for obj in form26as_partg_updated_result:
            obj["doc_type"] = "ITR"
            obj["sub_type"] = "form26as_partg"
            list1.append(obj)

    print(list1)
    return (list1)

import mysql.connector

@login_required
def update_after_download(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        lid = request.POST.get('lid')
        cid = request.POST.get('cid')
        identifier = request.POST.get('identifier')

        sub_type = request.POST.get('sub_type')
        print(sub_type)
        result = ''
        print(lid, cid, identifier, sub_type)
        identifier = identifier.replace("'", '')
        if sub_type == "BANK":
            with connection.cursor() as cursor:
                sql_query = (
                            "update a3_kit.bank_bank set customer_id =" + cid + " where deal_id=" + lid + " and account_number LIKE " + "'%" + identifier + "%'" + ";")
                print('sql=',sql_query)
                cursor.execute(sql_query)
                result = "Bank Successfuly Updated!"
        print(identifier)
        print(sub_type)

        if sub_type == "ITRV":
            with connection.cursor() as cursor:
                cursor.execute("update a3_kit.itrv_itrv set customer_id =" + cid + " where deal_id=" + lid + " and pan LIKE " + "'%" + identifier + "%'" + ";")
                result = "Successfuly Updated!"

        if sub_type == 'form16':
            form16_tables = ['form16_info','form16_partb','form16_challans','form16_quarters']
            with connection.cursor() as cursor:
                for item in form16_tables:
                    table_name = ' a3_kit'+'.'+item
                    try:
                        cursor.execute("update"+ table_name +" set customer_id =" + cid + " where lid=" + lid + " and pan_of_the_employee LIKE " + "'%" + identifier + "%'" + ";")
                        result = " Form16 Successfuly Updated!"
                    except Exception as e:
                        print(e)



        # if sub_type == "form16_info":
        #     with connection.cursor() as cursor:
        #         sql_query = ("update a3_kit.form16_info set customer_id =" + cid + " where lid=" + lid + " and pan_of_the_employee LIKE " + "'%" + identifier + "%'" + ";")
        #         print(sql_query)
        #         cursor.execute(sql_query)
        #         result = "Successfuly Updated!"
        #
        # if sub_type == "form16_partb":
        #     with connection.cursor() as cursor:
        #         sql_query = (
        #                 "update a3_kit.form16_partb set customer_id =" + cid + " where lid=" + lid + " and pan_of_the_employee LIKE " + "'%" + identifier + "%'" + ";")
        #         print(sql_query)
        #         cursor.execute(sql_query)
        #         result = "Successfuly Updated!"
        #
        # if sub_type == "form16_challans":
        #     with connection.cursor() as cursor:
        #         sql_query = (
        #                 "update a3_kit.form16_challans set customer_id =" + cid + " where lid=" + lid + " and pan_of_the_employee LIKE " + "'%" + identifier + "%'" + ";")
        #         print(sql_query)
        #         cursor.execute(sql_query)
        #         result = "Successfuly Updated!"
        #
        # if sub_type == "form16_quarters":
        #     with connection.cursor() as cursor:
        #         sql_query = (
        #                 "update a3_kit.form16_quarters set customer_id =" + cid + " where lid=" + lid + " and pan_of_the_employee LIKE " + "'%" + identifier + "%'" + ";")
        #         print(sql_query)
        #         cursor.execute(sql_query)
        #         result = "Successfuly Updated!"

        if sub_type == 'form26as':
            form26as_tables = ['form26as_asseseedetails','form26as_parta','form26as_partb','form26as_partc','form26as_partd','form26as_partg']
            with connection.cursor() as cursor:
                for item in form26as_tables:
                    table_name = ' a3_kit'+'.'+item
                    try:
                        cursor.execute("update"+ table_name+" set customer_id =" + cid + " where lid=" + lid + " and pan LIKE " + "'%" + identifier + "%'" + ";")
                        result = "Form26as Successfuly Updated!"
                    except:pass


        # if sub_type == "form26as_asseseedetails":
        #     with connection.cursor() as cursor:
        #         sql_query = (
        #                 "update a3_kit.form26as_asseseedetails set customer_id =" + cid + " where lid=" + lid + " and pan LIKE " + "'%" + identifier + "%'" + ";")
        #         print(sql_query)
        #         cursor.execute(sql_query)
        #         result = "Successfuly Updated!"
        #
        # if sub_type == "form26as_parta":
        #     with connection.cursor() as cursor:
        #         sql_query = (
        #                 "update a3_kit.form26as_parta set customer_id =" + cid + " where lid=" + lid + " and pan LIKE " + "'%" + identifier + "%'" + ";")
        #         print(sql_query)
        #         cursor.execute(sql_query)
        #         result = "Successfuly Updated!"
        #
        # if sub_type == "form26as_partb":
        #     with connection.cursor() as cursor:
        #         sql_query = (
        #                 "update a3_kit.form26as_partb set customer_id =" + cid + " where lid=" + lid + " and pan LIKE " + "'%" + identifier + "%'" + ";")
        #         print(sql_query)
        #         cursor.execute(sql_query)
        #         result = "Successfuly Updated!"
        #
        # if sub_type == "form26as_partg":
        #     with connection.cursor() as cursor:
        #         sql_query = (
        #                 "update a3_kit.form26as_partg set customer_id =" + cid + " where lid=" + lid + " and pan LIKE " + "'%" + identifier + "%'" + ";")
        #         print(sql_query)
        #         cursor.execute(sql_query)
        #         result = "Successfuly Updated!"
        # if sub_type == "form26as_partd":
        #     with connection.cursor() as cursor:
        #         sql_query = (
        #                 "update a3_kit.form26as_partd set customer_id =" + cid + " where lid=" + lid + " and pan LIKE " + "'%" + identifier + "%'" + ";")
        #         print(sql_query)
        #         cursor.execute(sql_query)
        #         result = "Successfuly Updated!"
        #
        # if sub_type == "form26as_partc":
        #     with connection.cursor() as cursor:
        #         sql_query = (
        #                 "update a3_kit.form26as_partc set customer_id =" + cid + " where lid=" + lid + " and pan LIKE " + "'%" + identifier + "%'" + ";")
        #         print(sql_query)
        #         cursor.execute(sql_query)
        #         result = "Successfuly Updated!"

        with connection.cursor() as cursor:
            cursor.execute("SELECT deal_id,name from a3_kit.los_did_cid_generation  where customer_id =" + cid + ";")
            data1 = dictfetchall(cursor)
            print(data1[0]['name'])
            name1 = data1[0]['name'];

        data_allocation_table = "";
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * from customer_allocation  where identifier LIKE" + "'%" + identifier + "%' and lid = " + lid + ";")
            data_allocation_table = dictfetchall(cursor)
            print(data_allocation_table)
        if len(data_allocation_table) > 0:
            print("XXXX")
            with connection.cursor() as cursor:
                sql_query = (
                            "update a3_kit.customer_allocation set cid = " + cid + " , name = '" + name1 + "' where lid = " + lid + " and identifier LIKE " + "'%" + identifier + "%'" + ";")
                cursor.execute(sql_query)
        else:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",  ###connect to database
                password="Knowlvers@555",
                database="a3_kit"
            )

            mycursor = mydb.cursor()

            sql = "INSERT INTO a3_kit.customer_allocation (lid,did,cid,identifier,name) VALUES (%s, %s, %s, %s, %s);"

            lid = lid
            did = data1[0]['deal_id']
            cid = cid
            name = data1[0]['name']

            identifier = identifier

            val = (lid, did, cid, identifier, name)

            mycursor.execute(sql, val)

            mydb.commit()

        return JsonResponse({"result": result,"cid":cid,"identifier":identifier,"sub_type":sub_type})


def summaryofallfile(request):
    # customer_id=str(120)
    # mydb = mysql.connector.connect(
    #     host="localhost",
    #     user="root",                        ###connect to database
    #     password="123456789",
    #     database="a3_kit"
    #         )

    # mycursor = mydb.cursor()
    # mycursor.execute("SELECT COUNT(file_name) as bank_upload , COUNT(distinct(lead_id)) as lead_id FROM bank_statment_of_lead WHERE type='bank';")
    # result = dictfetchall(mycursor)
    # print(result)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(file_name) as bank_upload , COUNT(distinct(lead_id)) as lead_id FROM upload_file_details WHERE type='bank';")
        count_bank = cursor.fetchall()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(file_name) as bank_upload , COUNT(distinct(lead_id)) as lead_id FROM upload_file_details WHERE type='itr';")
        count_itr = cursor.fetchall()
    # with connection.cursor() as cursor:
    #     cursor.execute("SELECT COUNT(file_name) as bank_upload FROM bank_statment_of_lead;")
    #     count_total=cursor.fetchall()
    count_total = int(count_bank[0][0]) + int(count_itr[0][0])
    print(count_total)
    print(count_bank[0][0])
    if (count_bank[0][1] > count_itr[0][1]):
        max1 = count_bank[0][1]
    if (count_bank[0][1] < count_itr[0][1]):
        max1 = count_itr[0][1]
    if (count_bank[0][1] == count_itr[0][1]):
        max1 = count_itr[0][1]
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT count(file_name) as download,count(distinct(lead_id))   FROM downloaded_file_details where substring(file_name,-5,1)='b' ;")
        count_bank1 = cursor.fetchall()
        print(count_bank1)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT count(file_name) as download,count(distinct(lead_id))   FROM downloaded_file_details where substring(file_name,-5,1)='i' ;")
        count_itr1 = cursor.fetchall()
    if (count_bank1[0][1] > count_itr1[0][1]):
        max2 = count_bank1[0][1]
    if (count_bank1[0][1] < count_itr1[0][1]):
        max2 = count_itr1[0][1]
    if (count_bank1[0][1] == count_itr1[0][1]):
        max2 = count_itr1[0][1]

    count_total1 = int(count_bank1[0][0]) + int(count_itr1[0][0])

    return render(request, "summaryofallfile.html",
                  {'count_bank': count_bank, 'count_itr': count_itr, 'max1': max1, 'count_total': count_total,
                   'count_bank1': count_bank1, 'count_itr1': count_itr1, 'max2': max2, 'count_total1': count_total1})


@login_required
def update_cust_id_if_c_gr_0(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        lead_id = request.POST.get('id')
        print(lead_id)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT dbs.lead_id, dbs.name,dbs.customer_id FROM a3_kit.los_did_cid_generation as dbs where dbs.lead_id=" + lead_id + ";")
            cust_details = dictfetchall(cursor)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT customer_id,bank_name as sub_type,account_name as name,account_number as identifier from a3_kit.bank_bank as bk where deal_id=" + lead_id + " group by account_number;")
            bank_updated_result = dictfetchall(cursor)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT customer_id,name,pan as identifier FROM a3_kit.itrv_itrv  where deal_id=" + lead_id + " group by pan ;")
            itr_updated_result = dictfetchall(cursor)
            print(itr_updated_result)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT customer_id,pan_of_the_employee as identifier FROM a3_kit.form16_challans  where lid=" + lead_id + " group by pan_of_the_employee ;")
            form16_challans_updated_result = dictfetchall(cursor)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT customer_id,employee_name as name,pan_of_the_employee as identifier FROM a3_kit.form16_info  where lid=" + lead_id + " group by pan_of_the_employee ;")
            form16_info_updated_result = dictfetchall(cursor)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT customer_id,pan_of_the_employee as identifier FROM a3_kit.form16_partb  where lid=" + lead_id + " group by pan_of_the_employee ;")
            form16_partb_updated_result = dictfetchall(cursor)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT customer_id,pan_of_the_employee as identifier FROM a3_kit.form16_quarters  where lid=" + lead_id + " group by pan_of_the_employee ;")
            form16_quarters_updated_result = dictfetchall(cursor)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT customer_id,name_of_assessee as name,pan as identifier FROM a3_kit.form26as_asseseedetails  where lid=" + lead_id + " group by pan ;")
            form26as_asseseedetails_updated_result = dictfetchall(cursor)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT customer_id,name_of_assessee as name,pan as identifier FROM a3_kit.form26as_parta  where lid=" + lead_id + " group by pan ;")
            form26as_parta_updated_result = dictfetchall(cursor)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT customer_id,name_of_assessee as name,pan as identifier FROM a3_kit.form26as_partb  where lid=" + lead_id + " group by pan ;")
            form26as_partb_updated_result = dictfetchall(cursor)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT customer_id,name_of_assessee as name,pan as identifier FROM a3_kit.form26as_partc  where lid=" + lead_id + " group by pan ;")
            form26as_partc_updated_result = dictfetchall(cursor)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT customer_id,name_of_assessee as name,pan as identifier FROM a3_kit.form26as_partd  where lid=" + lead_id + " group by pan ;")
            form26as_partd_updated_result = dictfetchall(cursor)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT customer_id,name_of_assessee as name,pan as identifier FROM a3_kit.form26as_partg  where lid=" + lead_id + " group by pan ;")
            form26as_partg_updated_result = dictfetchall(cursor)



        list1 = []
        if len(bank_updated_result) > 0:
            for obj in bank_updated_result:
                obj["doc_type"] = "BANK"
                list1.append(obj)
        if len(itr_updated_result) > 0:
            for obj in itr_updated_result:
                obj["doc_type"] = "ITR"
                obj["sub_type"] = "ITRV"
                list1.append(obj)
        if len(form16_challans_updated_result) > 0:
            for obj in form16_challans_updated_result:
                obj["doc_type"] = "ITR"
                obj["sub_type"] = "form16"
                obj["name"] = "-"
                list1.append(obj)
        # if len(form16_info_updated_result) > 0:
        #     for obj in form16_info_updated_result:
        #         obj["doc_type"] = "ITR"
        #         obj["sub_type"] = "form16_info"
        #         list1.append(obj)
        #
        # if len(form16_partb_updated_result) > 0:
        #     for obj in form16_partb_updated_result:
        #         obj["doc_type"] = "ITR"
        #         obj["sub_type"] = "form16_partb"
        #         obj["name"] = "-"
        #         list1.append(obj)
        #
        # if len(form16_quarters_updated_result) > 0:
        #     for obj in form16_quarters_updated_result:
        #         obj["doc_type"] = "ITR"
        #         obj["sub_type"] = "form16_quarters"
        #         obj["name"] = "-"
        #         list1.append(obj)

        if len(form26as_asseseedetails_updated_result) > 0:
            for obj in form26as_asseseedetails_updated_result:
                obj["doc_type"] = "ITR"
                obj["sub_type"] = "form26as"
                list1.append(obj)

        # if len(form26as_parta_updated_result) > 0:
        #     for obj in form26as_parta_updated_result:
        #         obj["doc_type"] = "ITR"
        #         obj["sub_type"] = "form26as_parta"
        #         list1.append(obj)
        #
        # if len(form26as_partb_updated_result) > 0:
        #     for obj in form26as_partb_updated_result:
        #         obj["doc_type"] = "ITR"
        #         obj["sub_type"] = "form26as_partb"
        #         list1.append(obj)
        #
        # if len(form26as_partc_updated_result) > 0:
        #     for obj in form26as_partc_updated_result:
        #         obj["doc_type"] = "ITR"
        #         obj["sub_type"] = "form26as_partc"
        #         list1.append(obj)
        #
        # if len(form26as_partd_updated_result) > 0:
        #     for obj in form26as_partd_updated_result:
        #         obj["doc_type"] = "ITR"
        #         obj["sub_type"] = "form26as_partd"
        #         list1.append(obj)

        # if len(form26as_partg_updated_result) > 0:
        #     for obj in form26as_partg_updated_result:
        #         obj["doc_type"] = "ITR"
        #         obj["sub_type"] = "form26as_partg"
        #         list1.append(obj)


        return_data = list1
        print(return_data)

    return JsonResponse({"afterdownload": return_data, "cust_details": cust_details})
