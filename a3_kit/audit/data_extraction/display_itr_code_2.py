# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 18:03:57 2020

@author: Vaibhav
"""

#THE FOLLOWING CODE CREATES THE ITR DISPLAY FOR TABLE2

import pandas as pd
import numpy as np
# import pymysql


def itr_display4(form16):
    
    #Connect with DB
    # conn = pymysql.connect(host = '10.20.30.40', port = 3306, user = 'ABC', passwd = 'PAS8765', charset = 'utf8', db='bureau')
    
    # #Select the required columns and table from DB
    # sql1 = "SELECT e.DEAL_ID AS deal_id, e.CUSTOMER_ID AS cust_id FROM cibil_ref_dtl e  where e.DEAL_ID = "1234567" and e.CUSTOMER_ID ="12345678""
    
    # deal_details = pd.read_sql(sql1, conn)
    
    #Read form 16
    # form16 = pd.read_excel(part_a_path, sheet_name = "Info")
    
    address=form16['employer_address'][0]
    # emp_name = form16['employee_name'
    # from_date=form16['period_with_the_employer_from']
    # to_date=form16['period_with_the_employer_to']
    #to_date = form16['period_with_the_employer_to']
    # address = address.replace('employer_address','address_of_latest_employer_for_reference')
    
    # address.columns = ['Measure','Address']

    return address

    #deal_details = pd.read_csv(deal)
    # deal_id = "XXXX777"
    # customer_id = "4000700"
    
    #Export the data
    # address.to_csv("{}\\Table2\\{}_{}_{}_{}_Table2.csv".format(out_path,deal_id,customer_id,from_date,to_date),index=False)

#Provide the input and output path    
# itr_display4(r"W:\\kavyant\\A3-KIT\\knowlver\\Form16\\output\\form16.xlsx",
#              r"W:\kavyant\A3-KIT\knowlver\itr analysis table\output")