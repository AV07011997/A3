import pandas as pd
import numpy as np
import tabula
from datetime import datetime as dt

def cbi_digitization(pdf_path, pdf_password):    
    
    col2str = {'dtype': str}
    file_name = pdf_path.split('\\')[-1][:-4]
    passcode=''
       
    try:
        tables = tabula.read_pdf(pdf_path,pages='all',password=passcode, pandas_options = col2str)
        cust_info=tabula.read_pdf(pdf_path,pages=1,password=passcode,area=[81.7,0,335.2,833], pandas_options = col2str)
    except:
        passcode=pdf_password
        tables = tabula.read_pdf(pdf_path,pages='all',password=passcode, pandas_options = col2str)
        cust_info=tabula.read_pdf(pdf_path,pages=1,password=passcode,area=[81.7,0,335.2,833], pandas_options = col2str)
        
    if len(tables)==0:
        print("This is an image-based statement, hence, cannot be digitized here.")
        return
    
    
    #for removing cr from balance
    for i in range(len(tables)):
        for j in tables[i].index:
            tables[i]=tables[i].replace(np.nan,'') 
            tables[i]['Balance']=list(map(str,tables[i]['Balance'])) #convert to str 
            tables[i]['Balance'][j] = tables[i]['Balance'][j][:-2]  
          
    
    # appending all tables of a pdf
    master_table = tables[0]
    
    for i in range(len(tables)-1):
        master_table = pd.concat([master_table, tables[i+1]])
    
    master_table = master_table.reset_index(drop=True)
    
    first_row=cust_info[0][cust_info[0].columns[0]].first_valid_index()
    account_name=cust_info[0].iloc[first_row,0]
    for i in range(len(cust_info[0])):
        for j in range(len(cust_info[0].columns)):
            if type(cust_info[0].iloc[i,j])==str and cust_info[0].iloc[i,j].find("Account Number")!=-1:
                account_no="'{}'".format(cust_info[0].iloc[i,j].split(":")[-1].strip())
                break
      
    ## adding three columns in the master table 
    master_table['Account Name'] = account_name
    master_table['Account Number'] = account_no
    
    master_table2 = master_table.reset_index(drop=True)
    master_table2.rename(columns={'Post Date':'Txn Date','Account Description':'Description', 'Cheque\rNumber':'Cheque Number'}, inplace=True)
    master_table2 = master_table2.replace('',np.nan)
    print(master_table2.columns)
    master_table2 = master_table2[['Txn Date', 'Description', 'Debit', 'Credit', 'Balance', 'Account Name', 'Account Number', 'Cheque Number']]
    master_table2['Txn Date'] = [dt.strftime(pd.to_datetime(x,dayfirst=True),"%d/%m/%Y") for x in master_table2['Txn Date']]
    last_trans_date = master_table2['Txn Date'].iat[-1]
    
    #exporting the master table to a csv - this is final having complete transactions table appended and essential account information
    #master_table2.to_csv("{}\\{}_{}_{}.csv".format(out_path,file_name, account_no, last_trans_date),index=False)
    
    
    
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
    
    #subsetting Cash deposit and cash withdrawal
    try:
        df1=master_df[(master_df["Description"].str.contains('CASH DEPOSIT')) | (master_df['Description'].str.contains('CASH WITHDRAWAL'))]
        df1[['sub-mode','entity']]=df1['Description'].str.split('/',expand=True)
        df1['sub-mode']=df1['sub-mode'].str.strip()
        df1['source_of_trans']='Self Initiated'
        df1['mode']='Cash'
        df1['entity_bank']="NA"
    except:
        pass
    
    
    #subsetting cash WDL
    try:
        df2=master_df[master_df["Description"].str.contains('CASH WDL')]
        df2[['entity','issuer','sub-mode','number1','number2']]=df2['Description'].str.rsplit(' ',4,expand=True)
        df2['source_of_trans']='Self Initiated'
        df2['mode']='Cash'
        df2['entity_bank']="NA"
        df2.drop(['issuer','number1','number2'],axis=1,inplace=True)
    except:
        pass
    
    #subsetting cash payment
    try:
        df3=master_df[(master_df["Description"].str.contains('CASHPAYMENT')) | (master_df["Description"].str.contains('CASH\\nPAYMENT'))]
        df3[['entity','issuer','number1','number2']]=df3['Description'].str.rsplit(' ',3,expand=True)
        df3['sub-mode']='CASH'
        df3['source_of_trans']='Self Initiated'
        df3['mode']='Cash'
        df3['entity_bank']="NA"
        df3.drop(['issuer','number1','number2'],axis=1,inplace=True)
    except:
        pass
    
    #ATM WDL
    try:
        df4=master_df[(master_df['Description'].str.contains('ATM WDL'))]
        df4[['sub-mode','entity_bank_string']]=df4['Description'].str.split('/',expand=True)
        df4['sub-mode']=df4['sub-mode'].str.strip()
        df4['source_of_trans']='Self Initiated'
        df4['mode']='Card'
        df4[['atm','number','entity_bank']]=df4['entity_bank_string'].str.split('|',3,expand=True)
        df4['entity_bank']=df4['entity_bank'].str.strip()
        df4['entity']="NA"
        df4.drop(['entity_bank_string','number','atm'],axis=1,inplace=True)
    except:
        pass
    
    #POS PRCH
    try:
        df5=master_df[(master_df['Description'].str.contains('POS PRCH'))]
        df5[['info','entity']]=df5['Description'].str.split('|',expand=True)
        df5['sub-mode']='POS PRCH'
        df5['source_of_trans']='Self Initiated'
        df5['mode']='Card'
        df5['entity_bank']="NA"
        df5['entity']=df5['entity'].str.strip()
        df5.drop(['info'],axis=1,inplace=True)
    except:
        pass
    
    
    #MC COMM
    try:
        df6=master_df[(master_df['Description'].str.contains('MC COMM'))]
        df6['sub-mode']='MC COMM'#service charge
        df6['source_of_trans']='Automated'
        df6['mode']='Charges'
        df6['entity_bank']="NA"
        df6['entity']="NA"
    except:
        pass
    
    #gst
    try:
        df7=master_df[(master_df['Description'].str.contains('GST'))]
        df8=df7[df7['Description'].str.contains('REFUN')]
        df7=df7[~df7["Description"].isin(df8["Description"])]
        df7['sub-mode']="NA"
        df7['source_of_trans']='Automated'
        df7['mode']='Tax'
        df7['entity_bank']="NA"
        df7['entity']="NA"
        df8['sub-mode']="NA"
        df8['source_of_trans']='Automated'
        df8[['mode','info']]=df8['Description'].str.split('/',expand=True)
        df8['entity_bank']="NA"
        df8['entity']="NA"
        df8.drop(['info'],axis=1,inplace=True)
    except:
        pass
    
    #UPI
    try:
        df9=master_df[(master_df['Description'].str.contains('UPI')) & (master_df['Description'].str.contains('TRANSFER'))]
        df9[['by_to_transfer','sub-mode','number','entity']]=df9['Description'].str.split('/',expand=True)
        df9['source_of_trans']='Self Initiated'
        df9['mode']='Mobile App'
        df9['entity_bank']="NA"
        df9.drop(['by_to_transfer','number'],axis=1,inplace=True)
    except:
        pass
    
    #sms chg
    try:
        df10=master_df[(master_df['Description'].str.contains('SMS CHG'))]
        df10['sub-mode']='SMS Charges'
        df10['source_of_trans']='Automated'
        df10['mode']='Charges'
        df10['entity_bank']="NA"
        df10['entity']="NA"
    except:
        pass
    
    #tax collection
    try:
        df11=master_df[(master_df['Description'].str.contains('TAX COLLECTN TXN')) | (master_df['Description'].str.contains('TAXCOLLECTN TXN'))]
        df11['sub-mode']='Tax'
        df11['source_of_trans']='Automated'
        df11['mode']='Charges'
        df11['entity_bank']="NA"
        df11[['by_to_transfer','entity_string']]=df11['Description'].str.split('/',expand=True)
        df11[['entity','info']]=df11['entity_string'].str.rsplit(':',1,expand=True)
        df11.drop(['by_to_transfer','entity_string','info'],axis=1,inplace=True)
    except:
        pass
    
    #to transfer
    try:
        df12=master_df[(master_df['Description'].str.contains('TO TRANSFER'))]
        df12=df12[~df12["Description"].isin(df9["Description"])]#excluding upi
        df12=df12[~df12["Description"].isin(df10["Description"])]#excluding sms chg
        df12=df12[~df12["Description"].isin(df11["Description"])]#excluding taxes
        df12['sub-mode']="NA"
        df12['source_of_trans']='Self Initiated'
        df12['mode']="NA"
        df12['entity_bank']="NA"
        df12[['by_to_transfer','entity']]=df11['Description'].str.split('/',expand=True)
        df12['entity']=np.where(df12['entity'].isna(),"NA",df12['entity'])
        df12.drop(['by_to_transfer'],axis=1,inplace=True)
    except:
        pass
    
    #by transfer
    #imps
    try:
        df13=master_df[master_df['Description'].str.contains('IMPS')]
        df13['sub-mode']='IMPS'
        df13['source_of_trans']='Self Initiated'
        df13['mode']='Net Banking'
        df13['entity_bank']="NA"
        df13[['by_to_transfer','entity_string']]=df13['Description'].str.split('/',expand=True)
        df13[['info','entity']]=df13['entity_string'].str.split(' ',1,expand=True)
        df13.drop(['by_to_transfer','entity_string','info'],axis=1,inplace=True)
    except:
        pass
    
    #neft
    try:
        df14=master_df[master_df['Description'].str.contains('NEFT')]
        df14['sub-mode']='NEFT'
        df14['source_of_trans']='Self Initiated'
        df14['mode']='Net Banking'
        df14['entity_bank']="NA"
        df14[['by_to_transfer','entity_string']]=df14['Description'].str.split('/',expand=True)
        df14[['info','entity']]=df14['entity_string'].str.split(' ',1,expand=True)
        df14.drop(['by_to_transfer','entity_string','info'],axis=1,inplace=True)
    except:
        pass
    
    #credit interest
    try:
        df15 =master_df[master_df["Description"].str.startswith("CREDIT INTEREST")]
        df15['sub-mode']='CREDIT INTEREST'
        df15['source_of_trans']='Automated'
        df15['mode']='Interest'
        df15['entity_bank']="NA"
        df15['entity']="NA"
    except:
        pass
    
    t1=pd.DataFrame()
    t1 = pd.concat([df1,df2,df3,df4,df5,df6,df7,df8,df9,df10,df11,df12,df13,df14,df15], axis=0) #axis =0 for vertically appending
    #t1['entity']=np.where(t1['entity'].isna(),"NA.",t1['entity'])
    t2 = master_df[~master_df["Description"].isin(t1["Description"])]
    t2['mode']='Others'
    t2['entity']="NA"
    t2['source_of_trans']="NA"
    t2['entity_bank']="NA"
    t2['sub-mode']="NA"
    
    final = pd.concat([t1,t2], axis=0)
    final = final.sort_values(by= ["Txn Date"])
    
    final = final.sort_index()
    final.rename(columns={'sub-mode':'sub_mode'}, inplace=True)
    final = final[['Txn Date', 'Description', 'Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number','mode','entity','source_of_trans','entity_bank','sub_mode']]
    
    return final
    #exporting the file
    # final.to_csv("{}\\{}_{}_{}.csv".format(out_path,file_name, account_no, last_trans_date),index=False)


    
# try:
#     centralbank_digitization(r"D:\D Drive\RAJAT\UW kit\Bank statements\STATEMENT FROM MITHUN\central bank\AccountStatement_3427294596_Oct23_131912.pdf",
#                              r"D:\D Drive\RAJAT\UW kit\Bank statements\STATEMENT FROM MITHUN\central bank\digitized")
# except:
#     print("\nThis statement cannot be digitized. \n")