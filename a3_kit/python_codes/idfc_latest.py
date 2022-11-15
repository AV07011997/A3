import pandas as pd
import numpy as np
import tabula
from datetime import datetime as dt

def idfc_digitization(pdf_path, pdf_password):

    col2str = {'dtype': str}
    file_name=pdf_path.split('\\')[-1][:-4]

    passcode=''
    try:
        #if file is encrypted but with empty password
        tables = tabula.read_pdf(pdf_path, pages='all', lattice=True, password=passcode, pandas_options = col2str)
        info = tabula.read_pdf(pdf_path, pages='1', password=passcode,area=[80,46,579,535],stream=True,guess=False,pandas_options={'header':None,'dtype': str})
    except:
        passcode=''
        tables = tabula.read_pdf(pdf_path, pages='all', lattice=True, password=passcode, pandas_options = col2str)
        info = tabula.read_pdf(pdf_path, pages='1', password=passcode,area=[80,46,579,535],stream=True,guess=False,pandas_options={'header':None,'dtype': str})

    if len(tables)==0:
        print("This is an image-based statement, hence, cannot be digitized here.")
        return
    
    # appending only the required tables - where no. of columns are 7 and first column should be 'Date'
    master_table = pd.DataFrame()
    
    for i in range(len(tables)):
        if len(tables[i].columns)==7 and tables[i].columns[0]=='Date':
            master_table = pd.concat([master_table, tables[i]])
    
    master_table = master_table.reset_index(drop=True)
    master_table.columns = ['Txn Date','Value Date', 'Description','Chq/RefNo', 'Debit', 'Credit', 'Balance']
    master_table.rename(columns={'Chq/RefNo':'Cheque Number'}, inplace=True)
    
    # removing \r from Details columns
    master_table['Description'] = master_table['Description'].str.replace('\r','')
    
    # removing Cr/Dr from Balance column
    master_table['Balance'] = master_table['Balance'].str.replace('CR','')
    for i in range(len(master_table)) :
        if master_table['Balance'][i].find('DR') != -1:
            master_table['Balance'][i] = '-' + master_table['Balance'][i][:-2]
    
    
    ## Now extracting account info
    
    for i in range(len(info)) :
        for element in info[i][0] :
            if element.startswith('Mr') or element.startswith('Ms') or element.startswith('Mrs') or element.startswith('Master') or element.startswith('Miss') or element.startswith('M/S'):
                name=element
            if element.find('SAVINGS ACCOUNT DETAILS FOR A/C :') !=-1 :
                account_no = "'{}'".format([i for i in element.split() if i.isdigit()][0])
    
    master_table2 = pd.DataFrame(master_table)
    
    ## adding columns in the master table 
    master_table2['Account Name'] = name
    master_table2['Account Number'] = account_no
    
    master_table2 = master_table2[['Txn Date', 'Description', 'Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number']]
    master_table2['Txn Date'] = [dt.strftime(pd.to_datetime(x,format='%d%b%y'),"%d/%m/%Y") for x in master_table2['Txn Date']]
    last_trans_date = master_table2['Txn Date'].iat[-1]
    
    #exporting the master table to a csv - this is final having complete transactions table appended and essential account information
    #master_table2.to_csv("{}\\{}_{}_{}.csv".format(out_path,file_name,account_no, last_trans_date),index=False)



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
    
    idfc_df=pd.DataFrame(master_table2)
    idfc_df["Description"]=idfc_df["Description"].str.lstrip()
    temp_df=idfc_df
    
    #subsetting UPI transactions
    try:
        
        df1=idfc_df[idfc_df["Description"].str.contains(pat="UPI/")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="UPI/")]
        #Converting text in Description into columns
        temp1=df1.Description.str.split("/", expand=True)
        df1["sub_mode"]=temp1[0]
        df1['entity'] = "NA"
        df1['entity_bank'] = "NA" 
        df1['source_of_trans']='Self Initiated'
        df1['mode']="Mobile App"
        
    except:
        pass    
    
    #subsetting ATM transactions
    try:
        
        df2=idfc_df[idfc_df["Description"].str.contains(pat="ATM-NFS")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="ATM-NFS")]
        #Converting text in Description into columns
        temp2=df2.Description.str.split("/", expand=True)
        df2["sub_mode"]=temp2[0]
        df2['entity'] = "NA"
        df2['entity_bank'] = "NA" 
        df2['source_of_trans']='Self Initiated'
        df2['mode']="CASH"
        
    except:
        pass    
    
    #subsetting IMPS-RIB transactions
    try:
        
        df3=idfc_df[idfc_df["Description"].str.contains(pat="IMPS-RIB")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="IMPS-RIB")]
        #Converting text in Description into columns
        temp3=df3.Description.str.split("/", expand=True)
        df3["sub_mode"]=temp3[0]
        df3['entity'] = "NA"
        df3['entity_bank'] = "NA" 
        df3['source_of_trans']='Self Initiated'
        df3['mode']="Net Banking"
        
    except:
        pass    
    
    #subsetting ECOMM Purchase transactions
    try:
        
        df4=idfc_df[idfc_df["Description"].str.contains(pat="Ecom Purchase")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="Ecom Purchase")]
        #Converting text in Description into columns
        temp4=df4.Description.str.split("/", expand=True)
        df4["sub_mode"]=temp4[0]
        df4['entity'] = "NA"
        df4['entity_bank'] = "NA" 
        df4['source_of_trans']='Self Initiated'
        df4['mode']="Mobile App"
        
    except:
        pass   
    
    #subsetting POS - VISA transactions
    try:
        
        df5=idfc_df[idfc_df["Description"].str.startswith(pat="POS-VISA")]
        temp_df=temp_df[~temp_df["Description"].str.startswith(pat="POS-VISA")]
        #Converting text in Description into columns
        temp5=df5.Description.str.split("/", expand=True)
        df5["sub_mode"]=temp5[0]
        df5['entity'] = temp5[1]
        df5['entity_bank'] = "NA" 
        df5['source_of_trans']='Self Initiated'
        df5['mode']="Card"
        
    except:
        pass 
    
    #subsetting NEFT transactions
    try:
        
        df6=idfc_df[idfc_df["Description"].str.startswith(pat="NEFT")]
        temp_df=temp_df[~temp_df["Description"].str.startswith(pat="NEFT")]
        #Converting text in Description into columns
        temp6=df6.Description.str.split("/", expand=True)
        df6["sub_mode"]=temp6[0]
        df6['entity'] = temp6[2]
        df6['entity_bank'] = "NA" 
        df6['source_of_trans']='Self Initiated'
        df6['mode']="Net Banking"
        
    except:
        pass     
    
    #subsetting Interest transactions
    try:
        
        df7=idfc_df[idfc_df["Description"].str.startswith(pat="QUARTERLY SAVINGS INTEREST CREDIT")]
        temp_df=temp_df[~temp_df["Description"].str.startswith(pat="QUARTERLY SAVINGS INTEREST CREDIT")]
        temp7=df7.Description.str.split("/", expand=True)
        df7["sub_mode"]="NA"
        df7['entity'] = "NA"
        df7['entity_bank'] = "NA" 
        df7['source_of_trans']='Automated'
        df7['mode']="Interest"
        
    except:
        pass     
    
    #subsetting IMPS-INET transactions
    try:
        
        df8=idfc_df[idfc_df["Description"].str.contains(pat="IMPS-INET")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="IMPS-INET")]
        #Converting text in Description into columns
        temp8=df8.Description.str.split("/", expand=True)
        df8["sub_mode"]=temp8[0]
        df8['entity'] = "NA"
        df8['entity_bank'] = "NA" 
        df8['source_of_trans']='Self Initiated'
        df8['mode']="Net Banking"
        
    except:
        pass  
    
    #subsetting  transactions
    try:
        
        df9=idfc_df[idfc_df["Description"].str.contains(pat="REF/POS-VISA")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="REF/POS-VISA")]
        #Converting text in Description into columns
        temp9=df9.Description.str.split("/", expand=True)
        df9["sub_mode"]=temp9[0]
        df9['entity'] = temp9[2]
        df9['entity_bank'] = "NA" 
        df9['source_of_trans']='Automated'
        df9['mode']="Refund"
        
    except:
        pass  
    
    
    final = pd.concat([df1,df2,df3,df4,df5,df6,df7,df8,df9], axis=0)
    final = final.sort_index()
    final['entity'].fillna('Other', inplace=True)
    final['entity'].replace('NA', 'Other', inplace=True)
    final['entity'].replace('', 'Other', inplace=True)
    final = final[['Txn Date', 'Description', 'Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number','mode','entity','source_of_trans','entity_bank','sub_mode']]
    
    final['Debit'] = final['Debit'].astype('str')
    final['Debit'] = final['Debit'].apply(lambda x : x.replace(',',''))
    final['Debit'] = final['Debit'].replace('nan',0)
    final['Debit'] = final['Debit'].astype('float64')
     
    final['Credit'] = final['Credit'].astype('str')
    final['Credit'] = final['Credit'].apply(lambda x : x.replace(',',''))
    final['Credit'] = final['Credit'].replace('nan',0)
    final['Credit'] = final['Credit'].astype('float64')
    
    final['Balance'] = final['Balance'].astype('str')
    final['Balance'] = final['Balance'].apply(lambda x : x.replace(',',''))
    final['Balance'] = final['Balance'].astype('float64')
    final.to_csv(r'D:\idfc.csv')
   
    return final
    #exporting the file
    # final.to_csv("{}\\{}_{}_{}.csv".format(out_path,file_name, account_no, last_trans_date),index=False)


# try :
#     idfc_digitization(r"D:\D Drive\RAJAT\UW kit\Bank statements\IDFC first\527870XXXX psw 03011998.pdf",
#                       r"D:\D Drive\RAJAT\UW kit\Bank statements\IDFC first\digitized")

# except :
#     print("\nThis statement cannot be digitized.\n")
