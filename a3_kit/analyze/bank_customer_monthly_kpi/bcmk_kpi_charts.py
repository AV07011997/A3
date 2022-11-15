# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 13:33:46 2021

@author: HP-Knowlvers
"""

##########  KPI ######################
#Importing the digitized bank statement
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import datetime as dt
import os
from django.conf import settings

def bcmk_charts(data):
    
    final = data

    #Converting string date into datetime 
    #final.info()
    # final["mode"].unique()
    # final["sub_mode"].unique()
    #Converting string date into datetime 

    final["txn_date"]=pd.to_datetime(final["txn_date"], format = '%Y-%m-%d')
    #final["txn_date"]=pd.to_datetime(final["txn_date"], format = '%d-%m-%Y')


    final["month_year"]=pd.to_datetime(final["txn_date"]).dt.to_period('m')

    # try:
    #     final["credit"]=final["credit"].str.replace(",","")

    #     final["debit"]=final["debit"].str.replace(",","")

    #     final["balance"]=final["balance"].str.replace(",","")
    # except:
    #     pass
    # final["credit"]=final["credit"].astype(float)
    # final["debit"]=final["debit"].astype(float)
    # final["balance"]=final["balance"].astype(float)

    ###########################Inflows
    #####Non Cash credits
    Non_cash_credits=final[~(final["mode"]=='Cash')].groupby(['month_year']).agg(Non_cash_credits_Count=("credit","count"),Non_cash_credits_Value=("credit","sum")).reset_index()

    #####Cash credits
    Cash_credits=final[(final["mode"]=='Cash')].groupby(['month_year']).agg(Cash_credits_Count=("credit","count"),Cash_credits_Value=("credit","sum")).reset_index()

    #####Total credits
    Total_credits=final.groupby(['month_year']).agg(Total_credits_Count=("credit","count"),Total_credits_Value=("credit","sum")).reset_index()

    ###########################Outflows
    #####Non Cash debits
    Non_cash_debits=final[~(final["mode"]=='Cash')].groupby(['month_year']).agg(Non_cash_debits_Count=("debit","count"),Non_cash_debits_Value=("debit","sum")).reset_index()

    #####Cash debits
    Cash_debits=final[(final["mode"]=='Cash')].groupby(['month_year']).agg(Cash_debits_Count=("debit","count"),Cash_debits_Value=("debit","sum")).reset_index()

    #####Total debits
    Total_debits=final.groupby(['month_year']).agg(Total_debits_Count=("debit","count"),Total_debits_Value=("debit","sum")).reset_index()

    ##### Auto debits
    Auto_debits = final[(final["mode"].isin(["Loan/MF","MF","Loan"]))].groupby(['month_year']).agg(Auto_debits_Count=("debit","count"),Auto_debits_Value=("debit","sum")).reset_index()

    ######Max_credit_Amount
    Max_credit_Amount=final.groupby(['month_year']).agg(Max_credit_Amount=("credit","max")).reset_index()

    ######Max_debit_Amount
    Max_debit_Amount=final.groupby(['month_year']).agg(Max_debit_Amount=("debit","max")).reset_index()

    ######Avg balance
    Average_balance=final.groupby(['month_year']).agg(Average_balance=("balance","mean")).reset_index()

    #######Month_End_Balance'
    #final.info()
    months_df=pd.DataFrame({"months":pd.date_range(final["txn_date"].min(),final["txn_date"].max(), freq='MS')})
    months_df["month_year"]=pd.to_datetime(months_df["months"]).dt.to_period('m')
    Month_End_Balance=final.groupby(['month_year']).agg(Month_End_Balance=("balance","last")).reset_index()
    Month_End_Balance1=pd.merge(months_df[["month_year"]],Month_End_Balance,on="month_year",how="left")

    while Month_End_Balance1["Month_End_Balance"].isnull().sum()>0:
        Month_End_Balance1["Month_End_Balance"]=np.where(Month_End_Balance1["Month_End_Balance"].isnull(),Month_End_Balance1["Month_End_Balance"].shift(1),Month_End_Balance1["Month_End_Balance"])
    #####EMI
    EMI = final[(final["mode"].isin(["Loan"]))].groupby(['month_year']).agg(EMI=("debit","sum")).reset_index()

    #######Merging all the KPIs
    ###getting 12 months from maximum transaction date
    months_12=pd.DataFrame({"months":pd.date_range((final["txn_date"].max()+relativedelta(day=31))+relativedelta(months=-12),(final["txn_date"].max()+relativedelta(day=31)), freq='MS')})
    months_12=months_12[months_12["months"]>=final["txn_date"].min().replace(day=1)]

    months_12["month_year"]=pd.to_datetime(months_12["months"]).dt.to_period('m')
    months_12=months_12[["month_year"]]

    credits=months_12.merge(Non_cash_credits,on="month_year",how="left").merge(Cash_credits,on="month_year",how="left").merge(Total_credits,on="month_year",how="left")

    debits=months_12.merge(Non_cash_debits,on="month_year",how="left").merge(Cash_debits,on="month_year",how="left").merge(Total_debits,on="month_year",how="left").merge(Auto_debits,on="month_year",how="left")

    cd1=credits.merge(debits,on="month_year",how="left").merge(Max_credit_Amount,on="month_year",how="left").merge(Max_debit_Amount,on="month_year",how="left")
    cd2=cd1.merge(Average_balance,on="month_year",how="left").merge(Month_End_Balance1,on="month_year",how="left")
    #cd2.info()
    
    cd2.iloc[:,1:]=cd2.iloc[:,1:].fillna(0)
    cd2["Net_Inflow_Amount"]=cd2["Total_credits_Value"]-cd2["Total_debits_Value"]
    cd3=cd2.merge(EMI,on="month_year",how="left")
    cd3["EMI"]=cd3["EMI"].fillna(0)

        
        
        
    cd3["month"]=cd3["month_year"].astype(str).str.split("-")
    cd3["month"]=cd3["month"].apply(lambda x: dt.date(int(x[0]),int(x[1]),1))
    cd3['month']=[d.strftime('%b-%y') for d in cd3['month']]
        
        
        
        
    df3 = cd3.copy()
    #Old code
    # plt.figure(figsize=(12,6))
    # a,=plt.plot(df3['month'],df3['Month_End_Balance'], color='#ee8a11', marker='o', linewidth=3)
    # plt.title('Bank Transaction Summary')
    # #plt.xlabel('Month-Year', fontsize=14)
    # #plt.ylabel('Closing Balance', fontsize=14)
    # b,=plt.plot(df3['month'],df3['Net_Inflow_Amount'], color='#3776ab', marker='o', linewidth=3)
    # c,=plt.plot(df3['month'],df3['EMI'], color='#808080', marker='o', linewidth=3)
    #
    # plt.grid(True)
    # #plt.legend([a, b, c], ['Month-End Balance','Net Inflows','EMI'],loc='lower right')
    # plt.legend([a, b, c], ['Month-End Balance','Net Inflows','EMI'],loc="lower center", mode = "expand", ncol = 3,
    #           bbox_to_anchor=(0.25, -0.15, 0.5, .102))
    #
    #
    #
    #     # plt.show()
    # plt.savefig(settings.STATICFILES_DIRS[0] + '/assets/images/bcmk_fig.png')
    #
    #     #fig.subplots_adjust(bottom)
    #
    #
    # df3 = cd3.copy()
    # plt.figure(figsize=(12,6))
    # a,=plt.plot(df3['month'],df3['Cash_credits_Value'], color='#ee8a11', marker='o', linewidth=3)
    # plt.title('Bank Transaction Summary')
    # #plt.xlabel('Month-Year', fontsize=14)
    # #plt.ylabel('Closing Balance', fontsize=14)
    # b,=plt.plot(df3['month'],df3['Cash_debits_Value'], color='#3776ab', marker='o', linewidth=3)
    # plt.grid(True)
    # plt.legend([a, b], ['Cash Credits','Cash Debits'],loc="lower center", mode = "expand", ncol = 2,
    #           bbox_to_anchor=(0.25, -0.15, 0.5, .102))
    #
    #     # plt.show()
    # plt.savefig(settings.STATICFILES_DIRS[0] + '/assets/images/bcmk_fig_1.png')

    #new code
    x = df3['month']
    y = df3['Month_End_Balance']
    y2 = df3['Net_Inflow_Amount']
    y3 = df3['EMI']
    fig, ax = plt.subplots(figsize=(12, 6))
    a, = plt.plot(x, y, marker='o')
    b, = plt.plot(x, y2, marker='o')
    c, = plt.plot(x, y3, marker='o')
    ax.set_yticklabels([])
    plt.title('Bank Transaction Summary')
    for xitem, yitem in np.nditer([x, y], flags=(["refs_ok"]), op_flags=["readwrite"]):
        ax.text(xitem, yitem, int(yitem), dict(size=9, color='blue'), ha="left")
    for xitem, y2item in np.nditer([x, y2], flags=(["refs_ok"]), op_flags=["readwrite"]):
        ax.text(xitem, y2item, int(y2item), dict(size=9, color='orange'), ha="right")
    for xitem, y3item in np.nditer([x, y3], flags=(["refs_ok"]), op_flags=["readwrite"]):
        ax.text(xitem, y3item, int(y3item), dict(size=9, color='green'), ha="right")
    plt.legend([a, b, c], ['Month-End Balance', 'Net Inflows', 'EMI'], loc="lower center", mode="expand", ncol=3,
               bbox_to_anchor=(0.25, -0.15, 0.5, .102))

    plt.grid(True)
    # plt.show()
    plt.savefig(settings.STATICFILES_DIRS[0] + '/assets/images/bcmk_fig.png')

    ##############################
    df3 = cd3.copy()
    plt.figure(figsize=(12, 6))
    x1 = df3['month']
    y1 = df3['Cash_credits_Value']
    y2 = df3['Cash_debits_Value']
    a, = plt.plot(x1, y1, color='#ee8a11', marker='o', linewidth=3)
    plt.title('Bank Transaction Summary')
    # plt.xlabel('Month-Year', fontsize=14)
    # plt.ylabel('Closing Balance', fontsize=14)
    b, = plt.plot(x1, y2, color='#3776ab', marker='o', linewidth=3)
    plt.grid(True)
    ax = plt.gca()
    ax.set_yticklabels([])

    for xitem, yitem in np.nditer([x1, y1], flags=(["refs_ok"]), op_flags=["readwrite"]):
        ax.text(xitem, yitem, int(yitem), dict(size=10, color='#ee8a11'), ha="left")
    for xitem, y2item in np.nditer([x1, y2], flags=(["refs_ok"]), op_flags=["readwrite"]):
        ax.text(xitem, y2item, int(y2item), dict(size=10, color='#3776ab'), ha="right")

    plt.legend([a, b], ['Cash Credits', 'Cash Debits'], loc="lower center", mode="expand", ncol=2,
               bbox_to_anchor=(0.25, -0.15, 0.5, .102))

    # plt.show()
    plt.savefig(settings.STATICFILES_DIRS[0] + '/assets/images/bcmk_fig_1.png')