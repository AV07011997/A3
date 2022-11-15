import pandas as pd
import numpy as np
import os
import re
import time
import glob
from datetime import datetime as dt
from datetime import timedelta



#global val
#val=''
#def description_combine(x):
#    global val
#    val += str(x[1])
#    if pd.isna(x[0]):
#        return None
#    else:
#        c=val
#        val=''
#        return c

#def cheq_no(x):
#    y=str(x).split('|')
#    if len(y)>1:
#        return y[1]
#    else:
#        return None
    
#def initbr_split(x):
#    if pd.isna(x):
#        return None
#    try:
#        return re.findall('\d+',x.split('|')[1])[0]
#    except:
#        try:
#            return re.findall('\d+',x.split(']')[1])[0]
#        except:
#            try:
#                return re.findall('\d+',x.split('}')[1])[0]
#            except:
#                return None

#def deb_cred(x):
#    if pd.isna(x):
#        return None
#    else:
#        x=str(x)
#        x=x.replace('.','')
#        x=x.replace(',','')
#        a = re.findall(r'\d+', x)[0]
#        a = a[:-2] + '.' + a[-2:]
#        return a
        
#def balance_split(x):
#    if pd.isna(x):
#        return None
#    else:
#        x=str(x)
#        x=x.replace(',','')
#        x=x.replace('.','')
#        a=re.findall(r'\d+', x)[0]
#        a=a[:-2]+'.'+a[-2:]
#        if len(a)>0:
#            return a
#        else:
#            return None

#def date_conv(x):
#    a = re.findall(r'[0-9]{2}[-]{1}[0-9]{2}[-]{1}[0-9]{4}', str(x))
#    if len(a)==0:
#        return None
#    else:
#        return pd.to_datetime(a[0],format='%d-%m-%Y')
    
#def align(tables, file):
#    file = file.split('.pdf')[0]
    
#    df = pd.DataFrame(columns=['Tran Date','Cheq no','Particulars', 'Debit', 'Credit','Balance','Init.Br'])
#    for i in range(len(tables)):
#        if i==0:
#            tables[i] = tables[i].iloc[2:].reset_index(drop=True)
#            if len(tables[i].columns)==5:
#                tables[i]['Particulars'] = tables[i][[0,1]].iloc[1:].apply(description_combine, axis=1)
#                tables[i].drop([2], axis=1, inplace=True)
#                tables[i].dropna(how='all', inplace=True)
#                tables[i]['Init.Br'] = tables[i][4].apply(initbr_split)
#                tables[i]['Cheq no'] = tables[i][0].apply(cheq_no)
#                tables[i].drop([1], axis=1, inplace=True)
#            elif len(tables[i].columns)==8:
#                tables[i].drop([6], axis=1, inplace=True)
#                tables[i]['Cheq no'] = tables[i][1].apply(lambda x: None if pd.isna(x) else re.findall(r'\d+',str(x))[0])
#                tables[i].drop([1], axis=1, inplace=True)
#                tables[i].columns = [0,1,2,3,4,5, 'Cheq no']
#                tables[i]['Particulars'] = tables[i][[0,1]].iloc[1:].apply(description_combine, axis=1)
#                tables[i].drop([1], axis=1, inplace=True)
#                tables[i].dropna(how='all', inplace=True)
#                tables[i]['Init.Br'] = tables[i][5].apply(lambda x: None if pd.isna(x) else re.findall(r'\d+',str(x))[0])
#                tables[i].drop([5], axis=1, inplace=True)       
#            elif len(tables[i].columns)==7:
#                tables[i]['Cheq no'] = tables[i][1].apply(lambda x: None if pd.isna(x) else re.findall(r'\d+',str(x))[0])
#                tables[i].drop([1], axis=1, inplace=True)
#                tables[i].columns = [0,1,2,3,4,5, 'Cheq no']
#                tables[i]['Particulars'] = tables[i][[0,1]].iloc[1:].apply(description_combine, axis=1)
#                tables[i].drop([1], axis=1, inplace=True)
#                tables[i].dropna(how='all', inplace=True)
#                tables[i]['Init.Br'] = tables[i][5].apply(lambda x: None if pd.isna(x) else re.findall(r'\d+',str(x))[0])
#                tables[i].drop([5], axis=1, inplace=True)
#        else:
#            tables[i]['Particulars'] = tables[i][[0,1]].apply(description_combine, axis=1)
#            tables[i].drop([1], axis=1, inplace=True)
#            tables[i].dropna(how='all', inplace=True)
#            tables[i]['Init.Br'] = tables[i][5].apply(lambda x: None if pd.isna(x) else re.findall(r'\d+',str(x))[0])
#            tables[i]['Cheq no'] = tables[i][0].apply(cheq_no)
#            tables[i].drop([5], axis=1, inplace=True)
#        tables[i]['Debit'] = tables[i][2].apply(deb_cred)
#        tables[i]['Credit'] = tables[i][3].apply(deb_cred)
#        tables[i]['Balance'] = tables[i][4].apply(balance_split)
#        tables[i]['Tran Date'] = tables[i][0].apply(date_conv)
#        tables[i].drop([0,2,3,4], axis=1, inplace=True)
#        tables[i].dropna(how='all', inplace=True)
#        tables[i] = tables[i].reset_index(drop=True)
#        tables[i] = tables[i][['Tran Date','Cheq no','Particulars', 'Debit', 'Credit','Balance','Init.Br']]
#        df = df.append(tables[i])
#    df.reset_index(drop=True, inplace=True)
#    df.drop(df[df['Tran Date'].isna()].index, inplace=True)
#    df.reset_index(drop=True, inplace=True)
#    df.to_csv('./Desktop/Source/{}_v2.csv'.format(file), index=False)
#    return df

