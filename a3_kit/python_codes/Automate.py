# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import re
import numpy as np
from pandasql import sqldf
pysqldf=lambda q: sqldf(q,globals())
import pymysql
import numpy_financial as npf
#######################################basic table#########################################################
# conn = pymysql.connect(host = '192.xxx.110.xx', port = 3306, user = 'xxxxxxxxxx', passwd = 'xxxxxxxxxx', charset = 'utf8', db='14july2020')
input=input("Please enter the DEAL_ID and CUSTOMER_ID with COMMA Seperator!")
did=input.split(',')[0]
cid = input.split(',')[1]
conn = pymysql.connect(host = 'localhost', port = 3306, user = 'root', passwd = 'Knowlvers@555', charset = 'utf8', db='a3_kit')

sql1 = "SELECT e.DEAL_ID AS deal_id, e.CUSTOMER_ID AS cust_id, e.BUREAU_ID AS report_id, e.BUREAU_DATE AS date_issued, e.DATE_OF_BIRTH AS DOB, e.NAME AS name, " \
       "e.PAN_NO AS PAN, v.SCORE, v.source FROM a3_kit.bureau_ref_dtl e LEFT JOIN a3_kit.bureau_score_segment v ON v.BUREAU_ID = e.BUREAU_ID AND v.CUSTOMER_ID = e.CUSTOMER_ID AND v.source = e.source "

data_basic = pd.read_sql(sql1, conn)

data_basic=data_basic[['deal_id','cust_id','source','report_id','date_issued','DOB','name','PAN','SCORE']]

print('data_basic = ',data_basic)
data_basic['Aadhar']=np.nan
######################################################################################################
#######################################loan table#########################################################
sql1 = "SELECT CUSTOMER_ID AS cust_id, BUREAU_ID AS report_id, ACCOUNT_HD_SEGMENT AS loan_id,ACCOUNT_TYPE AS account_type," \
       "HIGH_CREDIT_AMOUNT AS disbursed_amount,DATE_REPORTED_CERTIFIED AS date_reported,DATE_AC_DISBURSED AS date_disbursed," \
       "DATE_CLOSED AS date_closed,EMI_AMMOUNT AS emi, DATE_LAST_PAYMENT AS last_payment_date, RATE_OF_INTEREST AS interest_rate," \
       "REPAYMENT_TENURE AS tenure, SUIT_FILED AS suit_filed_willful_default, WRITTEN_OFF_STATUS AS written_off_status," \
       "OWNERSHIP_INDICATOR AS ownership,AMOUNT_OVER_DUE AS amount_overdue,CURRENT_BALANCE AS current_balance,CREDIT_LIMIT AS credit_limit," \
       "DATE_PAYMENT_HST_START,DATE_PAYMENT_HST_END,PAYMENT_HST_1,PAYMENT_HST_2, " \
       "source FROM bureau_account_segment_tl " \



#sql1 = "SELECT CUSTOMER_ID AS cust_id, CIBIL_ID AS report_id, ACCOUNT_HD_SEGMENT AS loan_id,ACCOUNT_TYPE AS account_type,HIGH_CREDIT_AMOUNT AS disbursed_amount,DATE_REPORTED_CERTIFIED AS date_reported,DATE_AC_DISBURSED AS date_disbursed,DATE_CLOSED AS date_closed,EMI_AMMOUNT AS emi, DATE_LAST_PAYMENT AS last_payment_date, RATE_OF_INTEREST AS interest_rate,REPAYMENT_TENURE AS tenure, SUIT_FILED AS suit_filed_willful_default, WRITTEN_OFF_STATUS AS written_off_status,OWNERSHIP_INDICATOR AS ownership,AMOUNT_OVER_DUE AS amount_overdue,CURRENT_BALANCE AS current_balance,CREDIT_LIMIT AS credit_limit,DATE_PAYMENT_HST_START,DATE_PAYMENT_HST_END,PAYMENT_HST_1,PAYMENT_HST_2, 'cibil' AS source FROM bureau_account_segment_tl UNION ALL SELECT CUSTOMER_ID AS cust_id, CRIF_ID AS report_id, ACCOUNT_HD_SEGMENT AS loan_id,ACCOUNT_TYPE AS account_type,HIGH_CREDIT_AMOUNT AS disbursed_amount,DATE_REPORTED_CERTIFIED AS date_reported,DATE_AC_DISBURSED AS date_disbursed,DATE_CLOSED AS date_closed,EMI_AMMOUNT AS emi, DATE_LAST_PAYMENT AS last_payment_date, RATE_OF_INTEREST AS interest_rate,REPAYMENT_TENURE AS tenure, SUIT_FILED AS suit_filed_willful_default, WRITTEN_OFF_STATUS AS written_off_status,OWNERSHIP_INDICATOR AS ownership,AMOUNT_OVER_DUE AS amount_overdue,CURRENT_BALANCE AS current_balance,CREDIT_LIMIT AS credit_limit,DATE_PAYMENT_HST_START,DATE_PAYMENT_HST_END,PAYMENT_HST_1,PAYMENT_HST_2, 'crif' AS source FROM bureau_account_segment_tl UNION ALL SELECT CUSTOMER_ID AS cust_id, EQUIFAX_ID AS report_id, ACCOUNT_HD_SEGMENT AS loan_id,ACCOUNT_TYPE AS account_type,HIGH_CREDIT_AMOUNT AS disbursed_amount,DATE_REPORTED_CERTIFIED AS date_reported,DATE_AC_DISBURSED AS date_disbursed,DATE_CLOSED AS date_closed,EMI_AMMOUNT AS emi, DATE_LAST_PAYMENT AS last_payment_date, RATE_OF_INTEREST AS interest_rate,REPAYMENT_TENURE AS tenure, SUIT_FILED AS suit_filed_willful_default, WRITTEN_OFF_STATUS AS written_off_status,OWNERSHIP_INDICATOR AS ownership,AMOUNT_OVER_DUE AS amount_overdue,CURRENT_BALANCE AS current_balance,CREDIT_LIMIT AS credit_limit,DATE_PAYMENT_HST_START,DATE_PAYMENT_HST_END,PAYMENT_HST_1,PAYMENT_HST_2, 'equifax' AS source FROM bureau_account_segment_tl UNION ALL SELECT CUSTOMER_ID AS cust_id, EXPERIAN_ID AS report_id, ACCOUNT_HD_SEGMENT AS loan_id,ACCOUNT_TYPE AS account_type,HIGH_CREDIT_AMOUNT AS disbursed_amount,DATE_REPORTED_CERTIFIED AS date_reported,DATE_AC_DISBURSED AS date_disbursed,DATE_CLOSED AS date_closed,EMI_AMMOUNT AS emi, DATE_LAST_PAYMENT AS last_payment_date, RATE_OF_INTEREST AS interest_rate,REPAYMENT_TENURE AS tenure, SUIT_FILED AS suit_filed_willful_default, WRITTEN_OFF_STATUS AS written_off_status,OWNERSHIP_INDICATOR AS ownership,AMOUNT_OVER_DUE AS amount_overdue,CURRENT_BALANCE AS current_balance,CREDIT_LIMIT AS credit_limit,DATE_PAYMENT_HST_START,DATE_PAYMENT_HST_END,PAYMENT_HST_1,PAYMENT_HST_2, 'experian' AS source FROM bureau_account_segment_tl"
data_loan_raw = pd.read_sql(sql1, conn)


