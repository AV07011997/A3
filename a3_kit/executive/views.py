
import json
import datetime as dt
import re
from dateutil import relativedelta
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from datetime import datetime, timedelta
import numpy as np
from datetime import datetime
import mysql.connector
import pandas as pd
from django.db import connection
from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic import TemplateView
from babel.numbers import format_currency
from analyze.bank_customer_kpi.a3_bank_kpi import bck


# Create your views here.

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
def executive_summary(request):

    status = {}
    if "deal_id" not in request.session or "customer_id" not in request.session:
        status["type"] = "deal"
        status["message"] = "Please select a deal first!"
    else:
        customer_id = request.session["customer_id"]
        deal_id=request.session["deal_id"]

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM bureau_ref_dtl WHERE CUSTOMER_ID = " + customer_id + ";")
            bureau_ref_dtl = dictfetchall(cursor)
            bureau_ref_dtl = pd.DataFrame(bureau_ref_dtl)



        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM a3_kit.bureau_account_segment_tl WHERE CUSTOMER_ID = " + customer_id + "  ;")
            bureau_account_segment_tl = dictfetchall(cursor)
            bureau_account_segment_tl = pd.DataFrame(bureau_account_segment_tl)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM a3_kit.bureau WHERE CUSTOMER_ID = " + customer_id + "  ;")
            bureau_automated = dictfetchall(cursor)
            bureau_automated = pd.DataFrame(bureau_automated)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM lead_details.cr_deal_dtl WHERE did = " + str(deal_id) + "  ;")
            findingleadid = dictfetchall(cursor)
            findingleadid = pd.DataFrame(findingleadid)

        lead_id=findingleadid['lid'][0]
        

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM lead_details.cr_lead_dtl WHERE LEAD_ID = " + str(lead_id) + "  ;")
            lmsdetails = dictfetchall(cursor)
            lmsdetails = pd.DataFrame(lmsdetails)
        
        
        

        


             # gantt_chart_loan_timeline(customer_id)

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM bureau_enquiry_segment_iq WHERE CUSTOMER_ID = " + customer_id + ";")
            bureau_enquiry_segment_iq = dictfetchall(cursor)
            bureau_enquiry_segment_iq = pd.DataFrame(bureau_enquiry_segment_iq)

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM bureau_address_segment WHERE CUSTOMER_ID = " + customer_id + ";")
            bureau_address_segment = dictfetchall(cursor)
            bureau_address_segment = pd.DataFrame(bureau_address_segment)

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM bureau_score_segment WHERE CUSTOMER_ID = " + customer_id + ";")
            bureau_score_segment = dictfetchall(cursor)
            bureau_score_segment = pd.DataFrame(bureau_score_segment)
            
        with connection.cursor() as cursor:
            cursor.execute("SELECT txn_date, credit, debit, balance, account_number, account_name, mode, sub_mode, entity, source_of_trans, description, transaction_type FROM bank_bank WHERE customer_id = " + customer_id  +";")
            bankdata = dictfetchall(cursor)
            bankdata=pd.DataFrame(bankdata)
        
        

        
    
    bureau_details={}

    try:
        bureau_details["creditscore"]=int(bureau_score_segment["SCORE"])
    except:
        bureau_details["creditscore"]="No Credit Score"

    try:
        bureau_details["activeloans"]=len(bureau_automated[bureau_automated['Loan_status']=="Active"])
    except:
        bureau_details["activeloans"]="No Active Loans."

    try:
        bureau_details["totalpos"]=format_currency(int(bureau_automated["Current_Balance"].sum()), 'INR', locale='en_IN')
    except:
        bureau_details["totalpos"]="Not Available"

    try:
        data_dpd=bureau_account_segment_tl
        data_dpd=data_dpd.dropna(subset=['PAYMENT_HST_1'])
        data_dpd['PAYMENT_HST_2']=data_dpd['PAYMENT_HST_2'].fillna("XXX")
        data_dpd['payment']=data_dpd['PAYMENT_HST_1']+data_dpd['PAYMENT_HST_2']
        data_dpd['payment_new']=data_dpd['payment'].apply(lambda x: [x[i:i+3] for i in range(0,len(x),3)])
        data_dpd['date']=data_dpd.apply(lambda row: list(pd.date_range(start=row['DATE_PAYMENT_HST_START'],end=row['DATE_PAYMENT_HST_END'],freq='-1MS')),axis=1)
        data_dpd['combined']=data_dpd.apply(lambda row: list(zip(row['payment_new'],row['date'])),axis=1)

        
        data_dpd=data_dpd.reset_index()
        data_dpd_final=pd.DataFrame(np.concatenate(data_dpd['combined']),columns=['DPD','DPD_month']).reset_index(drop=True)
        

        temp1=data_dpd_final.copy()
        temp1['DPD']=temp1['DPD'].replace("XXX",0)
        temp1['DPD']=temp1['DPD'].replace("STD",0)
        temp1['DPD']=temp1['DPD'].replace("SMA",90)
        temp1['DPD']=temp1['DPD'].replace("LSS",360)
        temp1['DPD']=temp1['DPD'].replace("DBT",270)
        temp1['DPD']=temp1['DPD'].replace("SUB",180)
        temp1['DPD']= pd.to_numeric(temp1['DPD'], errors="coerce")
        bureau_details["maxdpd"]=temp1['DPD'].max()


    except:

        bureau_details["maxdpd"]="Not Available"

    try:

        temp2=temp1[temp1['DPD']!=0]
        

    except:
        bureau_details['recentdpd']="Not Available"
    

    try:
        bureau_account_segment_tl['DATE_CLOSED']=pd.to_datetime(bureau_account_segment_tl['DATE_CLOSED'])
      

        recentlyclosedloandate=bureau_account_segment_tl['DATE_CLOSED'].max()
        bureau_details['recentlyclosedloandate']="{:.2f}".format((dt.datetime.today()-recentlyclosedloandate)/np.timedelta64(1, 'M'))
        if(pd.isnull(bureau_details['recentlyclosedloandate'])):
            bureau_details['recentlyclosedloandate']="No Loans Closed"
    except:pass

    try:
        bureau_details["Name"]=lmsdetails["CUSTOMER_NAME"][0]
        lmsdetails["CUSTOMER_DOB"]=pd.to_datetime(lmsdetails["CUSTOMER_DOB"])
        # bureau_details["Age"]=int((dt.date.today-lmsdetails["CUSTOMER_DOB"])/365)
        bureau_details["Location"]=lmsdetails["DISTRICT"][0]+" ,"+lmsdetails["STATE"][0]
        bureau_details["Deal_id"]=deal_id
        bureau_details["Purpose"]=lmsdetails["LOAN_PURPOSE"][0]
        bureau_details["Loan_amount"]=lmsdetails["LOAN_AMOUNT"][0]
        bureau_details["Tenure"]=lmsdetails["TENURE"][0]


    except:pass
    
    try:
        bureau_details["Salary"]=int(bureau_automated["salary"][0])
    except:pass
    
    
    
    try:
        temp=bureau_automated
        index=0
        for x in temp['valuetype']:
            if(x=='bureau'):
                temp['EMI_new'][index]=temp['EMI'][index]
            elif(x=='edited'):
                temp['EMI_new'][index]=temp['EMI_edited'][index]
            elif(x=='recommended'):
                temp['EMI_new'][index]=temp['EMI_new'][index]
            index=index+1
        emisum=temp['EMI_new'].sum()
        bureau_details["totalemi"]=int(emisum)
        

            
        
            
        
        
    except:pass
    try:
        temp=bankdata
        temp.sort_values(by=['txn_date'], inplace=True)
        closingbalance=temp.balance.tail(1) 
        bureau_details['closingbalance']=closingbalance.values[0]  
        
        
    except:pass
    
    try:
        temp=bankdata
        
        bureau_details['last3month']=int(temp['balance'].mean())
        bureau_details['dtocratio']=int(temp['debit'].sum()/temp['credit'].sum()*100)
        bureau_details['cashcreditratio'] =int(temp[temp['mode']=='Cash']['credit'].sum()/temp['credit'].sum()*100)
        
        
    except:pass
    
    try:
        KPI = bck(bankdata)
        bureau_details["averagemonthlycreditratio"]=int((emisum/KPI[0]["Average_Monthly_Credit"][0])*100)
        bureau_details["averagemonthlycredit"]=int(KPI[0]["Average_Monthly_Credit"][0])
        
    except:pass
    
    try:
       
        bureau_details["foirstated"]=int((emisum/bureau_automated["salary"][0])*100)
        
    except:pass
    
    try:
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM finaldata WHERE customer_id = " + customer_id + ";")
            finaldata = dictfetchall(cursor)
            finaldata = pd.DataFrame(finaldata)
            bureau_details['roigiven']=finaldata['roi'][0]
            bureau_details['loangiven']=finaldata['loan'][0]
            bureau_details['tenuregiven']=finaldata['tenure'][0]
            bureau_details['recommendationgiven']=finaldata['recommendation'][0]
            bureau_details['notegiven']=finaldata['note'][0]
           
            
        
        
    except:pass







   
        
    
    return render(request, "executive_summary.html", {"bureau_details":bureau_details})


def savedata(request):
    # print("hello")
    customer_id=request.session["customer_id"]
    notes=request.POST["notes"]
    rointrest=request.POST["rateofintrest"]
    tenure=request.POST["tenure"]
    loan=request.POST["loanconsidered"]
    recommendation=request.POST["recommendation"]
    now=datetime.now()
    time = now.strftime("%m/%d/%Y, %H:%M:%S")
    
    
    
    with connection.cursor() as cursor:
            cursor.execute( "INSERT INTO `finaldata` (`customer_id`,`loan`,`tenure`,`roi`,`note`,`datetime`,`recommendation`)  VALUES ('"+ customer_id+"','"+ loan+"','"+ tenure+"', '"+ rointrest+"', '"+ notes+"', '"+ time+"', '"+ recommendation+"') ON DUPLICATE KEY UPDATE `customer_id`='"+ customer_id+"', `loan`='"+ loan+"',`tenure`='"+ tenure+"',`roi`='"+ rointrest+"',`note`='"+ notes+"',`datetime`='"+ time+"',`recommendation`='"+recommendation+"';")
            
    
    return render(request, "executive_summary.html")
    
    

 