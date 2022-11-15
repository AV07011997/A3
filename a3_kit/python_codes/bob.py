import tabula
import pandas as pd
import numpy as np
from datetime import datetime as dt

#function to align the dataframes and extracting desired information
def bob_digitization(pdf_path, pdf_password):
    
    col2str = {'dtype': str}
    file_name=pdf_path.split('\\')[-1][:-4]
    passwrd=''
    
    try:
        #if file is encrypted but with empty password
        tables = tabula.read_pdf(pdf_path, password=passwrd, pages='all', pandas_options = col2str)
    except:
        passwrd = pdf_password
        tables = tabula.read_pdf(pdf_path, password=passwrd, pages='all', pandas_options = col2str)
    #return if image based (scanned) pdf
    if len(tables)==0:
        print("This is an image-based statement, hence, cannot be digitized here")
        return
    
    df = pd.DataFrame(columns=['Txn Date', 'Description', 'Debit', 'Credit', 'Balance', 'Cheque Number'])
    tables[0].rename(columns={'Unnamed: 0': 'value'}, inplace=True)
    
    #extracting account information (name/number)
    acct_name = tables[0].set_index('Account Statement').to_dict(orient='records')[0]['value']
    acct_no = tables[0].set_index('Account Statement').to_dict(orient='records')[1]['value']
    acct_no = "'"+str(acct_no)+"'"
    
    for i in range(1,len(tables)):
        tables[i].dropna(how='all', inplace=True)
        #standarising date, debit,credit and balance columns
        tables[i]['Txn Date'] = [dt.strftime(pd.to_datetime(x, dayfirst=True),"%d/%m/%Y") for x in tables[i]['Date']]
        tables[i]['Debit'] = ["{:,.2f}".format(float(x.replace(',',''))) if x!='-' else None for x in tables[i]['Debit']]
        tables[i]['Credit'] = ["{:,.2f}".format(float(x.replace(',',''))) if x!='-' else None for x in tables[i]['Credit']]
        tables[i]['Balance'] = ["{:,.2f}".format(float(x[:-2].replace(',',''))) for x in tables[i]['Balance']]
        tables[i]['Cheque\rNo'] = [str(x).split('.')[0] for x in tables[i]['Cheque\rNo']]
        tables[i]['Cheque\rNo'].replace('nan', np.nan, inplace=True)
        tables[i].drop(['S.No', 'Date'], inplace=True, axis=1)
        tables[i].rename(columns={'Cheque\rNo':'Cheque Number'}, inplace=True)
        tables[i]=tables[i][['Txn Date', 'Description', 'Debit', 'Credit','Balance', 'Cheque Number']]
        
        #appending into one super dataframe
        df = df.append(tables[i])
        df.reset_index(drop=True, inplace=True)
        
    df['Account Name'] = acct_name
    df['Account Number'] = acct_no
    
    #standardising csvs according to standard schema
    master_table2 = df.copy()
    del df
    master_table2 = master_table2[['Txn Date', 'Description', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number', 'Cheque Number']]
    master_table2['Txn Date'] = [dt.strftime(pd.to_datetime(x,dayfirst=True),"%d/%m/%Y") for x in master_table2['Txn Date']]
    last_trans_date = master_table2['Txn Date'].iat[-1]
    
    #master_table2.to_csv("{}/{}_{}_{}.csv".format(out_path,file_name, acct_no, last_trans_date),index=False)



    ## NOW PERFORMING FEW LOGICAL CHECKS TO CHECK DIGITIZATION HAS NO ISSUE
    
    df = pd.DataFrame(master_table2)
    column_names=['Statement_name','Wrong Credit', 'Wrong Debit', 'Remark']
    result=pd.DataFrame(index=[1],columns=column_names)
    
    if df['Credit'].dtype =='O':
        df['Credit_changed'] = (df['Credit'].str.replace(',','')).astype(float)
    else:
        df['Credit_changed']= df['Credit'].astype(float)
    if df['Debit'].dtype =='O':
        df['Debit_changed'] = (df['Debit'].str.replace(',','')).astype(float)
    else:
        df['Debit_changed']= df['Debit'].astype(float)
    if df['Balance'].dtype =='O':
        df['Balance_changed'] = (df['Balance'].str.replace(',','')).astype(float)
    else:
        df['Balance_changed']= df['Balance'].astype(float)
        
    df['Balance_changed'] = df['Balance_changed'].replace(0,np.nan)
    df['Debit_changed'] = df['Debit_changed'].replace(0,np.nan)
    df['Credit_changed'] = df['Credit_changed'].replace(0,np.nan)        
    
    col_credit=df.columns.get_loc('Credit_changed')
    col_debit=df.columns.get_loc('Debit_changed')
    col_bal=df.columns.get_loc('Balance_changed')
    col_desc=df.columns.get_loc('Description')
    
    for i in range(1,len(df)):
        #check 1 having, both debit and credit values
        if  (pd.isna(df.iloc[i,col_debit]) and pd.isna(df.iloc[i,col_credit])) or (pd.notna(df.iloc[i,col_debit]) and pd.notna(df.iloc[i,col_credit])) :
            data=pd.DataFrame({'Statement_name':file_name,'Wrong Credit': (i+2),'Wrong Debit':(i+2), 'Remark':'Only one of Debit/Credit should be filled'},index=[0])
            result=pd.concat([result,data])                
    
        #check 2, balance check
        else:
            #debited
            if pd.isna(df.iloc[i,col_credit]):
                if df.iloc[i,col_debit]>0:
                    if df.iloc[i-1,col_bal]<df.iloc[i,col_bal]:
                        data=pd.DataFrame({'Statement_name':file_name,'Wrong Credit': np.nan,'Wrong Debit':(i+2), 'Remark':'Balance should be less than previous since debit>0'},index=[0])
                        result=pd.concat([result,data])
                else:
                    if df.iloc[i-1,col_bal]>df.iloc[i,col_bal]:
                        data=pd.DataFrame({'Statement_name':file_name,'Wrong Credit': np.nan,'Wrong Debit':(i+2),'Remark':'Balance should be more than previous since debit<0'},index=[0])
                        result=pd.concat([result,data])
                  
    
            #credited
            elif pd.isna(df.iloc[i,col_debit]):
                if df.iloc[i,col_credit]>0:
                    if df.iloc[i-1,col_bal]>df.iloc[i,col_bal]:
                        data=pd.DataFrame([{'Statement_name':file_name,'Wrong Credit': (i+2),'Wrong Debit':np.nan,'Remark':'Balance should be more than previous since credit>0'}],index=[0])
                        result=pd.concat([result,data])
                else:
                    if df.iloc[i-1,col_bal]<df.iloc[i,col_bal]:
                        data=pd.DataFrame([{'Statement_name':file_name,'Wrong Credit': (i+2),'Wrong Debit':np.nan,'Remark':'Balance should be less than previous since credit<0'}],index=[0])
                        result=pd.concat([result,data])    
    
    result = result.dropna(how='all')
    
    # will continue only if 'result' is an empty dataframe
    if len(result)==0:
        pass
    else:
        print("\nThere are issues found after the Logical checks.\nThe digtitized output and the issues have been exported in CSVs.\n")
        # master_table2.to_csv("{}/{}_Digitized.csv".format(out_path,file_name),index=False)        
        # result.to_csv("{}/{}_LogicalChecks.csv".format(out_path,file_name),index=False)
        return



    # NOW THE ENTITY EXTRACTION PART

    def get_printable(s):
        res=''.join([i for i in s if i.isprintable()])
        return res
    
    
    master_df = pd.DataFrame(master_table2)
    
    master_df["Description"]=master_df["Description"].str.lstrip()
    master_df['Description']=[i  if i.isprintable() else get_printable(i) for i in master_df['Description'].astype(str)]
    pd.options.mode.chained_assignment = None
    
    #sms chg
    try:
        df1=master_df[(master_df['Description'].str.contains('SMS'))]
        df1['sub-mode']='SMS Charges'
        df1['source_of_trans']='Automated'
        df1['mode']='Charges'
        df1['entity-bank']="NA"
        df1['entity']="NA"
    except:
        pass
    
    #salary
    try:
        df2 =master_df[master_df["Description"].str.contains("SALARY")]
        df2['sub-mode']='Salary'
        df2['source_of_trans']='Automated'
        df2['mode']='Salary'
        df2['entity-bank']="NA"
        df2['entity']="NA"
    except:
        pass
    
    #atm cash
    try:
        df3=master_df[(master_df['Description'].str.contains('ATM/CASH'))]
        df3['sub-mode']='ATM'
        df3['source_of_trans']='Self Initiated'
        df3['mode']='Cash'
        df3['entity-bank']="NA"
        df3['entity']="NA"
    except:
        pass
    
    #ach debit
    try:
        df4=master_df[(master_df['Description'].str.contains('ACH Debit'))]
        df4[['sub-mode','entity','num']]=df4['Description'].str.split('/',expand=True)
        df4['source_of_trans']='Automated'
        df4['mode']='NA'
        df4['entity-bank']="NA"
        df4['entity']=np.where(df4['entity'].isna(),"NA",df4['entity'])
        df4.drop(['num'],axis=1,inplace=True)
    except:
        pass
    
    
    #upi
    try:
        df5=master_df[(master_df['Description'].str.contains('UPI'))]
        df5['new']=df5['Description'].str.rsplit('/')
        df5['sub-mode']=df5.new.apply(lambda x:x[0])
        df5['entity']=df5.new.apply(lambda x: x[-1] if len(x)==5 else x[-2])
        df5['source_of_trans']='Self Initiated'
        df5['mode']='Mobile App'
        df5['entity-bank']="NA"
        df5.drop(['new'],axis=1,inplace=True)
    except:
        pass
    
    #neft
    try:
        df6=master_df[master_df['Description'].str.contains('NEFT')]
        df6['source_of_trans']='Self Initiated'
        df6['mode']='Net Banking'
        df6['entity-bank']="NA"
        df6[['sub-mode','num','entity']]=df6['Description'].str.split('-',expand=True)
        df6.drop(['num'],axis=1,inplace=True)
    except:
        pass
    
    #imps
    try:
        df7=master_df[(master_df['Description'].str.contains('IMPS'))]
        df7['new']=df7['Description'].str.split('/')
        df7['sub-mode']="IMPS"
        df7['entity']=df7['new'].apply(lambda x: x[-1] if len(x)==3 else x[-2])
        df7['source_of_trans']='Self Initiated'
        df7['mode']='Net Banking'
        df7['entity-bank']="NA"
        df7.drop(['new'],axis=1,inplace=True)
    except:
        pass
    
    #by cash to cash
    try:
        df8=master_df[(master_df['Description'].str.contains('BY CASH')) | (master_df['Description'].str.contains('TO CASH'))]
        df8['sub-mode']='Cash'
        df8['source_of_trans']='Self Initiated'
        df8['mode']='Cash'
        df8['entity-bank']="NA"
        df8['entity']="NA"
    except:
        pass
    
    #MBK
    try:
        df9=master_df[(master_df['Description'].str.contains('MBK'))]
        df9['sub-mode']="NA"
        df9['entity']="NA"
        df9['source_of_trans']='Self Initiated'
        df9['mode']='Mobile App'
        df9['entity-bank']="NA"
    except:
        pass
    
    #to transfer
    try:
        df10=master_df[(master_df['Description'].str.contains('To Transfer'.upper()))]
        df10['sub-mode']="Transfer"
        df10['entity']="NA"
        df10['source_of_trans']='Self Initiated'
        df10['mode']="NA"
        df10['entity-bank']="NA"
    except:
        pass
    
    #cheque
    try:
        df11 =master_df[(master_df["Description"].str.contains("MICR")) & (master_df["Description"].str.contains("CTS"))]
        df11['sub-mode']='CLEARING CHEQUE'
        df11['source_of_trans']='Self Initiated'
        df11['mode']='Cheque'
        df11['entity-bank']="NA"
        df11['entity']="NA"
    except:
        pass
    
    #premium
    try:
        df12 =master_df[(master_df["Description"].str.contains("Premium"))]
        df12['sub-mode']='Premium'
        df12['source_of_trans']='Automated'
        df12['mode']='Insurance'
        df12['entity-bank']="NA"
        df12['entity']="NA"
    except:
        pass
    
    #prcr
    try:
        df13=master_df[(master_df['Description'].str.contains('PRCR'))]
        df13['sub-mode']='Debit card'
        df13['source_of_trans']='Self Initiated'
        df13['mode']='Card'
        df13['entity-bank']="NA"
        df13['new']=df13['Description'].str.split('/')
        df13['entity']=df13['new'].apply(lambda x:x[-2])
        df13.drop(['new'],inplace=True,axis=1)
    except:
        pass
    
    #pgdr ==> wallets
    try:
        df14=master_df[(master_df['Description'].str.contains('PGDR'))]
        df14['sub-mode']='Wallets'
        df14['source_of_trans']='Self Initiated'
        df14['mode']='Mobile App'
        df14['entity-bank']="NA"
        df14['entity']="NA"
    except:
        pass
    
    #BNA CDAR
    try:
        df15=master_df[(master_df['Description'].str.contains('BNA'))]
        df15['sub-mode']='BNA'
        df15['source_of_trans']='Self Initiated'
        df15['mode']='Deposit'
        df15['entity-bank']="NA"
        df15['entity']="NA"
    except:
        pass
    
    #charges
    try:
        df16=master_df[(master_df['Description'].str.contains('Charges'.upper()))]
        df16['sub-mode']='Charges'
        df16['source_of_trans']='Automated'
        df16['mode']='Charges'
        df16['entity-bank']="NA"
        df16['entity']="NA"
    except:
        pass
    
    #dd
    try:
        df17=master_df[(master_df['Description'].str.startswith('By DD'))]
        df17['sub-mode']="DD"
        df17['entity']="NA"
        df17['source_of_trans']='Self Initiated'
        df17['mode']='Demand Draft'
        df17['entity-bank']="NA"
    except:
        pass
    
    #returned charges
    try:
        df18=master_df[(master_df['Description'].str.startswith('Returned'.upper()))]
        df18['sub-mode']="Failed Txn"
        df18['entity']="NA"
        df18['source_of_trans']='Automated'
        df18['mode']="NA"
        df18['entity-bank']="NA"
    except:
        pass
    
    
    t1=pd.DataFrame()
    t1 = pd.concat([df1,df2,df3,df4,df5,df6,df7,df8,df9,df10,df11,df12,df13,df14,df15,df16,df17,df18], axis=0) #axis =0 for vertically appending
    
    t2 = master_df[~master_df["Description"].isin(t1["Description"])]
    t2['mode']='Others'
    t2['entity']="NA"
    t2['source_of_trans']="NA"
    t2['entity-bank']="NA"
    t2['sub-mode']="NA"
    
    final = pd.concat([t1,t2], axis=0)
    final = final.sort_index()
    final.rename(columns={'sub-mode':'sub_mode','entity-bank':'entity_bank'}, inplace=True)    
    final = final[['Txn Date', 'Description', 'Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number','mode','entity','source_of_trans','entity_bank','sub_mode']]
    
    return final
    #exporting the file
    # final.to_csv("{}/{}_{}_{}.csv".format(out_path,file_name, acct_no, last_trans_date),index=False)


# try:
#     bob_digitization(r"D:\D Drive\RAJAT\UW kit\Bank statements\STATEMENT FROM MITHUN\bank of baroda\harpreet singh Banking.pdf",
#                      r"D:\D Drive\RAJAT\UW kit\Bank statements\STATEMENT FROM MITHUN\bank of baroda\digitised")
# except:
#     print("\nThis statement cannot be digitised\n")