# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import matplotlib.pyplot as plt
import pandas as pd
import re
import numpy as np
from babel.numbers import format_currency
from pandasql import sqldf
pysqldf=lambda q: sqldf(q,globals())

def bureau_c_m_k(bureau_ref_dtl,bureau_score_segment,bureau_account_segment_tl,bureau_enquiry_segment_iq,bureau_address_segment,customer_id,deal_id,ten_acc_loan_amt,ten_acc_missing,loan_amt_bins,roi_cal):

  #######################################basic table#########################################################

  try:
    bureau_ref_dtl['DEAL_ID'] = bureau_ref_dtl['DEAL_ID'].astype('Int64')
  except:
    return
  
  bureau_ref_dtl['DEAL_ID'] = bureau_ref_dtl['DEAL_ID'].astype('Int64')
  bureau_ref_dtl['CUSTOMER_ID'] = bureau_ref_dtl['CUSTOMER_ID'].astype('Int64')

  bureau_score_segment['CUSTOMER_ID'] = bureau_score_segment['CUSTOMER_ID'].astype('Int64')

  bureau_account_segment_tl['CUSTOMER_ID'] = bureau_account_segment_tl['CUSTOMER_ID'].astype('Int64')

  bureau_enquiry_segment_iq['CUSTOMER_ID'] = bureau_enquiry_segment_iq['CUSTOMER_ID'].astype('Int64')

  bureau_address_segment['CUSTOMER_ID'] = bureau_address_segment['CUSTOMER_ID'].astype('Int64')


  data_basic=bureau_ref_dtl

  data_basic=data_basic.rename(columns={'BUREAU_ID':'report_id','BUREAU_DATE':'date_issued',
                    'DATE_OF_BIRTH':'DOB','NAME':'name','PAN_NO':'PAN','DEAL_ID':'deal_id',
                    'CUSTOMER_ID':'cust_id'})

  data_basic=data_basic[['deal_id','cust_id','source','report_id','date_issued','DOB','name','PAN']]


  data_score=bureau_score_segment
  data_score=data_score.rename(columns={'BUREAU_ID':'report_id','CUSTOMER_ID':'cust_id'})
  data_score=data_score[['source','report_id','cust_id','SCORE']]

  data_basic=data_basic.merge(data_score,on=['source','report_id','cust_id'],how='left')
  data_basic['Aadhar']=np.nan
  ######################################################################################################
  #######################################loan table#########################################################


  data_loan_raw=bureau_account_segment_tl

  data_loan_raw=data_loan_raw.rename(columns={'BUREAU_ID':'report_id','ACCOUNT_HD_SEGMENT':'loan_id',
                    'ACCOUNT_TYPE':'account_type','HIGH_CREDIT_AMOUNT':'disbursed_amount',
                   'DATE_REPORTED_CERTIFIED':'date_reported', 'DATE_AC_DISBURSED':'date_disbursed',
           'DATE_CLOSED':'date_closed', 'EMI_AMMOUNT':'emi', 'DATE_LAST_PAYMENT':'last_payment_date',
          'RATE_OF_INTEREST':'interest_rate','REPAYMENT_TENURE':'tenure','SUIT_FILED':'suit_filed_willful_default',
         'WRITTEN_OFF_STATUS':'written_off_status','OWNERSHIP_INDICATOR':'ownership',
        'AMOUNT_OVER_DUE':'amount_overdue','CURRENT_BALANCE':'current_balance','CUSTOMER_ID':'cust_id','CREDIT_LIMIT':'credit_limit'})
  
  
  data_loan_raw=data_loan_raw.merge(data_basic[['deal_id','cust_id','date_issued','source','report_id']],on=['source','report_id','cust_id'],how='left')
  
  
  data_loan_raw['security_status']=np.where(data_loan_raw['account_type'].isin(["05","06","08","09","10","12",
           "14","16","18","19","20","35","36","37","38","39","40","41","43","44","45","51","52",
           "53","54","55","56","57","58","61","00"]),"Un-secured","secured")

  data_loan_raw['ownership']=data_loan_raw['ownership'].astype(str).map({"1":"Individual",
           "2":"Supl Card Holder","3":"Guarantor","4":"Joint"})

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
  data_dpd['date']=data_dpd.apply(lambda row: list(pd.date_range(start=row['DATE_PAYMENT_HST_START'],end=row['DATE_PAYMENT_HST_END'],freq='-1MS')),axis=1)
  data_dpd['combined']=data_dpd.apply(lambda row: list(zip(row['payment_new'],row['date'])),axis=1)

  data_dpd=data_dpd[['deal_id','cust_id','source','report_id','loan_id','security_status','combined']]
  data_dpd=data_dpd.reset_index()
  data_dpd_final=pd.DataFrame(np.concatenate(data_dpd['combined']),columns=['DPD','DPD_month']).reset_index(drop=True)
  data_dpd_final['deal_id']=np.repeat(data_dpd['deal_id'].values,data_dpd['combined'].str.len())
  data_dpd_final['cust_id']=np.repeat(data_dpd['cust_id'].values,data_dpd['combined'].str.len())
  data_dpd_final['source']=np.repeat(data_dpd['source'].values,data_dpd['combined'].str.len())
  data_dpd_final['report_id']=np.repeat(data_dpd['report_id'].values,data_dpd['combined'].str.len())
  data_dpd_final['loan_id']=np.repeat(data_dpd['loan_id'].values,data_dpd['combined'].str.len())

  #############################################################Enquiry table##############################################

  data_inquiry=bureau_enquiry_segment_iq

  data_inquiry=data_inquiry.rename(columns={'BUREAU_ID':'report_id','ENQUIRY_SEGMENT_HEADER':'inquiry_id',
                    'DATE_OF_ENQUIRY':'date_of_inquiry','ENQUIRY_PURPOSE':'purpose_of_inquiry','CUSTOMER_ID':'cust_id' })

  data_inquiry=data_inquiry[['source','report_id','cust_id','inquiry_id','date_of_inquiry','purpose_of_inquiry']]
  data_inquiry['date_of_inquiry']=pd.to_datetime(data_inquiry['date_of_inquiry'],format="%Y-%m-%d")

  data_inquiry=data_inquiry.merge(data_basic[['deal_id','cust_id','date_issued','source','report_id']],on=['source','report_id','cust_id'],how='left')

  ###############################################################Address variation table############################################
  
  
  data_address=bureau_address_segment
  data_address['address']=(data_address['ADDRESS_1'].astype(str)+" "+data_address['ADDRESS_2'].astype(str)+" "+
  data_address['ADDRESS_3'].astype(str)+" "+data_address['ADDRESS_4'].astype(str)+" "+
  data_address['ADDRESS_5'].astype(str))
  data_address['address_var_value']=data_address['address'].apply(lambda x: x.replace("nan",""))

  data_address=data_address.rename(columns={'BUREAU_ID':'report_id','DATE_OF_ADDR_REPORTED_TO_BUREAU':'address_var_date',
                    'ADDRESS_HEADER':'address_var_id','CUSTOMER_ID':'cust_id'})

  data_address=data_address[['source','report_id','cust_id','address_var_id','address_var_value','address_var_date']]
  data_address=data_address.merge(data_basic[['deal_id','cust_id','date_issued','source','report_id']],on=['source','report_id','cust_id'],how='left')

  ######################################################################################################
  ##############################################################month since dpd in loan table########################################

  data_dpd_final=data_dpd_final.merge(data_basic[['deal_id','cust_id','date_issued','source','report_id']],on=['source','report_id','cust_id','deal_id'],how='left')
  data_dpd_final['date_issued'] = pd.to_datetime(data_dpd_final['date_issued'], format = "%Y-%m-%d")
  data_dpd_final['DPD_month'] = pd.to_datetime(data_dpd_final['DPD_month'], format = "%Y-%m-%d")
  data_dpd_final['month_since_dpd']=(data_dpd_final['date_issued']-data_dpd_final['DPD_month'])/np.timedelta64(1,"M")
  temp=data_dpd_final[~data_dpd_final['DPD'].isin(["XXX","STD","000"])]
  temp=temp[temp['month_since_dpd']<=12]
  temp=temp.groupby(['deal_id', 'cust_id', 'source', 'report_id', 'loan_id'])['DPD'].count().reset_index(name='count_of_dpd_12_month')
  data_loan=data_loan.merge(temp,on=['deal_id', 'cust_id', 'source', 'report_id', 'loan_id'],how='left')
  data_loan['count_of_dpd_12_month']=data_loan['count_of_dpd_12_month'].fillna(0)
  #################################duplicate loans#######################################################################

  data_loan['acc_type_new']=data_loan['account_type'].astype(str).apply(lambda x: re.sub('[\W_]+','',x).lower())


  data_loan_1=data_loan[((data_loan['disbursed_amount']>0) | (data_loan['acc_type_new'].isin(["corporatecreditcard","creditcard",
                                                        "fleetcard","kisancreditcard","loanagainstcard",
                                                        "loanoncreditcard","securedcreditcard","overdraft",
                                                        "primeministerjaandhanyojanaoverdraft","telcolandline",
                                                        "telcowireless","telcobroadband","autooverdraft"])))]
  loan_uniq=data_loan_1[['deal_id','cust_id','disbursed_amount','date_disbursed']]
  loan_uniq=loan_uniq.drop_duplicates()


  crif_select_ww=data_loan[(((data_loan['disbursed_amount']<=0) | (data_loan['disbursed_amount'].isna())) &
                        (~data_loan['acc_type_new'].isin(["corporatecreditcard","creditcard",
                                                        "fleetcard","kisancreditcard","loanagainstcard",
                                                        "loanoncreditcard","securedcreditcard","overdraft",
                                                        "primeministerjaandhanyojanaoverdraft","telcolandline",
                                                        "telcowireless","telcobroadband","autooverdraft"])))]

      
  ###########################################################adding id for unique loans
  loan_uniq['id']=list(range(1,len(loan_uniq)+1))
  crif_select_ww['id']=list(range(len(loan_uniq)+1,len(loan_uniq)+len(crif_select_ww)+1))

  data_loan_1=data_loan_1.merge(loan_uniq,on=['deal_id','cust_id','disbursed_amount','date_disbursed'],how='left')

  # cnt_source_1=pysqldf('select id, count(source) as cnt_source_1 from data_loan_1 group by id')
  cnt_source_1 = data_loan_1.groupby('id')['source'].count().reset_index()
  cnt_source_1 = cnt_source_1.rename(columns = {'source':'cnt_source_1'})


  # dedup_data_2=pysqldf('select a.*, b.cnt_source_1 from data_loan_1 a left join cnt_source_1 b on a.id=b.id')
  dedup_data_2 = data_loan_1.merge(cnt_source_1, how = "left", on="id")
  dedup_dataset1=dedup_data_2[dedup_data_2['cnt_source_1']==1]
  dedup_dataset2=dedup_data_2[dedup_data_2['cnt_source_1']>1]

  # dedup_dataset2a=pysqldf('select * from dedup_dataset2 where ownership is null or ownership not in ("Supl Card Holder","Guarantor")')
  dedup_dataset2a = dedup_dataset2[(dedup_dataset2['ownership'] == 'nan') | ((dedup_dataset2['ownership'] != 'Supl Card Holder') & (dedup_dataset2['ownership'] != 'Guarantor'))]  

  # dedup_dataset2a_remain=pysqldf('select * from dedup_dataset2 where id not in (select distinct id from dedup_dataset2a)')
  dedup_dataset2a_remain = dedup_dataset2[~dedup_dataset2['id'].isin(dedup_dataset2a['id'].unique().tolist())]

  # cnt_source_2a=pysqldf('select id, count(source) as cnt_source_2 from dedup_dataset2a group by id')
  cnt_source_2a = dedup_dataset2a.groupby('id')['source'].count().reset_index().rename(columns={'source':'cnt_source_2'})

  # dedup_dataset2a=pysqldf('select a.*, b.cnt_source_2 from dedup_dataset2a a left join cnt_source_2a b on a.id=b.id')
  dedup_dataset2a = dedup_dataset2a.merge(cnt_source_2a[['id', 'cnt_source_2']], on='id', how='left')
  dedup_dataset3a=dedup_dataset2a[dedup_dataset2a['cnt_source_2']==1]
  dedup_dataset3b=dedup_dataset2a[dedup_dataset2a['cnt_source_2']>1]
  ################################################date_reported_max
  temp=dedup_dataset3b.groupby('id')['date_reported'].max().reset_index(name="max_date_reported")
  dedup_dataset3b=dedup_dataset3b.merge(temp,on='id',how='left')

  # dedup_dataset3b_1=pysqldf('select * from dedup_dataset3b where date_reported=max_date_reported')
  dedup_dataset3b_1 = dedup_dataset3b[dedup_dataset3b['date_reported']==dedup_dataset3b['max_date_reported']]
  # dedup_dataset3b_1_remain=pysqldf('select * from dedup_dataset3b where id not in (select distinct id from dedup_dataset3b_1)')
  dedup_dataset3b_1_remain = dedup_dataset3b[~dedup_dataset3b['id'].isin(dedup_dataset3b_1['id'].unique().tolist())]
  # cnt_source_3b=pysqldf('select id, count(source) as cnt_source_3 from dedup_dataset3b_1 group by id')
  cnt_source_3b = dedup_dataset3b_1.groupby('id')['source'].count().reset_index().rename(columns={'source':'cnt_source_3'})
  # dedup_dataset3b_1=pysqldf('select a.*, b.cnt_source_3 from dedup_dataset3b_1 a left join cnt_source_3b b on a.id=b.id')
  dedup_dataset3b_1 = dedup_dataset3b_1.merge(cnt_source_3b[['id', 'cnt_source_3']], on='id', how='left')

  dedup_dataset4a=dedup_dataset3b_1[dedup_dataset3b_1['cnt_source_3']==1]
  dedup_dataset4b=dedup_dataset3b_1[dedup_dataset3b_1['cnt_source_3']>1]

  #######################################emi
  # dedup_dataset4b_1=pysqldf('select * from dedup_dataset4b where emi>500')
  dedup_dataset4b_1 = dedup_dataset4b[dedup_dataset4b['emi']>500]
  # dedup_dataset4b_1_remain=pysqldf('select * from dedup_dataset4b where id not in (select distinct id from dedup_dataset4b_1)')
  dedup_dataset4b_1_remain = dedup_dataset4b[~dedup_dataset4b['id'].isin(dedup_dataset4b_1['id'].unique().tolist())]
  # cnt_source_4b=pysqldf('select id, count(source) as cnt_source_4 from dedup_dataset4b_1 group by id')
  cnt_source_4b = dedup_dataset4b_1.groupby('id')['source'].count().reset_index().rename(columns={'source':'cnt_source_4'})
    # dedup_dataset4b_1=pysqldf('select a.*, b.cnt_source_4 from dedup_dataset4b_1 a left join cnt_source_4b b on a.id=b.id')
  dedup_dataset4b_1 = dedup_dataset4b_1.merge(cnt_source_4b[['id', 'cnt_source_4']], on='id', how='left')

  dedup_dataset5a=dedup_dataset4b_1[dedup_dataset4b_1['cnt_source_4']==1]
  dedup_dataset5b=dedup_dataset4b_1[dedup_dataset4b_1['cnt_source_4']>1]

  #####################################################12 month dpd-maximum times
  temp=dedup_dataset5b.groupby('id')['count_of_dpd_12_month'].max().reset_index(name="max_count_of_dpd_12_month")
  dedup_dataset5b=dedup_dataset5b.merge(temp,on='id',how='left')

  # dedup_dataset5b_1=pysqldf('select * from dedup_dataset5b where count_of_dpd_12_month=max_count_of_dpd_12_month')

  dedup_dataset5b_1 = dedup_dataset5b[dedup_dataset5b['count_of_dpd_12_month']==dedup_dataset5b['max_count_of_dpd_12_month']]

  # dedup_dataset5b_1_remain=pysqldf('select * from dedup_dataset5b where id not in (select distinct id from dedup_dataset5b_1)')
  dedup_dataset5b_1_remain = dedup_dataset5b[~dedup_dataset5b['id'].isin(dedup_dataset5b_1['id'])]

  # cnt_source_5b=pysqldf('select id, count(source) as cnt_source_5 from dedup_dataset5b_1 group by id')
  cnt_source_5b = dedup_dataset5b_1.groupby('id')['source'].count().reset_index().rename(columns={'source':'cnt_source_5'})

  # dedup_dataset5b_1=pysqldf('select a.*, b.cnt_source_5 from dedup_dataset5b_1 a left join cnt_source_5b b on a.id=b.id')
  dedup_dataset5b_1 = dedup_dataset5b_1.merge(cnt_source_5b[['id', 'cnt_source_5']], on='id', how='left')

  dedup_dataset6a=dedup_dataset5b_1[dedup_dataset5b_1['cnt_source_5']==1]
  dedup_dataset6b=dedup_dataset5b_1[dedup_dataset5b_1['cnt_source_5']>1]

  ##################################overdue amount
  dedup_dataset6b_1=dedup_dataset6b[dedup_dataset6b['amount_overdue']>0]

  # dedup_dataset6b_1_remain=pysqldf('select * from dedup_dataset6b where id not in (select distinct id from dedup_dataset6b_1)')
  dedup_dataset6b_1_remain = dedup_dataset6b[~dedup_dataset6b['id'].isin(dedup_dataset6b_1['id'].unique().tolist())]
  # cnt_source_6b=pysqldf('select id, count(source) as cnt_source_6 from dedup_dataset6b_1 group by id')
  cnt_source_6b = dedup_dataset6b_1.groupby('id')['source'].count().reset_index().rename(columns={'source':'cnt_source_6'})
  # dedup_dataset6b_1=pysqldf('select a.*, b.cnt_source_6 from dedup_dataset6b_1 a left join cnt_source_6b b on a.id=b.id')
  dedup_dataset6b_1 = dedup_dataset6b_1.merge(cnt_source_6b[['id','cnt_source_6']], on='id', how='left')

  dedup_dataset7a=dedup_dataset6b_1[dedup_dataset6b_1['cnt_source_6']==1]
  dedup_dataset7b=dedup_dataset6b_1[dedup_dataset6b_1['cnt_source_6']>1]


  ############################################last_payment_date
  # dedup_dataset8a=pysqldf('select * from dedup_dataset7b order by id, last_payment_date')
  dedup_dataset8a = dedup_dataset7b.sort_values(['id', 'last_payment_date'], ascending=[True, True])
  dedup_dataset8a=dedup_dataset8a.groupby('id').nth(-1).reset_index()

  #########################################remaining

  dedup_dataset_remain=pd.concat([dedup_dataset2a_remain,dedup_dataset3b_1_remain,dedup_dataset4b_1_remain,dedup_dataset5b_1_remain,dedup_dataset6b_1_remain])
  # dedup_dataset_remain_final=pysqldf('select * from dedup_dataset_remain order by id, date_reported,last_payment_date')
  dedup_dataset_remain_final = dedup_dataset_remain.sort_values(['id','date_reported','last_payment_date'], ascending=[True, True, True])
  dedup_dataset_remain_final=dedup_dataset_remain_final.groupby('id').nth(-1).reset_index()

  data_loan_final=pd.concat([dedup_dataset1,dedup_dataset3a,dedup_dataset4a,dedup_dataset5a,dedup_dataset6a,dedup_dataset7a,dedup_dataset8a,dedup_dataset_remain_final])


  data_loan_final=data_loan_final[(data_loan_final.columns) & (data_loan_1.columns)]

  data_loan_final=pd.concat([data_loan_final,crif_select_ww])
  #########################################################date correction##############################################
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

  ################################################removing Guarantor and Supl Card holder
  data_loan_final=data_loan_final[~data_loan_final['ownership'].isin(["Supl Card Holder","Guarantor"])]
  ####################################################score######################################################
  cust_level=data_loan_final[['deal_id','cust_id']]
  cust_level=cust_level.drop_duplicates()
  temp=data_basic.groupby(['deal_id','cust_id'])['SCORE'].max().reset_index(name='score')
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id'],how='left')
  ###################################################age###########################
  temp=data_basic.copy()
  temp['date_issued_som']=temp['date_issued']
  temp['date_issued_som']=pd.to_datetime(temp['date_issued_som'])
  temp['date_issued_som']=temp['date_issued_som'].apply(lambda x: x.replace(day=1))

  temp['date_issued_som'] = pd.to_datetime(temp['date_issued_som'])
  temp['DOB'] = pd.to_datetime(temp['DOB'], format = "%Y-%m-%d")
  temp['age']=(temp['date_issued_som']-temp['DOB'])/np.timedelta64(1,"Y")
  temp['age']=temp['age'].astype(int)
  temp=temp.groupby(['deal_id','cust_id'])['age'].max().reset_index(name='age')
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id'],how='left')
  ############################################################inquiry#########################

  temp=data_inquiry.copy()
  temp['date_issued_som']=temp['date_issued']
  temp['date_issued_som']=pd.to_datetime(temp['date_issued_som'])
  temp['date_issued_som']=temp['date_issued_som'].apply(lambda x: x.replace(day=1))
  temp['month_since_inquiry']=(temp['date_issued_som']-temp['date_of_inquiry'])/np.timedelta64(1,"M")
  temp=temp[temp['month_since_inquiry']<=24]

  temp=temp.groupby(['source','deal_id','cust_id'])['purpose_of_inquiry'].count().reset_index(name='number_of_inquiries')
  temp=temp.groupby(['deal_id','cust_id'])['number_of_inquiries'].max().reset_index(name='number_of_inquiries')
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id'],how='left')

  #######################################################number of loans last year#################################################

  temp=data_loan_final.copy()
  temp['date_issued_som']=pd.to_datetime(temp['date_issued_som'])
  temp['date_disbursed_som_new']=pd.to_datetime(temp['date_disbursed_som_new'])
  temp['month_since_disbursal']=(temp['date_issued_som']-temp['date_disbursed_som_new'])/np.timedelta64(1,"M")
  temp=temp[temp['month_since_disbursal']<=12]
  temp=temp.groupby(['deal_id','cust_id'])['account_type'].count().reset_index(name='number_of_loans_disbursed_last_year')
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id'],how='left')
  ######################################################total disbursed amount###################################################
  temp=data_loan_final[~data_loan_final['acc_type_new'].isin(["corporatecreditcard","creditcard",
                                                        "fleetcard","kisancreditcard","loanagainstcard",
                                                        "loanoncreditcard","securedcreditcard","overdraft",
                                                        "primeministerjaandhanyojanaoverdraft","telcolandline",
                                                        "telcowireless","telcobroadband","autooverdraft"])]
  temp=temp.groupby(['deal_id','cust_id'])['disbursed_amount'].sum().reset_index(name='total_disbursed_amount')
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id'],how='left')

  #################################################total unsecured disbursed amount################################################################################3
  temp=data_loan_final[~data_loan_final['acc_type_new'].isin(["corporatecreditcard","creditcard",
                                                        "fleetcard","kisancreditcard","loanagainstcard",
                                                        "loanoncreditcard","securedcreditcard","overdraft",
                                                        "primeministerjaandhanyojanaoverdraft","telcolandline",
                                                        "telcowireless","telcobroadband","autooverdraft"])]
  temp=temp[temp['security_status']=="Un-secured"]
  temp=temp.groupby(['deal_id','cust_id'])['disbursed_amount'].sum().reset_index(name='total_unsecured_disbursed_amount')
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id'],how='left')

  ##############################################removing duplicates from dpd table#########################################################################
  temp=data_loan_final[['deal_id','cust_id','source','loan_id']]
  temp=temp.drop_duplicates()
  data_dpd_final=temp.merge(data_dpd_final,on=['deal_id','cust_id','source','loan_id'],how='left')

  #data_dpd_final['DPD']=data_dpd_final['DPD'].replace("XXX",0)
  #data_dpd_final['DPD']=data_dpd_final['DPD'].replace("STD",0)
  #data_dpd_final['DPD']=data_dpd_final['DPD'].replace("SMA",180)
  #data_dpd_final['DPD']=data_dpd_final['DPD'].replace("LSS",180)
  #data_dpd_final['DPD']=data_dpd_final['DPD'].replace("DBT",180)
  #data_dpd_final['DPD']=data_dpd_final['DPD'].replace("SUB",180)
  #data_dpd_final['DPD']=data_dpd_final['DPD'].astype(int)
  #########################################written off############################################################################
  temp=data_dpd_final.copy()
  temp['DPD']=temp['DPD'].replace("XXX",0)
  temp['DPD']=temp['DPD'].replace("STD",0)
  temp['DPD']=temp['DPD'].replace("SMA",180)
  temp['DPD']=temp['DPD'].replace("LSS",180)
  temp['DPD']=temp['DPD'].replace("DBT",180)
  temp['DPD']=temp['DPD'].replace("SUB",180)
  temp['DPD']= pd.to_numeric(temp['DPD'], errors="coerce")
  temp['180_dpd_flag']=temp['DPD'].apply(lambda x: 1 if x>=80 else 0)
  temp=temp.groupby(['deal_id','cust_id','source','loan_id'])['180_dpd_flag'].sum().reset_index(name='count_180_dpd_flag')
  temp['count_180_dpd_flag']=temp['count_180_dpd_flag'].apply(lambda x: 1 if x>0 else 0)

  temp1=data_loan_final.copy()
  temp1['written_off_flag']=np.where(temp1['written_off_status'].isin([0,1,2,3,4,5,6,7,8,9,10,11,99]),1,0)
  temp1=temp1.merge(temp,on=['deal_id','cust_id','source','loan_id'],how='left')
  temp1['final_written_off_status']=np.where(((temp1['written_off_flag']>0) | (temp1['count_180_dpd_flag']>0)),1,0)
  data_loan_final=data_loan_final.merge(temp1[['deal_id','cust_id','source','loan_id','final_written_off_status']],on=['deal_id','cust_id','source','loan_id'],how='left')

  temp1=temp1.groupby(['deal_id','cust_id'])['final_written_off_status'].sum().reset_index(name='number_of_written_off_accounts')

  cust_level=cust_level.merge(temp1,on=['deal_id','cust_id'],how='left')

  ###################################################suit filled ################################################################
  temp1=data_loan_final.copy()

  temp1['suit_filed_flag']=np.where(temp1['suit_filed_willful_default'].isna(),0,1)

  temp1=temp1.groupby(['deal_id','cust_id'])['suit_filed_flag'].sum().reset_index(name='number_of_suit_filed_accounts')

  cust_level=cust_level.merge(temp1,on=['deal_id','cust_id'],how='left')

  #################################################security status in dpd table#############################################################################
  temp1=data_dpd_final.copy()
  temp1['DPD']=temp1['DPD'].replace("XXX",0)
  temp1['DPD']=temp1['DPD'].replace("STD",0)
  temp1['DPD']=temp1['DPD'].replace("SMA",180)
  temp1['DPD']=temp1['DPD'].replace("LSS",180)
  temp1['DPD']=temp1['DPD'].replace("DBT",180)
  temp1['DPD']=temp1['DPD'].replace("SUB",180)
  temp1['DPD']= pd.to_numeric(temp1['DPD'], errors="coerce")
  temp1=temp1.merge(data_loan_final[['deal_id','cust_id','source','loan_id','security_status']],on=['deal_id','cust_id','source','loan_id'],how='left')
  temp1=temp1[temp1['DPD']>0]
  #########################################################Un-secured-month since dpd and 60 dpd count in 36 month#############################
  temp2=temp1[temp1['security_status']=="Un-secured"]
  temp3=temp2.groupby(['deal_id','cust_id'])['month_since_dpd'].min().reset_index(name="month_since_dpd_unsecured")
  cust_level=cust_level.merge(temp3,on=['deal_id','cust_id'],how='left')
  temp3=temp2[temp2['DPD']>=60]
  temp3=temp3[temp3['month_since_dpd']<=36]
  temp3=temp3.groupby(['deal_id','cust_id'])['DPD'].count().reset_index(name="60_dpd_count_36_month_unsecured")
  cust_level=cust_level.merge(temp3,on=['deal_id','cust_id'],how='left')
  ############################################################Secured-month since dpd and 30 dpd count in 36 month #####################################################################################
  temp2=temp1[temp1['security_status']=="secured"]
  temp3=temp2.groupby(['deal_id','cust_id'])['month_since_dpd'].min().reset_index(name="month_since_dpd_secured")
  cust_level=cust_level.merge(temp3,on=['deal_id','cust_id'],how='left')
  temp3=temp2[temp2['DPD']>=30]
  temp3=temp3[temp3['month_since_dpd']<=36]
  temp3=temp3.groupby(['deal_id','cust_id'])['DPD'].count().reset_index(name="30_dpd_count_36_month_secured")
  cust_level=cust_level.merge(temp3,on=['deal_id','cust_id'],how='left')
  #####################################month since 30 dpd, 30 dpd loans##########################################################################################
  temp2=temp1.copy()
  temp2=temp2[temp2['DPD']>=30]
  temp3=temp2.groupby(['deal_id','cust_id'])['month_since_dpd'].min().reset_index(name="month_since_30_dpd")
  cust_level=cust_level.merge(temp3,on=['deal_id','cust_id'],how='left')

  temp3=temp2.copy()
  temp3=temp3.groupby(['deal_id','cust_id','source','loan_id'])['DPD'].count().reset_index(name="count_30_dpd_loans")
  temp3['30_dpd_loan_counts']=temp3["count_30_dpd_loans"].apply(lambda x: 1 if x>0 else 0)
  temp3=temp3.groupby(['deal_id','cust_id'])['30_dpd_loan_counts'].sum().reset_index(name="30_dpd_loan_counts")
  cust_level=cust_level.merge(temp3,on=['deal_id','cust_id'],how='left')
  #############################################number of active accounts##############################################################
  temp=data_loan_final.copy()

  conditions=[(temp['active_status'].notna()),
  ((temp['active_status'].isna()) & (temp['date_closed_som_new'].isna()) & (temp['final_written_off_status']==0))]
  choices=[temp['active_status'],"Active"]
  temp['loan_status']=np.select(conditions,choices,default="Closed")
  print(temp[['loan_status','emi']])
  temp=temp[temp['loan_status']=="Active"]
  temp=temp.groupby(['deal_id','cust_id'])['account_type'].count().reset_index(name="number_of_active_accounts")
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id'],how='left')


  #############################################################number of address var past year ###################################
  temp=data_address.copy()
  temp['date_issued_som']=temp['date_issued']
  temp['date_issued_som']=pd.to_datetime(temp['date_issued_som'])
  temp['date_issued_som']=temp['date_issued_som'].apply(lambda x: x.replace(day=1))
  temp['address_var_date'] = pd.to_datetime(temp['address_var_date'])
  temp['month_since_address_var']=(temp['date_issued_som']-temp['address_var_date'])/np.timedelta64(1,"M")
  temp=temp[temp['month_since_address_var']<=12]

  temp=temp.groupby(['source','deal_id','cust_id'])['address_var_value'].count().reset_index(name='number_of_address_var_past_year')
  temp=temp.groupby(['deal_id','cust_id'])['number_of_address_var_past_year'].max().reset_index(name='number_of_address_var_past_year')
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id'],how='left')

  #######################################emi variables##################################################################################################

  data_loan_final['acc_type_new']=data_loan_final['account_type'].astype(str).apply(lambda x:re.sub('[\W_]+','',x).lower())


  #tenure_by_acc_type_loan_amt=pd.read_excel(r"D:\prudhvi\sources-a3-kit\emi\tenure_by_acc_type_loan_amt_revised.xlsx")

  tenure_by_acc_type_loan_amt = ten_acc_loan_amt

  #tenure_by_acc_type_loan_amt=pd.read_excel("Z:/Priya/InputFiles/tenure_by_acc_type_loan_amt.xlsx")
  #tenure_by_acc_type_for_missing=pd.read_excel(r"D:\prudhvi\sources-a3-kit\emi\tenure_by_acc_type_for_missing.xlsx")

  tenure_by_acc_type_for_missing = ten_acc_missing

  #loan_amt_bins_for_tenure=pd.read_excel("Z:/Priya/InputFiles/loan_amt_bins_for_tenure.xlsx")
  #loan_amt_bins_for_tenure=pd.read_excel(r"D:\prudhvi\sources-a3-kit\emi\loan_amt_bins_for_tenure_revised.xlsx")

  loan_amt_bins_for_tenure = loan_amt_bins

  #ROI_for_EMI_impute=pd.read_excel(r"D:\prudhvi\sources-a3-kit\emi\ROI_calculation.xlsx",sheet_name="Sheet_ROI")

  ROI_for_EMI_impute = roi_cal

  cibil_crif_dedup_import=data_loan_final.copy()
  crif_cibil_dedup=cibil_crif_dedup_import.copy()

  tenure_by_acc_type_loan_amt['acc_type_new']=tenure_by_acc_type_loan_amt['acc_type'].astype(str).apply(lambda x:re.sub('[\W_]+','',x).lower())
  tenure_by_acc_type_for_missing['acc_type_new']=tenure_by_acc_type_for_missing['acc_type'].astype(str).apply(lambda x:re.sub('[\W_]+','',x).lower())
  loan_amt_bins_for_tenure['acc_type_new']=loan_amt_bins_for_tenure['acc_type'].astype(str).apply(lambda x:re.sub('[\W_]+','',x).lower())

  ###############################################################################################################
  
  ROI_for_EMI_impute['last_payment_date_som_new']=pd.to_datetime(ROI_for_EMI_impute['last_payment_date_som_new'],format="%d/%m/%Y")
  ROI_for_EMI_impute['acc_type_new']=ROI_for_EMI_impute['acct_type'].astype(str).apply(lambda x: re.sub('[\W_]+','',x).lower())

  ### rows 2064
  ROI_for_EMI_impute_201604=ROI_for_EMI_impute[ROI_for_EMI_impute['last_payment_date_som_new']==pd.to_datetime("2016-04-01")]
  ROI_for_EMI_impute_201604=ROI_for_EMI_impute_201604.rename(columns={"ROI_1":"ROI_201604"})
  ### rows 43

  ROI_for_EMI_impute_latest=ROI_for_EMI_impute[ROI_for_EMI_impute['last_payment_date_som_new']==ROI_for_EMI_impute['last_payment_date_som_new'].max()]
  ROI_for_EMI_impute_latest=ROI_for_EMI_impute_latest.rename(columns={"ROI_1":"ROI_latest","last_payment_date_som_new":"Latest_ROI_date"})

  ######################################################################################################################
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

  crif_cibil_dedup_1['tenure'] = crif_cibil_dedup_1['tenure'].replace('',0)
  crif_cibil_dedup_1['tenure'] = pd.to_numeric(crif_cibil_dedup_1['tenure'], errors='coerce')

  conditions=[((crif_cibil_dedup_1['tenure'].isna()) | ((crif_cibil_dedup_1['tenure']<=0) & (crif_cibil_dedup_1['mode_tenure_acct_type'].isna()))),
   ((crif_cibil_dedup_1['mode_tenure_acct_type'].notna()) & ((crif_cibil_dedup_1['tenure']<=0) | (crif_cibil_dedup_1['tenure'].isna()))),
  crif_cibil_dedup_1['tenure']>0]
  choices=[crif_cibil_dedup_1['mode_tenure'],crif_cibil_dedup_1['mode_tenure_acct_type'],crif_cibil_dedup_1['tenure']]
  crif_cibil_dedup_1['tenure_impute']=np.select(conditions,choices,default=np.nan)


  #ROI_for_EMI_impute['last_payment_date_som_new']=pd.to_datetime(ROI_for_EMI_impute['last_payment_date_som_new'],format="%Y-%m-%d")
  #ROI_for_EMI_impute['acc_type_new']=ROI_for_EMI_impute['acct_type'].astype(str).apply(lambda x:re.sub('[\W_]+','',x).lower())
  #
  #
  #ROI_for_EMI_impute_201604=ROI_for_EMI_impute[ROI_for_EMI_impute['last_payment_date_som_new']==pd.to_datetime("2016-04-01")]
  #ROI_for_EMI_impute_201604=ROI_for_EMI_impute_201604.rename(columns={"ROI_1":"ROI_201604"})


  crif_cibil_dedup_1['acc_type_new']=np.where(((~crif_cibil_dedup_1['acc_type_new'].isin(["corporatecreditcard","creditcard","fleetcard","kisancreditcard","loanagainstcard","loanoncreditcard","securedcreditcard","overdraft", "primeministerjaandhanyojanaoverdraft","telcolandline","telcowireless","telcobroadband", "autooverdraft"])) & (~crif_cibil_dedup_1['acc_type_new'].isin(ROI_for_EMI_impute['acc_type_new'].unique().tolist()))), "personalloan",crif_cibil_dedup_1['acc_type_new'])

  crif_cibil_dedup_2=pd.merge(crif_cibil_dedup_1, ROI_for_EMI_impute.iloc[:,1:],
                            on=["acc_type_new", "last_payment_date_som_new"], how='left')

  crif_cibil_dedup_3=pd.merge(crif_cibil_dedup_2, ROI_for_EMI_impute_201604[["acc_type_new","ROI_201604"]],
                            on="acc_type_new", how='left')

  crif_cibil_dedup_3=pd.merge(crif_cibil_dedup_3, ROI_for_EMI_impute_latest[["acc_type_new","ROI_latest","Latest_ROI_date"]],
                            on="acc_type_new", how='left')

  ### select the required variables
  ### rows 382917
  crif_cibil_dedup_4=crif_cibil_dedup_3.copy()

  conditions=[(crif_cibil_dedup_4['last_payment_date_som_new']<pd.to_datetime("2016-04-01")), (crif_cibil_dedup_4['last_payment_date_som_new']>crif_cibil_dedup_4['Latest_ROI_date'])]

  choices=[crif_cibil_dedup_4['ROI_201604'], crif_cibil_dedup_4['ROI_latest']]
  crif_cibil_dedup_4['ROI']=np.select(conditions,choices,default=crif_cibil_dedup_4['ROI_1'])


  #crif_cibil_dedup_4=crif_cibil_dedup_3.copy()
  #conditions=[crif_cibil_dedup_4['last_payment_date_som_new']<pd.to_datetime("2016-04-01")]
  #choices=[crif_cibil_dedup_4["ROI_201604"]]
  #crif_cibil_dedup_4['ROI']=np.select(conditions,choices,default=crif_cibil_dedup_4['ROI_1'])
  #
  #crif_cibil_dedup_4['ROI']=np.select(conditions,choices,default=crif_cibil_dedup_4['ROI_1'])

  crif_cibil_dedup_4['r']=crif_cibil_dedup_4['ROI']/(12*100)
  crif_cibil_dedup_4['r']=crif_cibil_dedup_4['r'].astype(float)
  crif_cibil_dedup_4['tenure_impute']=crif_cibil_dedup_4['tenure_impute'].astype(float)
  crif_cibil_dedup_4['t']=(1+crif_cibil_dedup_4['r'])**(crif_cibil_dedup_4['tenure_impute'])
  crif_cibil_dedup_4['emi_new']=(crif_cibil_dedup_4['disbursed_amount']*crif_cibil_dedup_4['r']*crif_cibil_dedup_4['t'])/(crif_cibil_dedup_4['t']-1)
  crif_cibil_dedup_4['emi_deflate']=crif_cibil_dedup_4['emi_new']*0.9



  #crif_cibil_dedup_4['emi_impute']=np.where(((crif_cibil_dedup_4['emi']<=500) | ((crif_cibil_dedup_4['emi']>crif_cibil_dedup_4['disbursed_amount']) & (crif_cibil_dedup_4['disbursed_amount']>0))),crif_cibil_dedup_4['emi_deflate'],crif_cibil_dedup_4['emi'])
  #crif_cibil_dedup_4['emi_impute']=np.where(crif_cibil_dedup_4['emi_impute']>500,crif_cibil_dedup_4['emi_impute'],np.nan)

  crif_cibil_dedup_4['emi_impute']=np.where(((crif_cibil_dedup_4['emi']<=500) | ((crif_cibil_dedup_4['emi']>=crif_cibil_dedup_4['disbursed_amount']) & (crif_cibil_dedup_4['disbursed_amount']>0))),crif_cibil_dedup_4['emi_deflate'],crif_cibil_dedup_4['emi'])
  #crif_cibil_dedup_4['emi_impute']=np.where(crif_cibil_dedup_4['emi_amount']<=500,crif_cibil_dedup_4['emi_deflate'],crif_cibil_dedup_4['emi_amount'])

  crif_cibil_dedup_5=crif_cibil_dedup_4[~crif_cibil_dedup_4['ownership'].isin(['Guarantor','Supl Card Holder'])]

  data_max_date_issue=crif_cibil_dedup_5.groupby(['deal_id','cust_id'])['date_issued_som'].max().reset_index(name='max_date_of_issue_som')
  data_max_date_issue['max_date_of_issue_som']=pd.to_datetime(data_max_date_issue['max_date_of_issue_som'])


  crif_cibil_dedup_5=pd.merge(crif_cibil_dedup_5,data_max_date_issue,on=['deal_id','cust_id'],how='left')
  crif_cibil_dedup_5['date_prior_36_months']=crif_cibil_dedup_5['max_date_of_issue_som']-pd.DateOffset(months=35)
  crif_cibil_dedup_5['date_prior_36_months_som']=crif_cibil_dedup_5['date_prior_36_months'].apply(lambda x: x.replace(day=1))


  #crif_cibil_dedup_6=crif_cibil_dedup_5[((crif_cibil_dedup_5['date_closed_som_new'].isna()) | (crif_cibil_dedup_5['date_closed_som_new']>=crif_cibil_dedup_5['date_prior_37_months_som']))]

  ### rows

  ####### 2) date reported is in last 36 months #######
  crif_cibil_dedup_7=crif_cibil_dedup_5.copy()
  #crif_cibil_dedup_7=crif_cibil_dedup_6[crif_cibil_dedup_6['date_reported_som_new']>=crif_cibil_dedup_6['date_prior_37_months_som']]
  ### rows

  ########### define loan_status ############

  crif_cibil_dedup_7['active_status']=crif_cibil_dedup_7['active_status'].astype(str).apply(lambda x:x.lower())


  conditions=[(crif_cibil_dedup_7['active_status']=="active"),
  ((crif_cibil_dedup_7['date_closed_som_new'].isna()) & (crif_cibil_dedup_7['final_written_off_status']==0))]
  choices=["active","active"]
  crif_cibil_dedup_7['loan_status_active']=np.select(conditions,choices,default="NA")

  conditions=[(crif_cibil_dedup_7['active_status']=="closed"),
  (crif_cibil_dedup_7['date_closed_som_new'].notna())]
  choices=["closed","closed"]
  crif_cibil_dedup_7['loan_status_closed']=np.select(conditions,choices,default="NA")

  conditions=[(crif_cibil_dedup_7['loan_status_active']!="NA"),
  (crif_cibil_dedup_7['loan_status_closed']!="NA")]
  choices=[crif_cibil_dedup_7['loan_status_active'],crif_cibil_dedup_7['loan_status_closed']]
  crif_cibil_dedup_7['loan_status']=np.select(conditions,choices,default="NA")

  ### rows 293756

  ####### Removing cc and od #######

  crif_cibil_dedup_7_cc_od=crif_cibil_dedup_7[
                                   ~crif_cibil_dedup_7['acc_type_orig'].isin(["corporatecreditcard","creditcard",
                                                        "fleetcard","kisancreditcard","loanagainstcard",
                                                        "loanoncreditcard","securedcreditcard","overdraft",
                                                        "primeministerjaandhanyojanaoverdraft","telcolandline",
                                                        "telcowireless","telcobroadband","autooverdraft"])]
  ### rows 261606

  ####### 36 months data #######

  crif_cibil_dedup_36months=crif_cibil_dedup_7[["deal_id","cust_id",'source','loan_id','account_type',"current_balance","disbursed_amount",
                                                         "emi_impute","max_date_of_issue_som",
                                                         "date_prior_36_months_som","date_reported_som_new",
                                                         'date_disbursed_som_new','date_closed_som_new',"acc_type_orig"]]
  ### rows 261606

  crif_cibil_dedup_36months['loan_id_new']=crif_cibil_dedup_36months.groupby(['deal_id','cust_id']).cumcount()+1


  # crif_cibil_dedup_36months=pysqldf('select * from crif_cibil_dedup_36months order by deal_id,cust_id')
  crif_cibil_dedup_36months = crif_cibil_dedup_36months.sort_values(['deal_id','cust_id'], ascending=[True,True])
  ### rows 261606
  crif_cibil_dedup_36months['serial_no']=list(range(1,len(crif_cibil_dedup_36months)+1))
  ### rows 261606
  global crif_cibil_dedup_36months_1
  crif_cibil_dedup_36months_1=pd.concat([crif_cibil_dedup_36months]*36)
  ###  rows 9941028

  crif_cibil_dedup_36months_1['month_no']=  crif_cibil_dedup_36months_1.groupby(['deal_id','cust_id','serial_no']).cumcount()
  ### group by deal_id and serial_no; assign row numbers (like you did for index_id) and subtarct 1 from it
  ###  rows 9941028

  #summary(as.factor(crif_cibil_dedup_37months_1$month_no))
  crif_cibil_dedup_36months_1['max_date_of_issue_som']=pd.to_datetime(crif_cibil_dedup_36months_1['max_date_of_issue_som'])
  crif_cibil_dedup_36months_1['date_som']=crif_cibil_dedup_36months_1.apply(lambda x: x['max_date_of_issue_som']-pd.DateOffset(months=x['month_no']),axis=1)

  ### rows 9941028

  #nrow(subset(crif_cibil_dedup_37months_1, month_no==37 & date_som==date_prior_37_months_som))
  #nrow(subset(crif_cibil_dedup_37months_1, month_no==0 & date_som==max_date_of_issue_som))
  ### both above should be same i.e. 261606

  #crif_cibil_dedup_37months_2=pysqldf('select *, case when date_disbursed_som_new<=date_som and date_reported_som_new>=date_som and (date_closed_som_new is null or date_closed_som_new>=date_som) then 1 else null end as ind_valid_account, case when date_disbursed_som_new<=date_som and date_reported_som_new>=date_som and (date_closed_som_new is null or date_closed_som_new>=date_som) then emi_impute else null end as valid_emi, case when date_disbursed_som_new<=date_som and date_reported_som_new>=date_som and (date_closed_som_new is null or date_closed_som_new>=date_som) then disbursed_amount else null end as valid_LN_amt from crif_cibil_dedup_37months_1 order by deal_id, cust_id, date_som')
  ### rows 9941028
  global crif_cibil_dedup_36months_2
  crif_cibil_dedup_36months_2=pysqldf('select *, case when date_disbursed_som_new<=date_som and max_date_of_issue_som>=date_som and (date_closed_som_new is null or date_closed_som_new>=date_som) then 1 else null end as ind_valid_account, case when date_disbursed_som_new<=date_som and max_date_of_issue_som>=date_som and (date_closed_som_new is null or date_closed_som_new>=date_som) and acc_type_orig not in ("corporatecreditcard", "creditcard","fleetcard","kisancreditcard","loanagainstcard","loanoncreditcard","securedcreditcard","overdraft", "primeministerjaandhanyojanaoverdraft","telcolandline","telcowireless","telcobroadband","autooverdraft") then emi_impute else null end as valid_emi, case when date_disbursed_som_new<=date_som and max_date_of_issue_som>=date_som and (date_closed_som_new is null or date_closed_som_new>=date_som) then account_type else null end as valid_acc_type from crif_cibil_dedup_36months_1 order by deal_id, cust_id, date_som')

  

  global crif_cibil_dedup_36months_3

  crif_cibil_dedup_36months_3=pysqldf('select deal_id, cust_id, date_som, month_no, sum(ind_valid_account) as cnt_valid_accounts, sum(valid_emi) as sum_emi from crif_cibil_dedup_36months_2 group by deal_id, cust_id, date_som, month_no order by deal_id, cust_id, date_som, month_no')
  ### rows 1455362
  #nrow(crif_cibil_dedup_37months_3)
  #nrow(sqldf('select distinct deal_id from crif_cibil_dedup_7_cc_od'))*38
  ### both above should be same i.e. 1455362

  ######################### deal_id_level monthly data ##################################

  crif_cibil_deal_level_monthly=pysqldf('select deal_id,cust_id,  max(case when month_no=0 then sum_emi else null end) as M0_emi, max(case when month_no=1 then sum_emi else null end) as M1_emi, max(case when month_no=2 then sum_emi else null end) as M2_emi, max(case when month_no=3 then sum_emi else null end) as M3_emi, max(case when month_no=4 then sum_emi else null end) as M4_emi, max(case when month_no=5 then sum_emi else null end) as M5_emi, max(case when month_no=6 then sum_emi else null end) as M6_emi, max(case when month_no=7 then sum_emi else null end) as M7_emi, max(case when month_no=8 then sum_emi else null end) as M8_emi, max(case when month_no=9 then sum_emi else null end) as M9_emi, max(case when month_no=10 then sum_emi else null end) as M10_emi, max(case when month_no=11 then sum_emi else null end) as M11_emi, max(case when month_no=12 then sum_emi else null end) as M12_emi, max(case when month_no=13 then sum_emi else null end) as M13_emi, max(case when month_no=14 then sum_emi else null end) as M14_emi, max(case when month_no=15 then sum_emi else null end) as M15_emi, max(case when month_no=16 then sum_emi else null end) as M16_emi, max(case when month_no=17 then sum_emi else null end) as M17_emi, max(case when month_no=18 then sum_emi else null end) as M18_emi, max(case when month_no=19 then sum_emi else null end) as M19_emi, max(case when month_no=20 then sum_emi else null end) as M20_emi, max(case when month_no=21 then sum_emi else null end) as M21_emi, max(case when month_no=22 then sum_emi else null end) as M22_emi, max(case when month_no=23 then sum_emi else null end) as M23_emi, max(case when month_no=24 then sum_emi else null end) as M24_emi, max(case when month_no=25 then sum_emi else null end) as M25_emi, max(case when month_no=26 then sum_emi else null end) as M26_emi,  max(case when month_no=27 then sum_emi else null end) as M27_emi, max(case when month_no=28 then sum_emi else null end) as M28_emi, max(case when month_no=29 then sum_emi else null end) as M29_emi, max(case when month_no=30 then sum_emi else null end) as M30_emi, max(case when month_no=31 then sum_emi else null end) as M31_emi, max(case when month_no=32 then sum_emi else null end) as M32_emi,  max(case when month_no=33 then sum_emi else null end) as M33_emi, max(case when month_no=34 then sum_emi else null end) as M34_emi,  max(case when month_no=35 then sum_emi else null end) as M35_emi from crif_cibil_dedup_36months_3 group by deal_id,cust_id')
  ### rows 38299

  ######################## loan information at deal_id level #####################
  crif_cibil_dedup_7_cc_od['current_balance']= crif_cibil_dedup_7_cc_od['current_balance'].astype(str).replace("None",np.nan)
  crif_cibil_dedup_7_cc_od['current_balance']= crif_cibil_dedup_7_cc_od['current_balance'].astype(str).apply(lambda x: float(x.replace(',', '')))
  crif_cibil_dedup_7_cc_od['current_balance']= crif_cibil_dedup_7_cc_od['current_balance'].astype(float)



  first=crif_cibil_dedup_7[crif_cibil_dedup_7['loan_status']=='active'].groupby(['deal_id','cust_id']).size().reset_index(name='cnt_active_loans')
  second=crif_cibil_dedup_7.groupby(['deal_id','cust_id'])['max_date_of_issue_som'].max().reset_index(name='Date_of_issue')

  third=crif_cibil_dedup_7[((crif_cibil_dedup_7['acc_type_orig'].isin(["corporatecreditcard","creditcard","fleetcard", "kisancreditcard","loanagainstcard","loanoncreditcard","securedcreditcard","overdraft", "primeministerjaandhanyojanaoverdraft","telcolandline","telcowireless","telcobroadband", "autooverdraft"])) & (crif_cibil_dedup_7['loan_status']=='active'))].groupby(['deal_id','cust_id'])['credit_limit'].sum().reset_index(name='sum_credit_limit_of_active_cc_od')
  fourth=crif_cibil_dedup_7[((crif_cibil_dedup_7['acc_type_orig'].isin(["corporatecreditcard","creditcard","fleetcard", "kisancreditcard","loanagainstcard","loanoncreditcard","securedcreditcard","overdraft", "primeministerjaandhanyojanaoverdraft","telcolandline","telcowireless","telcobroadband", "autooverdraft"])) & (crif_cibil_dedup_7['loan_status']=='active'))].groupby(['deal_id','cust_id'])['current_balance'].sum().reset_index(name='sum_current_balance_of_active_cc_od')

  try:
      crif_cibil_deal_level_loans_1=first.merge(second,on=['deal_id','cust_id'],how='left').merge(third,on=['deal_id','cust_id'],how='left').merge(fourth,on=['deal_id','cust_id'],how='left')
  except:
      third=pd.DataFrame(columns=['deal_id','cust_id','sum_credit_limit_of_active_cc_od'])
      fourth=pd.DataFrame(columns=['deal_id','cust_id','sum_current_balance_of_active_cc_od'])
      crif_cibil_deal_level_loans_1=first.merge(second,on=['deal_id','cust_id'],how='left').merge(third,on=['deal_id','cust_id'],how='left').merge(fourth,on=['deal_id','cust_id'],how='left')


  crif_cibil_deal_level_loans_1['Date_of_issue']=pd.to_datetime(crif_cibil_deal_level_loans_1['Date_of_issue'])


  first=crif_cibil_dedup_7_cc_od[crif_cibil_dedup_7_cc_od['loan_status']=='active'].groupby(['deal_id','cust_id'])['current_balance'].sum().reset_index(name='sum_current_balance_of_active_loans')
  second=crif_cibil_dedup_7_cc_od[crif_cibil_dedup_7_cc_od['loan_status']=='active'].groupby(['deal_id','cust_id'])['disbursed_amount'].sum().reset_index(name='sum_active_disbursed_amount')
  third=crif_cibil_dedup_7_cc_od[crif_cibil_dedup_7_cc_od['loan_status']=='closed'].groupby(['deal_id','cust_id']).size().reset_index(name='cnt_closed_loans')
  temp=crif_cibil_dedup_7_cc_od.copy()
  temp['disbursed_amount']=temp['disbursed_amount'].fillna(0)
  fourth=temp.groupby(['deal_id','cust_id'])['disbursed_amount'].min().reset_index(name='min_disbursed_amount')
  fifth=temp.groupby(['deal_id','cust_id'])['disbursed_amount'].max().reset_index(name='max_disbursed_amount')


  crif_cibil_deal_level_loans_2=first.merge(second,on=['deal_id','cust_id'],how='left').merge(third,on=['deal_id','cust_id'],how='left').merge(fourth,on=['deal_id','cust_id'],how='left').merge(fifth,on=['deal_id','cust_id'],how='left')

  #############################################################################3 largest closed loan amounts #########################################
  global loan_sort
  loan_sort=crif_cibil_dedup_7_cc_od[crif_cibil_dedup_7_cc_od['loan_status']=='closed']
  loan_sort=loan_sort.sort_values(['disbursed_amount'],ascending=False).groupby('deal_id').head(3)
  loan_sort=loan_sort.reset_index()
  loan_sort=loan_sort[['deal_id','cust_id','disbursed_amount']]
  loan_sort['loan_sort_id']=  loan_sort.groupby(['deal_id','cust_id']).cumcount()+1
  loan_sort_final=pysqldf('select deal_id, cust_id, max(case when loan_sort_id=1 then disbursed_amount else null end) as closed_amount1, max(case when loan_sort_id=2 then disbursed_amount else null end) as closed_amount2, max(case when loan_sort_id=3 then disbursed_amount else null end) as closed_amount3 from loan_sort group by deal_id,cust_id')
  
  crif_cibil_deal_level_loans_2=crif_cibil_deal_level_loans_2.merge(loan_sort_final,on=['deal_id','cust_id'],how='left')


  crif_cibil_deal_level_loans=pd.merge(crif_cibil_deal_level_loans_1,crif_cibil_deal_level_loans_2,on=['deal_id','cust_id'],how='left')


  #################################################################################################################################

  ### rows 38299

  ####################### overdue amount ################
  crif_cibil_deal_level_overdue=crif_cibil_dedup_5.groupby(['deal_id','cust_id'])['amount_overdue'].sum().reset_index(name='sum_overdue_ever')
  #second=crif_cibil_dedup_7.groupby('deal_id')['max_date_of_issue_som'].max().reset_index(name='Date_of_issue')
  #crif_cibil_deal_level_overdue=first.merge(second,on='deal_id',how='left')
  #crif_cibil_deal_level_overdue=pysqldf('select deal_id, sum(amount_overdue) as sum_overdue_overall_37_months, max(max_date_of_issue_som) as Date_of_issue from crif_cibil_dedup_7 group by deal_id')
  #crif_cibil_deal_level_overdue['Date_of_issue']=pd.to_datetime(crif_cibil_deal_level_overdue['Date_of_issue'])
  ### rows 39319

  ######## final #######

  crif_cibil_deal_level_1=pd.merge(crif_cibil_deal_level_loans,crif_cibil_deal_level_overdue,
                                 on=['deal_id','cust_id'], how='left')
  ### rows 39319

  crif_cibil_deal_level_2=pd.merge(crif_cibil_deal_level_1, crif_cibil_deal_level_monthly,
                                 on=['deal_id','cust_id'], how='left')
  #crif_cibil_deal_level_loans=pysqldf('select deal_id, count(*) as cnt_total_loans, count(case when loan_status="active" then deal_id else null end) as cnt_active_loans, sum(case when loan_status="active" then disbursed_amount else null end) as sum_active_disbursed_amount, sum(case when loan_status="active" then current_balance else null end) as sum_current_balance_of_active_loans from crif_cibil_dedup_7_cc_od group by deal_id')


  ########################################Bureau Booster decision making##########################################################################################################

  final_data=cust_level.copy()



  ###############################################approval
  final_data['total_disbursed_amount']=final_data['total_disbursed_amount'].fillna(0)
  final_data['total_unsecured_disbursed_amount']=final_data['total_unsecured_disbursed_amount'].fillna(0)
  final_data['month_since_dpd_secured']=final_data['month_since_dpd_secured'].fillna(99)
  final_data['month_since_dpd_unsecured']=final_data['month_since_dpd_unsecured'].fillna(99)
  final_data['month_since_30_dpd']=final_data['month_since_30_dpd'].fillna(99)
  final_data['score']=final_data['score'].fillna(0)
  final_data['number_of_loans_disbursed_last_year']=final_data['number_of_loans_disbursed_last_year'].fillna(0)
  final_data['month_since_dpd_secured']=final_data['month_since_dpd_secured'].astype(int)
  final_data['month_since_dpd_unsecured']=final_data['month_since_dpd_unsecured'].astype(int)
  final_data['month_since_30_dpd']=final_data['month_since_30_dpd'].astype(int)

  ################################################rejection
  final_data['30_dpd_loan_counts']=final_data['30_dpd_loan_counts'].fillna(0)
  final_data['number_of_active_accounts']=final_data['number_of_active_accounts'].fillna(0)
  final_data['number_of_address_var_past_year']=final_data['number_of_address_var_past_year'].fillna(99)



  #############################################approval
  final_data['score>=768']=[1 if x>=768 else 0 for x in final_data['score']]
  final_data['age=40 to 50']=[1 if x>=40 and x<=50 else 0 for x in final_data['age']]
  final_data['number_of_inquiries_24_month=0']=[1 if x<=0.5 else 0 for x in final_data['number_of_inquiries']]
  final_data['total_unsecured_disbursed_amount=150000 to 500000']=[1 if x>=150000 and x<=500000 else 0 for x in final_data['total_unsecured_disbursed_amount']]
  final_data['number_of_loans_disbursed_last_year=0']=[1 if x<=0.5 else 0 for x in final_data['number_of_loans_disbursed_last_year']]
  final_data['total_disbursed_amount=500000 to 1000000']=[1 if x>=500000 and x<=1000000 else 0 for x in final_data['total_disbursed_amount']]

  #############################################################rejection
  final_data['score<=650']=[1 if x<=650 else 0 for x in final_data['score']]
  final_data['number_of_loans_disbursed_last_year>=4']=[1 if x>=4 else 0 for x in final_data['number_of_loans_disbursed_last_year']]
  final_data['number_of_inquiries_24_month>=3']=[1 if x>=3 else 0 for x in final_data['number_of_inquiries']]
  final_data['month_since_30_dpd<=4']=[1 if x<=4 else 0 for x in final_data['month_since_30_dpd']]
  final_data['30_dpd_loan_counts>=2']=[1 if x>=2 else 0 for x in final_data['30_dpd_loan_counts']]
  final_data['number_of_active_accounts>=5']=[1 if x>=5 else 0 for x in final_data['number_of_active_accounts']]
  final_data['number_of_address_var_past_year>=7']=[1 if x>=7 else 0 for x in final_data['number_of_address_var_past_year']]


  ##########################################approval_score

  final_data['approval_score']=(0.1657*(final_data['number_of_inquiries_24_month=0'])
  +0.1308*(final_data['age=40 to 50'])
  +0.1912*(final_data['score>=768'])
  +0.1657*(final_data['total_unsecured_disbursed_amount=150000 to 500000'])
  +0.1554*(final_data['number_of_loans_disbursed_last_year=0'])
  +0.1912*(final_data['total_disbursed_amount=500000 to 1000000']))
  ########################################################rejection_score
  final_data['rejection_score']=(0.161137*(final_data['score<=650'])
  +0.175355*(final_data['number_of_loans_disbursed_last_year>=4'])
  +0.123223*(final_data['number_of_inquiries_24_month>=3'])
  +0.156398*(final_data['month_since_30_dpd<=4'])
  +0.151659*(final_data['30_dpd_loan_counts>=2'])
  +0.118483*(final_data['number_of_active_accounts>=5'])
  +0.113744*(final_data['number_of_address_var_past_year>=7']))





  ##########################################################################filling missing value
  final_data['30_dpd_count_36_month_secured']=final_data['30_dpd_count_36_month_secured'].fillna(0)
  final_data['60_dpd_count_36_month_unsecured']=final_data['60_dpd_count_36_month_unsecured'].fillna(0)


  #####################################min_scoring_flag
  conditions=[((final_data['score']>=632)  & (final_data['month_since_dpd_unsecured']>7) &
  (final_data['month_since_dpd_secured']>12) & (final_data['30_dpd_count_36_month_secured']==0) & 
  (final_data['60_dpd_count_36_month_unsecured']==0) & (final_data['number_of_written_off_accounts']==0))]
  choicelist=[1]
  final_data['min_scoring_flag']=np.select(conditions,choicelist,default=0)

  #######################################################################approval_flag
  conditions=[(final_data['approval_score']>=0.30)]
  choicelist=[1]
  final_data['approval_flag']=np.select(conditions,choicelist,default=0)


  #####################################################rejection_flag
  conditions=[(final_data['rejection_score']>=0.40)]
  choicelist=[1]
  final_data['rejection_flag']=np.select(conditions,choicelist,default=0)

  #########################################################final_decision

  conditions=[((final_data['approval_score']>=0.60) & (final_data['min_scoring_flag']==1)),
              ((final_data['approval_score']>=0.30) & (final_data['min_scoring_flag']==1) & (final_data['approval_score']<0.60)),
              ((final_data['rejection_flag']==1) & (final_data['min_scoring_flag']==0))]
  choicelist=["Green channel","Fast-track","Auto-rejection"]
  final_data['decision_flag']=np.select(conditions,choicelist,default="None")

  ######################combine bureau booster and emi #####################################
  final_data=final_data.merge(crif_cibil_deal_level_2,on=['deal_id','cust_id'],how='left')

  ######################################################################################################
  ########################################################################################################
  ########################################################################################################





  ########################################addition_of_code_new_grid_variables#############################################################





  df1=data_dpd_final.copy()


  df1['asset_classification']=np.where(df1['DPD'].isin(["SUB","STD","LSS","DBT","SMA"]),df1['DPD'],"XXX")
  df1['DPD']=np.where(df1['DPD'].isin(["SUB","STD","LSS","DBT","SMA"]),"XXX",df1['DPD'])

  df1['asset_classification']=np.where(df1['asset_classification'].isin(["SUB","STD","LOS","LSS","DBT","SMA"]),df1['asset_classification'],"NR")
  df1['DPD']=np.where(df1['DPD'].str.isdigit(),df1['DPD'],"NR")
  df1['DPD']=df1['DPD'].fillna("NR")

  #df1['date_issue'] = pd.to_datetime(df1['date_issue'])
  #df1['Reporting Month']=pd.to_datetime(df1['Reporting Month'])

  ####################################################################################################################
  temp=df1.copy()


  ############################################################merging############################################################################
  crif_cibil_dedup_36months_2['date_som']=pd.to_datetime(crif_cibil_dedup_36months_2['date_som'])
  temp=crif_cibil_dedup_36months_2.merge(temp,left_on=['deal_id','cust_id','source','loan_id','date_som'],right_on=['deal_id','cust_id','source','loan_id','DPD_month'],how='left')
  temp['DPD']=temp['DPD'].fillna("NR")
  temp['asset_classification']=temp['asset_classification'].fillna("NR")




  temp1=temp.copy()
  temp1['valid_emi']=temp1['valid_emi'].astype(str).replace("None",np.nan)
  temp1['valid_emi']=temp1['valid_emi'].astype(float)


  temp4=temp1.groupby(['deal_id','cust_id','date_som', 'month_no'])['valid_emi'].sum().reset_index(name="sum_emi")

  temp1=temp1[temp1['ind_valid_account']==1]
  # temp1.to_csv(r"D:\prudhvi\temp1_2.csv")
  dict1={'jlgindividual': 'JLI',
   'individual': 'IND',
   'jlggroup': 'JLG',
   'shgindividual': 'SHI',
   'shggroup': 'SHG',
   'consumerloan': 'CNL',
   'personalloan': 'PRL',
   'goldloan': 'GDL',
   'creditcard': 'CRC',
   'housingloan': 'HSL',
   'twowheelerloan': 'TWL',
   'autoloanpersonal': 'ALP',
   'commercialvehicleloan': 'CVL',
   'other': 'OTH',
   'businessloangeneral': 'BLG',
   'propertyloan': 'PPL',
   'businessloanprioritysectoragriculture': 'BLPSA',
   'overdraft': 'OVD',
   'kisancreditcard': 'KCC',
   'usedcarloan': 'UCL',
   'businessloanprioritysectorsmallbusiness': 'BLPSSB',
   'tractorloan': 'TRL',
   'loanagainstbankdeposits': 'LABD',
   'mudraloansshishukishortarun': 'MLSKT',
   'businessloanunsecured': 'BLU',
   'businessloanprioritysectorothers': 'BLPSO',
   'educationloan': 'EDL',
   'constructionequipmentloan': 'CEL',
   'microfinancebusinessloan': 'MBL',
   'loanagainstsharessecurities': 'LASS',
   'businessloansecured': 'BLS',
   'microfinanceothers': 'MFO',
   'loantoprofessional': 'LTP',
   'microfinancehousingloan': 'MHL',
   'pradhanmantriawasyojanaclss': 'PMAYC',
   'businessnonfundedcreditfacilityprioritysectorsmallbusiness': 'BNFCFPSSB',
   'microfinancepersonalloan': 'MPL',
   'securedcreditcard': 'SCC',
   'businessnonfundedcreditfacilitygeneral': 'BNFCFG',
   'primeministerjaandhanyojanaoverdraft': 'PMJDYO',
   'businessloanagainstbankdeposits': 'BLABD',
   'nonfundedcreditfacility': 'NFCF',
   'corporatecreditcard': 'CCC',
   'leasing': 'LSN',
   'staffloan': 'STL',
   'loanoncreditcard': 'LCC',
   'commercialequipmentloan': 'CML',
   'fleetcard': 'FLC',
   'businessnonfundedcreditfacilityprioritysectoragriculture': 'BNFCFPSA',
   'businessnonfundedcreditfacilityprioritysectorothers': 'BNFCFPSO',
   'telcolandline': 'TCL',
   'loanagainstcard': 'LAC',
   'autooverdraft': 'AOD',
   'telcowireless': 'TWS',
   'telcobroadband': 'TBD',
   'pradhanmantriawasyojanacreditlinksubsidyschememayclss': 'PMAYC'}


  temp1['acc_type_to_use']=temp1['account_type'].astype(str).apply(lambda x: re.sub('[\W_]+','',x).lower())
  temp1['acc_type_new1']=temp1['acc_type_to_use'].map(dict1).fillna("NEW")
  # temp1.to_csv("D:\\prudhvi\\temp1.csv")
  #acct_to_sql=temp1[temp1['acc_type_new1']=="NEW"]
  #acct_to_sql=acct_to_sql[['deal_id','acc_type_to_use']]
  #from sqlalchemy import create_engine
  #engine=create_engine("mysql+pymysql://A_analytics:PASSpass^%$#@12345@192.168.10.124/booster")
  #acct_to_sql.to_sql(name='data_new',con=engine,if_exists="replace",index=False)

  temp2=temp1.groupby(['deal_id','cust_id','date_som', 'month_no'])['acc_type_new1'].apply(lambda x: "|".join(x)).reset_index(name="account_type")
  temp3=temp1.groupby(['deal_id','cust_id','date_som', 'month_no'])['ind_valid_account'].sum().reset_index(name="cnt_active_accounts")





  temp5=temp1.groupby(['deal_id','cust_id','date_som', 'month_no'])['DPD'].apply(lambda x: "|".join(x)).reset_index(name="DPD")
  temp6=temp1.groupby(['deal_id','cust_id','date_som', 'month_no'])['asset_classification'].apply(lambda x: "|".join(x)).reset_index(name="asset_classification")
  global temp7
  temp7=temp4.merge(temp3,on=['deal_id','cust_id','date_som', 'month_no'],how='left').merge(temp2,on=['deal_id','cust_id','date_som', 'month_no'],how='left').merge(temp5,on=['deal_id','cust_id','date_som', 'month_no'],how='left').merge(temp6,on=['deal_id','cust_id','date_som', 'month_no'],how='left')

  # temp7.to_csv("D:\\prudhvi\\temp7.csv")

  #######################################################################################################################################33
  ###################### CODE ADDED ################################

  ######### DATA FOR EMI GRID ##################

  data_for_emi_grid=pysqldf('select deal_id,cust_id, date_som, sum_emi, cnt_active_accounts, account_type,DPD,asset_classification from temp7 order by deal_id,cust_id, month_no')
  data_for_emi_grid['date_som_temp']=data_for_emi_grid['date_som'].apply(lambda x: x[0:10])
  data_for_emi_grid['deal_id_emi_month']=data_for_emi_grid['deal_id'].astype(str)+"+"+data_for_emi_grid['cust_id'].astype(str)+"+"+data_for_emi_grid['date_som_temp'].astype(str)

  #### paste0 is used so that there are no extra spaces while concatenating deal_id and date_som
  #### output of deal_id_emi_month looks like 295249+2020-02-01
  #### pls check its the same output in python as well

  #### renaming date_som to emi_month
  data_for_emi_grid=data_for_emi_grid.rename(columns={'date_som':'emi_month'})
  print(data_for_emi_grid[['sum_emi','emi_month']])
  #### reordering variables as required
  data_for_emi_grid=data_for_emi_grid[["deal_id",'cust_id',"emi_month","deal_id_emi_month","sum_emi",'cnt_active_accounts','account_type',"DPD","asset_classification"]]
  data_for_emi_grid.loc[data_for_emi_grid["sum_emi"].notnull(),"sum_emi"]=data_for_emi_grid.loc[data_for_emi_grid["sum_emi"].notnull(),"sum_emi"].apply(lambda x:round(x))
  data_for_emi_grid["sum_emi"]=data_for_emi_grid["sum_emi"].fillna("NA")
  data_for_emi_grid['emi_month'] = pd.to_datetime(data_for_emi_grid['emi_month'], format = "%Y-%m-%d").apply(lambda x : x.date())




  return data_for_emi_grid,temp1



















