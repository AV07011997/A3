
import pandas as pd
import numpy as np
import tabula
from datetime import datetime as dt

def obc_digitization(pdf_path, pdf_password):

    col2str = {'dtype': str}
    file_name=pdf_path.split('\\')[-1][:-4]
    passcode=''
    
    try:
        #if file is encrypted but with empty password
        tables = tabula.read_pdf(pdf_path, pages='all',lattice=True,password=passcode, pandas_options = col2str)
        cust_info=tabula.read_pdf(pdf_path,pages=1,password=passcode,area=[95.9,28.2,545.7,1228.7],pandas_options={'header':None,'dtype': str})
    except:
        passcode=pdf_password
        tables = tabula.read_pdf(pdf_path, pages='all',lattice=True,password=passcode, pandas_options = col2str)
        cust_info=tabula.read_pdf(pdf_path,pages=1,password=passcode,area=[95.9,28.2,545.7,1228.7],pandas_options={'header':None,'dtype': str})

    if len(tables)==0:
        print("This is an image-based statement, hence, cannot be digitized here")
        return
    
    tables[0].columns = ['Sl. No.', 'Transaction Date', 'Value Date', 'Instrument ID','Narration', 'Debit','Credit','Account Balance','Remarks']
    master_table2=tables[0]
    # Bringing the tables in proper sturcture which have first row as header
    for i in range(1,len(tables)):
        tables[i].loc[max(tables[i].index)+1,:] = None
        tables[i] = tables[i].shift(1,axis=0)
        tables[i].iloc[0]=tables[i].columns
        tables[i].columns = ['Sl. No.', 'Transaction Date', 'Value Date', 'Instrument ID','Narration', 'Debit','Credit','Account Balance','Remarks']
        master_table2=pd.concat([master_table2,tables[i]])
    
    master_table2.reset_index(drop=True,inplace=True)
    
    master_table2['Debit']=master_table2['Debit'].apply(lambda x: np.nan if (type(x)==str and x.startswith('Unnamed')) else x)
    master_table2['Credit']=master_table2['Credit'].apply(lambda x: np.nan if (type(x)==str and x.startswith('Unnamed')) else x)
    master_table2.drop(['Remarks'],inplace=True,axis=1)
    
    
    for i in range(len(cust_info[0])):
        for j in range(len(cust_info[0].columns)):
            if type(cust_info[0].iloc[i,j])==str and cust_info[0].iloc[i,j].find("Account Number")!=-1:
                account_no="'{}'".format(cust_info[0].iloc[i,j].split("Number")[-1])
            if type(cust_info[0].iloc[i,j])==str and cust_info[0].iloc[i,j].find("Customer Name")!=-1:
                account_name=cust_info[0].iloc[i,j].split(":")[-1]
    
    ## adding columns in the master table 
    master_table2['Account Name'] = account_name
    master_table2['Account Number'] = account_no
    
    master_table2 = master_table2.iloc[::-1]
    # bring the format of OBC like the format of SBI (after digitized)
    master_table2.rename(columns={'Transaction Date':'Txn Date','Account Balance':'Balance','Narration':'Description', 'Instrument ID':'Cheque Number'}, inplace=True)
    
    master_table2['Txn Date'] = [dt.strftime(pd.to_datetime(x,dayfirst=True),"%d/%m/%Y") for x in master_table2['Txn Date']]
    master_table2 = master_table2[['Txn Date', 'Description', 'Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number']]
    last_trans_date = master_table2['Txn Date'].iat[-1]
    master_table2['Cheque Number'].replace('Unnamed: 0', np.nan, inplace=True)
        
    # exporting the master table to a csv - this is final having complete transactions table appended and essential account information
    #master_table2.to_csv("{}/{}_{}_{}.csv".format(out_path,file_name, account_no, last_trans_date),index=False)


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

    obc = pd.DataFrame(master_table2)
    obc["Description"]=obc["Description"].str.lstrip()
    
    
    #subsetting UPI transaction
    try:
        df1=obc[obc["Description"].str.startswith('UPI')]
        df1=df1[~df1["Description"].str.contains('REV')]
        df1["new"]=df1.Description.str.split("/")
        df1["sub-mode"]='UPI'
        df1['entity'] = df1["new"].apply(lambda x:x[-1])
        df1['entity_bank'] = "NA" 
        df1['source_of_trans']='Self Initiated'
        df1['mode']="Mobile App"
        df1.drop(["new"],axis=1,inplace=True) 
    except:
        pass
    
     #subsetting cash transactions
    try:
        df2=obc[obc["Description"].str.startswith('CASH')]
        df2["entity"]="NA"
        df2["sub-mode"]='CASH'
        df2['entity_bank'] = "NA" 
        df2['source_of_trans']='Self Initiated'
        df2['mode']="Cash"
    except:
        pass 
    #subsetting CWDR transaction
    try:
        df3=obc[obc["Description"].str.startswith('CWDR')]
        df3["entity"]="NA"
        df3["sub-mode"]='CWDR'
        df3['entity_bank'] = "NA" 
        df3['source_of_trans']='Self Initiated'
        df3['mode']="Cash"
    except:
        pass
    
    #subsetting CWDR transaction
    try:
        df3a=obc[obc["Description"].str.startswith('CWRR')]
        df3a["entity"]="NA"
        df3a["sub-mode"]='CWRR'
        df3a['entity_bank'] = "NA" 
        df3a['source_of_trans']='Automated'
        df3a['mode']="Reversal"
    except:
        pass
   
    #subsetting REV transaction
    try:
        df4=obc[obc["Description"].str.contains('REV')]
        df4["entity"]="NA"
        df4["sub-mode"]='REV'
        df4['entity_bank'] = "NA" 
        df4['source_of_trans']='Automated'
        df4['mode']="Reversal"
    except:
        pass

    #subsetting ECOM transaction
    try:
        df5=obc[obc["Description"].str.contains('ECOM')]
        df5=df5[~df5["Description"].str.contains('REV')]
        df5["new"]=df5.Description.str.split("/")
        df5["entity"]=df5["new"].apply(lambda x: x[2])
        df5["sub-mode"]='ECOM'
        df5['entity_bank'] = "NA" 
        df5['source_of_trans']='Self Initiated'
        df5['mode']="Net Banking/Card"
        df5.drop(["new"],axis=1,inplace=True) 
    
    except:
        pass
    
    #NEFT
    try:
        df6=obc[obc["Description"].str.startswith('NEFT-')]
        df6a=obc[obc["Description"].str.contains('-NEFT-')]
        df6=df6.append(df6a)
        df6["new"]=df6["Description"].str.split("-")
        df6["new1"]=df6["new"].apply(lambda x: x[1:])
        df6["new1"]=df6["new1"].str.join(" ")
        df6["new2"]=df6["new1"].str.split("/")        
        df6["entity"]=df6["new2"].apply(lambda x: x[-1])
        df6["sub-mode"]='NEFT'
        df6['entity_bank'] = "NA"
        df6['source_of_trans']='Self Initiated'
        df6['mode']="Net Banking"
        df6.drop(["new","new1","new2"],axis=1,inplace=True) 
    except:
        pass
    
    # IMPS
    try:
        df7=obc[obc["Description"].str.startswith('IMPS')]
        df7["new"]=df7["Description"].str.split("/")
        df7["entity"]=df7["new"].apply(lambda x: x[2])
        df7["sub-mode"]='IMPS'
        df7['entity_bank'] = "NA"
        df7['source_of_trans']='Self Initiated'
        df7['mode']="Net Banking"
        df7.drop(["new"],axis=1,inplace=True) 
    except:
        pass
    
    #subsetting interest transactions
    try:
        df8=obc[obc["Description"].str.contains('Int.Pd')]
        df8["entity"]="NA"
        df8["sub-mode"]='Int.Pd'
        df8['entity_bank'] = "NA" 
        df8['source_of_trans']='Automated'
        df8['mode']="Interest"
    except:
        pass
    
    
    try:
        df9a=obc[obc["Description"].str.startswith('IB SM')]
        df9b=obc[obc["Description"].str.contains('CHG')]
        df9a=df9a.append(df9b)
        df9a["entity"]="NA"
        df9a["sub-mode"]='IB SM'
        df9a['entity_bank'] = "NA" 
        df9a['source_of_trans']='Automated'
        df9a['mode']="Charges"
    except:
        pass

    #subsetting PRCR (card) transaction
    try:
        df10=obc[obc["Description"].str.startswith('PRCR')]
        df10["entity"]="NA"
        df10["sub-mode"]='PRCR'
        df10['entity_bank'] = "NA" 
        df10['source_of_trans']='Self Initiated'
        df10['mode']="Card"
    except:
        pass
   
    #subsetting refund transactions
    try:
        df11=obc[obc["Description"].str.contains('REF')]
        df11["entity"]="NA"
        df11["sub-mode"]='Refund'
        df11['entity_bank'] = "NA" 
        df11['source_of_trans']='Automated'
        df11['mode']="Refund"
    except:
        pass
    
    try:
        df12=obc[obc["Description"].str.contains('By')]
        df12=df12[df12["Description"].str.contains('Inst')]
        
        df12["new"]=df12["Description"].str.split("/")
        df12["new1"]=df12["new"].apply(lambda x: x[0])
        df12["entity"]=df12["new1"].str.split("-").apply(lambda x: x[0])
        df12["sub-mode"]='BY INST'
        df12['entity_bank'] = df12["new"].apply(lambda x: x[1])
        df12['source_of_trans']='Self Initiated'
        df12['mode']="Cheque"
        df12.drop(["new","new1"],axis=1,inplace=True) 
    except:
        pass
    

    #appending dataframes
    t1 = pd.concat([df1,df2,df3,df3a,df4,df5,df6,df7,df8,df9a,df10,df11,df12], axis=0) #axis =0 for vertically appending
 
    try:
        t1.drop(["new"],axis=1,inplace=True)
    except:
        pass
    t2 = obc[~obc["Description"].isin(t1["Description"])]
  
    try:
        df13=t2[t2["Description"].str.contains('TO', case=False)]
        df13["new"]=df13["Description"].str.split("TO")
        df13["entity"]=df13["new"].apply(lambda x: x[-1])        
        df13["sub-mode"]='Others'
        df13['entity_bank'] = "NA"
        df13['source_of_trans']='NA'
        df13['mode']="NA"
        df13.drop(["new"],axis=1,inplace=True) 
    except:
        pass
    
    t3=pd.concat([t1,df13])
    t4 = obc[~obc["Description"].isin(t3["Description"])]
    
    t4['sub-mode']='Others'
    t4['entity']='NA'
    t4['source_of_trans']='NA'
    t4['entity_bank']='NA'
    t4['mode']='NA'
        
    final = pd.concat([t3,t4], axis=0)
    final = final.sort_index(ascending=False)
    final.rename(columns={'sub-mode':'sub_mode'}, inplace=True)    
    final = final[['Txn Date', 'Description', 'Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number','mode','entity','source_of_trans','entity_bank','sub_mode']]

    return final
    #exporting the file
    # final.to_csv("{}/{}_{}_{}.csv".format(out_path,file_name, account_no, last_trans_date),index=False)


# try :
#     obc_digitization(r"D:\D Drive\RAJAT\UW kit\Bank statements\STATEMENT FROM MITHUN\OBC\OpTransactionHistory16-11-2019(3)-min.pdf",
#                      r"D:\D Drive\RAJAT\UW kit\Bank statements\STATEMENT FROM MITHUN\OBC")

# except :
#     print("\nThis statement cannot be digitized.\n")
