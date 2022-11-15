from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, Http404
from django.db import connection
import json
import pandas as pd
from django.core.serializers.json import DjangoJSONEncoder
from pymysql import NULL



@login_required
def bureau_page(request):
    status = {}
    if "deal_id" not in request.session or "customer_id" not in request.session:
        status["type"] = "deal"
        status["message"] = "Please select a deal first!"
    else:
        customer_id = request.session["customer_id"]
        deal_id=request.session["deal_id"]

    payload = {"bureau_page": True, "status": status if status else None}
    return render(request, "bureau.html", payload)


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    all_data = []
    for row in cursor.fetchall():
        data_row = dict(zip(columns, row))
        data_row["Disbursal_date"] = data_row["Disbursal_date"].strftime('%d/%m/%Y')
        data_row["Date_reported"] = data_row["Date_reported"].strftime('%d/%m/%Y')
        all_data.append(data_row)

    return all_data


@login_required
def get_bureau_data(request):
    # print("Getting bureau data.")
    if "deal_id" not in request.session or "customer_id" not in request.session:
        status["type"] = "deal"
        status["message"] = "Please select a deal first!"
        return JsonResponse({"status": "failed"})

    else:
        customer_id = request.session["customer_id"]
        deal_id=request.session["deal_id"]
        with connection.cursor() as cursor:
            cursor.execute("select * from bureau where customer_id = " + customer_id + ";")
            data = dictfetchall(cursor)
            # data = json.dumps(cursor.fetchall(), sort_keys=True, indent=1, cls=DjangoJSONEncoder)
            # print(data)
            for x in data:
                x['Overdue_amount'] =x['Overdue amount']

                if(x['DPD']==None):
                    x['DPD']=0



            return JsonResponse(data, safe=False)
            # return JsonResponse(data)


@login_required
def update_bureau_data(request):
    # print("update_bureau_data")
    # data=json.loads(request.POST['data'])
    datatemp = json.loads(request.POST['data'])
    selectedoptionsinarow=datatemp.pop('data')
    
    data=datatemp
    # selectedoptionsinarow=request.GET['series',False]
    # print(data)
    customer_id = request.session["customer_id"]
    deal_id=request.session["deal_id"]
    
    for x in selectedoptionsinarow:
        index=x['index']+1
        selectedoption=x['selectedoption']
        
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE bureau SET valuetype = '{selectedoption}' WHERE `index` = '{index}';")
        
    
    
        
    with connection.cursor() as cursor:
        for row_index in data:
            row_data = data[row_index]
            for column in row_data:
                # print("row data: ", row_data[column])
                if type(row_data[column]) == str:
                    # print("data type string.")
                    sql_query_1 = "update bureau set " + column + "_edited = '" + row_data[column] + "' where `index` = " + row_index + ";"
                    # print(sql_query_1)
                    cursor.execute(sql_query_1)

                elif type(row_data[column]) == int:
                    # print("data type integer.")
                    sql_query_1 = "update bureau set " + column + "_edited = '" + str(row_data[column]) + "' where `index` = " + row_index + ";"
                    # print(sql_query_1)
                    cursor.execute(sql_query_1)

                if row_data[column]=='0' or row_data[column]=='' or row_data[column]==' ' or row_data[column]==None :
                    sql_query_2 = "update bureau set " + column + "_user_edited = 1 where `index` = " + row_index + ";"
                    cursor.execute(sql_query_2)
                # print(sql_query_2)

    status = {}
    status["type"] = "success"
    status["message"] = "Data has been updated successfully."
    return HttpResponse(json.dumps({"bureau_page": True, "status": status}))

@login_required
def reset_bureau_data(request):
    customer_id = request.session["customer_id"]
    deal_id=request.session["deal_id"]
    index = request.POST['index']
    with connection.cursor() as cursor:
        sql_query = "update bureau set Loan_Selection_edited=NULL, Loan_Selection_user_edited=0, Disbursed_amount_edited=NULL, Disbursed_amount_user_edited=0, Tenure_edited=NULL, Tenure_user_edited=0, ROI_edited=NULL, ROI_user_edited=0, EMI_edited=NULL, EMI_user_edited=0 where `index` = "+ index +";"
        # print(sql_query)
        cursor.execute(sql_query)
    status = {}
    status["type"] = "success"
    status["message"] = "Data reset successful"
    return HttpResponse(json.dumps({"bureau_page": True, "status": status}))