data_loan_raw=data_loan_raw.merge(data_basic[['deal_id','cust_id','date_issued','source','report_id']],on=['source','report_id','cust_id'],how='left')

############################security status
data_loan_raw['security_status']=np.where(data_loan_raw['account_type'].isin(["05","06","08","09","10","12",
         "14","16","18","19","20","35","36","37","38","39","40","41","43","44","45","51","52",
         "53","54","55","56","57","58","61","00"]),"Un-secured","secured")

##########################ownership

data_loan_raw['ownership']=data_loan_raw['ownership'].astype(str).map({"1":"Individual",
         "2":"Supl Card Holder","3":"Guarantor","4":"Joint"})

##########################3account type
data_loan_raw['account_type'] = data_loan_raw['account_type'].apply(lambda x: ('0'+str(x)) if(len(x)==1) else x)
data_loan_raw['account_type']=data_loan_raw['account_type'].astype(str).map({"01": "Auto Loan (Personal)",
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
"00":"Other"})

data_loan_raw['account_type']=data_loan_raw['account_type'].fillna("Other")


data_loan=data_loan_raw[['deal_id','cust_id','source','report_id','loan_id','date_issued','account_type','disbursed_amount','credit_limit','date_reported',
                        'date_disbursed','date_closed','emi','last_payment_date','interest_rate','security_status',
                       'tenure', 'suit_filed_willful_default','written_off_status','ownership',
                       'amount_overdue','current_balance','DATE_PAYMENT_HST_START','DATE_PAYMENT_HST_END']]

data_loan=data_loan.rename(columns={'DATE_PAYMENT_HST_START':'start_date','DATE_PAYMENT_HST_END':'end_date'})
data_loan['active_status']=np.nan





###############################################################DPD table#############################################
data_dpd=data_loan_raw[['deal_id','cust_id','source','report_id','loan_id','security_status','PAYMENT_HST_1', 'PAYMENT_HST_2', 'DATE_PAYMENT_HST_START',
       'DATE_PAYMENT_HST_END']]
data_dpd=data_dpd.dropna(subset=['PAYMENT_HST_1'])
data_dpd['PAYMENT_HST_2']=data_dpd['PAYMENT_HST_2'].fillna("XXX")
data_dpd['payment']=data_dpd['PAYMENT_HST_1']+data_dpd['PAYMENT_HST_2']
data_dpd['payment_new']=data_dpd['payment'].apply(lambda x: [x[i:i+3] for i in range(0,len(x),3)])
data_dpd['DATE_PAYMENT_HST_START'] = pd.to_datetime(data_dpd['DATE_PAYMENT_HST_START'], format="%Y-%m-%d")
data_dpd['DATE_PAYMENT_HST_END'] = pd.to_datetime(data_dpd['DATE_PAYMENT_HST_END'], format="%Y-%m-%d")
data_dpd['date']=data_dpd.apply(lambda row: list(pd.date_range(start=row['DATE_PAYMENT_HST_START'],end=row['DATE_PAYMENT_HST_END'],freq='-1MS')),axis=1)
# data_dpd.to_csv(r'D:\\testing1.csv')
data_dpd['combined']=data_dpd.apply(lambda row: list(zip(row['payment_new'],row['date'])),axis=1)

data_dpd=data_dpd[['deal_id','cust_id','source','report_id','loan_id','security_status','combined']]
data_dpd=data_dpd.reset_index()
# data_dpd.to_csv(r'D:\\testing.csv')
data_dpd_final=pd.DataFrame(np.concatenate(data_dpd['combined']),columns=['DPD','DPD_month']).reset_index(drop=True)
print('data_dpd_final = ',data_dpd_final)
data_dpd_final['deal_id']=np.repeat(data_dpd['deal_id'].values,data_dpd['combined'].str.len())
data_dpd_final['cust_id']=np.repeat(data_dpd['cust_id'].values,data_dpd['combined'].str.len())
data_dpd_final['source']=np.repeat(data_dpd['source'].values,data_dpd['combined'].str.len())
data_dpd_final['report_id']=np.repeat(data_dpd['report_id'].values,data_dpd['combined'].str.len())
data_dpd_final['loan_id']=np.repeat(data_dpd['loan_id'].values,data_dpd['combined'].str.len())

