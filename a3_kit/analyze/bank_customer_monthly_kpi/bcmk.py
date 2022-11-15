# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 16:40:37 2021

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


def KPIs(data):
    try:
        #input_path="D:\\User DATA\\Documents\\A3\\KPI\\bank.csv"
        final=data

        #final.info()
        final["mode"].unique()
        final["sub_mode"].unique()
        #Converting string date into datetime 
        final.debit = final.debit.replace(0,np.nan)
        final.credit = final.credit.replace(0,np.nan)
        final["txn_date"]=pd.to_datetime(final["txn_date"], format = '%Y-%m-%d')
        #final["txn_date"]=pd.to_datetime(final["txn_date"], format = '%d-%m-%Y')


        final["month_year"]=pd.to_datetime(final["txn_date"]).dt.to_period('m')

        try:
            final["credit"]=final["credit"].str.replace(",","")

            final["debit"]=final["debit"].str.replace(",","")

            final["balance"]=final["balance"].str.replace(",","")
        except:
            pass
        final["credit"]=final["credit"].astype(float)
        final["debit"]=final["debit"].astype(float)
        final["balance"]=final["balance"].astype(float)

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

        #######Month_End_balance'
        #final.info()
        check_month_df = {"month_min":(final['txn_date'].min()).month,"month_max":(final['txn_date'].max()).month,"year_min": (final['txn_date'].min()).year,"year_max": (final['txn_date'].max()).year}

        if((check_month_df['month_min']==check_month_df['month_max']) and (check_month_df['year_min']==check_month_df['year_max'])):
            try:
                months_df=pd.DataFrame([{"months":final["txn_date"].max()}])
            except Exception as e:
                print(e)

        else:
            months_df=pd.DataFrame({"months":pd.date_range(final["txn_date"].min(),final["txn_date"].max(), freq='MS')})
        #months_df=pd.DataFrame({"months":pd.date_range(final["txn_date"].min(),final["txn_date"].max(), freq='MS')})
        months_df["month_year"]=pd.to_datetime(months_df["months"]).dt.to_period('m')
        Month_End_balance=final.groupby(['month_year']).agg(Month_End_balance=("balance","last")).reset_index()
        Month_End_balance1=pd.merge(months_df[["month_year"]],Month_End_balance,on="month_year",how="left")

        while Month_End_balance1["Month_End_balance"].isnull().sum()>0:
            Month_End_balance1["Month_End_balance"]=np.where(Month_End_balance1["Month_End_balance"].isnull(),Month_End_balance1["Month_End_balance"].shift(1),Month_End_balance1["Month_End_balance"])
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
        cd2=cd1.merge(Average_balance,on="month_year",how="left").merge(Month_End_balance1,on="month_year",how="left")
        #cd2.info()
        cd2.columns
        cd2.iloc[:,1:]=cd2.iloc[:,1:].fillna(0)
        cd2["Net_Inflow_Amount"]=cd2["Total_credits_Value"]-cd2["Total_debits_Value"]
        cd3=cd2.merge(EMI,on="month_year",how="left")
        cd3["EMI"]=cd3["EMI"].fillna(0)

        #Transposing the table
        Monthly_KPIs = cd3.transpose().sort_index(axis=1,ascending=False)
        Monthly_KPIs.columns
        Monthly_KPIs.iloc[0,:]=Monthly_KPIs.iloc[0,:].astype(str).str.split("-").apply(lambda x: dt.date(int(x[0]),int(x[1]),1))
        Monthly_KPIs.iloc[0,:]=Monthly_KPIs.iloc[0,:].apply(lambda x:x.strftime('%b-%y') )                           


        
        return(Monthly_KPIs)
    except:
        pass

