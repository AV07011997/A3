from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, Http404
from django.db import connection
import json
from django.core.serializers.json import DjangoJSONEncoder
from bank.models import Bank, Bank_master
# from .bank_customer_monthly_kpi.bcmk import KPIs
import pandas as pd
from django.views.decorators.csrf import csrf_protect
# Create your views here.

def dictfetchall(cursor):
    # "Return all rows from a cursor as a dict"
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

def test(request):
   status = {}
    
   if "deal_id" not in request.session or "customer_id" not in request.session:
      status["type"] = "deal"
      status["message"] = "Please select a deal first!"
   else:
      customer_id = request.session["customer_id"]
      deal_id=request.session["deal_id"]
      with connection.cursor() as cursor:
         cursor.execute("SELECT account_number, bank_name, min(txn_date) as from_date, max(txn_date) as to_date, COUNT(DISTINCT(entity)) as num_entities  FROM bank_bank WHERE customer_id = " + customer_id  + " GROUP BY account_number" + ";")
         data = dictfetchall(cursor)
         print(data) 
         # for date in data:

         #    date['from_date'] = date['from_date'].strftime('%d/%m/%Y')
         #    date['to_date'] = date['to_date'].strftime('%d/%m/%Y')

      if request.method=="POST":
         n=request.POST.get('optbank')
            
         if n is not None:
            n = "'%" + n[1:-1] + "%'"
            with connection.cursor() as cursor:
               cursor.execute("SELECT * FROM bank_bank WHERE account_number like " + n  +";")
               data1 = dictfetchall(cursor)
               
               data1 = data1
            return render(request, "test.html", {'data':data, 'data1':data1})

   return render(request, "test.html", {'data':data})