#############################################################Enquiry table##############################################
sql1 = "SELECT CUSTOMER_ID AS cust_id, BUREAU_ID AS report_id, ENQUIRY_SEGMENT_HEADER AS inquiry_id,DATE_OF_ENQUIRY AS date_of_inquiry," \
       "ENQUIRY_PURPOSE AS purpose_of_inquiry, source FROM bureau_enquiry_segment_iq"

data_inquiry = pd.read_sql(sql1, conn)


data_inquiry=data_inquiry[['source','report_id','cust_id','inquiry_id','date_of_inquiry','purpose_of_inquiry']]
data_inquiry['date_of_inquiry']=pd.to_datetime(data_inquiry['date_of_inquiry'])

data_inquiry=data_inquiry.merge(data_basic[['deal_id','cust_id','date_issued','source','report_id']],on=['source','report_id','cust_id'],how='left')

###############################################################Address variation table############################################
sql1 = "SELECT CUSTOMER_ID AS cust_id, BUREAU_ID AS report_id, ADDRESS_1,ADDRESS_2,ADDRESS_3,ADDRESS_4,ADDRESS_5,DATE_OF_ADDR_REPORTED_TO_BUREAU AS address_var_date," \
       " ADDRESS_HEADER AS address_var_id,source FROM bureau_address_segment"

data_address = pd.read_sql(sql1, conn)

data_address['address']=(data_address['ADDRESS_1'].astype(str)+" "+data_address['ADDRESS_2'].astype(str)+" "+
data_address['ADDRESS_3'].astype(str)+" "+data_address['ADDRESS_4'].astype(str)+" "+
data_address['ADDRESS_5'].astype(str))
data_address['address_var_value']=data_address['address'].apply(lambda x: x.replace("nan",""))


data_address=data_address[['source','report_id','cust_id','address_var_id','address_var_value','address_var_date']]
data_address=data_address.merge(data_basic[['deal_id','cust_id','date_issued','source','report_id']],on=['source','report_id','cust_id'],how='left')

#########################################################################################################################################################
##############################################filtering single customer(Replace deal_id and cust_id with session deal_id and session customer_id)

# sql1=pysqldf("SELECT * FROM data_loan WHERE deal_id=1114 AND cust_id=116")
sql1=pysqldf("SELECT * FROM data_loan WHERE cust_id="+cid+" AND (deal_id="+did+" OR deal_id is NULL)")
data_loan = sql1
print("data_loan  ",data_loan)
# data_loan = pd.read_sql(sql1, conn)
#####################################################date correction######################################################################################
#############
data_loan_final=data_loan.copy()
data_loan_final['date_issued_som']=data_loan_final['date_issued']
data_loan_final['date_issued_som']=pd.to_datetime(data_loan_final['date_issued_som'])
data_loan_final['date_issued_som']=data_loan_final['date_issued_som'].apply(lambda x: x.replace(day=1))

data_loan_final['date_reported_som']=data_loan_final['date_reported']
data_loan_final['date_reported_som']=pd.to_datetime(data_loan_final['date_reported_som'])
data_loan_final['date_reported_som']=data_loan_final['date_reported_som'].apply(lambda x: x.replace(day=1))

data_loan_final['date_disbursed_som']=data_loan_final['date_disbursed']
data_loan_final['date_disbursed_som']=pd.to_datetime(data_loan_final['date_disbursed_som'])
data_loan_final['date_disbursed_som']=data_loan_final['date_disbursed_som'].apply(lambda x: x.replace(day=1))

data_loan_final['date_closed_som']=data_loan_final['date_closed']
data_loan_final['date_closed_som']=pd.to_datetime(data_loan_final['date_closed_som'])
data_loan_final['date_closed_som']=data_loan_final['date_closed_som'].apply(lambda x: x.replace(day=1))

data_loan_final['last_payment_date_som']=data_loan_final['last_payment_date']
data_loan_final['last_payment_date_som']=pd.to_datetime(data_loan_final['last_payment_date_som'])
data_loan_final['last_payment_date_som']=data_loan_final['last_payment_date_som'].apply(lambda x: x.replace(day=1))



data_loan_final['min_dpd_date_new']=data_loan_final['end_date']
data_loan_final['min_dpd_date_new']=pd.to_datetime(data_loan_final['min_dpd_date_new'])
data_loan_final['min_dpd_date_som']=data_loan_final['min_dpd_date_new'].apply(lambda x: x.replace(day=1))

conditions=[data_loan_final['date_reported_som']>data_loan_final['date_issued_som']]
choices=[data_loan_final['date_issued_som']]
data_loan_final['date_reported_som_new']=np.select(conditions,choices,default=data_loan_final['date_reported_som'])


conditions=[((data_loan_final['date_closed_som'].dt.year<=1900) | (data_loan_final['date_closed_som']>data_loan_final['date_issued_som']))]
choices=[pd.NaT]
data_loan_final['date_closed_som_new']=np.select(conditions,choices,default=data_loan_final['date_closed_som'])
data_loan_final['date_closed_som_new']=pd.to_datetime(data_loan_final['date_closed_som_new'])


conditions=[((data_loan_final['date_disbursed_som'].dt.year<=1900) |
        (data_loan_final['date_disbursed_som'].isna()) |
        (data_loan_final['date_disbursed_som']>data_loan_final['date_reported_som']) |
        (data_loan_final['date_disbursed_som']>data_loan_final['date_issued_som']) |
        ((data_loan_final['date_disbursed_som']>data_loan_final['date_closed_som_new']) & (data_loan_final['date_closed_som_new'].notna()))
        )]
