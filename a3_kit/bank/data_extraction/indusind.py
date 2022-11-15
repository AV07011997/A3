import tabula
import pandas as pd
import numpy as np
from datetime import datetime as dt

#function to align the dataframes and extracting desired information
def indusind_digitization(pdf_path,out_path):
    #extracting file name from pdf_path
    file_name=pdf_path.split('\\')[-1][:-4]
    
    #to oversee the warning to concatenate descriptions/narrations
    pd.options.mode.chained_assignment = None
    passcode=''
    try:
        #if file is encrypted but with empty password
        tables=tabula.read_pdf(pdf_path,pages='all',stream=True,password=passcode)
        cust_info = tabula.read_pdf(pdf_path, pages=1,password=passcode,stream=True,area=[80.7,27.8,328.1,790.1],pandas_options={'header':None})
    except:
        #password prompt
        passcode=input("Enter the Password:")
        tables=tabula.read_pdf(pdf_path,pages='all',stream=True,password=passcode)
        cust_info = tabula.read_pdf(pdf_path, pages=1,password=passcode,stream=True,area=[80.7,27.8,328.1,790.1],pandas_options={'header':None})

    #return if image based (scanned) pdf
    if len(tables)==0:
        print("This is an image-based statement, hence, cannot be digitized here.")
        return
    
    #concatenate description splited into different rows and dropping of invalid rows afterwards
    def concat_desc( df, start_row):
        for j in range(start_row, len(df)):
            while j<len(df) and pd.isna(df['Date'][j]):
                if(pd.isna(df['Description'][j+1])):
                    df['Description'][j+1]=df['Description'][j]
                else:
                    df['Description'][j+1]=df['Description'][j]+df['Description'][j+1]
                if(pd.isna(df['Type'][j+1])):
                    df['Type'][j+1]=df['Type'][j]
                else:
                    df['Type'][j+1]=str(df['Type'][j])+str(df['Type'][j+1])
                j+=1
        df.dropna(subset=['Date'],inplace=True)
        df.reset_index(drop=True,inplace=True)
        return df
    
    master_table2=pd.DataFrame()
    #aligning dataframes and concatenating into super dataframe
    for i in range(len(tables)):
        df_copy=tables[i]
        df_copy=df_copy.rename(columns={df_copy.keys()[-1]: 'Balance'})
        df_copy=concat_desc(df_copy,df_copy['Type'].first_valid_index())
        df_copy['Debit'] = df_copy['Debit'].replace({'-':''})
        df_copy['Credit'] = df_copy['Credit'].replace({'-':''})
        master_table2=pd.concat([master_table2,df_copy])
    #dropping off all extra columns
    master_table2.drop(master_table2.columns.difference(['Date','Balance','Description','Debit','Credit']),axis=1, inplace=True)
    #extracting account information (name/number)
    account_name=cust_info[0].iloc[1,0]
    for i in range(len(cust_info[0])):
        for j in range(len(cust_info[0].columns)):
            if type(cust_info[0].iloc[i,j])==str and cust_info[0].iloc[i,j].find("Account No.")!=-1:
                if cust_info[0].iloc[i,j].find(':') != -1:
                    account_no="'{}'".format(cust_info[0].iloc[i,j].split(":")[-1].strip())
                if cust_info[0].iloc[i,j].find(':') == -1 or account_no=="''":
                    account_no="'{}'".format(cust_info[0].iloc[i,j+1].split(":")[-1].strip())
    
    master_table2['Account Name'] = account_name
    master_table2['Account Number'] = account_no
    master_table2.rename(columns={'Date':'Txn Date'},inplace=True)
    
    # inverting the dataframe;to arrange in increasing order of dates
    master_table2 = master_table2.iloc[::-1]
    master_table2.reset_index(drop=True,inplace=True)
    #standardising dataframes according to standard scehma
    master_table2['Txn Date'] = [dt.strftime(pd.to_datetime(x, dayfirst=True),"%d-%m-%Y") for x in master_table2['Txn Date']]
    master_table2 = master_table2[['Txn Date', 'Description', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number']]
    last_trans_date = master_table2['Txn Date'].iat[-1]
    
    #conversion into csv
    #master_table2.to_csv("{}\\{}_{}_{}.csv".format(out_path,file_name,account_no, last_trans_date),index=False)


    ## NOW PERFORMING FEW LOGICAL CHECKS TO CHECK DIGITIZATION HAS NO ISSUE
    
    df = pd.DataFrame(master_table2)
    column_names=['Statement_name','Wrong Credit', 'Wrong Debit', 'Remark']
    result=pd.DataFrame(index=[1],columns=column_names)
    df['Credit']=[np.nan if i=='' else i for i in df['Credit']]
    df['Debit']=[np.nan if i=='' else i for i in df['Debit']]
    if df['Credit'].dtype =='O':
        df['Credit_changed'] = (df['Credit'].astype(str).str.replace(',','')).astype(float)
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
        pass
    else:
        print("\nThere are issues found after the Logical checks.\nThe digtitized output and the issues have been exported in CSVs.\n")
        master_table2.to_csv("{}/{}_Digitized.csv".format(out_path,file_name),index=False)        
        result.to_csv("{}/{}_LogicalChecks.csv".format(out_path,file_name),index=False)
        return


    # NOW THE ENTITY EXTRACTION PART

    def get_printable(s):
        res=''.join([i for i in s if i.isprintable()])
        return res
    
    master_df = pd.DataFrame(master_table2)
    
    master_df["Description"]=master_df["Description"].str.lstrip()
    master_df['Description']=[i  if i.isprintable() else get_printable(i) for i in master_df['Description'].astype(str)]
    pd.options.mode.chained_assignment = None
    
    #imps
    try:
        df1=master_df[master_df['Description'].str.startswith('IMPS')]
        df1[['sub-mode','p2a','num','entity-bank','entity']]=df1['Description'].str.split('/',expand=True)
        df1['entity-bank']=np.where(df1['entity'].str.isdigit(), "IndusInd",df1['entity-bank'])
        df1['source_of_trans']='Self Initaited'
        df1['mode']='Net Banking'
        df1['Cheque Number']="NA."
        df1.drop(['p2a','num'],axis=1,inplace=True)
    except:
        pass
    
    #neft
    try:
        df2=master_df[master_df['Description'].str.startswith('NEFT')]
        df2[['sub-mode','num','entity']]=df2['Description'].str.split('/',expand=True)
        df2['source_of_trans']='Self Initaited'
        df2['mode']='Net Banking'
        df2['entity-bank']="NA."
        df2['Cheque Number']="NA."
        df2.drop(['num'],axis=1,inplace=True)
    except:
        pass
    
    #cheque depsit
    try:
        df3=master_df[master_df['Description'].str.startswith('CHEQUE DEPOSIT')]
        df3[['sub-mode','Cheque Number','entity-bank','place']]=df3['Description'].str.split('/',expand=True)
        df3['entity']="NA."
        df3['entity-bank']=np.where(df3['entity-bank'].str.isdigit(), "IndusInd",df3['entity-bank'])
        df3['source_of_trans']='Self Initaited'
        df3['mode']='Cheque'
        df3.drop(['place'],axis=1,inplace=True)
    except:
        pass
    
    #cheque return
    try:
        df4a=master_df[(master_df['Description'].str.contains('Cheque return'))]
        df4b=master_df[(master_df['Description'].str.contains('Cheque Return'))]
        df4c=master_df[(master_df['Description'].str.contains('Cheque dep. Return'))]
        
        df4a['sub-mode']="NA."
        df4a['entity']="NA."
        df4a['entity-bank']="NA."
        df4a['source_of_trans']='Automated'
        df4a['mode']="Cheque Bounce"
        df4a[['chq','Cheque Number','Reason']]=df4a['Description'].str.split(':',2,expand=True)
        df4a.drop(['chq'],axis=1,inplace=True)
        
        df4b['sub-mode']="NA."
        df4b['entity']="NA."
        df4b['entity-bank']="NA."
        df4b['source_of_trans']='Automated'
        df4b['mode']="Charges"
        
        df4c['sub-mode']="NA."
        df4c['entity']="NA."
        df4c['entity-bank']="NA."
        df4c['source_of_trans']='Automated'
        df4c['mode']="Cheque Bounce"
        df4c[['chq','Cheque Number','Reason']]=df4c['Description'].str.split(':',2,expand=True)
        df4c.drop(['chq'],axis=1,inplace=True)
    except:
        pass
    
    #cheque return
    try:
        df5=master_df[(master_df['Description'].str.contains('charges')) | (master_df['Description'].str.contains('Chrg')) | (master_df['Description'].str.contains('CHRG'))]
        df5['sub-mode']="NA."
        df5['entity']="NA."
        df5['entity-bank']="NA."
        df5['source_of_trans']='Automated'
        df5['mode']="Charges"
        df5['Cheque Number']="NA."
    except:
        pass
    
    # MC POS
    try:
        df6=master_df[(master_df['Description'].str.contains('MC POS TXN'))]
        df6[['info','entity']]=df6['Description'].str.split('/',expand=True)
        df6['sub-mode']='MC POS TXN'
        df6['source_of_trans']='Self-Initiated'
        df6['mode']='Card'
        df6['entity-bank']="NA."
        df6.drop(['info'],axis=1,inplace=True)
        df6['Cheque Number']="NA."
    except:
        pass
    
    #cash deposit
    try:
        df7=master_df[(master_df["Description"].str.contains('CASH DEPOSIT'))]
        df7['sub-mode']="Cash deposit"
        df7['source_of_trans']='Self Initiated'
        df7['mode']='Cash'
        df7['entity-bank']="NA."
        df7['entity']="NA."
        df7['Cheque Number']="NA."
    except:
        pass
    
    #ach
    try:
        df8=master_df[master_df["Description"].str.startswith("ACH DEBIT")]
        df8[['sub-mode','entity_string']]=df8['Description'].str.split(':',expand=True)
        df8[['num','entity']]=df8['entity_string'].str.split(',',expand=True)
        df8['source_of_trans']='Automated'
        df8['mode']="NA."
        df8['entity-bank']="NA."
        df8.drop(['entity_string','num'],axis=1,inplace=True)
        df8['Cheque Number']="NA."
    except:
        pass
    
    #To Duplicate Statement Issuance
    try:
        df9=master_df[(master_df['Description'].str.contains('To Duplicate Statement Issuance'))]
        df9['sub-mode']="NA."
        df9['entity']="NA."
        df9['entity-bank']="NA."
        df9['source_of_trans']='Automated'
        df9['mode']="NA."
        df9['Cheque Number']="NA."
    except:
        pass
    
    
    #UPI
    try:
        df10=master_df[(master_df['Description'].str.contains('UPI'))]
        df10['sub-mode']="UPI"
        df10['source_of_trans']='Self Initiated'
        df10['mode']='Mobile App'
        df10['entity-bank']="NA."
        df10['entity']="NA."
        df10['Cheque Number']="NA."
    except:
        pass
    
    #cash deposit
    try:
        df11=master_df[master_df["Description"].str.contains('NFS CASH TXN')]
        df11['sub-mode']="NFS CASH TXN"
        df11['source_of_trans']='Self Initiated'
        df11['mode']='Cash'
        df11['entity-bank']="NA."
        df11['entity']="NA."
        df11['Cheque Number']="NA."
    except:
        pass
    
    t1=pd.DataFrame()
    t1 = pd.concat([df1,df2,df3,df4a,df4b,df4c,df5,df6,df7,df8,df9,df10,df11], axis=0) #axis =0 for vertically appending
    
    t2 = master_df[~master_df["Description"].isin(t1["Description"])]
    t2['mode']='Others'
    t2['entity']="NA."
    t2['source_of_trans']="NA."
    t2['entity-bank']="NA."
    t2['sub-mode']="NA."
    
    final = pd.concat([t1,t2], axis=0)
    final = final.sort_values(by= ["Txn Date"])
    
    final = final.sort_index()
    final.rename(columns={'sub-mode':'sub_mode','entity-bank':'entity_bank'}, inplace=True)    
    final = final[['Txn Date', 'Description','Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number','mode','entity','source_of_trans','entity_bank','sub_mode']]
    return final
    #exporting the file
    #final.to_csv("{}\\{}_{}_{}.csv".format(out_path,file_name, account_no, last_trans_date),index=False)


#try:
 #   indusind_digitization(r".\input_files\Indusind Bank (1 April 2019 to 31 March 2020).pdf", r".\output_files")
#except Exception as e:
 #       print(e)
 #       print("\nThis statement cannot be digitized.\n")