from decimal import Decimal
def v2_transform_qc_hdfc(dataframe):
    try:
        df2 = dataframe
        
        df = df2.copy()
        df.rename(columns={'Date': 'Txn Date', 'Narration':'Description', 'Withdrawal Amt.':'Debit', 'Deposit Amt.':'Credit', 'Closing Balance':'Balance'}, inplace=True)
        df = df[['Txn Date', 'Description', 'Debit', 'Credit', 'Balance']]
        df['F_Dt1'] = 0
        df['F_Dt2'] = -1
        df['F_Invalid_Desc'] = 0
        df['F_Date'] = 0
        regex = re.compile('[@_!#$%^&*(),=\-<>?/\|}.\]\[{~:+]')
        df['Description'].replace(to_replace='', value=np.nan, inplace=True)
        df['Txn Date'].replace(to_replace='', value=np.nan, inplace=True)
        df['F_Dt1'].loc[df[df['Txn Date'].isnull()].index.to_list()] = 1
        df['F_Invalid_Desc'].loc[df[df.Description.isnull()].index.to_list()] = 1
        sign_desc = [0 if regex.search(str(i).strip()[:1]) == None else 1 for i in df['Description']]
        small_desc = [1 if len(str(i).strip())<4 else 0 for i in df['Description']]
        df['F_Invalid_Desc'] = df['F_Invalid_Desc'] + small_desc + sign_desc
        df['F_Invalid_Desc'] = [1 if i>0 else i for i in df['F_Invalid_Desc']]
        df['Date']=''
        df['Txn Date'] = df['Txn Date'].apply(lambda x : pd.to_datetime(x, errors='raise', dayfirst=True).date())
    
        for i in range(len(df)):
            try:
                df['Date'][i] = pd.to_datetime(df['Txn Date'][i], errors='raise', dayfirst=True).date()
                df['F_Dt2'][i] += 1
               
            except:
                df['Date'][i] = pd.NaT
                df['F_Dt2'][i] += 2
        l=0
        if df['Txn Date'][0]>df['Txn Date'][len(df)-1]:
            df = df.iloc[::-1]
            l=1

        df['F_Dt_Seq'] = 0
        df['F_Future_Dt'] = 0
        df['F_Diff_Year'] = 0
        for i in range(len(df)-1):
            try:
                if df['Date'][i]>df['Date'][i+1]:
                    df['F_Dt_Seq'][i+1] = 1
            except:
                df['F_Dt_Seq'][i+1] = 1

        df['F_Diff_Year'] = [1 if (dt.now().date() - i)/timedelta(days=365)>1 else 0 for i in df['Date']]
        df['F_Future_Dt'] = [1 if dt.now().date()<i else 0 for i in df['Date']]
        df['Ascending'] = df['Date'].sort_values(ascending=True).reset_index(drop=True)
        df['Descending'] = df['Date'].sort_values(ascending=False).reset_index(drop=True)
        df['Order1'] = df.apply(lambda x: 1 if x['Date']!=x['Ascending'] else 0, axis=1)
        df['Order2'] = df.apply(lambda x: 1 if x['Date']!=x['Descending'] else 0, axis=1)

        df['F_Date'] = df.apply(lambda x: 1 if (x['F_Dt1'] + x['F_Dt2'] + x['F_Dt_Seq'] + x['F_Future_Dt'] + x['F_Diff_Year']) > 0 else 0, axis=1)
        df.drop(['F_Dt1', 'F_Dt2', 'F_Dt_Seq', 'F_Diff_Year', 'F_Future_Dt'], axis=1, inplace=True)
        
        df['Credit'] = df['Credit'].astype(str)
        df['Credit'] = df['Credit'].apply(lambda x: Decimal(x.replace(',','')))

        df['Debit'] = df['Debit'].astype(str)
        df['Debit'] = df['Debit'].apply(lambda x: Decimal(x.replace(',','')))

        df['Balance'] = df['Balance'].astype(str)
        df['Balance'] = df['Balance'].apply(lambda x: Decimal(x.replace(',','')))
        
        df['F_Bal_Deb_Cred'] = 1

        for i in range(len(df['Txn Date'])):
            if str(df['Credit'][i]) == '0.0' or str(df['Credit'][i]) == '0.00':
                df['Credit'][i] = 'NaN'
            if str(df['Debit'][i]) == '0.0' or str(df['Debit'][i]) == '0.00':
                df['Debit'][i] = 'NaN'

        for i in range(1,len(df['Txn Date'])):
            if str(df['Debit'][i]) == 'NaN':
                cr = df['Balance'][i-1] + df['Credit'][i]

                if cr == df['Balance'][i]:
                    df['F_Bal_Deb_Cred'][i] = 0
                else:
                    df['F_Bal_Deb_Cred'][i] = 1

            if str(df['Credit'][i]) == 'NaN':
                cr = df['Balance'][i-1] - df['Debit'][i]

                if cr == df['Balance'][i]:
                    df['F_Bal_Deb_Cred'][i] = 0
                else:
                    df['F_Bal_Deb_Cred'][i] = 1

            if str(df['Credit'][i]) != 'NaN' and str(df['Debit'][i]) != 'NaN':
                df['F_Bal_Deb_Cred'][i] = 2

            if str(df['Credit'][i]) == 'NaN' and str(df['Debit'][i]) == 'NaN':
                df['F_Bal_Deb_Cred'][i] = 2

        df['F_Bal_Deb_Cred'][0] = 0  
        df.drop(['Date', 'Ascending', 'Descending'], axis=1, inplace=True)
    
        if l==1:
            df = df.iloc[::-1]

        df2['F_Date'] = df['F_Date']
        df2['F_Invalid_Desc'] = df['F_Invalid_Desc']
        df2['F_Bal_Deb_Cred'] = df['F_Bal_Deb_Cred']
        df2['Order1'] = df['Order1']
        df2['Order2'] = df['Order2']
        tot_flag = (df['F_Date'].sum().sum() + df['F_Invalid_Desc'].sum() + df['F_Bal_Deb_Cred'].sum())
        grade=''
        if tot_flag == 0:
            grade = 'A'
        elif tot_flag<=6:
            grade = 'B'
        else:
            grade = 'C'
        
        print('Passed Date Test : ', (~(df[df['F_Date']==1].any()['F_Date']) & (~(df[df['Order1']==1].any()['Order1'] & df[df['Order2']==1].any()['Order2']))))
        print('Passed Description Test : ', ~(df[df['F_Invalid_Desc']==1].any()['F_Invalid_Desc']))
        print('Passed Invalid Debit/Credit/Balance Test : ', ~(df['F_Bal_Deb_Cred'].sum()>0))
        print('Total Transactions : ', len(df))
        print('Total Flags : ', tot_flag)
        print('Grade : ', grade)
        status_qc = ((~(df[df['F_Date']==1].any()['F_Date'])) & (~df[df['F_Invalid_Desc']==1].any()['F_Invalid_Desc']) & (~df[df['Order1']==1].any()['Order1'] & df[df['Order2']==1].any()['Order2']) & (~(df['F_Bal_Deb_Cred'].sum()>0)))
        if  status_qc:
            print('All OK. Push Forward.')
            return 'ok'
        else:
            print('Failed test. Send for human review.')
            return 'failed'
    except Exception as e:
        print(e)
    #print('*****************************')
    #df.drop(['Order1', 'Order2'], axis=1, inplace=True)
    #df2.drop(['Order1', 'Order2'], axis=1, inplace=True)

    
    #return (status_qc, df, df2)