choices=[data_loan_final['min_dpd_date_som']]
data_loan_final['date_disbursed_som_new']=np.select(conditions,choices,default=data_loan_final['date_disbursed_som'])


conditions=[data_loan_final['last_payment_date'].isna()]
choices=[data_loan_final['date_reported_som_new']]
data_loan_final['last_payment_date_som_1']=np.select(conditions,choices,default=data_loan_final['last_payment_date_som'])

conditions=[(data_loan_final['last_payment_date_som_1'].dt.year<2000),
        (data_loan_final['last_payment_date_som_1']>data_loan_final['date_reported_som_new']),
        ((data_loan_final['last_payment_date_som_1']<data_loan_final['date_disbursed_som_new']) & (data_loan_final['date_disbursed_som_new'].notna()))
        ]
choices=[data_loan_final['date_reported_som_new'],data_loan_final['date_reported_som_new'],data_loan_final['date_reported_som_new']]
data_loan_final['last_payment_date_som_2']=np.select(conditions,choices,default=data_loan_final['last_payment_date_som_1'])

data_loan_final['last_payment_date_som_new']=data_loan_final['last_payment_date_som_2']-pd.DateOffset(months=1)

data_loan=data_loan_final.copy()



###################################written-off(Replace deal_id and cust_id with session deal_id and session customer_id)
# sql1=pysqldf("SELECT * FROM data_dpd_final WHERE deal_id=1114 AND cust_id=116")
sql1=pysqldf("SELECT * FROM data_dpd_final WHERE cust_id="+cid+" AND deal_id="+did+"")
data_dpd_final = sql1
# data_dpd_final = pd.read_sql(sql1, conn)

temp=data_dpd_final.copy()
temp['DPD']=temp['DPD'].replace("XXX",0)
temp['DPD']=temp['DPD'].replace("0XX",0)
temp['DPD']=temp['DPD'].replace("NEW",0)
temp['DPD']=temp['DPD'].replace("STD",0)
temp['DPD']=temp['DPD'].replace("SMA",180)
temp['DPD']=temp['DPD'].replace("LSS",180)
temp['DPD']=temp['DPD'].replace("DBT",180)
temp['DPD']=temp['DPD'].replace("SUB",180)
temp['DPD']=temp['DPD'].astype(int)
temp['180_dpd_flag']=temp['DPD'].apply(lambda x: 1 if x>=80 else 0)
temp=temp.groupby(['deal_id','cust_id','source','loan_id'])['180_dpd_flag'].sum().reset_index(name='count_180_dpd_flag')
temp['count_180_dpd_flag']=temp['count_180_dpd_flag'].apply(lambda x: 1 if x>0 else 0)

temp1=data_loan.copy()
temp1['written_off_flag']=np.where(temp1['written_off_status'].isin([0,1,2,3,4,5,6,7,8,9,10,11,99]),1,0)
temp1=temp1.merge(temp,on=['deal_id','cust_id','source','loan_id'],how='left')
temp1['final_written_off_status']=np.where(((temp1['written_off_flag']>0) | (temp1['count_180_dpd_flag']>0)),1,0)
data_loan=data_loan.merge(temp1[['deal_id','cust_id','source','loan_id','final_written_off_status']],on=['deal_id','cust_id','source','loan_id'],how='left')


########################################active_sattus
temp=data_loan.copy()

conditions=[(temp['active_status'].notna()),((temp['active_status'].isna()) & (temp['date_closed'].isna()) & (temp['final_written_off_status']==0))]
choices=[temp['active_status'],"Active"]
temp['loan_status']=np.select(conditions,choices,default="Closed")

data_loan=temp.copy()

#########################################last dpd

data_dpd_final=data_dpd_final.merge(data_basic[['deal_id','cust_id','date_issued','source','report_id']],on=['source','report_id','cust_id','deal_id'],how='left')
data_dpd_final['date_issued'] = pd.to_datetime(data_dpd_final['date_issued'], errors='coerce')
data_dpd_final['DPD_month'] = pd.to_datetime(data_dpd_final['DPD_month'], errors='coerce')
data_dpd_final['month_since_dpd']=(data_dpd_final['date_issued']-data_dpd_final['DPD_month'])/np.timedelta64(1,"M")
temp=data_dpd_final[~data_dpd_final['DPD'].isin(["XXX","STD","000"])]

#df.loc[df.groupby('A')['C'].idxmin()]
temp=temp.loc[temp.groupby(['deal_id', 'cust_id', 'source', 'report_id', 'loan_id'])['month_since_dpd'].idxmin()]
temp=temp[['deal_id', 'cust_id', 'source', 'report_id', 'loan_id','DPD', 'DPD_month']]
temp['DPD_month_new']=temp['DPD_month']
temp['DPD_month_new']=temp['DPD_month_new'].apply(lambda x:x.strftime("%b %Y"))
data_loan=data_loan.merge(temp,on=['deal_id', 'cust_id', 'source', 'report_id', 'loan_id'],how='left')

#############################################identifying duplicate loans

loan_uniq=data_loan[['deal_id','cust_id','disbursed_amount','date_disbursed','account_type']]
loan_uniq=loan_uniq.drop_duplicates()
loan_uniq['id']=list(range(1,len(loan_uniq)+1))
print(len(loan_uniq['id']))
print(loan_uniq['id'].nunique())

data_loan=data_loan.merge(loan_uniq,on=['deal_id','cust_id','disbursed_amount','date_disbursed','account_type'],how='left')
print(len(data_loan['id']))
print(data_loan['id'].nunique())

#########################replacing disbursed_amount with credit_limit in the case of cc od
data_loan['acc_type_new']=data_loan['account_type'].astype(str).apply(lambda x: re.sub('[\W_]+','',x).lower())


