import pandas as pd
import pymysql
import numpy as np
import datetime
import calendar
import time
from dateutil.relativedelta import relativedelta

def inflow_outflow(bank,itrv,form16,form26):

  

    def get_years_months(start_date, months):
        for i in range(months):
            yield (start_date.year, start_date.month)
            start_date -= datetime.timedelta(days=calendar.monthrange(start_date.year, start_date.month)[1])
            

    months = []
    for i in get_years_months(datetime.date.today().replace(day=12), 12):
        months.append(datetime.datetime.strftime(pd.to_datetime(str(i[1])+'-'+str(i[0]),format='%m-%Y'), '%b-%y'))

    months = pd.DataFrame(data={'month':months})


    ###########################BANK STATEMENTS#####################################
    '''conn1 = pymysql.connect(host = '10.20.30.40', port = 3306, user = 'ABC', passwd = 'PAS8765', charset = 'utf8', db='abc')#make sql connection using pymysql

    query1 = 'Select * from bank_table where deal_id=123 AND cust_id=123 AND YEAR(Txn_Date) = YEAR(DATE_SUB(CURDATE(), INTERVAL 3 YEAR))' #change as per backend data format
    df = pd.read_sql(query, conn1)
    '''

    #sample data from csv, will need to remove this portion
    # df = pd.read_csv(r"C:\Users\Siddhant\Desktop\Digitisation\Statements\hdfc.csv")
    df = bank
    try:
        df.rename(columns={'account_number':'acc_no', 'txn_date':'Txn_Date'}, inplace=True)
        # df.credit.replace(np.nan, '0', inplace=True)
        # df.credit = [float(i.replace(',','')) for i in df.credit]
        # #

        c = pd.DataFrame(columns=['month', 'credit', 'acc_no'])
        for acc_no, banks in df.groupby('acc_no'):
            a = banks.reset_index(drop=True)
            a['Txn_Date'] = pd.to_datetime(a['Txn_Date'], dayfirst=True)
            a['month'] = [datetime.datetime.strftime(i,'%b-%y') for i in a['Txn_Date']]
            
           

            a = a.merge(months, on='month', how='left')
        
            a = a[a['credit']>0]

            a.reset_index(drop=True, inplace=True)
            b=a.groupby('month')['credit'].sum().reset_index()
            b['acc_no'] = acc_no
            c = c.append(b)
            c.reset_index(drop=True, inplace=True)
        c['acc_no'] = "(A/C: "+ c['acc_no']+")"
        c.credit.fillna(0, inplace=True)
        # total = c.groupby('month').credit.sum().reset_index()
        # total.month = pd.to_datetime(total.month, format='%b-%y')
        # total.sort_values('month', ascending=True, inplace=True)
        # total['acc_no'] = 'Bank Credit Total'
        # accounts_net_pivot = total.pivot_table(columns='month', values='credit', index='acc_no')
        # accounts_net_pivot.columns=[datetime.datetime.strftime(i, format='%b-%y') for i in accounts_net_pivot.columns.to_list()]

        c.month = pd.to_datetime(c.month, format='%b-%y')
        c.sort_values(['acc_no', 'month'], ascending=[True, True], inplace=True)

        a=c.set_index('acc_no')
        accounts_pivot = a.pivot_table(columns='month', values='credit', index='acc_no')


        accounts_pivot.columns=[datetime.datetime.strftime(i, format='%b-%y') for i in accounts_pivot.columns.to_list()]

        bank_pivot = accounts_pivot

        
        bank_pivot = bank_pivot.reset_index()
        
        
       
       
        # print(bank_pivot.T.reset_index())

        bank_pivot = bank_pivot.T.reset_index()
        bank_pivot_head = bank_pivot.iloc[0]

        bank_pivot = bank_pivot.iloc[1:]
        print(bank_pivot)

        bank_overall = months
        bank_overall = bank_overall.merge(bank_pivot, left_on='month', right_on='index', how='left')
        bank_overall = bank_overall.drop(columns = ['index'])

    except:
        bank_overall = months
      
        bank_pivot_head=''
    # if len(bank_overall.columns)
    

    ###########################SALARY#####################################
    '''
    conn2 = pymysql.connect(host = '10.20.30.40', port = 3306, user = 'ABC', passwd = 'PAS8765', charset = 'utf8', db='bureau')
    query2 = "select date, salary from salary_table where customer_id="123" and deal_id="111" "  # customer_id and deal_id will be dynamic
    df_salary = pd.read_sql(query2, conn2)
    '''
    #sample data from csv, will need to remove this portion
    # df = pd.read_csv('./Desktop/salary.csv')
    # df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    # #

    # df['month'] = [datetime.datetime.strftime(i, format='%b-%y') for i in df['date']]
    # df.sort_values('date', ascending=True, inplace=True)
    # df = df.merge(months, on='month', how='right')
    # df['heading'] = 'Net Salary'
    # df['date'] = pd.to_datetime(df['month'], format='%b-%y')
    # df.salary.fillna(-99999999999999, inplace=True)
    # salary_pivot = df.pivot_table(columns='date', index='heading', values='salary')
    # salary_pivot.columns=[datetime.datetime.strftime(i, format='%b-%y') for i in salary_pivot.columns.to_list()]

    #############################ITR-V#####################################
    '''
    conn3 = pymysql.connect(host = '10.20.30.40', port = 3306, user = 'ABC', passwd = 'PAS8765', charset = 'utf8', db='bureau')
    query3 = "select assessment_year,total_income from itrv_table where customer_id="123" and deal_id="111" "  # customer_id and deal_id will be dynamic
    df = pd.read_sql(query3, conn3)
    '''
    #sample data from csv, will need to remove this portion
    df = itrv
    #


    year = int(df['assessment_year'][0].split('-')[0])
    months_itr = []
    try:
        for i in get_years_months(datetime.date(year=year, month=3, day=15), 12):

            months_itr.append(datetime.datetime.strftime(pd.to_datetime(str(i[1])+'-'+str(i[0]),format='%m-%Y'), '%b-%y'))
            # print(datetime.datetime.strftime(pd.to_datetime(str(i[1])+'-'+str(i[0]),format='%m-%Y'), '%b-%y'))


        df_itr = pd.DataFrame(data={'month':months_itr})
        # print(df_itr)
        df['gross_total_income'] = df['gross_total_income'].astype('float64')
        # print(df['gross_total_income'])
        # print(df_itr)
        df_itr['income'] = ''
        df_itr['income'] = df['gross_total_income'][0]/12
        # df_itr['income'] = df['gross_total_income'].apply(lambda x : round(x/12,2))
        
        # print(months)
        df_itr = df_itr.merge(months, on='month', how='right')
        df_itr['date'] = pd.to_datetime(df_itr['month'], format='%b-%y')
        df_itr.sort_values('date', ascending=True, inplace=True)
        df_itr['header']='ITRV'
        df_itr.fillna(0, inplace=True)
        itrv_pivot = df_itr.pivot_table(columns='date', index='header', values='income')
        itrv_pivot.columns=[datetime.datetime.strftime(i, format='%b-%y') for i in itrv_pivot.columns.to_list()]


        itrv_pivot = itrv_pivot.T
        itrv_pivot = itrv_pivot.reset_index()
        # print(itrv_test)
        itr_overall = months
        
        # overall = overall.rename(columns = {0:'month_year'})
        # print(overall)
        # overall = overall.merge(itrv_test, left_on='month', right_on='index', how='left')
        itr_overall = itr_overall.merge(itrv_pivot, left_on='month', right_on='index', how='left')
        itr_overall = itr_overall.drop(columns = ['index'])
    except:
        itr_overall = ''
    #############################FORM 16#####################################
    '''
    conn4 = pymysql.connect(host = '10.20.30.40', port = 3306, user = 'ABC', passwd = 'PAS8765', charset = 'utf8', db='bureau')
    query4 = "select assessment_year, quarter, amount_paid_credited from form16_table where customer_id="123" and deal_id="111" "  # customer_id and deal_id will be dynamic
    df = pd.read_sql(query4, conn4)
    '''
    #sample data from csv, will need to remove this portion 
    # df = pd.read_csv('./Desktop/form16.csv')

    df = form16

    form16 = pd.DataFrame(columns=['date', 'month', 'amount', 'quarter'], index=range(len(df.index.tolist())*3))
    #

    try:

        year = df['assessment_year'][0].split('-')[0]
            
        year = str(int(year)-1)

        form16['quarter'] = np.repeat(df['quarter'].values, 3)
        form16['quarter'] = year+'-'+form16['quarter']
       
        df['amount_paid_credited'] = df['amount_paid_credited'].astype('float64')
        form16['amount'] = np.repeat(df['amount_paid_credited'].values/3, 3)
        form16['date'] = [i + relativedelta(months=3) for i in pd.PeriodIndex(form16['quarter'].to_list(), freq='Q').to_timestamp()]

        def func(x):
            x['date'] = [i+relativedelta(months=ind) for ind, i in enumerate(x['date'])]
            return x
        form16 = form16.groupby('quarter').apply(func)

        form16['month'] = [datetime.datetime.strftime(i, format='%b-%y') for i in form16['date']]
        form16 = form16.merge(months, on='month', how='right')
        # print(form16)
        form16['date'] = pd.to_datetime(form16['month'], format='%b-%y')
        form16.sort_values('date', inplace=True)
        form16['ind'] = 'Form16'
        form16.amount.fillna(0, inplace=True)
        form16_pivot = form16.pivot_table(columns='date', index='ind', values='amount')
        form16_pivot.columns=[datetime.datetime.strftime(i, format='%b-%y') for i in form16_pivot.columns.to_list()]

        form16_pivot = form16_pivot.T
        form16_pivot = form16_pivot.reset_index()

        form16_overall = months

        form16_overall = form16_overall.merge(form16_pivot, left_on='month', right_on='index', how='left')

        # overall = overall.merge(form16_pivot, left_on='month', right_on='index', how='left')
        # overall = overall.drop(columns = ['index_x','index_y'])
        
        
        form16_overall = form16_overall.drop(columns = ['index'])

    except:
        form16_overall = ''

    #############################FORM 26AS#####################################
    '''
    conn5 = pymysql.connect(host = '10.20.30.40', port = 3306, user = 'ABC', passwd = 'PAS8765', charset = 'utf8', db='bureau')
    query5 = "select assessment_year, amount_paid_credited, transaction_date from form26as_table where customer_id="123" and deal_id="111" "  # customer_id and deal_id will be dynamic
    df = pd.read_sql(sql3, conn)
    '''
    #sample data from csv, will need to remove this portion
    # df = pd.read_csv('./Desktop/form26as.csv')

    df = form26
    try:
        df = df[['amount_paid_credited', 'transaction_date']]
        df.rename(columns={'amount_paid_credited':'amount', 'transaction_date':'date'}, inplace=True)
        form26as = df.copy()
        #

        form26as['date'] = pd.to_datetime(form26as['date'], format='%d-%b-%Y')
        form26as['month'] = [datetime.datetime.strftime(i, format='%b-%y') for i in form26as['date']]
        form26as = form26as.groupby('month').amount.sum().reset_index()
        form26as = form26as.merge(months, on='month', how='right')
        form26as['date'] = pd.to_datetime(form26as['month'], format='%b-%y')
        form26as.sort_values('date', inplace=True)
        form26as['ind'] = 'Form26AS'
        form26as.amount.fillna(0, inplace=True)
        form26as_pivot = form26as.pivot_table(columns='date', index='ind', values='amount')
        form26as_pivot.columns=[datetime.datetime.strftime(i, format='%b-%y') for i in form26as_pivot.columns.to_list()]

        form26as_pivot = form26as_pivot.T
        form26as_pivot = form26as_pivot.reset_index()

        form26as_overall = months

        form26as_overall = form26as_overall.merge(form26as_pivot, left_on='month', right_on='index', how='left')

        # overall = overall.merge(form26as_pivot, left_on='month', right_on='index', how='left')
        # overall = overall.drop(columns = ['index'])


        form26as_overall = form26as_overall.drop(columns = ['index'])

    except:
        form26as_overall = ''
    

    # final = itrv_pivot.append(form16_pivot.append(form26as_pivot.append(bank_pivot)))
    # final.replace(-99999999999999,np.nan, inplace=True)

    # #table should have 12 or more columns (upper limit = 36). Adjusting number of columns by removing empty columns.
    # if len(final.loc[:,final.apply(lambda x: (pd.notna(x)).any(), axis=0).idxmax():].columns)<12:
    #     final = final.iloc[:-12:]
    # else:
    #     final = final.loc[:,final.apply(lambda x: (pd.notna(x)).any(), axis=0).idxmax():]
        

#output table => final

    
    
    return bank_overall, bank_pivot_head, itr_overall, form16_overall, form26as_overall