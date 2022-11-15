import tabula
import pandas as pd
import numpy as np
from datetime import datetime as dt   

def standard_chartered_digitization(pdf_path,out_path):
    # function to merge the Description column
    def concat_desc( df, start_row):
        for j in range(start_row, len(df)):
            prev_row=j-1
            while j<len(df) and pd.isna(df['Balance'][j]):
                df['Description'][prev_row]=str(df['Description'][prev_row])+" "+str(df['Description'][j])
                j+=1
        df.dropna(subset=['Balance'],inplace=True)
        df.reset_index(drop=True,inplace=True)
        return df

    col2str = {'dtype': str}

    def old_format(tables,master_table2):
        for i in range(len(tables)):
            df_copy=tables[i].copy()
            #identifying start of trasaction inside datframe
            header_row=-1
            for j in range(len(df_copy)):
                if type(df_copy.iloc[j,0])==str and df_copy.iloc[j,0]=='Date':
                          header_row=j
                          #date_col=0
                          df_copy=df_copy.rename(columns={df_copy.keys()[0]: 'Date'})
                          break
            #if dataframe is valid; identifying the columns and renaming them
            if header_row!=-1:
                for k in range(len(df_copy.columns)):
                    if type(df_copy.iloc[header_row,k])==str and df_copy.iloc[header_row,k]=='Balance':
                        df_copy=df_copy.rename(columns={df_copy.keys()[k]: 'Balance'})
                    if type(df_copy.iloc[header_row,k])==str and df_copy.iloc[header_row,k].startswith('Cheque'):
                        df_copy=df_copy.rename(columns={df_copy.keys()[k]: 'Cheque Number'})
                    if type(df_copy.iloc[header_row,k])==str and df_copy.iloc[header_row,k].startswith('Description'):
                        df_copy=df_copy.rename(columns={df_copy.keys()[k]: 'Description'})
                    if type(df_copy.iloc[header_row,k])==str and df_copy.iloc[header_row,k].find('Deposit')!=-1:
                        df_copy=df_copy.rename(columns={df_copy.keys()[k]: 'Deposit'})
                    if type(df_copy.iloc[header_row,k])==str and df_copy.iloc[header_row,k].startswith('Withdrawal'):
                        df_copy=df_copy.rename(columns={df_copy.keys()[k]: 'Withdrawal'})
                if len(df_copy.columns)==5 or len(df_copy.columns)==6:
                        #removing dates from descriptions
                        for j in range(len(df_copy)):
                            if not pd.isna(df_copy['Date'][j]):
                              df_copy['Description'][j]=df_copy['Description'][j][10:]
                #to handle one exception in pdf - 5-unlocked table[1]
                if len(df_copy.columns)==9:
                      df_copy['Balance']=df_copy.iloc[1:,8]
                      df_copy.drop([df_copy.columns[-1]],inplace=True,axis=1)
                df_copy=concat_desc(df_copy,header_row+2)
                    #dropping the extra columns and framing the final df
                if len(df_copy.columns)>7:
                      df_copy.dropna(axis=1,how='all',inplace=True)
                if len(df_copy.columns)==7:
                      df_copy.drop(df_copy.columns.difference(['Date','Balance','Description','Cheque Number','Deposit','Withdrawal']),axis=1, inplace=True)
                    #adding dates to trasactions of same day
                    #here the number columns will either be 6 or 7
                df_copy['Date']=df_copy[['Date']].fillna(method='pad')
                master_table2=pd.concat([master_table2,df_copy[1:]])
        return master_table2

    def new_format(path,passcode):
        master_table=pd.DataFrame()
        tables = tabula.read_pdf(path,stream=True,password=passcode,area=[207,27,688,569],pages='all',columns=[71,113,328,371,437,507], pandas_options = col2str)
        for i in range(len(tables)) :
           df_copy=tables[i].copy()
           if df_copy.columns[0] != 'Date':
              df_copy.loc[max(df_copy.index)+1,:] = None
              df_copy = df_copy.shift(1,axis=0)
              df_copy.iloc[0] = df_copy.columns
              if len(df_copy.columns) == 7:
                  df_copy.columns = ['Date', 'Value Date', 'Description', 'Cheque','Deposit','Withdrawal','Balance']
           df_copy=concat_desc(df_copy,1)
           #dropping the extra columns and framing the final df
           if len(df_copy.columns)==7:
                df_copy.drop(df_copy.columns.difference(['Date','Balance','Description','Deposit','Withdrawal','Cheque']),axis=1, inplace=True)
            #adding dates to trasactions of same day
            #here the number columns will either be 6 or 7
           df_copy['Date']=df_copy[['Date']].fillna(method='pad')
           master_table=pd.concat([master_table,df_copy[1:]])
        master_table.rename({'Cheque':'Cheque Number'},axis=1,inplace=True)
        return master_table

    file_name=pdf_path.split('\\')[-1][:-4]
    master_table2=pd.DataFrame()
    passcode=''
    try:
        #if file is encrypted but with empty password
        tables = tabula.read_pdf(pdf_path,pages='all',stream=True,password=passcode, pandas_options = col2str)
    except:
        passcode=input("Enter the Password:")
        tables = tabula.read_pdf(pdf_path,pages='all',stream=True,password=passcode, pandas_options = col2str)
    if len(tables)==0:
        print("This is an image-based statement, hence, cannot be digitized here")
        return

    #to oversee the warning to concatenate descriptions/narrations
    pd.options.mode.chained_assignment = None
    check_df=tables[0].copy()
    for a in range(len(check_df)):
        same=0
        if type(check_df.iloc[a,0])==str and check_df.iloc[a,0].find('Date   Value Description')!=-1:
            same =-1
            master_table2=new_format(pdf_path,passcode)
            break
    if same==0:
            same=-2
            master_table2=old_format(tables,master_table2)
    master_table2=master_table2[master_table2['Description']!="BALANCE FORWARD"]
    master_table2.reset_index(inplace=True,drop=True)  
    if (not(master_table2.iloc[-1,2]!=master_table2.iloc[-1,2]) and not(master_table2.iloc[-1,3]!=master_table2.iloc[-1,3])):
        master_table2=master_table2.iloc[:-1]
    if (same==-2):
        account_name=tables[0].iloc[1,tables[0][tables[0].columns[1]].first_valid_index()]
        for i in range(len(tables[0])):
            for j in range(len(tables[0].columns)):
                if tables[0].iloc[i,j]=="ACCOUNT NO. :":
                    account_no="'{}'".format(tables[0].iloc[i,j+1])
                    break
    if same==-1:
        account_info = tabula.read_pdf(pdf_path,stream=True, password=passcode, area=[51,27,207,568], pages='1', pandas_options={'header': None,'dtype': str},columns=[315,404])
        account_detail= account_info[0].copy()
        for x in range(len(account_detail)):
           if type(account_detail.iloc[x,1])==str and account_detail.iloc[x,1]=='ACCOUNT NO:':
             account_no=account_detail.iloc[x,2]
             account_name= account_detail.iloc[0,0]
           if type(account_detail.iloc[x,1])==str and account_detail.iloc[x,1]=='STATEMENT DATE :':
             statement_date=account_detail.iloc[x,2]
             year=account_detail.iloc[x,2][7:12]
             master_table2['Date']=master_table2['Date'].apply(lambda x:'{} {}'.format(x,year))
    master_table2=master_table2[master_table2["Description"]!="TOTAL"]
    master_table2=master_table2[~master_table2["Description"].str.contains("Description nan")]
    master_table2=master_table2[~master_table2["Description"].str.contains("Balance Brought Forward")]
    master_table2.reset_index(inplace=True,drop=True)
    master_table2['Account Name'] = account_name
    master_table2['Account Number'] = account_no
    master_table2.rename(columns={'Date':'Txn Date','Withdrawal':'Debit','Deposit':'Credit'}, inplace=True)
    master_table2 = master_table2[['Txn Date', 'Description','Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number']]
    master_table2['Txn Date'] = [dt.strftime(pd.to_datetime(x,dayfirst=True),"%d-%m-%Y") for x in master_table2['Txn Date']]
    last_trans_date = master_table2['Txn Date'].iat[-1]
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
        print("go ahead")
        pass
    else:
        print("\nThere are issues found after the Logical checks.\nThe digtitized output and the issues have been exported in CSVs.\n")
        master_table2.to_csv(r"{}\{}_Digitized.csv".format(out_path,file_name),index=False)        
        result.to_csv(r"{}\{}_LogicalChecks.csv".format(out_path,file_name),index=False)
        return
    def get_printable(s):
        res=''.join([i for i in s if i.isprintable()])
        return res
    master_df=df
    master_df['Description']=master_df['Description'].str.lstrip()
    master_df['Description']=[i  if i.isprintable() else get_printable(i) for i in master_df['Description'].astype(str)]
    pd.options.mode.chained_assignment = None
        #gst
    try:
        df1=master_df[(master_df['Description'].str.contains('GST'))]
        df1['sub_mode']='GST'
        df1['source_of_trans']='Automated'
        df1['mode']='Tax'
        df1['entity_bank']='NA'
        df1['entity']='NA'
    except:
        pass
    
        #balance forward
    try:
        df2=master_df[master_df['Description'].str.contains('Balance Forward'.upper())]
        df2['sub_mode']='NA'
        df2['source_of_trans']='Automated'
        df2['mode']='Tax'
        df2['entity_bank']='NA'
        df2['entity']='NA'
    except:
        pass
        
        #sms charges
    try:
        df3=master_df[(master_df['Description'].str.contains('SMS TRANSACTION ALERT CHARGES'))]
        df3['sub_mode']='SMS Charges'
        df3['source_of_trans']='Automated'
        df3['mode']='Charges'
        df3['entity_bank']='NA'
        df3['entity']='NA'
    except:
        pass
        
        #emi
    try:
        df4=master_df[(master_df['Description'].str.contains('LOAN REPAYMENT'))]
        df4['sub_mode']='EMI'
        df4['source_of_trans']='Automated'
        df4['mode']='NA'
        df4['entity_bank']='NA'
                                                #    df4['entity']='{}'.join([j for j in [i for i in df4['Description'].str[14:]] if not j.isdigit()])
        df4['entity']=df4['Description'].str[22:]
    except:
        pass
        
        
        #credit interest
    try:
        df5 =master_df[(master_df['Description'].str.contains('CREDIT OF INTEREST')) | (master_df['Description'].str.contains('CREDIT INTEREST'))]
        df5['sub_mode']='CREDIT INTEREST'
        df5['source_of_trans']='Automated'
        df5['mode']='Interest'
        df5['entity_bank']='NA'
        df5['entity']='NA'
    except:
        pass
        
        #Cheque withdrawal
    try:
        df6 =master_df[master_df['Description'].str.contains('CHQ WITHDRAWAL')]
        df6['sub_mode']='Cheque withdrawal'
        df6['source_of_trans']='Self Initiated'
        df6['mode']='Cheque'
        df6['entity_bank']='NA'
        df6['entity']=df6['Description'].str[32:]
    except:
        pass
        
        #salary
    try:
        df7 =master_df[master_df['Description'].str.contains('SALARY')]
        df7['sub_mode']='Salary'
        df7['source_of_trans']='Automated'
        df7['mode']='NA'
        df7['entity_bank']='NA'
        df7['entity']='NA'
    except:
        pass
        
        #payment gateways
    try:
        df8 =master_df[master_df['Description'].str.startswith('PAYMENT GATEWAY')]
        df8['sub_mode']='Card'
        df8['source_of_trans']='Self Initiated'
        df8['mode']='Card'
        df8['entity_bank']='NA'
        df8['entity']='NA'
    except:
        pass

        #PURCHASE
        
    try:
        df12 =master_df[master_df['Description'].str.startswith('PURCHASE')]
        df12['new']=df12['Description'].str.split('E ')
        df12['sub_mode']='Debit Card'
        df12['source_of_trans']='Self Initiated'
        df12['mode']='Card'
        df12['entity_bank']='NA'
        df12['entity'] = df12['new'].apply(lambda x: x[1])
        df12.drop(['new'], axis=1, inplace=True)
        df12['entity'], df12['B'] = df12['entity'].str.split('/', 1).str 
        df12.drop(['B'], axis=1, inplace=True)
        
    except:
        pass
        
    
    #Online Fund Transfer
    
    try:
        df13 =master_df[master_df['Description'].str.startswith('ONLINE')]
        df13=df13[~df13['Description'].str.contains('ONLINE CARD')]
        df13['new']=df13['Description'].str.split('A/C')
        df13['sub_mode']='Mutual Funds'
        df13['source_of_trans']='Automated'
        df13['mode']='Net Banking'
        df13['entity_bank']='NA'
        df13['entity']=df13['new'].apply(lambda x: x[1])
        df13.drop(['new'], axis=1, inplace=True)    
    except:
        pass
    
    
    
    #ATM Withdrawal
    
    
    try:
        df14 =master_df[master_df['Description'].str.startswith('ATM WITHDRAWAL')]
        df14['new']=df14['Description'].str.split('S')
        df14['sub_mode']='Cash Withdrawal'
        df14['source_of_trans']='Self Initiated'
        df14['mode']='Cash'
        df14['entity_bank']='NA'
        df14['entity']='Self'
        df14.drop(['new'], axis=1, inplace=True)
    except:
        pass
    
    #SUPP
    
    try:
        df15 =master_df[master_df['Description'].str.contains('RTGS')]
        df15['new']=df15['Description'].str.split(' RTGS')
        df15['A']=df15['new'].apply(lambda x: x[0])
        df15['no_use'], df15['entity'] = df15['A'].str.split(' ', 1).str
        df15.drop(['A'],axis=1,inplace=True)
        df15.drop(['no_use'],axis=1,inplace=True)
        df15['sub_mode']='RTGS'
        df15['source_of_trans']='Self Initiated'
        df15['mode']='Branch'
        df15['entity_bank']='NA'
        df15.drop(['new'], axis=1, inplace=True)
    except:
        pass
    
    #ibanking
    
    try:
        df16 =master_df[master_df['Description'].str.startswith('IBANKING')]
        df16['new']=df16['Description'].str.split('PAYMENT')
        df16['A']=df16['new'].apply(lambda x: x[0])
        df16['sub_mode'], df16['no_use'] = df16['A'].str.split(' ', 1).str
        df16.drop(['A'],axis=1,inplace=True)
        df16.drop(['no_use'],axis=1,inplace=True)
        df16['source_of_trans']='Self Initiated'
        df16['mode']="Net Banking"
        df16["entity_bank"]="NA"
        df16["E"]=df16["new"].apply(lambda x: x[1])
        df16['E']=df16['E'].str.lstrip()
        df16['F']=df16['E'].str.split(' ')
         
        df16['entity']=df16['F'].apply(lambda x: x[0:4])
        df16.drop(['E'], axis=1, inplace=True)
        df16.drop(['F'], axis=1, inplace=True)
        df16.drop(['new'], axis=1, inplace=True)
        df16['entity']=[' '.join(i) for i in df16['entity']]
        
    except:
        pass
    
    
    
    #NEFT
    
    try:
        df17 =master_df[master_df['Description'].str.contains('NEFT')]
        df17['new']=df17['Description'].str.split(' NEFT')
        df17['sub_mode']='NEFT' 
        df17['A']=df17['new'].apply(lambda x: x[0])
        df17['no_use'], df17['entity'] = df17['A'].str.split(' ', 1).str
        df17.drop(['A'],axis=1,inplace=True)
        df17.drop(['no_use'],axis=1,inplace=True)
        df17['source_of_trans']='Self Initiated'
        df17['mode']="Net Banking"
        df17['entity_bank']='NA'
        df17.drop(['new'], axis=1, inplace=True)       
    except:
        pass
    
    
    # #Cash Pyment
    
    # try:
    #     df18 =master_df[master_df['Description'].str.startswith('CASH')]
    #     df18['new']=df18['Description'].str.split('RTGS')
    #     df18['A']=df18['new'].apply(lambda x: x[0])
    #     df18['no_use'], df18['entity'] = df18['A'].str.split(' ', 1).str
    #     df18.drop(['A'],axis=1,inplace=True)
    #     df18.drop(['no_use'],axis=1,inplace=True)
    #     df18['sub_mode']='RTGS'
    #     df18['source_of_trans']='Self Initiated'
    #     df18['mode']='Branch'
    #     df18["entity_bank"]="NA"
    #     df18.drop(['new'], axis=1, inplace=True)    
    # except:
    #     pass
    
    #IMPS
    
    try:
         df9=master_df[(master_df['Description'].str.startswith('IMPS/P2A'))]
         df9['new']=df9['Description'].str.split('/')
         df9['A']=df9['new'].apply(lambda x: x[3])
         df9['B']=df9['A'].str.split(' ',2)
         df9['entity']=df9['B'].apply(lambda x: x[2])
         df9["entity_bank"]=df9['B'].apply(lambda x: x[1][0:4])
         df9.drop(['A'], axis=1, inplace=True) 
         df9.drop(['B'], axis=1, inplace=True) 
         df9['sub_mode']='IMPS'
         df9['source_of_trans']='Self Initiated'
         df9['mode']='Net Banking'
         df9.drop(['new'], axis=1, inplace=True) 
    except:
        pass
    
    
      #IMPS 2nd version
      
    try:
        df10=master_df[(master_df['Description'].str.startswith('IMPS P2A'))]
        df10['new']=df10['Description'].str.split(' ')
        df10['entity']=df10['new'].apply(lambda x: x[3])
        df10['sub_mode']='IMPS Charges'
        df10['source_of_trans']='Automated'
        df10['mode']='Charges'
        df10["entity_bank"]="NA"
        df10.drop(['new'], axis=1, inplace=True)    
    except:
        pass
    
    
    #Cheque Deposit
    
    try:
        df11=master_df[(master_df['Description'].str.startswith('CHQ DEPOSIT'))]
        df11['new']=df11['Description'].str.split(' ',2)
        df11['entity']=df11['new'].apply(lambda x: x[1])
        df11['sub_mode']='Cheque Deposit'
        df11['source_of_trans']='Self Initiated'
        df11['mode']='Cheque'
        df11["entity_bank"]=df11['new'].apply(lambda x: x[2])
        df11.drop(['new'], axis=1, inplace=True)
        
    except:
        pass
    
    
    #emi verison 2.0
    
    try:
        df19=master_df[(master_df['Description'].str.startswith('LOANREPAYMENT'))]
        df19['new']=df19['Description'].str.split(' ')
        df19['sub_mode']='EMI'
        df19['source_of_trans']='Automated'
        df19['mode']='NA'
        df19['entity_bank']='NA'
        df19["entity"]=df19['new'].apply(lambda x: x[1])
        df19.drop(['new'], axis=1, inplace=True)
    except:
        pass
    
    
    #OTHR
    
    try:
        df20=master_df[(master_df['Description'].str.startswith('OTHR'))]
        df20['new']=df20['Description'].str.split(' ',1)
        df20["new2"]=df20['new'].apply(lambda x: x[1])
        df20['new3']=df20['new2'].str.split('RTGS')
        df20["entity"]=df20['new3'].apply(lambda x: x[0])
        df20["new4"]=df20['new3'].apply(lambda x: x[1])
        df20['new4']=df20['new4'].str.lstrip()
        df20['new5']=df20['new4'].str.split('CHQ')
        df20['sub_mode']='RTGS'
        df20['source_of_trans']='Self Initiated'
        df20['mode']='Branch'
        df20["entity_bank"]=df20['new5'].apply(lambda x: x[0])
        df20.drop(['new'], axis=1, inplace=True)
        df20.drop(['new2'], axis=1, inplace=True)
        df20.drop(['new3'], axis=1, inplace=True)
        df20.drop(['new4'], axis=1, inplace=True)
        df20.drop(['new5'], axis=1, inplace=True)
    except:
        pass
    
    
    
    #IMPS version 3.0
    
    try:
        df21=master_df[(master_df['Description'].str.startswith('RVSL IMPS'))]
        df21['entity']='NA'
        df21['sub_mode']='IMPS Reversal'
        df21['source_of_trans']='Automated'
        df21['mode']='Net Banking'
        df21["entity_bank"]="NA"   
    except:
        pass
    
    
    #Outward Return
    
    try:
        df22=master_df[(master_df['Description'].str.startswith('OUTWARD'))]
        df22['new']=df22['Description'].str.split('-')
        df22['sub_mode']="Reversal"
        df22['A']=df22['new'].apply(lambda x: x[1])
        df22['A']=df22['A'].str.split(':') 
        df22['entity']=df22['A'].apply(lambda x: x[1])
        df22['entity'],df22['B']=df22['entity'].str.split(' ', 1).str
        df22['source_of_trans']='Automated'
        df22['mode']='Cheque'
        df22["entity_bank"]="NA"  
        df22.drop(['A'], axis=1, inplace=True)
        df22.drop(['B'], axis=1, inplace=True)
        df22.drop(['new'], axis=1, inplace=True)
    except:
        pass
    
    
    
    #UPI
    try:
        df23=master_df[(master_df['Description'].str.startswith('UPI'))]
        df23['new']=df23['Description'].str.split('/')
        df23['entity']=df23['new'].apply(lambda x: x[4])
        df23['sub_mode']='UPI'
        df23['source_of_trans']='Self Initiated'
        df23['mode']='Mobile App'
        df23['entity_bank']='NA'
        df23.drop(['new'], axis=1, inplace=True)
        
    except:
        pass
    
    #Online card payment
    try:
        df24=master_df[(master_df['Description'].str.startswith('ONLINE CARD'))]
        df24['new']=df24['Description'].str.split(' ')
        df24['entity']=df24['new'].apply(lambda x: x[5])
        df24['sub_mode']='Card'
        df24['source_of_trans']='Self Initiated'
        df24['mode']='Card'
        df24['entity_bank']='NA'
        df24.drop(['new'], axis=1, inplace=True)
        
        
        
    except:
        pass
    
    t1=pd.DataFrame()
    t1 = pd.concat([df1,df2,df3,df4,df5,df6,df7,df8,df9,df10,df11,df12,df13,df14,df15,df16,df17,df19,df20,df21,df22,df23,df24], axis=0) #axis =0 for vertically appending
    t2 = master_df[~master_df['Description'].isin(t1['Description'])]
    t2['mode']='Others'
    t2['entity']='NA'
    t2['source_of_trans']='NA'
    t2['entity_bank']='NA'
    t2['sub_mode']='NA'
    
    final = pd.concat([t1,t2], axis=0)
    final = final.sort_values(by= ['Txn Date'])
    final['Cheque Number']=final['Cheque Number'].fillna("NA.")
    final = final[['Txn Date', 'Description','Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number','mode','entity','source_of_trans','entity_bank','sub_mode']]
    return final
    #name=file_name.split("\\")[-1]
    #name_path=os.path.join(".\output_files",name)
    #exporting the file
    #final.to_csv("{}\\{}_{}_{}.csv".format(out_path,name,account_no, last_trans_date),index=False)


"""
try:
    standard_chartered_digitization(r".\input_files\3216261_20200827 psd 52510681014.pdf",
                                    r".\output_files")
except Exception as e:
    print(e)
    print("This statement cannot be digitized.")

standard_chartered_digitization(r".\input_files\eStatement6556IN_2020-02-29_10_02.pdf", r".\output_files")
"""