#********************Alignment of Statement
#t=time.time()
#sp = './Desktop/Digitisation/Bank Statements/Scanned/Axis' #location where pdf files are kept
#files = [f for f in os.listdir(sp) if f.endswith('_out.pdf')]
#for f in files[:1]:
#    path = os.path.join(sp, f)
#    print(path)
#    tables = tabula.read_pdf(path, pages='all', silent=True, pandas_options={'header': None})
#    df = align(tables, f)
#print("--- %s seconds ---" % (time.time() - t))
##********************QC of Statement

#i=0
#while i<100:
#    t=time.time()
#    i+=1
#    sp = './Desktop/Digitisation/Bank Statements/Scanned/Axis'
#    src = './Desktop/Source'
#    dstp = './Desktop/Pass'#kept here if QC test passed
#    dstf = './Desktop/Fail'#kept here if QC test failed
#    f_v2 = [i for i in os.listdir(src) if os.path.isfile(os.path.join(src,i)) and i.endswith('_v2.csv')]
#    f_v3 = [f.replace('_v2.csv', '_v3.csv') for f in f_v2]
#    path = [i for i in os.listdir(sp) if i.endswith('_out.pdf') and i.split('.pdf')[0] in ([f.split('_v2.csv')[0] for f in f_v2])]
    
#    if len(f_v2)>0:
#        for f2, f3, p in zip(f_v2, f_v3, path):
#            result = v2_transform_qc(os.path.join(src,f2))
#            if result[0] == True:
#                result[1].to_csv(os.path.join(dstp, f3), index=False)
#                result[2].to_csv(os.path.join(dstp, f2), index=False)
#                shutil.move(os.path.join(sp, p), dstp)    
#            else:
#                result[1].to_csv(os.path.join(dstf, f3), index=False)
#                result[2].to_csv(os.path.join(dstf, f2), index=False)
#                shutil.move(os.path.join(sp, p), dstf)
#            os.remove(os.path.join(src, f2))
#        print("--- %s seconds ---" % (time.time() - t))
#    else:
#        continue
#*******************************