data_loan['disbursed_amount']=np.where(data_loan['acc_type_new'].isin(["corporatecreditcard","creditcard",
                                                      "fleetcard","kisancreditcard","loanagainstcard",
                                                      "loanoncreditcard","securedcreditcard","overdraft",
                                                      "primeministerjaandhanyojanaoverdraft","telcolandline",
                                                      "telcowireless","telcobroadband","autooverdraft"]),data_loan['credit_limit'],data_loan['disbursed_amount'])



##############################imputing tenure
data_loan['interest_rate']=data_loan['interest_rate'].astype(float)
data_loan['interest_rate_1']=data_loan['interest_rate']/(12*100)
data_loan['emi']=data_loan['emi'].replace(to_replace=[None], value=0)
data_loan['emi']=data_loan['emi'].astype(float)
data_loan['disbursed_amount']=data_loan['disbursed_amount'].replace(to_replace=[None], value=0)
data_loan['disbursed_amount']=data_loan['disbursed_amount'].astype(float)

###########################################imputing tenure by formula
conditions=[((data_loan['disbursed_amount']>0) & (data_loan['interest_rate_1']>0) & (data_loan['emi']>0) & ((data_loan['tenure'].isna()) | (data_loan['tenure']==0)))]
#choices=[(np.log2(data_loan['emi']/(data_loan['emi']-(data_loan['disbursed_amount']*data_loan['interest_rate_1'])))/np.log2(data_loan['interest_rate_1']+1))]
choices=[npf.nper(data_loan['interest_rate']/1200, data_loan['emi'], data_loan['disbursed_amount'])]

data_loan['tenure_new']=np.select(conditions,choices,default=data_loan['tenure'])
print('tenure_new=',data_loan['tenure_new'])
##################################### imputing tenure max of same group

data_loan['tenure']=data_loan['tenure'].replace(0,np.nan).replace('',np.nan).astype('float64')
data_loan['tenure_temp'] = data_loan['tenure'].fillna(data_loan.groupby('id')['tenure'].transform('max'))
data_loan['tenure_new']=np.where(((data_loan['tenure_new'].isna()) | (data_loan['tenure_new']==0)),data_loan['tenure_temp'],data_loan['tenure_new'])
print('tenure_new=',data_loan['tenure_new'])

###########################################imputing interest rate
###########################################imputing tenure by formula
print(data_loan.dtypes)
conditions=[((data_loan['disbursed_amount']>0) & (data_loan['tenure']>0) & (data_loan['emi']>0) & ((data_loan['interest_rate'].isna()) | (data_loan['interest_rate']==0)))]

choices=[npf.rate(data_loan['tenure'], data_loan['emi'], -data_loan['disbursed_amount'], 0)*1200]

data_loan['interest_rate_new']=np.select(conditions,choices,default=data_loan['interest_rate'])
# print('interest_rate_new =',data_loan['interest_rate_new'])
##################################### imputing tenure max of same group
data_loan['interest_rate']=data_loan['interest_rate'].replace(0,np.nan)
data_loan['interest_rate_temp'] = data_loan['interest_rate'].fillna(data_loan.groupby('id')['interest_rate'].transform('max'))
data_loan['interest_rate_new']=np.where(((data_loan['interest_rate_new'].isna()) | (data_loan['interest_rate_new']==0)),data_loan['interest_rate_temp'],data_loan['interest_rate_new'])

# print('interest_rate_new =',data_loan['interest_rate_new'])


######################################################imputation by aavas method
tenure_by_acc_type_loan_amt=pd.read_excel("/Users/hardikbhardwaj/Downloads/tenure_by_acc_type_loan_amt_revised.xlsx")
tenure_by_acc_type_for_missing=pd.read_excel("/Users/hardikbhardwaj/Downloads/tenure_by_acc_type_for_missing.xlsx")
loan_amt_bins_for_tenure=pd.read_excel("/Users/hardikbhardwaj/Downloads/loan_amt_bins_for_tenure_revised.xlsx")
ROI_for_EMI_impute=pd.read_excel("/Users/hardikbhardwaj/Downloads/ROI_calculation.xlsx",sheet_name="Sheet_ROI")

crif_cibil_dedup=data_loan.copy()

tenure_by_acc_type_loan_amt['acc_type_new']=tenure_by_acc_type_loan_amt['acc_type'].astype(str).apply(lambda x:re.sub('[\W_]+','',x).lower())
tenure_by_acc_type_for_missing['acc_type_new']=tenure_by_acc_type_for_missing['acc_type'].astype(str).apply(lambda x:re.sub('[\W_]+','',x).lower())
loan_amt_bins_for_tenure['acc_type_new']=loan_amt_bins_for_tenure['acc_type'].astype(str).apply(lambda x:re.sub('[\W_]+','',x).lower())

###############################################################################################################
ROI_for_EMI_impute['last_payment_date_som_new']=pd.to_datetime(ROI_for_EMI_impute['last_payment_date_som_new'],format="%Y-%m-%d")
ROI_for_EMI_impute['acc_type_new']=ROI_for_EMI_impute['acct_type'].astype(str).apply(lambda x: re.sub('[\W_]+','',x).lower())

### rows 2064
ROI_for_EMI_impute_201604=ROI_for_EMI_impute[ROI_for_EMI_impute['last_payment_date_som_new']==pd.to_datetime("2016-04-01")]
ROI_for_EMI_impute_201604=ROI_for_EMI_impute_201604.rename(columns={"ROI_1":"ROI_201604"})
### rows 43

