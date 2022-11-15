import pandas as pd
import re
import numpy as np
import plotly.express as px
import plotly
import datetime as dt
import plotly.figure_factory as ff

def bureau_cust_kpi(bureau_ref_dtl,bureau_score_segment,bureau_account_segment_tl,bureau_enquiry_segment_iq,bureau_address_segment,customer_id,deal_id,bureau_automated):

  #######################################basic table#########################################################

  try:
    data_basic=bureau_ref_dtl

    data_basic=data_basic.rename(columns={'BUREAU_ID':'report_id','BUREAU_DATE':'date_issued',
                      'DATE_OF_BIRTH':'DOB','NAME':'name','PAN_NO':'PAN','DEAL_ID':'deal_id',
                      'CUSTOMER_ID':'cust_id'})

    data_basic=data_basic[['deal_id','cust_id','source','report_id','date_issued','DOB','name','PAN']]
    data_basic['date_issued'] = pd.to_datetime(data_basic['date_issued'], format="%Y-%m-%d")
  except:
    return

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
  data_loan_raw['account_type']=data_loan_raw['account_type']
  data_loan_raw['security_status']=np.where(data_loan_raw['account_type'].isin(['5','6','8','9','10','12',
         '14','16','18',19,20,35,36,37,38,39,40,41,43,44,45,51,52,
         53,54,55,56,57,58,61,00]),"Un-secured","secured")

  data_loan_raw['ownership']=data_loan_raw['ownership'].astype(str).map({"1":"Individual",
         "2":"Supl Card Holder","3":"Guarantor","4":"Joint"})

  data_loan_raw['account_type']=data_loan_raw['account_type'].astype(str).map({"1": "Auto Loan (Personal)",
  "2":"Housing Loan",
  "3":"Property Loan",
  "4":"Loan Against Shares/Securities",
  "5":"Personal Loan",
  "6":"Consumer Loan",
  "7":"Gold Loan",
  "8":"Education Loan",
  "9":"Loan to Professional",
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



  # chart=data_loan.sort_values('disbursed_amount')

  # start_dates=list(chart['start_date'])  
  # end_dates=list(chart['end_date'])
  # amt=list(chart['disbursed_amount'])
  # types=list(chart['account_type'])

  # df_chart=pd.DataFrame()
  # df_chart['Start']=start_dates
  # df_chart['Task']=amt
  
  # df_chart['Finish']=end_dates
  # df_chart['Resource']=types

  # fig = ff.create_gantt(df_chart,  index_col='Resource', showgrid_x=True, showgrid_y=False, title='Loan Timeline', show_colorbar=True, bar_width=0.25,height=900)
  # fig.layout.xaxis.tickformat = '%b-%y'

  # plotly.offline.plot(fig,filename=r"templates/test.html")

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
                  'DATE_OF_ENQUIRY':'date_of_inquiry','ENQUIRY_PURPOSE':'purpose_of_inquiry','CUSTOMER_ID':'cust_id','ENQUIRY_AMOUNT':'amount_of_inquiry' })

  data_inquiry=data_inquiry[['source','report_id','cust_id','inquiry_id','date_of_inquiry','purpose_of_inquiry','amount_of_inquiry']]
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

  #dedup_dataset2a_remain=pysqldf('select * from dedup_dataset2 where id not in (select distinct id from dedup_dataset2a)')
  dedup_dataset2a_remain = dedup_dataset2[~dedup_dataset2['id'].isin(dedup_dataset2a['id'].unique().tolist())]

  #cnt_source_2a=pysqldf('select id, count(source) as cnt_source_2 from dedup_dataset2a group by id')
  cnt_source_2a = dedup_dataset2a.groupby('id')['source'].count().reset_index().rename(columns={'source':'cnt_source_2'})
  #dedup_dataset2a=pysqldf('select a.*, b.cnt_source_2 from dedup_dataset2a a left join cnt_source_2a b on a.id=b.id')
  dedup_dataset2a = dedup_dataset2a.merge(cnt_source_2a[['id', 'cnt_source_2']], on='id', how='left')
  dedup_dataset3a=dedup_dataset2a[dedup_dataset2a['cnt_source_2']==1]
  dedup_dataset3b=dedup_dataset2a[dedup_dataset2a['cnt_source_2']>1]
  ################################################date_reported_max
  temp=dedup_dataset3b.groupby('id')['date_reported'].max().reset_index(name="max_date_reported")
  dedup_dataset3b=dedup_dataset3b.merge(temp,on='id',how='left')

  #dedup_dataset3b_1=pysqldf('select * from dedup_dataset3b where date_reported=max_date_reported')
  dedup_dataset3b_1 = dedup_dataset3b[dedup_dataset3b['date_reported']==dedup_dataset3b['max_date_reported']]

  #dedup_dataset3b_1_remain=pysqldf('select * from dedup_dataset3b where id not in (select distinct id from dedup_dataset3b_1)')
  dedup_dataset3b_1_remain = dedup_dataset3b[~dedup_dataset3b['id'].isin(dedup_dataset3b_1['id'].unique().tolist())]

  #cnt_source_3b=pysqldf('select id, count(source) as cnt_source_3 from dedup_dataset3b_1 group by id')
  cnt_source_3b = dedup_dataset3b_1.groupby('id')['source'].count().reset_index().rename(columns={'source':'cnt_source_3'})

  #dedup_dataset3b_1=pysqldf('select a.*, b.cnt_source_3 from dedup_dataset3b_1 a left join cnt_source_3b b on a.id=b.id')
  dedup_dataset3b_1 = dedup_dataset3b_1.merge(cnt_source_3b[['id', 'cnt_source_3']], on='id', how='left')

  dedup_dataset4a=dedup_dataset3b_1[dedup_dataset3b_1['cnt_source_3']==1]
  dedup_dataset4b=dedup_dataset3b_1[dedup_dataset3b_1['cnt_source_3']>1]

  #######################################emi
  #dedup_dataset4b_1=pysqldf('select * from dedup_dataset4b where emi>500')
  dedup_dataset4b_1 = dedup_dataset4b[dedup_dataset4b['emi']>500]

  #dedup_dataset4b_1_remain=pysqldf('select * from dedup_dataset4b where id not in (select distinct id from dedup_dataset4b_1)')
  dedup_dataset4b_1_remain = dedup_dataset4b[~dedup_dataset4b['id'].isin(dedup_dataset4b_1['id'].unique().tolist())]

  #cnt_source_4b=pysqldf('select id, count(source) as cnt_source_4 from dedup_dataset4b_1 group by id')
  cnt_source_4b = dedup_dataset4b_1.groupby('id')['source'].count().reset_index().rename(columns={'source':'cnt_source_4'})

  #dedup_dataset4b_1=pysqldf('select a.*, b.cnt_source_4 from dedup_dataset4b_1 a left join cnt_source_4b b on a.id=b.id')
  dedup_dataset4b_1 = dedup_dataset4b_1.merge(cnt_source_4b[['id', 'cnt_source_4']], on='id', how='left')

  dedup_dataset5a=dedup_dataset4b_1[dedup_dataset4b_1['cnt_source_4']==1]
  dedup_dataset5b=dedup_dataset4b_1[dedup_dataset4b_1['cnt_source_4']>1]

  #####################################################12 month dpd-maximum times
  temp=dedup_dataset5b.groupby('id')['count_of_dpd_12_month'].max().reset_index(name="max_count_of_dpd_12_month")
  dedup_dataset5b=dedup_dataset5b.merge(temp,on='id',how='left')

  #dedup_dataset5b_1=pysqldf('select * from dedup_dataset5b where count_of_dpd_12_month=max_count_of_dpd_12_month')
  dedup_dataset5b_1 = dedup_dataset5b[dedup_dataset5b['count_of_dpd_12_month']==dedup_dataset5b['max_count_of_dpd_12_month']]

  #dedup_dataset5b_1_remain=pysqldf('select * from dedup_dataset5b where id not in (select distinct id from dedup_dataset5b_1)')
  dedup_dataset5b_1_remain = dedup_dataset5b[~dedup_dataset5b['id'].isin(dedup_dataset5b_1['id'])]

  #cnt_source_5b=pysqldf('select id, count(source) as cnt_source_5 from dedup_dataset5b_1 group by id')
  cnt_source_5b = dedup_dataset5b_1.groupby('id')['source'].count().reset_index().rename(columns={'source':'cnt_source_5'})

  #dedup_dataset5b_1=pysqldf('select a.*, b.cnt_source_5 from dedup_dataset5b_1 a left join cnt_source_5b b on a.id=b.id')
  dedup_dataset5b_1 = dedup_dataset5b_1.merge(cnt_source_5b[['id', 'cnt_source_5']], on='id', how='left')

  dedup_dataset6a=dedup_dataset5b_1[dedup_dataset5b_1['cnt_source_5']==1]
  dedup_dataset6b=dedup_dataset5b_1[dedup_dataset5b_1['cnt_source_5']>1]

  ##################################overdue amount
  dedup_dataset6b_1=dedup_dataset6b[dedup_dataset6b['amount_overdue']>0]

  #dedup_dataset6b_1_remain=pysqldf('select * from dedup_dataset6b where id not in (select distinct id from dedup_dataset6b_1)')
  dedup_dataset6b_1_remain = dedup_dataset6b[~dedup_dataset6b['id'].isin(dedup_dataset6b_1['id'].unique().tolist())]

  #cnt_source_6b=pysqldf('select id, count(source) as cnt_source_6 from dedup_dataset6b_1 group by id')
  cnt_source_6b = dedup_dataset6b_1.groupby('id')['source'].count().reset_index().rename(columns={'source':'cnt_source_6'})

  #dedup_dataset6b_1=pysqldf('select a.*, b.cnt_source_6 from dedup_dataset6b_1 a left join cnt_source_6b b on a.id=b.id')
  dedup_dataset6b_1 = dedup_dataset6b_1.merge(cnt_source_6b[['id','cnt_source_6']], on='id', how='left')

  dedup_dataset7a=dedup_dataset6b_1[dedup_dataset6b_1['cnt_source_6']==1]
  dedup_dataset7b=dedup_dataset6b_1[dedup_dataset6b_1['cnt_source_6']>1]


  ############################################last_payment_date
  #dedup_dataset8a=pysqldf('select * from dedup_dataset7b order by id, last_payment_date')
  dedup_dataset8a = dedup_dataset7b.sort_values(['id', 'last_payment_date'], ascending=[True, True])

  dedup_dataset8a=dedup_dataset8a.groupby('id').nth(-1).reset_index()

  #########################################remaining

  dedup_dataset_remain=pd.concat([dedup_dataset2a_remain,dedup_dataset3b_1_remain,dedup_dataset4b_1_remain,dedup_dataset5b_1_remain,dedup_dataset6b_1_remain])
  #dedup_dataset_remain_final=pysqldf('select * from dedup_dataset_remain order by id, date_reported,last_payment_date')
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
  data_loan_final2=data_loan_final.copy()
  data_loan_final=data_loan_final[~data_loan_final['ownership'].isin(["Supl Card Holder","Guarantor"])]

  ####################################################score######################################################
  cust_level=data_loan[['deal_id','cust_id','source']]

  cust_level=cust_level.drop_duplicates()

  deal_id = int(deal_id)
  customer_id = int(customer_id)
  cust_level['deal_id'] = cust_level['deal_id'].fillna(0)
  cust_level['deal_id'] = cust_level['deal_id'].astype('int64')
  cust_level=cust_level[(cust_level['cust_id']==customer_id)] #REPLACE WITH YOUR INPUT VALUE
  
  temp=data_basic.groupby(['deal_id','cust_id','source'])['SCORE'].max().reset_index(name='score')
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id','source'],how='left')
  
  ####################################################age######################################################
  data_basic['date_issued'] = pd.to_datetime(data_basic['date_issued'])
  data_basic['DOB'] = pd.to_datetime(data_basic['DOB'], format = "%Y-%m-%d")
  data_basic['DOB']
  data_basic['age'] = (data_basic['date_issued'] - data_basic['DOB']).astype('<m8[Y]')

  cust_level = cust_level.merge(data_basic[['deal_id', 'cust_id', 'source', 'age']],
                                on=['deal_id', 'cust_id', 'source'],
                                how='left')

  ##############################################removing duplicates from dpd table#########################################################################
  temp=data_loan_final[['deal_id','cust_id','source','loan_id']]
  temp=temp.drop_duplicates()
  data_dpd_final=temp.merge(data_dpd_final,on=['deal_id','cust_id','source','loan_id'],how='left')


  #########################################written off############################################################################
  temp=data_dpd_final.copy()
  temp['DPD']=temp['DPD'].replace("XXX",0)
  temp['DPD']=temp['DPD'].replace("STD",0)
  temp['DPD']=temp['DPD'].replace("SMA",180)
  temp['DPD']=temp['DPD'].replace("LSS",180)
  temp['DPD']=temp['DPD'].replace("DBT",180)
  temp['DPD']=temp['DPD'].replace("SUB",180)
  temp['DPD']= pd.to_numeric(temp['DPD'], errors="coerce")
  temp['180_dpd_flag']=temp['DPD'].apply(lambda x: 1 if x>=180 else 0)
  temp=temp.groupby(['deal_id','cust_id','source','loan_id'])['180_dpd_flag'].sum().reset_index(name='count_180_dpd_flag')
  temp['count_180_dpd_flag']=temp['count_180_dpd_flag'].apply(lambda x: 1 if x>0 else 0)

  temp1=data_loan_final.copy()
  temp1['written_off_flag']=np.where(temp1['written_off_status'].isin([0,1,2,3,4,5,6,7,8,9,10,11,99]),1,0)
  temp1=temp1.merge(temp,on=['deal_id','cust_id','source','loan_id'],how='left')
  temp1['final_written_off_status']=np.where(((temp1['written_off_flag']>0) | (temp1['count_180_dpd_flag']>0)),1,0)
  data_loan_final=data_loan_final.merge(temp1[['deal_id','cust_id','source','loan_id','final_written_off_status']],on=['deal_id','cust_id','source','loan_id'],how='left')

  temp1=temp1.groupby(['deal_id','cust_id','source'])['final_written_off_status'].sum().reset_index(name='number_of_written_off_accounts')
  ################################

  data_loan_final=data_loan_final.drop_duplicates()
  ################################
  cust_level=cust_level.merge(temp1,on=['deal_id','cust_id','source'],how='left')

  ##########################total overdue amount
  temp1=data_loan_final.copy()
  temp1=temp1.groupby(['deal_id','cust_id','source'])['amount_overdue'].sum().reset_index(name='total_overdue_amount')
  cust_level=cust_level.merge(temp1,on=['deal_id','cust_id','source'],how='left')


  ###################################################suit filed ################################################################
  temp1=data_loan_final.copy()

  temp1['suit_filed_flag']=np.where(temp1['suit_filed_willful_default'].isna(),0,1)

  temp1=temp1.groupby(['deal_id','cust_id','source'])['suit_filed_flag'].sum().reset_index(name='number_of_suit_filed_accounts')

  cust_level=cust_level.merge(temp1,on=['deal_id','cust_id','source'],how='left')

  ###################################################suit filed cases (separate table - 'all_suits_filed'################################################################
  temp1=data_loan_final.copy()

  temp1['suit_filed_flag']=np.where(temp1['suit_filed_willful_default'].isna(),0,1)

  all_suits_filed = cust_level[['deal_id', 'cust_id', 'source']].merge(temp1[temp1['suit_filed_flag']==1], on=['deal_id', 'cust_id', 'source'], how='inner')

  ################################################Loan Status Update
  temp=data_loan_final.copy()
  conditions=[(temp['active_status'].notna()),
  ((temp['active_status'].isna()) & (temp['date_closed'].isna()) & (temp['final_written_off_status']==0))]
  choices=[temp['active_status'],"Active"]
  temp['loan_status']=np.select(conditions,choices,default="Closed")
  data_loan_final=temp.copy()
  print(data_loan_final)
  #############################################################number of address var###################################
  temp=data_address.copy()
  temp=temp.groupby(['source','deal_id','cust_id'])['address_var_value'].count().reset_index(name='number_of_address_var')
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id','source'],how='left')

  ##########################################################last reported address var value###################################################
  temp = data_address.copy()
  temp = temp.sort_values(by=['source', 'deal_id', 'cust_id', 'address_var_date'], ascending=[True, True, True, False]).groupby(['source','deal_id','cust_id'])['address_var_value'].first().reset_index(name='last_reported_address')
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id','source'],how='left')

  ##########################################################last reported address var date###################################################
  temp = data_address.copy()
  temp = temp.sort_values(by=['source', 'deal_id', 'cust_id', 'address_var_date'], ascending=[True, True, True, False]).groupby(['source','deal_id','cust_id'])['address_var_date'].first().reset_index(name='last_reported_address_date')
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id','source'],how='left')

  ##########################################################all reported addresses(separate table - 'all_reported_addresses')###################################################
  all_reported_addresses = data_address.merge(cust_level[['deal_id', 'cust_id', 'source']], on=['deal_id', 'cust_id', 'source'], how='right')

  ######################################last loan disbursed CC/OD###################################################
  temp=data_loan_final[data_loan_final['acc_type_new'].isin(["corporatecreditcard","creditcard",
                                                      "fleetcard","kisancreditcard","loanagainstcard",
                                                      "loanoncreditcard","securedcreditcard","overdraft",
                                                      "primeministerjaandhanyojanaoverdraft","telcolandline",
                                                      "telcowireless","telcobroadband","autooverdraft"])]
  temp = temp.sort_values(by=['source','deal_id','cust_id','date_disbursed'], ascending=[True, True, True, False]).groupby(['source','deal_id','cust_id']).first().reset_index()[['deal_id', 'cust_id', 'source', 'account_type', 'disbursed_amount', 'date_disbursed']]
  temp['date_disbursed']=pd.to_datetime(temp['date_disbursed'], format='%Y-%m-%d')
  temp['last_disbursed_cc/od_loan'] = temp['account_type'].astype(str)+" of "+temp['disbursed_amount'].astype(str)+" , "+temp['date_disbursed'].dt.strftime("%b %Y")
  cust_level=cust_level.merge(temp[['source','deal_id','cust_id','last_disbursed_cc/od_loan']],on=['deal_id','cust_id','source'],how='left')

  ######################################last loan disbursed Non CC/OD###################################################
  temp=data_loan_final[~data_loan_final['acc_type_new'].isin(["corporatecreditcard","creditcard",
                                                      "fleetcard","kisancreditcard","loanagainstcard",
                                                      "loanoncreditcard","securedcreditcard","overdraft",
                                                      "primeministerjaandhanyojanaoverdraft","telcolandline",
                                                      "telcowireless","telcobroadband","autooverdraft"])]
  temp = temp.sort_values(by=['source','deal_id','cust_id','date_disbursed'], ascending=[True, True, True, False]).groupby(['source','deal_id','cust_id']).first().reset_index()[['deal_id', 'cust_id', 'source', 'account_type', 'disbursed_amount', 'date_disbursed']]
  temp['date_disbursed']=pd.to_datetime(temp['date_disbursed'], format='%Y-%m-%d')
  temp['last_disbursed_loan'] = temp['account_type'].astype(str)+" of "+temp['disbursed_amount'].astype(str)+" , "+temp['date_disbursed'].dt.strftime("%b %Y")
  cust_level=cust_level.merge(temp[['source','deal_id','cust_id','last_disbursed_loan']],on=['deal_id','cust_id','source'],how='left')


  ######################################Oldest Loan Disbursed###################################################
  temp = data_loan_final.copy()
  temp = temp.sort_values(by=['source','deal_id','cust_id','date_disbursed'], ascending=[True, True, True, True]).groupby(['source','deal_id','cust_id']).first().reset_index()[['deal_id', 'cust_id', 'source', 'account_type', 'disbursed_amount', 'date_disbursed']]
  temp['date_disbursed']=pd.to_datetime(temp['date_disbursed'], format='%Y-%m-%d')
  temp['oldest_loan_disbursed'] = temp['account_type'].astype(str)+" of "+temp['disbursed_amount'].astype(str)+" , "+temp['date_disbursed'].dt.strftime("%b %Y")
  cust_level=cust_level.merge(temp[['source','deal_id','cust_id','oldest_loan_disbursed']],on=['source','deal_id','cust_id'],how='left')

  ###########################number of closed loans
  temp=data_loan_final.copy()
  temp=temp[temp['loan_status']=="Closed"]
  temp=temp.groupby(['deal_id','cust_id','source'])['account_type'].count().reset_index(name="number_of_closed_accounts")
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id','source'],how='left')

  ###########################number of active tradelines
  temp=data_loan_final.copy()
  temp=temp[temp['loan_status']=="Active"]
  temp=temp.groupby(['deal_id','cust_id','source'])['account_type'].count().reset_index(name="number_of_active_tradelines")
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id','source'],how='left')

  ###########################number of secured active loans
  temp=data_loan_final.copy()
  temp=temp[temp['loan_status']=="Active"]
  temp=temp[temp['security_status']=="secured"]
  temp=temp.groupby(['deal_id','cust_id','source'])['account_type'].count().reset_index(name="number_of_secured_active_tradelines")
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id','source'],how='left')

  #######################number of unsecured active loans
  temp=data_loan_final.copy()
  temp=temp[temp['loan_status']=="Active"]
  temp=temp[temp['security_status']=="Un-secured"]

  temp=temp.groupby(['deal_id','cust_id','source'])['account_type'].count().reset_index(name="number_of_unsecured_active_tradelines")
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id','source'],how='left')

  ##########################last closed loan
  temp=data_loan_final.copy()
  temp=temp[temp['loan_status']=="Closed"]
  temp['month_since_closed_loan']=(temp['date_issued_som']-temp['date_disbursed_som_new'])/np.timedelta64(1,"M")

  temp2=temp.groupby(['deal_id','cust_id','source'])['month_since_closed_loan'].min().reset_index(name='max_closed_month')
  temp=temp.merge(temp2,on=['deal_id','cust_id','source'],how='left')
  temp=temp[temp['month_since_closed_loan']==temp['max_closed_month']]

  temp=temp.reset_index()
  temp=temp.drop(columns=['index'])
  temp['disbursed_amount']=temp['disbursed_amount'].astype(int)
  temp1=temp.loc[temp.groupby(['source','deal_id','cust_id'])['disbursed_amount'].idxmax()]
  temp1['last_closed_loan']=temp1['account_type'].astype(str)+" of "+temp1['disbursed_amount'].astype(str)+" , "+temp1['date_disbursed_som_new'].dt.strftime("%b %Y")
  cust_level=cust_level.merge(temp1[['source','deal_id','cust_id','last_closed_loan']],on=['source','deal_id','cust_id'],how='left')\

  ############################sum of current blance of un-secured active loans
  temp=data_loan_final.copy()
  temp=temp[temp['loan_status']=="Active"]
  temp=temp[temp['security_status']=="Un-secured"]
  temp=temp.groupby(['deal_id','cust_id','source'])['current_balance'].sum().reset_index(name="sum_of_current_balance_of_unsecured_active_loans")
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id','source'],how='left')

  ############################sum of current blance of secured active loans
  temp=data_loan_final.copy()
  temp=temp[temp['loan_status']=="Active"]
  temp=temp[temp['security_status']=="secured"]
  temp=temp.groupby(['deal_id','cust_id','source'])['current_balance'].sum().reset_index(name="sum_of_current_balance_of_secured_active_loans")
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id','source'],how='left')

  ############################sum of scheduled emi of active loans
  temp=bureau_automated
  temp=temp[temp['Loan_status']=="Active"]
  #print(temp['emi'])
  #print(temp)
  for i in range(len(temp)):
    if(temp.loc[i,'EMI']==0):
      temp.loc[i,'EMI']=temp.loc[i,'EMI_new']
  
  temp['cust_id']=temp['Customer_Id']
  temp['source']=temp['Source']

    

    

  temp=temp.groupby(['cust_id','source'])['EMI'].sum().reset_index(name="sum_of_emi_of_active_loans")
  # print(temp)
  cust_level=cust_level.merge(temp,on=['cust_id','source'],how='left')

  ############################max scheduled emi of active loans
  temp=bureau_automated
  temp['cust_id']=temp['Customer_Id']
  temp['source']=temp['Source']
  for i in range(len(temp)):
    if(temp.loc[i,'EMI']==0):
      temp.loc[i,'EMI']=temp.loc[i,'EMI_new']
  
  
  temp=temp.groupby(['cust_id','source'])['EMI'].max().reset_index(name="max_emi_of_active_loans")
  cust_level=cust_level.merge(temp,on=['cust_id','source'],how='left')

  ############################min scheduled emi of active loans
  temp=bureau_automated
  temp['cust_id']=temp['Customer_Id']
  temp['source']=temp['Source']
  for i in range(len(temp)):
    if(temp.loc[i,'EMI']==0):
      temp.loc[i,'EMI']=temp.loc[i,'EMI_new']
  temp=temp.groupby(['cust_id','source'])['EMI'].min().reset_index(name="min_emi_of_active_loans")
  cust_level=cust_level.merge(temp,on=['cust_id','source'],how='left')

  ##################################################secured last dpd status ##########################################################################
  temp1=data_dpd_final.copy()
  temp1['DPD']=temp1['DPD'].replace("XXX",0)
  temp1['DPD']=temp1['DPD'].replace("STD",0)
  temp1['DPD']=temp1['DPD'].replace("SMA",90)
  temp1['DPD']=temp1['DPD'].replace("LSS",360)
  temp1['DPD']=temp1['DPD'].replace("DBT",270)
  temp1['DPD']=temp1['DPD'].replace("SUB",180)
  temp1['DPD']= pd.to_numeric(temp1['DPD'], errors="coerce")

  temp1=temp1[temp1['DPD']>0]

  temp=data_loan_final.copy()
  temp=temp[['deal_id', 'cust_id', 'source', 'report_id', 'loan_id', 'security_status']]
  temp1=temp1.merge(temp, on=['deal_id', 'cust_id', 'source', 'report_id', 'loan_id'], how='left')
  temp1=temp1[temp1['security_status']=='secured']
  temp2=temp1.groupby(['deal_id','cust_id','source'])['DPD_month'].max().reset_index(name='max_DPD_month')
  temp1=temp1.merge(temp2,on=['deal_id','cust_id','source'],how='left')
  temp1=temp1[temp1['DPD_month']==temp1['max_DPD_month']]
  temp=temp1.loc[temp1.groupby(['source','deal_id','cust_id'])['DPD'].idxmax()]
  temp['secured_last_dpd_status']=temp['DPD'].astype(str)+" , "+temp['DPD_month'].dt.strftime("%b %Y")
  cust_level=cust_level.merge(temp[['source','deal_id','cust_id','secured_last_dpd_status']],on=['source','deal_id','cust_id'],how='left')

  ##################################################un-secured last dpd status ##########################################################################
  temp1=data_dpd_final.copy()
  temp1['DPD']=temp1['DPD'].replace("XXX",0)
  temp1['DPD']=temp1['DPD'].replace("STD",0)
  temp1['DPD']=temp1['DPD'].replace("SMA",90)
  temp1['DPD']=temp1['DPD'].replace("LSS",360)
  temp1['DPD']=temp1['DPD'].replace("DBT",270)
  temp1['DPD']=temp1['DPD'].replace("SUB",180)
  temp1['DPD']= pd.to_numeric(temp1['DPD'], errors="coerce")
  temp1=temp1[temp1['DPD']>0]

  temp=data_loan_final.copy()
  temp=temp[['deal_id', 'cust_id', 'source', 'report_id', 'loan_id', 'security_status']]
  temp1=temp1.merge(temp, on=['deal_id', 'cust_id', 'source', 'report_id', 'loan_id'], how='left')
  temp1=temp1[temp1['security_status']=='Un-secured']
  temp2=temp1.groupby(['deal_id','cust_id','source'])['DPD_month'].max().reset_index(name='max_DPD_month')
  temp1=temp1.merge(temp2,on=['deal_id','cust_id','source'],how='left')
  temp1=temp1[temp1['DPD_month']==temp1['max_DPD_month']]
  temp=temp1.loc[temp1.groupby(['source','deal_id','cust_id'])['DPD'].idxmax()]
  temp['unsecured_last_dpd_status']=temp['DPD'].astype(str)+" , "+temp['DPD_month'].dt.strftime("%b %Y")
  cust_level=cust_level.merge(temp[['source','deal_id','cust_id','unsecured_last_dpd_status']],on=['source','deal_id','cust_id'],how='left')

  ##################################################Un-secured Max dpd status ##########################################################################
  temp1=data_dpd_final.copy()
  temp1['DPD']=temp1['DPD'].replace("XXX",0)
  temp1['DPD']=temp1['DPD'].replace("STD",0)
  temp1['DPD']=temp1['DPD'].replace("SMA",90)
  temp1['DPD']=temp1['DPD'].replace("LSS",360)
  temp1['DPD']=temp1['DPD'].replace("DBT",270)
  temp1['DPD']=temp1['DPD'].replace("SUB",180)
  temp1['DPD']= pd.to_numeric(temp1['DPD'], errors="coerce")
  temp1=temp1[temp1['DPD']>0] 

  temp=data_loan_final.copy()
  temp=temp[['deal_id', 'cust_id', 'source', 'report_id', 'loan_id', 'security_status']]
  temp1=temp1.merge(temp, on=['deal_id', 'cust_id', 'source', 'report_id', 'loan_id'], how='left')

  temp1=temp1[temp1['security_status']=='Un-secured']
  temp2=temp1.groupby(['deal_id','cust_id','source'])['DPD'].max().reset_index(name='max_DPD')
  temp1=temp1.merge(temp2,on=['deal_id','cust_id','source'],how='left')
  temp1=temp1[temp1['DPD']==temp1['max_DPD']]

  temp=temp1.loc[temp1.groupby(['source','deal_id','cust_id'])['DPD_month'].idxmax()]
  
  temp['unsecured_max_dpd_status']=temp['DPD'].astype(str)+" , "+temp['DPD_month'].dt.strftime("%b %Y")
  cust_level=cust_level.merge(temp[['source','deal_id','cust_id','unsecured_max_dpd_status']],on=['source','deal_id','cust_id'],how='left')
  
  ##################################################secured Max dpd status ##########################################################################
  temp1=data_dpd_final.copy()
  temp1['DPD']=temp1['DPD'].replace("XXX",0)
  temp1['DPD']=temp1['DPD'].replace("STD",0)
  temp1['DPD']=temp1['DPD'].replace("SMA",90)
  temp1['DPD']=temp1['DPD'].replace("LSS",360)
  temp1['DPD']=temp1['DPD'].replace("DBT",270)
  temp1['DPD']=temp1['DPD'].replace("SUB",180)
  temp1['DPD']= pd.to_numeric(temp1['DPD'], errors="coerce")
  temp1=temp1[temp1['DPD']>0]

  temp=data_loan_final.copy()
  temp=temp[['deal_id', 'cust_id', 'source', 'report_id', 'loan_id', 'security_status']]
  temp1=temp1.merge(temp, on=['deal_id', 'cust_id', 'source', 'report_id', 'loan_id'], how='left')
  temp1=temp1[temp1['security_status']=='secured']
  temp2=temp1.groupby(['deal_id','cust_id','source'])['DPD'].max().reset_index(name='max_DPD')
  temp1=temp1.merge(temp2,on=['deal_id','cust_id','source'],how='left')
  temp1=temp1[temp1['DPD']==temp1['max_DPD']]

  temp=temp1.loc[temp1.groupby(['source','deal_id','cust_id'])['DPD_month'].idxmax()]
  temp['secured_max_dpd_status']=temp['DPD'].astype(str)+" , "+temp['DPD_month'].dt.strftime("%b %Y")
  cust_level=cust_level.merge(temp[['source','deal_id','cust_id','secured_max_dpd_status']],on=['source','deal_id','cust_id'],how='left')
  
  ########################largest active loan
  temp=data_loan_final.copy()
  temp=temp[temp['loan_status']=="Active"]
  temp['date_disbursed']=pd.to_datetime(temp['date_disbursed'], format='%Y-%m-%d')
  temp=temp.sort_values(by=['deal_id','cust_id','source','disbursed_amount'], ascending=[True,True,True,False]).groupby(['deal_id','cust_id','source'], as_index=False).first()[['deal_id', 'cust_id', 'source', 'account_type', 'disbursed_amount', 'date_disbursed']]
  temp['largest_active_loan'] = temp['account_type'].astype(str)+" of "+temp['disbursed_amount'].astype(str)+" in "+temp['date_disbursed'].dt.strftime("%b %Y")
  cust_level=cust_level.merge(temp[['source','deal_id','cust_id','largest_active_loan']],on=['deal_id','cust_id','source'],how='left')

  ########################largest closed loan
  temp=data_loan_final.copy()
  temp=temp[temp['loan_status']=="Closed"]
  temp['date_disbursed']=pd.to_datetime(temp['date_disbursed'], format='%Y-%m-%d')
  temp=temp.sort_values(by=['deal_id','cust_id','source','disbursed_amount'], ascending=[True,True,True,False]).groupby(['deal_id','cust_id','source'], as_index=False).first()[['deal_id', 'cust_id', 'source', 'account_type', 'disbursed_amount', 'date_disbursed']]
  temp['largest_closed_loan'] = temp['account_type'].astype(str)+" of "+temp['disbursed_amount'].astype(str)+" in "+temp['date_disbursed'].dt.strftime("%b %Y")
  cust_level=cust_level.merge(temp[['source','deal_id','cust_id','largest_closed_loan']],on=['deal_id','cust_id','source'],how='left')

  ########################smallest active loan
  temp=data_loan_final.copy()
  temp=temp[temp['loan_status']=="Active"]
  temp['date_disbursed']=pd.to_datetime(temp['date_disbursed'], format='%Y-%m-%d')
  temp=temp.sort_values(by=['deal_id','cust_id','source','disbursed_amount'], ascending=[True,True,True,True]).groupby(['deal_id','cust_id','source'], as_index=False).first()[['deal_id', 'cust_id', 'source', 'account_type', 'disbursed_amount', 'date_disbursed']]
  temp['smallest_active_loan'] = temp['account_type'].astype(str)+" of "+temp['disbursed_amount'].astype(str)+" in "+temp['date_disbursed'].dt.strftime("%b %Y")
  cust_level=cust_level.merge(temp[['source','deal_id','cust_id','smallest_active_loan']],on=['deal_id','cust_id','source'],how='left')

  #####################################max credit limit of active cc od
  temp=data_loan_final[data_loan_final['acc_type_new'].isin(["corporatecreditcard","creditcard",
                                                      "fleetcard","kisancreditcard","loanagainstcard",
                                                      "loanoncreditcard","securedcreditcard","overdraft",
                                                      "primeministerjaandhanyojanaoverdraft","telcolandline",
                                                      "telcowireless","telcobroadband","autooverdraft"])]

  temp1=temp[temp['loan_status']=="Active"]
  temp1=temp1.reset_index()
  # temp1['credit_limit']=temp1['credit_limit','current_balance'].apply(lambda x,y:  y if x == 0 or x == None else x )
  i=0
  for i in range(len(temp1.index)):
    if(temp1['credit_limit'][i]==None):
      temp1['credit_limit'][i]=0

    temp1['credit_limit'][i]=max(temp1['credit_limit'][i],temp1['disbursed_amount'][i])


  temp1=temp1.groupby(['deal_id','cust_id','source'])['credit_limit'].max().reset_index(name='max_credit_limit_of_active_cc_od')
  print('temp',temp)
  print('cust_level',cust_level)
  try:
    cust_level=cust_level.merge(temp1,on=['deal_id','cust_id','source'],how='left')
  except:
    cust_level = cust_level


  #####################################total credit limit of active cc od
  temp1=temp[temp['loan_status']=="Active"]
  temp1 = temp1.reset_index()
  # temp1['credit_limit']=temp1['credit_limit','current_balance'].apply(lambda x,y:  y if x == 0 or x == None else x )
  i = 0
  for i in range(len(temp1.index)):
    if (temp1['credit_limit'][i] == None):
      temp1['credit_limit'][i] = 0

    temp1['credit_limit'][i] = max(temp1['credit_limit'][i], temp1['disbursed_amount'][i])

  temp1=temp1.groupby(['deal_id','cust_id','source'])['credit_limit'].sum().reset_index(name='total_credit_limit_of_active_cc_od')
  try:
    cust_level=cust_level.merge(temp1,on=['deal_id','cust_id','source'],how='left')
  except:
    cust_level = cust_level
  #####################################total current balance of active cc od
  temp1=temp[temp['loan_status']=="Active"]
  temp1=temp1.groupby(['deal_id','cust_id','source'])['current_balance'].sum().reset_index(name='total_current_balance_of_active_cc_od')
  try:
    cust_level=cust_level.merge(temp1,on=['deal_id','cust_id','source'],how='left')
  except:
    cust_level = cust_level

  #############################credit card and overdraft utlization
  #######################check if it is needed only for active loan then introduce a filter
  ##########################check exact definition of credit limit used and change accordingly, I have taken high credit amount as credit limit used
  temp=data_loan_final[data_loan_final['acc_type_new'].isin(["corporatecreditcard","creditcard",
                                                      "fleetcard","kisancreditcard","loanagainstcard",
                                                      "loanoncreditcard","securedcreditcard","overdraft",
                                                      "primeministerjaandhanyojanaoverdraft","telcolandline",
                                                      "telcowireless","telcobroadband","autooverdraft"])]
  temp=temp.groupby(
   ['deal_id', 'cust_id','source']
  ).agg(
    {
         'disbursed_amount':sum,    # Sum of high credit ampount
         # 'credit_limit': sum,  # sum of credit limit
          'current_balance':sum,
    }
  )

  temp=temp.reset_index()
  # temp['cc_od_utilization_ratio']=temp['disbursed_amount']/temp['credit_limit']
  temp['cc_od_utilization_ratio'] = round((temp['current_balance'] / temp['disbursed_amount'])*100,2)
  try:
    cust_level=cust_level.merge(temp[['deal_id','cust_id','source','cc_od_utilization_ratio']],on=['deal_id','cust_id','source'],how='left')
  except:
    cust_level = cust_level

  ##########################credit utilization loans
  temp=data_loan_final[~data_loan_final['acc_type_new'].isin(["corporatecreditcard","creditcard",
                                                      "fleetcard","kisancreditcard","loanagainstcard",
                                                      "loanoncreditcard","securedcreditcard","overdraft",
                                                      "primeministerjaandhanyojanaoverdraft","telcolandline",
                                                      "telcowireless","telcobroadband","autooverdraft"])]
  temp=temp.groupby(
   ['deal_id', 'cust_id','source']
  ).agg(
    {
         'disbursed_amount':sum,    # Sum of disbursed amount
         'current_balance': sum,  # sum of current balance
    }
  )

  temp=temp.reset_index()
  temp['credit_utilization_ratio']=round((temp['current_balance']/temp['disbursed_amount'])*100,2)
  cust_level=cust_level.merge(temp[['deal_id','cust_id','source','credit_utilization_ratio']],on=['deal_id','cust_id','source'],how='left')

  #########################number of loans in last 12,24,36 months
  temp=data_loan_final.copy()
  temp['date_issued_som']=pd.to_datetime(temp['date_issued_som'])
  temp['date_disbursed_som_new']=pd.to_datetime(temp['date_disbursed_som_new'])
  temp['month_since_disbursal']=(temp['date_issued_som']-temp['date_disbursed_som_new'])/np.timedelta64(1,"M")
  temp1=temp[temp['month_since_disbursal']<=12]
  temp1=temp1.groupby(['deal_id','cust_id','source'])['account_type'].count().reset_index(name='number_of_loans_disbursed_last_year')
  cust_level=cust_level.merge(temp1,on=['deal_id','cust_id','source'],how='left')
  temp1=temp[(temp['month_since_disbursal']<=24) & (temp['month_since_disbursal']>12)]
  temp1=temp1.groupby(['deal_id','cust_id','source'])['account_type'].count().reset_index(name='number_of_loans_disbursed_last_two_year')
  cust_level=cust_level.merge(temp1,on=['deal_id','cust_id','source'],how='left')
  temp1=temp[(temp['month_since_disbursal']<=36) & (temp['month_since_disbursal']>24)]
  temp1=temp1.groupby(['deal_id','cust_id','source'])['account_type'].count().reset_index(name='number_of_loans_disbursed_last_three_year')
  cust_level=cust_level.merge(temp1,on=['deal_id','cust_id','source'],how='left')

  temp=data_dpd_final.copy()
  temp['DPD']=temp['DPD'].replace("XXX",0)
  temp['DPD']=temp['DPD'].replace("STD",0)
  temp['DPD']=temp['DPD'].replace("SMA",180)
  temp['DPD']=temp['DPD'].replace("LSS",180)
  temp['DPD']=temp['DPD'].replace("DBT",180)
  temp['DPD']=temp['DPD'].replace("SUB",180)
  temp['DPD']= pd.to_numeric(temp['DPD'], errors="coerce")
  temp['180_dpd_flag']=temp['DPD'].apply(lambda x: 1 if x>=180 else 0)
  temp=temp.groupby(['deal_id','cust_id','source','loan_id'])['180_dpd_flag'].sum().reset_index(name='count_180_dpd_flag')
  temp['count_180_dpd_flag']=temp['count_180_dpd_flag'].apply(lambda x: 1 if x>0 else 0)

  temp1=data_loan_final2.copy()
  temp1['written_off_flag']=np.where(temp1['written_off_status'].isin([0,1,2,3,4,5,6,7,8,9,10,11,99]),1,0)
  temp1=temp1.merge(temp,on=['deal_id','cust_id','source','loan_id'],how='left')
  temp1['final_written_off_status']=np.where(((temp1['written_off_flag']>0) | (temp1['count_180_dpd_flag']>0)),1,0)
  data_loan_final2=data_loan_final2.merge(temp1[['deal_id','cust_id','source','loan_id','final_written_off_status']],on=['deal_id','cust_id','source','loan_id'],how='left')

  temp=data_loan_final2.copy()
  conditions=[(temp['active_status'].notna()),
  ((temp['active_status'].isna()) & (temp['date_closed_som_new'].isna()) & (temp['final_written_off_status']==0))]
  choices=[temp['active_status'],"Active"]
  temp['loan_status']=np.select(conditions,choices,default="Closed")
  data_loan_final2=temp.copy()


  ###########################number of loans as guarantor - total
  temp=data_loan_final2.copy()
  temp=temp[temp['ownership']=="Guarantor"]
  temp=temp.groupby(['deal_id','cust_id','source'])['account_type'].count().reset_index(name="number_of_loans_as_guarantor_total")
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id','source'],how='left')

  ###########################number of loans as invidual - total
  temp=data_loan_final2.copy()
  temp=temp[temp['ownership']=="Individual"]
  temp=temp.groupby(['deal_id','cust_id','source'])['account_type'].count().reset_index(name="number_of_loans_as_individual_total")
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id','source'],how='left')

  ###########################number of loans as joint - total
  temp=data_loan_final2.copy()
  temp=temp[temp['ownership']=="Joint"]
  temp=temp.groupby(['deal_id','cust_id','source'])['account_type'].count().reset_index(name="number_of_loans_as_join_total")
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id','source'],how='left')

  ###########################number of loans as guarantor - active
  temp=data_loan_final2.copy()
  temp=temp[temp['ownership']=="Guarantor"]
  temp=temp[temp['loan_status']=="Active"]
  temp=temp.groupby(['deal_id','cust_id','source'])['account_type'].count().reset_index(name="number_of_loans_as_guarantor_active")
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id','source'],how='left')

  ###########################number of loans as invidual - active
  temp=data_loan_final2.copy()
  temp=temp[temp['ownership']=="Individual"]
  temp=temp[temp['loan_status']=="Active"]
  temp=temp.groupby(['deal_id','cust_id','source'])['account_type'].count().reset_index(name="number_of_loans_as_individual_active")
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id','source'],how='left')

  ###########################number of loans as joint - active
  temp=data_loan_final2.copy()
  temp=temp[temp['ownership']=="Joint"]
  temp=temp[temp['loan_status']=="Active"]
  temp=temp.groupby(['deal_id','cust_id','source'])['account_type'].count().reset_index(name="number_of_loans_as_joint_active")
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id','source'],how='left')

  ############################################################number of inquiries in last 6 month#########################

  temp=data_inquiry.copy()
  temp['date_issued_som']=temp['date_issued']
  temp['date_issued_som']=pd.to_datetime(temp['date_issued_som'])
  temp['date_issued_som']=temp['date_issued_som'].apply(lambda x: x.replace(day=1))
  temp['month_since_inquiry']=(temp['date_issued_som']-temp['date_of_inquiry'])/np.timedelta64(1,"M")
  temp=temp[temp['month_since_inquiry']<=6]

  temp=temp.groupby(['source','deal_id','cust_id'])['purpose_of_inquiry'].count().reset_index(name='number_of_inquiries_in_last_6_month')
  cust_level=cust_level.merge(temp,on=['deal_id','cust_id','source'],how='left')

  #########################latest inquiry made
  #########################will need mapping for purpose of inquiry and corresponding loan types. for time being I have assumed it to be similar to account type mapping
  temp1=data_inquiry.copy()
  temp1['purpose_of_inquiry']=temp1['purpose_of_inquiry'].astype(str).map({"1": "Auto Loan (Personal)",
  "2":"Housing Loan",
  "3":"Property Loan",
  "4":"Loan Against Shares/Securities",
  "5":"Personal Loan",
  "6":"Consumer Loan",
  "7":"Gold Loan",
  "8":"Education Loan",
  "9":"Loan to Professional",
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

  temp2=temp1.groupby(['deal_id','cust_id','source'])['date_of_inquiry'].max().reset_index(name='max_date_inquiry')
  temp1=temp1.merge(temp2,on=['deal_id','cust_id','source'],how='left')
  temp1=temp1[temp1['date_of_inquiry']==temp1['max_date_inquiry']]

  temp=temp1.loc[temp1.groupby(['source','deal_id','cust_id'])['amount_of_inquiry'].idxmax()]
  temp['last_inquiry']=temp['amount_of_inquiry'].astype(str)+" for "+temp['purpose_of_inquiry'].astype(str)+" of "+temp['date_of_inquiry'].dt.strftime("%b %Y")
  cust_level=cust_level.merge(temp[['source','deal_id','cust_id','last_inquiry']],on=['source','deal_id','cust_id'],how='left')

  #########################all enquiries made (stored in separate table - 'all_enquiries')
  temp1=data_inquiry.copy()
  temp1['purpose_of_inquiry']=temp1['purpose_of_inquiry'].astype(str).map({"1": "Auto Loan (Personal)",
  "2":"Housing Loan",
  "3":"Property Loan",
  "4":"Loan Against Shares/Securities",
  "5":"Personal Loan",
  "6":"Consumer Loan",
  "7":"Gold Loan",
  "8":"Education Loan",
  "9":"Loan to Professional",
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

  all_enquiries = cust_level[['deal_id', 'cust_id', 'source']].merge(temp1, on=['deal_id', 'cust_id', 'source'], how='inner')

  ##################################################count dpd instances##########################################################################
  #inputs
  a,b=(10,200) #give range of dpd required for filter ie dpd>=a & dpd<=b in form of tuple
  accts = ['Credit Card', 'Other'] #give the loan products required for filter in form of list
  t1, t2 = (0,12) #give the duration (in months) for which filter to be applied eg for dpd occuring in last two years input will be (0,24) (t>=0 & t<=24)

  temp1=data_dpd_final.copy()
  
  temp1['DPD']=temp1['DPD'].replace("XXX",0)
  temp1['DPD']=temp1['DPD'].replace("STD",0)
  temp1['DPD']=temp1['DPD'].replace("SMA",90)
  temp1['DPD']=temp1['DPD'].replace("LSS",360)
  temp1['DPD']=temp1['DPD'].replace("DBT",270)
  temp1['DPD']=temp1['DPD'].replace("SUB",180)
  temp1['DPD']= pd.to_numeric(temp1['DPD'], errors="coerce")
  # temp1=temp1[temp1['DPD']>0]
  #

  temp = data_loan_final.copy()
  temp1 = temp1.merge(cust_level[['deal_id', 'cust_id', 'source']], on=['deal_id', 'cust_id', 'source'], how='inner')
  
  temp1 = temp1[(temp1['DPD']>=a) & (temp1['DPD']<=b)]
  temp1 = temp1.merge(temp[['deal_id', 'cust_id', 'source', 'loan_id', 'report_id', 'account_type']], on=['deal_id', 'cust_id', 'source', 'loan_id', 'report_id'], how='left')

  temp1 = temp1[temp1['account_type'].isin(accts)]
  temp1 = temp1[(temp1['month_since_dpd']>=t1) & (temp1['month_since_dpd']<=t2)]
  temp1.reset_index(drop=True, inplace=True)
  cust_level = cust_level.merge(temp1.groupby(['deal_id', 'cust_id', 'source'], as_index=False)['account_type'].count().rename(columns={'account_type':'count_dpd_instance'}), on=['deal_id', 'cust_id', 'source'], how='left')
  dpd_instances = temp1.copy()
  dpd_instances = dpd_instances.drop_duplicates().reset_index(drop=True)
  
  '''
  ### Output Tables - 
  1. **cust_level** - (Level = deal_id, cust_id & source)
  2. **all_suits_filed** - (Level = deal_id, cust_id, source, loan_id)
  3. **all_enquiries** - (Level = deal_id, cust_id, source, inquiry_id)
  4. **all_reported_addresses** - (Level = deal_id, cust_id, source, address_var_id)
  5. **dpd_instances** - (Level = deal_id, cust_id, source, loan_id, DPD_month)
  '''



  return cust_level, all_suits_filed, all_enquiries, all_reported_addresses, dpd_instances