@login_required
def bureau_data_by_condition(request):
    # customer_id = request.session["customer_id"]
    # deal_id=request.session["deal_id"]
    option = request.POST['select']
    index = request.POST['index']
    data = ''
    selected = ''
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM bureau where `index` = " + index + ";")
        data = dictfetchall(cursor)
        ### updating valuetype in the bureau table
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE bureau SET valuetype = '{option}' WHERE `index` = '{index}';")
        
    if option == 'bureau':
            selected = 'bureau'
    if option == 'edited':
            selected = 'edited'
    if option == 'recommended':
            selected = 'recommended'
    status = {}
    status["type"] = "success"
    status["message"] = "Data reset successful"
    return JsonResponse({"bureau_page": True, "status": status, "data":data, "selected":selected})


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
def selected_bureau_data(request):
    selected_data = (json.loads(request.body)).get('selected')
    unselected_data = (json.loads(request.body)).get('unselected')
    loan = {"01": "Auto Loan (Personal)",
      "02":"Housing Loan",
      "03":"Property Loan",
      "04":"Loan Against Shares/Securities",
      "05":"Personal Loan",
      "06":"Consumer Loan",
      "07":"Gold Loan",
      "08":"Education Loan",
      "09":"Loan to Professional",
      "10":"Credit Card",
      "11":"Leasing",
      "12":"Overdraft",
      "13":"Two-wheeler Loan",
      "14":"Non-Funded Credit Facility",
      "15":"Loan Against Bank Deposits",
      "16":"Fleet Card",
      "17":"Commercial Vehicle Loan",
      "18":"Telco – Wireless",
      "19":"Telco – Broadband",
      "20":"Telco – Landline",
      "31":"Secured Credit Card",
      "32":"Used Car Loan",
      "33":"Construction Equipment Loan",
      "34":"Tractor Loan",
      "35":"Corporate Credit Card",
      "36":"Kisan Credit Card",
      "37":"Loan on Credit Card",
      "38":"Prime Minister Jaan Dhan Yojana - Overdraft",
      "39":"Mudra Loans - Shishu/Kishor/Tarun",
      "40":"Microfinance – Business Loan",
      "41":"Microfinance – Personal Loan",
      "42":"Microfinance – Housing Loan",
      "43":"Microfinance – Other",
      "44":"Pradhan Mantri Awas Yojana - Credit Linked Subsidy Scheme MAYCLSS",
      "45":"Other",
      "51":"Business Loan – General",
      "52":"Business Loan – Priority Sector – Small Business",
      "53":"Business Loan – Priority Sector – Agriculture",
      "54":"Business Loan – Priority Sector – Others",
      "55":"Business Non-Funded Credit Facility – General",
      "56":"Business Non-Funded Credit Facility – Priority Sector – Small Business",
      "57":"Business Non-Funded Credit Facility – Priority Sector – Agriculture",
      "58":"Business Non-Funded Credit Facility – Priority Sector - Others",
      "59":"Business Loan Against Bank Deposits",
      "61":"Business Loan - Unsecured",
      "00":"Other"
    }

    if unselected_data:
        DATE_CLOSED = ''
        for i in unselected_data:
          
            cid = request.session["customer_id"]
            loan_type = i.get('loan_type')
            loan_status = i.get('loan_status')
            DATE_CLOSED = loan_status
            disbursal_date = i.get('disbursal_date')
            disbursal_amount = i.get('disbursal_amount').replace(',','').replace('₹','')
            
            source = i.get('source')
            with connection.cursor() as cursor:
                sql_query = ("update a3_kit.bureau set final_selected=0 where Customer_Id="+cid+" and Loan_type="+"'"+loan_type+"'"+" and Loan_status="+"'"+loan_status+"'"+" and Disbursal_date="+"'"+disbursal_date+"'"+" and Disbursed_amount="+disbursal_amount+" and Source="+"'"+source+"'"+";")
             
                cursor.execute(sql_query)
            try:
                account_type = (list(loan.keys())[list(loan.values()).index(loan_type)])
            except Exception as e:
                account_type = '00'
            if loan_status == 'Active':
                DATE_CLOSED = ''
                with connection.cursor() as cursor:
                    #sql_query = ("update a3_kit.bureau_account_segment_tl set final_selected=0 where CUSTOMER_ID=" + cid + " and DATE_CLOSED=" + "'" + DATE_CLOSED + "'" + " and DATE_AC_DISBURSED=" + "'" + disbursal_date + "'" + " and HIGH_CREDIT_AMOUNT=" + disbursal_amount + " and source=" + "'" + source + "'" + " and ACCOUNT_TYPE=" + account_type + ";")
                    #update a3_kit.bureau_account_segment_tl set final_selected = 1 where CUSTOMER_ID = 1200360 and DATE_AC_DISBURSED = '2019-04-20' and HIGH_CREDIT_AMOUNT = 1950000 and source = 'cibil' and ACCOUNT_TYPE = 02 and (DATE_CLOSED is null or DATE_CLOSED='');
                    sql_query = ("update a3_kit.bureau_account_segment_tl set final_selected=0 where CUSTOMER_ID=" + cid + " and DATE_AC_DISBURSED=" + "'" + disbursal_date + "'" + " and HIGH_CREDIT_AMOUNT=" + disbursal_amount + " and source=" + "'" + source + "'" + " and ACCOUNT_TYPE=" + account_type + " and (DATE_CLOSED is null or DATE_CLOSED='' or DATE_CLOSED<>'');")
                    # sql_query = ("update a3_kit.bureau_account_segment_tl set final_selected=0 where CUSTOMER_ID=" + cid + " and DATE_CLOSED<>''" + " and DATE_AC_DISBURSED=" + "'" + disbursal_date + "'" + " and HIGH_CREDIT_AMOUNT=" + disbursal_amount + " and source=" + "'" + source + "'" + " and ACCOUNT_TYPE=" + account_type + ";")
                    # print('unselected_data_active= ',sql_query)
                    cursor.execute(sql_query)
            else:
                with connection.cursor() as cursor:
                    sql_query = ("update a3_kit.bureau_account_segment_tl set final_selected=0 where CUSTOMER_ID=" + cid + " and DATE_CLOSED<>''" + " and DATE_AC_DISBURSED=" + "'" + disbursal_date + "'" + " and HIGH_CREDIT_AMOUNT=" + disbursal_amount + " and source=" + "'" + source + "'" + " and ACCOUNT_TYPE=" + account_type + ";")
                    # print('unselected_data_closed= ',sql_query)
                    cursor.execute(sql_query)


    if selected_data:
        DATE_CLOSED = ''
        for j in selected_data:
           
            cid = request.session["customer_id"]
            loan_type = j.get('loan_type')
            loan_status = j.get('loan_status')
            disbursal_date = j.get('disbursal_date')
            disbursal_amount = j.get('disbursal_amount').replace(',','').replace('₹','')
            source = j.get('source')
            with connection.cursor() as cursor:
                sql_query = ("update a3_kit.bureau set final_selected=1 where Customer_Id="+cid+" and Loan_type="+"'"+loan_type+"'"+" and Loan_status="+ "'"+loan_status+"'" +" and Disbursal_date="+"'"+disbursal_date+"'"+" and Disbursed_amount="+disbursal_amount+" and Source="+"'"+source+"'"+";")
                cursor.execute(sql_query)
            try:
                account_type = (list(loan.keys())[list(loan.values()).index(loan_type)])
            except Exception as e:
                account_type = '00'
            if loan_status == 'Active':
                DATE_CLOSED = ''
                with connection.cursor() as cursor:
                    # sql_query = ("update a3_kit.bureau_account_segment_tl set final_selected=1 where CUSTOMER_ID="+cid+" and DATE_CLOSED="+"'"+DATE_CLOSED+"'"+" and DATE_AC_DISBURSED="+"'"+disbursal_date+"'"+" and HIGH_CREDIT_AMOUNT="+disbursal_amount+" and source="+"'"+source+"'"+" and ACCOUNT_TYPE="+account_type+";")
                    sql_query = ("update a3_kit.bureau_account_segment_tl set final_selected=1 where CUSTOMER_ID=" + cid + " and DATE_AC_DISBURSED=" + "'" + disbursal_date + "'" + " and HIGH_CREDIT_AMOUNT=" + disbursal_amount + " and source=" + "'" + source + "'" + " and ACCOUNT_TYPE=" + account_type + " and (DATE_CLOSED is null or DATE_CLOSED='' or DATE_CLOSED<>'');")
                    # print('selected_data_active= ',sql_query)
                    cursor.execute(sql_query)
            else:
                with connection.cursor() as cursor:
                    sql_query = ("update a3_kit.bureau_account_segment_tl set final_selected=1 where CUSTOMER_ID="+cid+" and DATE_CLOSED<>''"+" and DATE_AC_DISBURSED="+"'"+disbursal_date+"'"+" and HIGH_CREDIT_AMOUNT="+disbursal_amount+" and source="+"'"+source+"'"+" and ACCOUNT_TYPE="+account_type+";")
                    # print('selected_data_closed= ',sql_query)
                    cursor.execute(sql_query)


    result = 'Done!'
    return JsonResponse({'result':result})



