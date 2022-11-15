from pandas import set_option, isna, DataFrame, concat, to_datetime, notna
from numpy import nan, where
from tabula import read_pdf
from datetime import datetime as dt
from time import time
set_option('mode.chained_assignment', None)


def axis_digitization(pdf_path,pdf_password):
    start = time()
    def concat_desc(df):
        for j in range(len(df)):
            if not isna(df['Particulars'][j]) and df['Particulars'][j].startswith("OPENING BALANCE"):
                continue
            if not isna(df['Particulars'][j]) and df['Particulars'][j]=="TRANSACTION TOTAL DR/CR" :
                break
            if isna(df['Txn Date'][j]) and not isna(df['Particulars'][j]):
                if (j+1)<len(df):
                    df['Particulars'][j+1]=str(df['Particulars'][j])+str(df['Particulars'][j+1])
        df.dropna(subset=['Txn Date'],inplace=True)
        df.reset_index(drop=True,inplace=True)
        return df
        
    col2str = {'dtype': str}
    file_name=pdf_path.split('\\')[-1][:-4]
    passcode=''
    try:
        #if file is encrypted but with empty password
        tables =read_pdf(pdf_path, pages='all',password=passcode, pandas_options = col2str)
    except:
        #if the file is encrypted with a non empty password
        passcode=''
        tables = read_pdf(pdf_path, pages='all',password=passcode, pandas_options = col2str)
    
    if len(tables)==0:
        print("This is an image-based statement, hence, cannot be digitized here")
        return
    
    if tables[0].columns[1].startswith("Value") and tables[0].columns[1].endswith("Date"):
        #non retail statements
        col_name=['Txn Date', 'Value Date', 'Particulars', 'Cheq No','Amount', 'DR/CR', 'Balance', 'Branch Name']
        master_table=DataFrame()
        #len-3 bcz last page is being twice
        for i in range(len(tables)):
            if len(tables[i].columns)==8:
                tables[i].columns=col_name
                #removing last unwanted lines of closing balance
                #version before 2k19
                if tables[i]['Particulars'].str.contains("TRANSACTION TOTAL DR/CR").any():
                    v_2020=False
                    idx=tables[i].index[tables[i]['Particulars']=="TRANSACTION TOTAL DR/CR"][0]
                    tables[i]=tables[i][:idx]
                    #handling duplicate dataframes for last page (occurs in some files)
                    if i!=(len(tables)-1):
                        tables=tables[:(i+1)]
                    tables[i]=concat_desc(tables[i])
                    master_table=concat([master_table,tables[i]])
                    break
                #version 2020
                if tables[i]['Txn Date'].str.startswith("TRANSACTION TOTAL DR/CR").any():
                    v_2020=True
                    tables[i]['Txn Date']=tables[i]['Txn Date'].astype(str)
                    idx=tables[i].index[tables[i]['Txn Date'].str.startswith("TRANSACTION TOTAL DR/CR")][0]
                    tables[i]['Txn Date']=[nan if i=="nan" else i for i in tables[i]['Txn Date']]
                    tables[i]=tables[i][:idx]
                    #handling duplicate dataframes for last page (occurs in some files)
                    if i!=(len(tables)-1):
                        tables=tables[:(i+1)]
                    tables[i]=concat_desc(tables[i])
                    master_table=concat([master_table,tables[i]])
                    break
                tables[i]=concat_desc(tables[i])
                tables[i].sort_index(inplace=True)
                if i>0 and len(tables[i]['Txn Date'])==len(tables[i-1]['Txn Date']) and (tables[i]['Txn Date']==tables[i-1]['Txn Date']).all():
                    continue
                master_table=concat([master_table,tables[i]])
            else:
                #to handle any exception in format
                if len(tables[i].columns)!=5:
                    print("check for tables["+i+"]")
                    
        master_table.reset_index(inplace=True,drop=True)
        if v_2020:
            master_table['Debit'] = master_table.loc[master_table['DR/CR'] == "Dr" , 'Amount']
            master_table['Credit'] = master_table.loc[master_table['DR/CR'] == "Cr" , 'Amount']
        else:
            master_table['Debit'] = master_table.loc[master_table['DR/CR'] == "DR" , 'Amount']
            master_table['Credit'] = master_table.loc[master_table['DR/CR'] == "CR" , 'Amount']
        master_table.rename({'Particulars':'Description'},inplace=True,axis=1)
        master_table.drop(['Value Date','Amount','DR/CR','Branch Name'],axis=1,inplace=True)
        master_table.dropna(subset=['Txn Date'],inplace=True)
        master_table2=master_table.reset_index(drop=True)
        #reading account information corresponding to versions
        if v_2020==True:
            cust_info=read_pdf(pdf_path, pages=1,password=passcode,area=[38.6,9.5,179.9,573.8],pandas_options={'header':None},stream=True)
        else:
            cust_info=read_pdf(pdf_path, pages=1,password=passcode,area=[56.1,34,183.6,564.1],pandas_options={'header':None},stream=True)
    else:
        v_2020=False
        #cust_info=tabula.read_pdf(pdf_path, pages=1,password=passcode,area=[56.1,34,183.6,564.1],pandas_options={'header':None})
        cust_info=read_pdf(pdf_path, pages=1,password=passcode,area=[49.9,28.7,192.1,575.6],pandas_options={'header':None})
        for i in range(len(tables)):
            if len(tables[i].columns)==8:
                if "Unnamed: 0" in tables[i].columns:
                    tables[i].drop('Unnamed: 0',axis=1,inplace=True)
                tables[i].columns = ['Tran Date','Cheq no','Particulars', 'Debit', 'Credit','Balance','Init.Br']
            else:
                continue
            
        for i in range(len(tables)):
            if len(tables[i].columns)==6:
                tables[i].insert(1,'Cheq no',nan)
                
            
        #Giving proper names to the headers in the tables other than the first one(which did not have proper header beforehand)
        for i in range(len(tables)):
            if len(tables[i].columns)==7:
                if tables[i].columns[0]=='Tran Date':
                    tables[i].columns = ['Tran Date','Cheq no','Particulars', 'Debit', 'Credit','Balance','Init.Br']
                elif tables[i].columns[0]!='Tran Date':
                    tables[i].loc[max(tables[i].index)+1,:] = None
                    tables[i] = tables[i].shift(1,axis=0)
                    tables[i].iloc[0] = tables[i].columns
                    tables[i].columns = ['Tran Date','Cheq no','Particulars', 'Debit', 'Credit','Balance','Init.Br']        
            else :
                continue
            
        # For replacing the unwanted values in the 1 row of the table which would create problems in the calculations in the column        
        #for i in range(len(tables)):
        #   tables[i].replace(to_replace=['Unnamed: 0','Unnamed: 1','Unnamed: 2'], value=np.nan,inplace=True)
        for i in range(len(tables)):
            for x in tables[i].index:
                for j in tables[i].columns :
                    if type(tables[i].loc[x][j])==str and tables[i].loc[x][j].startswith('Unnamed:') :
                        tables[i].loc[x][j] = nan
                    else:
                        continue
                    
        for i in range(len(tables)):
            for x in tables[i].index:
                if type(tables[i]['Tran Date'][x])==str and len(tables[i]['Tran Date'][x])>10:
                    tables[i]['Tran Date'][x]=nan
                else:
                    continue
        #concat_desc
        for i in range(len(tables)):
            if tables[i].empty:
                continue
            df=tables[i]
            for j in range(len(df)):
                if not isna(df['Particulars'][j]) and df['Particulars'][j]=="OPENING BALANCE" :
                    continue
                if not isna(df['Particulars'][j]) and df['Particulars'][j]=="TRANSACTION TOTAL DR/CR" :
                    break
                if isna(df['Tran Date'][j]) and not isna(df['Particulars'][j]):
                    if (j+1)<len(df) and not isna(df['Particulars'][j+1]):
                        df['Particulars'][j+1]=str(df['Particulars'][j])+str(df['Particulars'][j+1])
            df.dropna(subset=['Tran Date'],inplace=True)
            df.reset_index(drop=True,inplace=True)
            tables[i]=df
            
        # Appending all tables of a pdf
        master_table = tables[0]
                        
        for i in range(len(tables)-1) :
            master_table = concat([master_table, tables[i+1]])
            
        master_table=master_table.drop_duplicates(keep='first')
        master_table.rename(columns={'Tran Date':'Txn Date','Particulars':'Description'}, inplace=True)
        
    
    #extracting customer information
    if v_2020==True:
        account_name=cust_info[0].iloc[cust_info[0][0].first_valid_index()+1,0]
    else:
        account_name=cust_info[0].iloc[0,0]
    for i in range(len(cust_info[0])):
        for j in range(len(cust_info[0].columns)):
            if type(cust_info[0].iloc[i,j])==str and (cust_info[0].iloc[i,j].find('Account No :')!=-1):
                acc_no_string="{}".format(cust_info[0].iloc[i,j].split(':')[1].strip())
                account_no="'{}'".format(acc_no_string.split()[0])
                break
            if type(cust_info[0].iloc[i,j])==str and (cust_info[0].iloc[i,j].find('FOR A/C:')!=-1):
                account_no="'{}'".format(cust_info[0].iloc[i,j].split(':')[1].strip())
                break
    
    ## adding three columns in the master table 
    master_table['Account Name'] = account_name
    master_table['Account Number'] = account_no
    
    master_table2 = master_table.reset_index(drop=True)
    
    master_table2['Txn Date'] = [dt.strftime(to_datetime(x, dayfirst=True),"%d-%m-%Y") for x in master_table2['Txn Date']]
    master_table2 = master_table2[['Txn Date', 'Cheq no', 'Description', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number']]
    last_trans_date = master_table2['Txn Date'].iat[-1]

    ## NOW PERFORMING FEW LOGICAL CHECKS TO CHECK DIGITIZATION HAS NO ISSUE
    
    df = DataFrame(master_table2)
    column_names=['Statement_name','Wrong Credit', 'Wrong Debit', 'Remark']
    result=DataFrame(index=[1],columns=column_names)
    
    if df['Credit'].dtype =='O':
        df['Credit_changed'] = (df['Credit'].astype(str).str.replace(',','')).astype(float)
    else:
        df['Credit_changed']= df['Credit'].astype(float)
    if df['Debit'].dtype =='O':
        df['Debit_changed'] = (df['Debit'].astype(str).str.replace(',','')).astype(float)
    else:
        df['Debit_changed']= df['Debit'].astype(float)
    if df['Balance'].dtype =='O':
        df['Balance_changed'] = (df['Balance'].astype(str).str.replace(',','')).astype(float)
    else:
        df['Balance_changed']= df['Balance'].astype(float)
        
    
    col_credit=df.columns.get_loc('Credit_changed')
    col_debit=df.columns.get_loc('Debit_changed')
    col_bal=df.columns.get_loc('Balance_changed')
    for i in range(1,len(df)):
        #check 1 having, both debit and credit values
        if  (isna(df.iloc[i,col_debit]) and isna(df.iloc[i,col_credit])) or (notna(df.iloc[i,col_debit]) and notna(df.iloc[i,col_credit])) :
            data=DataFrame({'Statement_name':file_name,'Wrong Credit': (i+2),'Wrong Debit':(i+2), 'Remark':'Only one of Debit/Credit should be filled'},index=[0])
            result=concat([result,data])                
    
        #check 2, balance check
        else:
            #debited
            if isna(df.iloc[i,col_credit]):
                if df.iloc[i,col_debit]>0:
                    if df.iloc[i-1,col_bal]<df.iloc[i,col_bal]:
                        data=DataFrame({'Statement_name':file_name,'Wrong Credit': nan,'Wrong Debit':(i+2), 'Remark':'Balance should be less than previous since debit>0'},index=[0])
                        result=concat([result,data])
                else:
                    if df.iloc[i-1,col_bal]>df.iloc[i,col_bal]:
                        data=DataFrame({'Statement_name':file_name,'Wrong Credit': nan,'Wrong Debit':(i+2),'Remark':'Balance should be more than previous since debit<0'},index=[0])
                        result=concat([result,data])
                  
    
            #credited
            elif isna(df.iloc[i,col_debit]):
                if df.iloc[i,col_credit]>0:
                    if df.iloc[i-1,col_bal]>df.iloc[i,col_bal]:
                        data=DataFrame([{'Statement_name':file_name,'Wrong Credit': (i+2),'Wrong Debit':nan,'Remark':'Balance should be more than previous since credit>0'}],index=[0])
                        result=concat([result,data])
                else:
                    if df.iloc[i-1,col_bal]<df.iloc[i,col_bal]:
                        data=DataFrame([{'Statement_name':file_name,'Wrong Credit': (i+2),'Wrong Debit':nan,'Remark':'Balance should be less than previous since credit<0'}],index=[0])
                        result=concat([result,data])    
    
    result = result.dropna(how='all')
    
    # will continue only if 'result' is an empty dataframe
    if len(result)==0:
        print("go ahead")
        pass
    else:
        print("\nThere are issues found after the Logical checks.\nThe digtitized output and the issues have been exported in CSVs.\n")
        #master_table2.to_csv("{}/{}_Digitized.csv".format(out_path,file_name),index=False)        
        #result.to_csv("{}/{}_LogicalChecks.csv".format(out_path,file_name),index=False)
        return

    # NOW THE ENTITY EXTRACTION PART
    axis = DataFrame(master_table2)
    axis["Description"]=axis["Description"].str.lstrip()
    axis['Credit_Debit']=where(axis['Credit'].isna(), "Debit","Credit")
    
    #Converting string date into datetime 
    axis["Txn Date"]=to_datetime(axis["Txn Date"], format = '%d-%m-%Y')
    axis["month_name"]= axis["Txn Date"].dt.strftime('%b')
    axis["month_year"]= axis["Txn Date"].dt.to_period('M')
    axis["weekday"]= axis["Txn Date"].dt.strftime('%A')
    
    #Converting string into float 
    axis["Debit"] = axis["Debit"].apply(lambda x: float(str(x).replace(",","")))
    axis["Credit"] = axis["Credit"].apply(lambda x: float(str(x).replace(",","")))
    axis["Balance"] = axis["Balance"].apply(lambda x: float(str(x).replace(",","")))
    
       #subsetting upi transactions
    try:
       df1=axis[axis["Description"].str.startswith("UPI")]
       df1['new'] = df1.Description.str.split("/")
       df1['count']=df1['new'].apply(lambda x: len(x))
       df1['sub_mode'] = df1['new'].apply(lambda x:x[0])
       df1['entity']= df1['new'].apply(lambda x:x[3])
       df1['entity_bank'] = 'NA'
       df1['source_of_trans']='Self Initiated'
       df1['mode']="Mobile App"
       df1.drop(['new','count'], axis=1, inplace=True)
    except:
       pass
       
       #subsetting pos transactions
    try:
       df2=axis[axis["Description"].str.startswith("POS")]
       df2['new'] = df2.Description.str.split("/")
       df2['sub_mode'] = df2['new'].apply(lambda x:x[0])
       df2['entity']=df2['new'].apply(lambda x:x[1])
       df2['entity_bank'] = "NA"
       df2['source_of_trans']='Self Initiated'
       df2['mode']="Card"
       df2.drop(['new'], axis=1, inplace=True)
    except:
       pass
       
       #subsetting ECOM PUR transactions
    try:
       df3=axis[axis["Description"].str.startswith("ECOM")]
       df3['new'] = df3.Description.str.split("/")
       df3['sub_mode'] = df3['new'].apply(lambda x:x[0])
       df3['entity']=df3['new'].apply(lambda x:x[1])
       df3['entity_bank'] = "NA"
       df3['source_of_trans']='Self Initiated'
       df3['mode']="Mobile Apps"
       df3.drop(['new'], axis=1, inplace=True)
    except:
       pass
       
       #subsetting  MOB transactions
    try:
       df4=axis[axis["Description"].str.startswith("MOB")]
       df4['new']=df4.Description.str.split("/")
       df4['count']=df4['new'].apply(lambda x: len(x))
       df4['sub_mode']=df4['new'].apply(lambda x:x[0])
       df4['entity']=df4['new'].apply(lambda x:x[2])
       df4['entity_bank'] = "NA"
       df4['source_of_trans']='Self Initiated'
       df4['mode']='Mobile App'
       df4.drop(['new', 'count'], axis=1, inplace=True)
    except:
       pass
       
       #subsetting ATM-CASH transactions
    try:
       df5=axis[axis["Description"].str.contains(pat="ATM-CASH")]
       df5['new']=df5.Description.str.split("/")
       df5['count']=df5['new'].apply(lambda x: len(x))
       df5['sub_mode']=df5['new'].apply(lambda x:x[0])
       df5['entity']=df5['new'].apply(lambda x:x[1])
       df5['entity_bank'] = "NA"
       df5['source_of_trans']='Self Initiated'
       df5['mode']='Cash'
       df5.drop(['new', 'count'], axis=1, inplace=True)
    except:
       pass
       
    try:
       df26=axis[axis["Description"].str.contains(pat="BY CASH DEPOSIT-")]
       df26['new']=df26.Description.str.split("/")
       df26['count']=df26['new'].apply(lambda x: len(x))
       df26['sub_mode']=df26['new'].apply(lambda x:x[0])
       df26['entity']=df26['new'].apply(lambda x:x[1])
       df26['entity_bank'] = "NA"
       df26['source_of_trans']='Self Initiated'
       df26['mode']='Cash'
       df26.drop(['new', 'count'], axis=1, inplace=True)
    except:
       pass
       #subsetting EMI transactions
       
    try:
       df22=axis[axis['Description'].str.startswith('BRN-CLG-CHQ')]
       df22['new']=df22.Description.str.split('/')
       df22['entity_bank']=df22['new'].apply(lambda x:x[1])
       df22['A']=df22['new'].apply(lambda x:x[0])
       df22['B']=df22['A'].str.split('TO')
       df22['entity']=df22['B'].apply(lambda x:x[1])
       df22['sub_mode']='EMI'
       df22['mode']='Loan'
       df22['source_of_trans']='Automated'
       df22.drop(['new', 'A','B'], axis=1, inplace=True)
       
       
       # df22.drop(['new', 'count'], axis=1, inplace=True)
       
       
       
    except:
       pass
       
    try:
        df6=axis[axis["Description"].str.contains("EMI")]
        df6['sub_mode']='EMI'
        df6['entity'] = "NA"
        df6['entity_bank'] = "NA"
        df6['source_of_trans']="Automated"
        df6['mode']="Loan"
       
    except:
        pass 
       
       #subsetting Charges transactions
    
    try:
        df25 = axis[(axis['Description'].str.startswith('Consolidated Charges'))]
        df25['sub_mode']='Charges'
        df25['entity']='Bank'
        df25['entity_bank'] = "Axis Bank"
        df25['source_of_trans']='Self Initiated'
        df25['mode']="Charges"
    except:
        pass
       
    try:
       df7 = axis[(axis['Description'].str.startswith('Dr Card Charges'))]
       df7['sub_mode']='Charges'
       df7['entity']='Bank'
       df7['entity_bank'] = "Axis Bank"
       df7['source_of_trans']='Automated'
       df7['mode']="Charges"
       df7.drop(['new'], axis=1, inplace=True)
    except:
      pass
       
       #subsetting Investment transactions
    try:
        df8=axis[axis["Description"].str.startswith("NACH")]
        df8['new'] = df8.Description.str.split("-")
        df8['sub_mode']=df8['new'].apply(lambda x:x[0])
        df8['entity']=df8['new'].apply(lambda x:x[-1])
        df8['source_of_trans']='Automated'
        df8['mode']='Loan'
        df8['entity_bank']='NA'
    
        df8.drop(['new'], axis=1, inplace=True)
    except:
        pass
       
       #subsetting Refund transactions
    try:
       df9=axis[axis["Description"].str.contains(pat="REFUND", case=False)]
       df9['new'] = df9.Description.str.split("/")
       df9['sub_mode'] = df9['new'].apply(lambda x:x[0])
       df9['entity'] = df9['new'].apply(lambda x:x[1])
       df9['entity_bank'] = "NA"
       df9['source_of_trans']='Automated'
       df9['mode']='Refund'
       # df9.drop(['new'], axis=1, inplace=True)
       
    except:
       pass
       
       #subsetting TB transactions
    try:
       df10=axis[axis["Description"].str.startswith(pat="TRANSFER")]
       df10["new"] = df10.Description.str.split("/")
       df10['sub_mode'] = df10['new'].apply(lambda x:x[0]+" "+x[1])
       df10['entity'] = df10['new'].apply(lambda x:x[3])
       df10['entity_bank']='NA'
       df10['source_of_trans']='Self Initiated'
       df10['mode']='credit'
       df10.drop(["new"], axis = 1, inplace=True)
    except:
       pass
       
       #subsetting REVERSAL transactions
    try:
       df11=axis[axis["Description"].str.contains(pat="CASH-REVERSAL-ATM")]
       df11['sub_mode'] = "CASH-REVERSAL-ATM"
       df11['entity'] = "NA"
       df11['entity_bank'] = "NA"
       df11['source_of_trans']='Automated'
       df11['mode']='Reversal'
       
    except:
       pass
       
       #subsetting Interest transactions
    try:
       
       df12=axis[axis["Description"].str.contains(pat="Int.Pd")]
       df12['sub_mode'] = "Int.Pd"
       df12['entity'] = "NA"
       df12['entity_bank'] = "NA"
       df12['source_of_trans']='Automated'
       df12['mode']='Interest'
       
    except:
       pass
       
       #subsetting JANALAKSHMI FIN transactions
    try:
       df13=axis[axis["Description"].str.contains(pat="JANALAKSHMI FIN")]
       df13['sub_mode'] = "NA"
       df13[["entity", "other1"]] = df13.Description.str.split("/", expand=True)
       df13['entity_bank'] = "NA"
       df13['source_of_trans']='Self Initiated'
       df13['mode']='Loan'
       df13.drop(["other1"], axis = 1, inplace=True)
       
    except:
       pass
       
       #subsetting RTGS transactions
    try:
       df14=axis[axis["Description"].str.startswith("RTGS")]
       df14['new']=df14.Description.str.split("/")
       df14['sub_mode']=df14['new'].apply(lambda x:x[0])
       df14['entity'] = df14['new'].apply(lambda x:x[2])
       df14['entity_bank'] = "NA"
       df14['source_of_trans']="Self initiated"
       df14['mode']="Net Banking"
       df14.drop(["new"], axis = 1, inplace=True)
       
    except:
       pass 
       
       #subsetting IMPS transactions
    try:
       df15=axis[axis["Description"].str.startswith(pat="IMPS")]
       df15['new']=df15.Description.str.split("/")
       df15['count']=df15['new'].apply(lambda x: len(x))
       df15['sub_mode']=df15['new'].apply(lambda x:x[0])
       
    except:
       pass    
       
    try:
       df15a = df15[df15['count']<=5]
       df15a['entity']= df15a['new'].apply(lambda x:x[3])
       df15a["entity_bank"]="NA"
       df15a['source_of_trans']='Self Initiated'
       df15a['mode']= "Net Banking"
       df15a.drop(["new", "count"], axis = 1, inplace=True)
    except:
       pass
       
    try:
       df15b = df15[df15['count']>5]
       df15b['entity']= df15b['new'].apply(lambda x:x[3])
       df15b["entity_bank"]=df15b['new'].apply(lambda x:x[4])
       df15b['source_of_trans']='Self Initiated'
       df15b['mode']= "Net Banking"
       df15b.drop(["new", "count"], axis = 1, inplace=True)
    except:
       pass
       
       #subsetting Salary transactions
       
    try:
       df16=axis[axis["Description"].str.contains(pat="SALARY", case = False)]
    except:
       pass
    
    try:
       df16a= df16[df16["Description"].str.contains(pat="NEFT")]
       df16a['new']=df16a.Description.str.split("/")
       df16a['sub_mode']=df16a['new'].apply(lambda x:x[0])
       df16a['entity'] = df16a['new'].apply(lambda x:x[2])
       df16a['entity_bank'] = "NA"
       df16a['source_of_trans']="Automated"
       df16a['mode']="Salary"
       df16a.drop(["new"], axis = 1, inplace=True)
    except:
       pass
       
    try:
       df16b= df16[~df16["Description"].str.contains(pat="NEFT")]
       df16b['sub_mode']='Salary'
       df16b['entity'] = 'NA'
       df16b['entity_bank'] = "NA"
       df16b['source_of_trans']="Automated"
       df16b['mode']="Salary"
    except:
       pass
       
       #subsetting By Clg transactions
       
    try:
       df17=axis[axis["Description"].str.contains(pat="By Clg")]
       df17['new']=df17.Description.str.split(" ")
       df17['sub_mode']=df17['new'].apply(lambda x:x[0]+" "+x[1])
       df17['entity'] = "NA"
       df17['entity_bank'] = "NA"
       df17['source_of_trans']="Self Initiated"
       df17['mode']="NA"
       df17.drop(["new"], axis = 1, inplace=True)
       
    except:
       pass
       
       #subsetting ECS transactions
    try:
       df18=axis[axis["Description"].str.startswith("ECS")]
       df18['new']=df18.Description.str.split("/")
       df18['sub_mode']=df18['new'].apply(lambda x:x[0])
       df18['entity'] = df18['new'].apply(lambda x:x[1])
       df18['entity_bank'] ='NA'
       df18['source_of_trans']="Self Initiated"
       df18['mode']="Loan"
       df18.drop(["new"], axis = 1, inplace=True)
    except:
       pass 
       
       
       #subsetting INB transactions
       
       
    try:
        df19 = axis[axis["Description"].str.startswith("INB/IFT")]
        df19['new']=df19.Description.str.split("/")
        df19['sub_mode']=df19['new'].apply(lambda x:x[0]+" "+x[1])
        df19['entity'] = df19['new'].apply(lambda x:x[2])
        df19['entity_bank'] = "NA"
        df19['source_of_trans']="Self Initiated"
        df19['mode']="Net Banking"
        df19.drop(["new"], axis = 1, inplace=True)
    except:
       pass 
       
    try:
        df28 = axis[axis["Description"].str.startswith("INB/NEFT")]
        df28['new']=df28.Description.str.split("/")
        df28['sub_mode']=df28['new'].apply(lambda x:x[0]+" "+x[1])
        df28['entity'] = df28['new'].apply(lambda x:x[2])
        df28['entity_bank'] = "NA"
        df28['source_of_trans']="Self Initiated"
        df28['mode']="Net Banking"
        df28.drop(["new"], axis = 1, inplace=True)
    except:
       pass 
    
    
    try:
        df29=axis[axis["Description"].str.startswith("INB")]
        df29=df29[~df29["Description"].str.startswith("INB/IFT")]
        df29=df29[~df29["Description"].str.startswith("INB/NEFT")]
        df29['new']=df29.Description.str.split("/")
        df29['sub_mode']=df29['new'].apply(lambda x:x[0])
        df29['entity'] = df29['new'].apply(lambda x:x[2])
        df29['entity_bank'] = "NA"
        df29['source_of_trans']="Self Initiated"
        df29['mode']="Net Banking"
        df29.drop(["new"], axis = 1, inplace=True)
        
    except:
        pass 
       
    
       
       
       #subsetting NEFT transactions
    try:
       df20=axis[axis["Description"].str.contains(pat="NEFT")]
       df20=df20[~df20["Description"].str.contains(pat="Salary", case=False)]
       df20=df20[~df20["Description"].str.contains(pat="INB", case=False)]
       df20['new']=df20.Description.str.split("/")
       df20['count']=df20['new'].apply(lambda x: len(x))
    except:
       pass    
       
    try:
       df20a = df20[df20["Description"].str.contains(pat="MB/")]
       df20a['entity']= df20a['new'].apply(lambda x:x[3])
       df20a['sub_mode']=df20a['new'].apply(lambda x:x[0]+" "+x[1])
       df20a['entity_bank'] = "NA"
       df20a['source_of_trans']="Self Initiated"
       df20a['mode']="Net Banking"
       df20a.drop(["new","count"], axis = 1, inplace=True)
    except:
       pass 
       
    try:
       df20b = df20[~df20["Description"].str.contains(pat="MB/")]
       df20b['entity']= df20b['new'].apply(lambda x:x[2])
       df20b['sub_mode']=df20b['new'].apply(lambda x:x[0])
       df20b['entity_bank'] = "NA"
       df20b['source_of_trans']="Self Initiated"
       df20b['mode']="Net Banking"
       df20b.drop(["new","count"], axis = 1, inplace=True)
    except:
       pass 
       
    try:
       df21=axis[axis["Description"].str.startswith("TRF")]
       df21['new']=df21.Description.str.split("/")
       df21['sub_mode']=df21['new'].apply(lambda x:x[0])
       df21['entity']=df21['new'].apply(lambda x:x[1])
       df21['source_of_trans']="Self Initiated"
       df21['mode']='Transfer'
       df21['entity_bank']='NA'
       df21.drop(["new"], axis = 1, inplace=True)
       
    except:
       pass
       
       
    try:
       df23=axis[axis['Description'].str.startswith('IFT')]
       df23['new']=df23['Description'].str.split('/')
       df23['sub_mode']=df23['new'].apply(lambda x:x[0])
       df23['entity'] = df23['new'].apply(lambda x:x[1])
       df23['entity_bank'] = "NA"
       df23['source_of_trans']="Self Initiated"
       df23['mode']="Net Banking"
       df23.drop(["new"], axis = 1, inplace=True)   
    except:
       pass
    try:
       df24=axis[axis['Description'].str.startswith('SAK/CASH DEP')]
       df24['new']=df24.Description.str.split('/')
       df24['sub_mode']='Cash Deposit'
       df24['entity']=df24['new'].apply(lambda x:x[4])
       df24['entity_bank']='NA'
       df24['source_of_trans']="Self Initiated"
       df24['mode']="Cash"
       df24.drop(["new"], axis = 1, inplace=True) 
    except:
       pass
       
    try:
       df30=axis[axis['Description'].str.startswith('SAK/CASH WDL')]
       df30['new']=df30.Description.str.split('/')
       df30['sub_mode']='Cash Withdrawal'
       df30['entity']=df30['new'].apply(lambda x:x[4])
       df30['entity_bank']='NA'
       df30['source_of_trans']="Self Initiated"
       df30['mode']="Cash"
       df30.drop(["new"], axis = 1, inplace=True) 
        
    except:
        pass
       
       
    try:
       df27=axis[(axis['Description'].str.contains('GST'))]
       df27['sub_mode']='GST'
       df27['source_of_trans']='Automated'
       df27['mode']='Tax'
       df27['entity_bank']='NA'
       df27['entity']='NA'
    except:
       pass
   
   
   #Concatenating dfs
    t1 = concat([df1,df2,df3,df4,df5,df6,df7,df8,df9,df10,df11,df12,df13,df14,df15a,df15b,df16a,df16b,df17,df18,df19,df20a,df20b,df21,df22,df23,df24,df25,df26,df27,df28,df29,df30], axis=0)
    
    t2 = axis[~axis["Description"].isin(t1["Description"])]
    t2['mode']='Others'
    t2['entity']='NA'
    t2['source_of_trans']='NA'
    t2['entity_bank']='NA'
    t2['sub_mode']='NA'
    
    final = concat([t1,t2], axis=0)
    final['count']=final['Description'].apply(lambda x: len(x.rstrip().split('/')))
    final = final.sort_index()
    final.rename(columns={'sub-mode':'sub_mode', 'Cheq no':'Cheque Number'}, inplace=True)
    final['Txn Date'] = [dt.strftime(i, '%d/%m/%Y') for i in final['Txn Date']]
    final=final[['Txn Date', 'Description', 'Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number','mode','entity','source_of_trans','sub_mode']]
    # exporting the final table to a csv - this is final having complete transactions table appended and essential account information
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

    d = {}
    for i,j in enumerate(final['Balance']):
        if j < 0:
            d[i] = 'Overdrawn'
            if final.iloc[i]['Debit'] == final.iloc[i+1]['Credit'] and final.iloc[i]['Txn Date'] == final.iloc[i+1]['Txn Date'] and final.iloc[i]['entity'] == final.iloc[i+1]['entity']:
                d[i] = 'Bounced'
                d[i+1] = 'Bounced'
            
        else:
            if i not in d.keys():
                if final.iloc[i]["source_of_trans"]=="Automated" and final.iloc[i]["Credit"] != 0 and final.iloc[i]["Debit"]==0:
                    d[i]="Auto Credit"
                elif final.iloc[i]["source_of_trans"]=="Automated" and final.iloc[i]["Credit"] == 0 and final.iloc[i]["Debit"]!=0:
                    d[i]="Auto Debit"
                elif final.iloc[i]["source_of_trans"]=="Self Initiated" and final.iloc[i]["Credit"] != 0 and final.iloc[i]["Debit"]==0:
                    d[i]="Self Credit"
                elif final.iloc[i]["source_of_trans"]=="Self Initiated" and final.iloc[i]["Credit"] == 0 and final.iloc[i]["Debit"]!=0:
                    d[i]="Self Debit"
                else:
                    d[i]="Not available"
                        
    final["Transaction_Type"] = final.index.map(d)
    
    final['bank_name'] = 'AXIS'
    
    final['lid'] = file_name.split('_')[0]

    final.to_csv(r'C:\Users\hardi\OneDrive\Documents\Project Nishchay\A3_Demo\Bank\AXIS\{}_b.csv'.format(file_name), index=False)

    end = time()

    print(end-start)
   
    return r'C:\Users\hardi\OneDrive\Documents\Project Nishchay\A3_Demo\Bank\AXIS\{}_b.csv'.format(file_name)
    #final.to_csv("{}\\{}_{}_{}.csv".format(out_path,file_name,account_no, last_trans_date),index=False)