ROI_for_EMI_impute_latest=ROI_for_EMI_impute[ROI_for_EMI_impute['last_payment_date_som_new']==ROI_for_EMI_impute['last_payment_date_som_new'].max()]
ROI_for_EMI_impute_latest=ROI_for_EMI_impute_latest.rename(columns={"ROI_1":"ROI_latest","last_payment_date_som_new":"Latest_ROI_date"})

###############################################################################tenure#######################################
crif_cibil_dedup=crif_cibil_dedup.rename(columns={ "acc_type_new":"acc_type_orig"})

conditions=[((~crif_cibil_dedup["acc_type_orig"].isin(["corporatecreditcard","creditcard","fleetcard","kisancreditcard","loanagainstcard","loanoncreditcard","securedcreditcard","overdraft", "primeministerjaandhanyojanaoverdraft","telcolandline","telcowireless","telcobroadband","autooverdraft"])) & (~crif_cibil_dedup['acc_type_orig'].isin(ROI_for_EMI_impute['acc_type_new'].unique().tolist())))]
choices=["personalloan"]
crif_cibil_dedup["acc_type_new"]=np.select(conditions,choices,default=crif_cibil_dedup['acc_type_orig'])



crif_cibil_dedup_t=pd.merge(crif_cibil_dedup,loan_amt_bins_for_tenure.iloc[:,1:],on='acc_type_new',how='left')

conditions=[((crif_cibil_dedup_t['disbursed_amount']>0) & (crif_cibil_dedup_t['disbursed_amount']<=crif_cibil_dedup_t['loan_amt_25'])),
 ((crif_cibil_dedup_t['disbursed_amount']>crif_cibil_dedup_t['loan_amt_25']) & (crif_cibil_dedup_t['disbursed_amount']<=crif_cibil_dedup_t['loan_amt_50'])),
((crif_cibil_dedup_t['disbursed_amount']>crif_cibil_dedup_t['loan_amt_50']) & (crif_cibil_dedup_t['disbursed_amount']<=crif_cibil_dedup_t['loan_amt_75'])),
(crif_cibil_dedup_t['disbursed_amount']>crif_cibil_dedup_t['loan_amt_75'])]
choices=["bin_1","bin_2","bin_3","bin_4"]
crif_cibil_dedup_t['loan_amt_bins']=np.select(conditions,choices,default="NA")

crif_cibil_dedup_1=pd.merge(crif_cibil_dedup_t,tenure_by_acc_type_loan_amt.iloc[:,1:],on=['acc_type_new',"loan_amt_bins"],how='left')
crif_cibil_dedup_1=pd.merge(crif_cibil_dedup_1,tenure_by_acc_type_for_missing.iloc[:,1:],on='acc_type_new',how='left')

crif_cibil_dedup_1['tenure_new']= crif_cibil_dedup_1['tenure_new'].replace(0,np.nan).replace('',np.nan).astype('float64')
# print(crif_cibil_dedup_1['tenure_new'],crif_cibil_dedup_1['tenure_new'].dtypes)
conditions=[((crif_cibil_dedup_1['tenure_new'].isna()) | ((crif_cibil_dedup_1['tenure_new']<=0) & (crif_cibil_dedup_1['mode_tenure_acct_type'].isna()))),
 ((crif_cibil_dedup_1['mode_tenure_acct_type'].notna()) & ((crif_cibil_dedup_1['tenure_new']<=0) | (crif_cibil_dedup_1['tenure_new'].isna()))),
crif_cibil_dedup_1['tenure_new']>0]
choices=[crif_cibil_dedup_1['mode_tenure'],crif_cibil_dedup_1['mode_tenure_acct_type'],crif_cibil_dedup_1['tenure_new']]
crif_cibil_dedup_1['tenure_new']=np.select(conditions,choices,default=np.nan)

print('tenure_new=',crif_cibil_dedup_1['tenure_new'])


#########################################################ROI

crif_cibil_dedup_1['acc_type_new']=np.where(((~crif_cibil_dedup_1['acc_type_new'].isin(["corporatecreditcard","creditcard","fleetcard","kisancreditcard","loanagainstcard","loanoncreditcard","securedcreditcard","overdraft", "primeministerjaandhanyojanaoverdraft","telcolandline","telcowireless","telcobroadband", "autooverdraft"])) & (~crif_cibil_dedup_1['acc_type_new'].isin(ROI_for_EMI_impute['acc_type_new'].unique().tolist()))), "personalloan",crif_cibil_dedup_1['acc_type_new'])

crif_cibil_dedup_2=pd.merge(crif_cibil_dedup_1, ROI_for_EMI_impute.iloc[:,1:],
                          on=["acc_type_new", "last_payment_date_som_new"], how='left')

crif_cibil_dedup_3=pd.merge(crif_cibil_dedup_2, ROI_for_EMI_impute_201604[["acc_type_new","ROI_201604"]],
                          on="acc_type_new", how='left')

crif_cibil_dedup_3=pd.merge(crif_cibil_dedup_3, ROI_for_EMI_impute_latest[["acc_type_new","ROI_latest","Latest_ROI_date"]],
                          on="acc_type_new", how='left')


crif_cibil_dedup_4=crif_cibil_dedup_3.copy()

conditions=[((crif_cibil_dedup_4['last_payment_date_som_new']<pd.to_datetime("2016-04-01")) & ((crif_cibil_dedup_4['interest_rate_new'].isna()) | (crif_cibil_dedup_4['interest_rate_new']==0))), ((crif_cibil_dedup_4['last_payment_date_som_new']>crif_cibil_dedup_4['Latest_ROI_date']) & ((crif_cibil_dedup_4['interest_rate_new'].isna()) | (crif_cibil_dedup_4['interest_rate_new']==0))),((crif_cibil_dedup_4['interest_rate_new'].isna()) | (crif_cibil_dedup_4['interest_rate_new']==0))]