@login_required
def some(request):
    customer_id = request.session["customer_id"]
    data = ''
    with connection.cursor() as cursor:
        # sql_query = "SELECT b.Date_reported, b.Loan_type,b.Loan_status,b.Disbursal_date,b.Disbursed_amount,b.Current_Balance,b.Overdue_amount,"\
        #                 "b.Tenure,b.ROI,b.EMI,b.Customer_Id,bast.ACCOUNT_NUMBER,bast.OWNERSHIP_INDICATOR," \
        #             "bast.DATE_LAST_PAYMENT FROM a3_kit.bureau as b LEFT JOIN a3_kit.bureau_account_segment_tl as bast ON b.customer_id = bast.CUSTOMER_ID " \
        #             "where (b.final_selected=1 and b.Customer_Id="+customer_id+") and (bast.final_selected=1 and bast.CUSTOMER_ID="+customer_id+");"
        try:
            cursor.execute("SELECT * FROM a3_kit.bureau where final_selected=1 and Customer_Id="+customer_id+";")
            bureau_data = dictfetchall(cursor)
            cursor.execute("SELECT * FROM a3_kit.bureau_account_segment_tl where final_selected=1 and CUSTOMER_ID=" + customer_id + ";")
            bureau_segment_data = dictfetchall(cursor)

            bureau_data = pd.DataFrame(bureau_data)
            # print('bureau',bureau_data)
            bureau_data = bureau_data.rename(columns={"Customer_Id":"CUSTOMER_ID","Source":"source"})
            bureau_segment_data = pd.DataFrame(bureau_segment_data)
            # print('bureau_s',bureau_segment_data)
            data = bureau_segment_data.merge(bureau_data,on=["CUSTOMER_ID","source"],how="left")
            data['Date_reported'] = data['Date_reported'].apply(lambda x: x.strftime('%d/%m/%Y'))
            data['Disbursal_date'] = data['Disbursal_date'].apply(lambda x: x.strftime('%d/%m/%Y'))
            data['DATE_LAST_PAYMENT'] = pd.to_datetime(data['DATE_LAST_PAYMENT'], format="%Y-%m-%d")
            data['DATE_LAST_PAYMENT'] = data['DATE_LAST_PAYMENT'].apply(lambda x: x.strftime('%d/%m/%Y'))

            # print("M",data)
            json_records = data.reset_index().to_json(orient='records')
            data = json.loads(json_records)
            # print(data);
        except Exception as e:
            pass

    return render(request, "selected_bureau_data_list.html", {'selected':data})


@login_required
def updateBureauAccountSegmentTl(request):
    # print('Hello')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM a3_kit.bureau_account_segment_tl where Tenure is NULL and DPD is NULL;")
        data = dictfetchall(cursor)
        try:
            Tenure = ''
            DPD = ''
            for obj in data:
                # id = obj['id']
                id = 1
                if obj['REPAYMENT_TENURE'] == '' or obj['REPAYMENT_TENURE'] == 'None':
                    if obj['EMI_AMMOUNT'] != 0:
                        Tenure = obj['HIGH_CREDIT_AMOUNT'] // obj['EMI_AMMOUNT']
                    else:
                        Tenure = 'NULL'
                else:
                    Tenure = obj['REPAYMENT_TENURE']
                some_of_PH_1_2 = obj['PAYMENT_HST_1']+obj['PAYMENT_HST_2']
                DPD = some_of_PH_1_2[:3]
                # print('id = ',id, 'Tenure = ',Tenure,'DPD = ',DPD)
                sql_query = ("update a3_kit.bureau_account_segment_tl set Tenure ="+"'"+ str(Tenure) +"', "+" DPD="+"'"+DPD+"'"+" where id=" + str(id) + ";")
                cursor.execute(sql_query)
        except Exception as e:
            pass

