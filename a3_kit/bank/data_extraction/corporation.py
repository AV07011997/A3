import pandas as pd
import numpy as np
import tabula
from datetime import datetime as dt

def corporation_digitization(pdf_path,pdf_password):
    file_name=pdf_path.split('\\')[-1][:-4]
    passcode=''
    try:
        #if file is encrypted but with empty password
        tables = tabula.read_pdf(pdf_path,password=passcode, pages='all')
        other_details_list =  tabula.read_pdf(pdf_path, pages=1,password=passcode, area=[0,0,576,775])
    except:
        passcode=pdf_password
        tables = tabula.read_pdf(pdf_path,password=passcode, pages='all')
        other_details_list =  tabula.read_pdf(pdf_path, pages=1,password=passcode, area=[0,0,576,775])
        
    if len(tables)==0:
        print("This is an image-based statement, hence, cannot be digitized here")
        return
    
    #reading account number and account name from pdf
    
    other_details = other_details_list[0]
    
    no_of_columns = len(other_details.columns)
    
    column_names = []
    for i in range(1,no_of_columns+1):
        temp = 'column' + str(i)
        column_names.append(temp)
        
    other_details.columns = column_names  
    
    for i in range(len(other_details)):
        if type(other_details.iloc[i,0])==str and other_details.iloc[i,0].find("Name")!=-1:
            account_name = other_details.iloc[i,0].split(":")[-1]
        if type(other_details.iloc[i,0])==str and other_details.iloc[i,0].find("Number")!=-1:
            account_no = "'{}'".format(other_details.iloc[i,0].split(":")[1].lstrip())
    
    ##dropping extra tables
    for i in reversed(range(len(tables))) :
        if len(tables[i].columns) < 5:
            del (tables[i])
        else:
            continue
    
    # Dropping the rows that are originally above the table but are read into the table by Tabula
    for i in range(len(tables)) :
        if len(tables[i].columns) == 7:
            tables[i][tables[i].columns[0]]=list(map(str,tables[i][tables[i].columns[0]]))
            for j in tables[i].index :
                if tables[i][tables[i].columns[0]][j].startswith("Date") :
                    tables[i] = tables[i][j+1:]
                    # tables[i]=tables[i].drop(range(j,len(tables[i])), axis=0)
                    break
                else :
                    continue
    
    ##renaming columns
    for i in range(len(tables)) :
        if len(tables[i].columns) == 7:
            if tables[i].columns[0] == 'Date':
                tables[0].columns=tables[i].columns
                break
            else:
                continue
    
    # removing Cr & Dr from balance column
    for i in range(len(tables)) :
        for j in tables[i].index :
            if tables[i].loc[j,'Balance'][-2:] == 'Dr':
                tables[i].loc[j,'Balance'] = '-' + tables[i].loc[j,'Balance']
            tables[i].loc[j,'Balance'] = tables[i].loc[j,'Balance'][ :-3]
    
    
    # finally appending all tables of a pdf
    master_table = tables[0]
    
    for i in range(len(tables)-1) :
        master_table = pd.concat([master_table, tables[i+1]])
        
    master_table2 = master_table.reset_index(drop=True) 
    
    master_table2.rename(columns={'Date':'Txn Date','Particulars':'Description', 'Withdrawal':'Debit', 'Deposit':'Credit', 'Instrument ID':'Cheque Number'}, inplace=True)
    
    ## adding three columns in the master table 
    master_table2['Account Name'] = account_name
    master_table2['Account Number'] = account_no
    
    
    master_table2 = master_table2[['Txn Date', 'Description', 'Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number']]
    master_table2['Txn Date'] = [dt.strftime(pd.to_datetime(x,dayfirst=True),"%d-%m-%Y") for x in master_table2['Txn Date']]
    last_trans_date = master_table2['Txn Date'].iat[-1]
    
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
        master_table2.to_csv("{}/{}_Digitized.csv".format(out_path,file_name),index=False)        
        result.to_csv("{}/{}_LogicalChecks.csv".format(out_path,file_name),index=False)
        return


    # NOW THE ENTITY EXTRACTION PART

    corp_df = pd.DataFrame(master_table2)
    corp_df["Description"]=corp_df["Description"].str.lstrip()
    temp_df=corp_df
    
    #subsetting RTGS transactions
    try:
        
        df1=corp_df[corp_df["Description"].str.contains(pat="RTGS TO")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="RTGS TO")]
        #Converting text in Description into columns
        temp1=df1.Description.str.split(" " or "/", expand=True)
        temp2=temp1[2].str.split(":", expand=True)
        df1["sub_mode"]=temp1[0]
        df1['entity'] = temp2[0]
        df1['entity_bank'] = "NA" 
        df1['source_of_trans']='Self Initiated'
        df1['mode']="Net Banking"   
    except:
        pass    
            
    #subsetting Sweep Trf transactions
    try:
        
        df2=corp_df[corp_df["Description"].str.contains(pat="Sweep Trf")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="Sweep Trf")]
        df2[["other1","other2","other3","other4","other5","other6","other7"]] = df2.Description.str.split(" ", expand=True)
        df2["sub_mode"]= df2["other1"]+" "+df2["other2"]
        df2['entity'] = "NA"
        df2['entity_bank'] = "NA" 
        df2['source_of_trans']='Automated'
        df2['mode']='NA'
        df2.drop(["other1","other2","other3","other4","other5","other6","other7"], axis = 1, inplace=True)
    
    except:
        pass  
    
    #subsetting BY transactions
    try:
        #subsetting BY transactions
        df3=corp_df[corp_df["Description"].str.contains(pat="BY 0")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="BY 0")]
        df3["sub_mode"]= "NA"
        df3['entity'] = "NA"
        df3['entity_bank'] = "NA" 
        df3['source_of_trans']='Automated'
        df3['mode']="Interest"
    
    except:
        pass  
    
    #subsetting BY Inst transactions
    try:
        
        df4=corp_df[corp_df["Description"].str.contains(pat="By Inst")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="By Inst")]
        temp3=df4.Description.str.split(" ON ", expand=True)
        #df4[["sub_mode","other1"]] = df4.Description.str.split(":", expand=True)
        df4['sub_mode']='By Inst'
        df4['entity'] = "NA"
        df4['entity_bank'] = temp3[1]
        df4['source_of_trans']='Self Initiated'
        df4['mode']='NA'
        #df4.drop(["other1"], axis = 1, inplace=True)
    except:
        pass  
    
    
    #subsetting BY CHQ transactions
    try:
        
        df5=corp_df[corp_df["Description"].str.contains(pat="BY CHQ")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="BY CHQ")]
        df5[["sub_mode","other1"]] = df5.Description.str.split("NO", expand=True)
        df5['entity'] = "NA"
        df5['entity_bank'] = "NA"
        df5['source_of_trans']='Self Initiated'
        df5['mode']='Cheque'
        df5.drop(["other1"], axis = 1, inplace=True)
    except:
        pass      
    
    #subsetting RTGS FM transactions
    try:
        
        df6=corp_df[corp_df["Description"].str.contains(pat="RTGS fm")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="RTGS fm")]
        temp4=df6.Description.str.split("RTGS fm ", expand=True)
        temp4=temp4[1].str.split(":", expand=True)
        df6["sub_mode"]= "RTGS"
        df6['entity'] = temp4[0]
        df6['entity_bank'] = "NA"
        df6['source_of_trans']='Self Initiated'
        df6['mode']='Net Banking'
    
    except:
        pass  
    
    #subsetting Blank Category(Closure) transactions
    try:
        
        df7=corp_df[corp_df["Description"].str.contains(pat="Closure Proceeds")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="Closure Proceeds")]
        df7["sub_mode"]= "NA"
        df7['entity'] = "NA"
        df7['entity_bank'] = "NA"
        df7['source_of_trans']='Self Initiated'
        df7['mode']='NA'
    
    except:
        pass  
    
    #subsetting Repayment credit transactions
    try:
        df8=corp_df[corp_df["Description"].str.contains(pat="Repayment credit")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="Repayment credit")]
        df8["sub_mode"]= "Repayment credit"
        df8['entity'] = "NA"
        df8['entity_bank'] = "NA"
        df8['source_of_trans']='Self Initiated'
        df8['mode']='NA'
        
    except:
        pass     
    
    try:
        #subsetting BY INT transactions
        df9=corp_df[corp_df["Description"].str.contains(pat="BY INT ")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="BY INT ")]
        temp_df9=df9.Description.str.split(" ", expand=True)
        df9["sub_mode"]= temp_df9[0]+" "+temp_df9[1]
        df9['entity'] = "NA"
        df9['entity_bank'] = "NA"
        df9['source_of_trans']='Automated'
        df9['mode']='Interest'
    except:
        pass  
    
    #subsetting FUND TRANSFER transactions
    try:
        
        df10=corp_df[corp_df["Description"].str.contains(pat="FUND TRANSFER")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="FUND TRANSFER")]
        temp_df10=df10.Description.str.split("BY", expand=True)
        df10['sub_mode']=temp_df10[0]
        df10[["other1","other2", "entity"]] = df10.Description.str.split("/", expand=True)
        df10['entity_bank'] = "NA"
        df10['source_of_trans']='Self Initiated'
        df10["mode"]='Net Banking'
        df10.drop(["other1","other2"], axis = 1, inplace=True)
    
    except:
        pass 
    
    #subsetting NEFT fm transactions
    try:
        df11=corp_df[corp_df["Description"].str.contains(pat="NEFT fm")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="NEFT fm")]
        temp5=df11.Description.str.split("NEFT fm ", expand=True)
        temp5=temp5[1].str.split(":", expand=True)
        temp_df11=df11.Description.str.split(" ", expand=True)
        df11["sub_mode"]= temp_df11[0]
        df11['entity'] = temp5[0]
        df11['entity_bank'] = "NA"
        df11['source_of_trans']='Self Initiated'
        df11["mode"]='Net Banking'
    
    except:
        pass 
    
    #subsetting RETURNED transactions
    try:
        df12=corp_df[corp_df["Description"].str.contains(pat="RETURNED")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="RETURNED")]
        df12["sub_mode"]= "RETURNED"
        df12['entity'] = "NA"
        df12['entity_bank'] = "NA"
        df12['source_of_trans']='Automated'
        df12["mode"]='NA'
    
    except:
        pass 
    
    
    #subsetting To transactions
    try:
        df13=corp_df[corp_df["Description"].str.contains(pat="Months")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="Months")]
        df13["sub_mode"]= "NA"
        df13['entity'] = "NA"
        df13['entity_bank'] = "NA"
        df13['source_of_trans']='Self Initiated'
        df13["mode"]='Other'
    
    except:
        pass
    
    #subsetting Charges for NEFT REF transactions
    try:
        df14=corp_df[corp_df["Description"].str.contains(pat="Charges for NEFT REF")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="Charges for NEFT REF")]
        df14["sub_mode"]= "Charges for NEFT REF"
        df14['entity'] = "NA"
        df14['entity_bank'] = "NA"
        df14['source_of_trans']='Automated'
        df14["mode"]='Net Banking'
    
    except:
        pass
    
    #subsetting Charges for RTGS REF transactions
    try:
        df15=corp_df[corp_df["Description"].str.contains(pat="Charges for RTGS REF")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="Charges for RTGS REF")]
        temp_df15=df15.Description.str.split(":", expand=True)
        df15["sub_mode"]= temp_df15[0]
        df15['entity'] = "NA"
        df15['entity_bank'] = "NA"
        df15['source_of_trans']='Automated'
        df15["mode"]='Charges'
    
    except:
        pass
    
    #subsetting INDUSIND BANK CR CARD transactions
    try:
        df16=corp_df[corp_df["Description"].str.contains(pat="INDUSIND BANK CR CARD")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="INDUSIND BANK CR CARD")]
        temp_df16=df16.Description.str.split("/", expand=True)
        df16["sub_mode"]=temp_df16[0]
        df16['entity'] = "NA"
        df16['entity_bank'] = "NA"
        df16['source_of_trans']='Automated'
        df16["mode"]='Card'
    except:
        pass
    
    #subsetting KOTAK transactions
    try:
        df17=corp_df[corp_df["Description"].str.contains(pat="KOTAK")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="KOTAK")]
        temp_df17=df17.Description.str.split("/", expand=True)
        df17["sub_mode"]= temp_df17[0]
        df17['entity'] = "NA"
        df17['entity_bank'] = "NA"
        df17['source_of_trans']='Self Initiated'
        df17["mode"]='NA'
    except:
        pass
    
    
    #subsetting NEFT TO transactions
    try:
        df18=corp_df[corp_df["Description"].str.contains(pat="NEFT TO")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="NEFT TO")]
        temp6=df18.Description.str.split("NEFT TO ", expand=True)
        temp6=temp6[1].str.split(":", expand=True)
        temp_df18=df18.Description.str.split(" ", expand=True)
        df18["sub_mode"]=temp_df18[0]
        df18['entity'] = temp6[0]
        df18['entity_bank'] = "NA"
        df18['source_of_trans']='Self Initiated'
        df18["mode"]='Net Banking'
    except:
        pass
    
    #subsetting Cheque leaf charges transactions
    try:
        df19=corp_df[corp_df["Description"].str.contains(pat="Cheque leaf charges")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="Cheque leaf charges")]
        temp_df19=df19.Description.str.split("/", expand=True)
        df19["sub_mode"]= temp_df19[0]
        df19['entity'] = "NA"
        df19['entity_bank'] = "NA"
        df19['source_of_trans']='Automated'
        df19["mode"]='Charges'
    except:
        pass
    
    
    #subsetting CBDT transactions
    try:
        df20=corp_df[corp_df["Description"].str.contains(pat="CBDT")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="CBDT")]
        temp_df20=df20.Description.str.split(" ", expand=True)
        df20["sub_mode"]= temp_df20[0]
        df20['entity'] = "NA"
        df20['entity_bank'] = "NA"
        df20['source_of_trans']='Automated'
        df20["mode"]='NA'
    except:
        pass
    
    #subsetting GOODS AND SERVICE TAX  transactions
    try:
        df21=corp_df[corp_df["Description"].str.contains(pat="GOODS AND SERVICE TAX ")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="GOODS AND SERVICE TAX ")]
        temp_df21=df21.Description.str.split("/", expand=True)
        df21["sub_mode"]= temp_df21[0]
        df21['entity'] = "NA"
        df21['entity_bank'] = "NA"
        df21['source_of_trans']='Automated'
        df21["mode"]='NA'
    except:
        pass
    
    
    #subsetting ACH-DR  transactions
    try:
        df22=corp_df[corp_df["Description"].str.startswith("ACH")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="ACH")]
        df22=df22[~df22["Description"].str.startswith("ACHDR")]
        temp12=df22[df22["Description"].str.startswith("ACH-")]
        temp12['new'] = temp12['Description'].str.split("/")
        temp12['new1'] = temp12['Description'].str.split("-")
        df22['sub_mode']=temp12['new'].apply(lambda x:x[0]).str[:6]
        df22['entity']=temp12['new1'].apply(lambda x:x[2])
        df22['entity_bank'] = "NA"
        df22['source_of_trans']='Automated'
        df22["mode"]='NA'
    except:
        pass
    
    #subsetting BY Trf transactions
    try:
        df23=corp_df[corp_df["Description"].str.contains(pat="BY TRF")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="BY TRF")]
        temp11=df23.Description.str.split("BY TRF ", expand=True)
        temp_df23=df23.Description.str.split(" ", expand=True)
        df23["sub_mode"]= temp_df23[0]+" "+temp_df23[1]
        df23['entity'] = temp11[1]
        df23['entity_bank'] = "NA"
        df23['source_of_trans']='Self Initiated'
        df23["mode"]='NA'
    except:
        pass
    
    try:
        ACH=corp_df[corp_df["Description"].str.startswith("ACH")]
        df25=ACH[~ACH["Description"].str.startswith("ACH-")]
        df25['new'] = df25['Description'].str.split("/")
        df25['sub_mode']=df25['new'].apply(lambda x:x[0]).str[:5]
        df25['entity']=df25['new'].apply(lambda x:x[0]).str[5:]
        df25['entity_bank'] = "NA"
        df25['source_of_trans']='Automated'
        df25["mode"]='NA'
        df25.drop(["new",], axis = 1, inplace=True)
    except:
        pass
    
    #subsetting loan transactions
    try:
        df26=corp_df[corp_df["Description"].str.contains(pat="LOAN")]
        temp_df=temp_df[~temp_df["Description"].str.contains(pat="LOAN")]
        temp14=df26.Description.str.split("/", expand=True)
        df26['sub_mode']=temp14[0]
        df26['entity']="NA"
        df26['entity_bank'] = "NA"
        df26['source_of_trans']='Automated'
        df26["mode"]='Loan'
    except:
        pass
    
    #subsetting others and TO transactions
    try:
        df24=temp_df
        df24["sub_mode"]= "NA"
        df24['entity'] = "NA"
        df24['entity_bank'] = "NA"
        df24['source_of_trans']='NA'
        df24["mode"]='Others'
    except:
        pass
        
    
    final = pd.concat([df1,df2,df3,df4,df5,df6,df7,df8,df9,df10,df11,df12,df13,df14,df15,df16,df17,df18,df19,df20,df21,df22,df23,df24,df25,df26], axis=0)
    
    final = final.sort_index()
    final = final[['Txn Date', 'Description', 'Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number','mode','entity','source_of_trans','entity_bank','sub_mode']]
    
    return final

    #exporting the file
    #final.to_csv("{}\\{}_{}_{}.csv".format(out_path,file_name, account_no, last_trans_date),index=False)


#try:
#    corporation_digitization(r"D:\D Drive\RAJAT\UW kit\Bank statements\STATEMENT FROM MITHUN\corporation bank\01-10-2019 to 31-12-2019.pdf",
#                             r"D:\D Drive\RAJAT\UW kit\Bank statements\STATEMENT FROM MITHUN\corporation bank\digitized")
#except:
#    print("\nThis statement cannot be digitized. \n")