choices=[crif_cibil_dedup_4['ROI_201604'], crif_cibil_dedup_4['ROI_latest'],crif_cibil_dedup_4['ROI_1']]
crif_cibil_dedup_4['interest_rate_new']=np.select(conditions,choices,default=crif_cibil_dedup_4['interest_rate_new'])

# print('interest_rate_new =',crif_cibil_dedup_4['interest_rate_new'])
######################################################################emi

crif_cibil_dedup_4['r']=crif_cibil_dedup_4['interest_rate_new']/(12*100)
crif_cibil_dedup_4['r']=crif_cibil_dedup_4['r'].astype(float)
crif_cibil_dedup_4['tenure_new']=crif_cibil_dedup_4['tenure_new'].astype(float)
crif_cibil_dedup_4['t']=(1+crif_cibil_dedup_4['r'])**(crif_cibil_dedup_4['tenure_new'])
crif_cibil_dedup_4['emi_temp']=(crif_cibil_dedup_4['disbursed_amount']*crif_cibil_dedup_4['r']*crif_cibil_dedup_4['t'])/(crif_cibil_dedup_4['t']-1)


crif_cibil_dedup_4['emi_new']=np.where(((crif_cibil_dedup_4['emi'].isna()) | (crif_cibil_dedup_4['emi']==0)),crif_cibil_dedup_4['emi_temp'],crif_cibil_dedup_4['emi'])
data_loan=crif_cibil_dedup_4.copy()

print('emi_new=',data_loan['emi_new'])
#################################################################duplicate loan yes or no



data_loan['serial_number']=list(range(1,len(data_loan)+1))
data_loan_1=data_loan.copy()

first=data_loan_1[(((data_loan_1['disbursed_amount'].isna()) | (data_loan_1['disbursed_amount']==0)) & ((data_loan_1['emi'].isna()) | (data_loan_1['emi']==0)))]
first['extra_column']="emi and disbursed amount both are zero"

data_loan_1=data_loan_1[~data_loan_1['serial_number'].isin(first['serial_number'].unique().tolist())]
#####################################unique loans
cnt_source_1=pysqldf('select id, count(source) as cnt_source_1 from data_loan_1 group by id')

dedup_data_2=pysqldf('select a.*, b.cnt_source_1 from data_loan_1 a left join cnt_source_1 b on a.id=b.id')
dedup_dataset1=dedup_data_2[dedup_data_2['cnt_source_1']==1]
dedup_dataset2=dedup_data_2[dedup_data_2['cnt_source_1']>1]
################################################based on ownership
dedup_dataset2a=pysqldf('select * from dedup_dataset2 where ownership is null or ownership not in ("Supl Card Holder","Guarantor","Joint")')

dedup_dataset2a_remain=pysqldf('select * from dedup_dataset2 where id not in (select distinct id from dedup_dataset2a)')
cnt_source_2a=pysqldf('select id, count(source) as cnt_source_2 from dedup_dataset2a group by id')

dedup_dataset2a=pysqldf('select a.*, b.cnt_source_2 from dedup_dataset2a a left join cnt_source_2a b on a.id=b.id')
dedup_dataset3a=dedup_dataset2a[dedup_dataset2a['cnt_source_2']==1]
dedup_dataset3b=dedup_dataset2a[dedup_dataset2a['cnt_source_2']>1]
################################################date_reported_max
temp=dedup_dataset3b.groupby('id')['date_reported'].max().reset_index(name="max_date_reported")
dedup_dataset3b=dedup_dataset3b.merge(temp,on='id',how='left')

dedup_dataset3b_1=pysqldf('select * from dedup_dataset3b where date_reported=max_date_reported')
dedup_dataset3b_1_remain=pysqldf('select * from dedup_dataset3b where id not in (select distinct id from dedup_dataset3b_1)')
cnt_source_3b=pysqldf('select id, count(source) as cnt_source_3 from dedup_dataset3b_1 group by id')
dedup_dataset3b_1=pysqldf('select a.*, b.cnt_source_3 from dedup_dataset3b_1 a left join cnt_source_3b b on a.id=b.id')

dedup_dataset4a=dedup_dataset3b_1[dedup_dataset3b_1['cnt_source_3']==1]
dedup_dataset4b=dedup_dataset3b_1[dedup_dataset3b_1['cnt_source_3']>1]

#####################################################last DPD
temp=dedup_dataset4b.groupby('id')['DPD_month'].max().reset_index(name="most_recent_dpd_month")
dedup_dataset4b=dedup_dataset4b.merge(temp,on='id',how='left')

dedup_dataset4b_1=pysqldf('select * from dedup_dataset4b where DPD_month=most_recent_dpd_month')

dedup_dataset4b_1_remain=pysqldf('select * from dedup_dataset4b where id not in (select distinct id from dedup_dataset4b_1)')
cnt_source_4b=pysqldf('select id, count(source) as cnt_source_4 from dedup_dataset4b_1 group by id')
dedup_dataset4b_1=pysqldf('select a.*, b.cnt_source_4 from dedup_dataset4b_1 a left join cnt_source_4b b on a.id=b.id')

dedup_dataset5a=dedup_dataset4b_1[dedup_dataset4b_1['cnt_source_4']==1]
dedup_dataset5b=dedup_dataset4b_1[dedup_dataset4b_1['cnt_source_4']>1]

##################################overdue amount
dedup_dataset5b_1=dedup_dataset5b[dedup_dataset5b['amount_overdue']>0]

dedup_dataset5b_1_remain=pysqldf('select * from dedup_dataset5b where id not in (select distinct id from dedup_dataset5b_1)')
cnt_source_5b=pysqldf('select id, count(source) as cnt_source_5 from dedup_dataset5b_1 group by id')
dedup_dataset5b_1=pysqldf('select a.*, b.cnt_source_5 from dedup_dataset5b_1 a left join cnt_source_5b b on a.id=b.id')

dedup_dataset6a=dedup_dataset5b_1[dedup_dataset5b_1['cnt_source_5']==1]
dedup_dataset6b=dedup_dataset5b_1[dedup_dataset5b_1['cnt_source_5']>1]



#######################################emi
dedup_dataset6b_1=pysqldf('select * from dedup_dataset6b where emi>0')
dedup_dataset6b_1_remain=pysqldf('select * from dedup_dataset6b where id not in (select distinct id from dedup_dataset6b_1)')
cnt_source_6b=pysqldf('select id, count(source) as cnt_source_6 from dedup_dataset6b_1 group by id')
dedup_dataset6b_1=pysqldf('select a.*, b.cnt_source_6 from dedup_dataset6b_1 a left join cnt_source_6b b on a.id=b.id')

dedup_dataset7a=dedup_dataset6b_1[dedup_dataset6b_1['cnt_source_6']==1]
dedup_dataset7b=dedup_dataset6b_1[dedup_dataset6b_1['cnt_source_6']>1]


############################################source
dict1={'cibil': 1,
 'crif': 2,
 'experian': 3,
 'equifax': 4}

dedup_dataset7b['source_map']=dedup_dataset7b['source'].map(dict1)



dedup_dataset8a=pysqldf('select * from dedup_dataset7b order by id, source_map')
dedup_dataset8a=dedup_dataset8a.groupby('id').nth(0).reset_index()

#########################################remaining

dedup_dataset_remain=pd.concat([dedup_dataset2a_remain,dedup_dataset3b_1_remain,dedup_dataset4b_1_remain,dedup_dataset5b_1_remain,dedup_dataset6b_1_remain])
dedup_dataset_remain['source_map']=dedup_dataset_remain['source'].map(dict1)

dedup_dataset_remain_final=pysqldf('select * from dedup_dataset_remain order by id, source_map')
dedup_dataset_remain_final=dedup_dataset_remain_final.groupby('id').nth(0).reset_index()

data_loan_final=pd.concat([dedup_dataset1,dedup_dataset3a,dedup_dataset4a,dedup_dataset5a,dedup_dataset6a,dedup_dataset7a,dedup_dataset8a,dedup_dataset_remain_final])


data_loan_final=data_loan_final[(data_loan_final.columns) & (data_loan_1.columns)]

data_loan_final=pd.concat([data_loan_final,first])

data_loan_final['selection']="Yes"

#############################################All other loans

remaining=data_loan[~data_loan['serial_number'].isin(data_loan_final['serial_number'].unique().tolist())]
remaining['selection']="No"

##########################final_data
final_data=pd.concat([data_loan_final,remaining])
final_data=final_data.rename(columns={'selection':'Loan_Selection','cust_id':'Customer_Id','date_reported':'Date_reported','account_type':'Loan_type',
                                    'loan_status':'Loan_status', 'disbursed_amount':'Disbursed_amount',
                                    'date_disbursed':'Disbursal_date','tenure':'Tenure','tenure_new':'Tenure_new','interest_rate':'ROI',
                                    'interest_rate_new':'ROI_new','emi':'EMI','emi_new':'EMI_new','current_balance':'Current Balance',
                                    'amount_overdue':'Overdue amount','source':'Source'})
print('tenure_new=',final_data['Tenure_new'])
final_data['index']=0
final_data['Loan_Selection_edited']='NULL'
final_data['Loan_Selection_user_edited']=0
final_data['Disbursed_amount_edited']='NULL'
final_data['Disbursed_amount_user_edited']=0
final_data['Tenure_edited']='NULL'
final_data['Tenure_user_edited']=0
final_data['ROI_edited']='NULL'
final_data['ROI_user_edited']=0
final_data['EMI_edited']='NULL'
final_data['EMI_user_edited']=0
final_data['lead_id']='NULL'
final_data['final_selected']=0

final_data['Disbursed_amount'].fillna(value=0,inplace=True)
final_data['EMI'].fillna(value=0,inplace=True)

cols = ['Tenure','Tenure_new','ROI','ROI_new','ROI_edited','EMI_new','EMI_edited','DPD','DPD_month_new']
final_data[cols]=final_data[cols].fillna("NULL")
# print('interest_rate_new =',data_loan['interest_rate_new'])
# print('emi_new=',final_data['emi_new '])

final_data=final_data[['index','Loan_Selection','Loan_Selection_edited','Loan_Selection_user_edited','Customer_Id','Date_reported','Loan_type','Loan_status','Disbursed_amount','Disbursed_amount_edited','Disbursed_amount_user_edited','Disbursal_date','Tenure','Tenure_new','Tenure_edited','Tenure_user_edited',
                      'ROI','ROI_new','ROI_edited','ROI_user_edited', 'EMI','EMI_new','EMI_edited','EMI_user_edited','Current Balance','DPD','DPD_month_new','Overdue amount','Source','lead_id','final_selected']]

final_data['Loan_type']=final_data['Loan_type'].astype('string')
final_data['Disbursed_amount']=final_data['Disbursed_amount'].astype(float)


final_data['Disbursal_date']=pd.to_datetime(final_data['Disbursal_date'])



final_data=final_data.sort_values(['Disbursal_date', 'Loan_type','Disbursed_amount'], ascending=[False, True,True])
final_data['index']=list(range(1,len(final_data)+1))
final_data['DPD']=final_data['DPD'].apply(lambda x: 'NULL' if (x=='nan' or x==None) else x)
final_data.to_csv("/Users/hardikbhardwaj/Downloads/"+cid +"_bureau.csv",index=False)

#final_data.to_excel("\\final_data_output.xlsx", index=False)






