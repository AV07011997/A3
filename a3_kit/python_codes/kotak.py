import pandas as pd
import numpy as np
import tabula
from datetime import datetime as dt


def kotak_digitization(pdf_path,pdf_password):

    col2str = {'dtype': str}

    pdf_file=pdf_path.split('\\')[-1][:-4]
    
    #to oversee the warning to concatenate descriptions/narrations
    pd.options.mode.chained_assignment = None
    
    passcode=''
    try:
        tables = tabula.read_pdf(pdf_path, pages='1',password=passcode, pandas_options = col2str)
        
    except:
        passcode=pdf_password
        tables = tabula.read_pdf(pdf_path, pages='1',password=passcode, pandas_options = col2str)
    
    if len(tables)==0:
        print("This is an image-based statement, hence, cannot be digitized here")
        return
    
    if 'Period' in (tables[0].columns) or 'Period:' in tables[0].columns:
        #non retail statements
        #sample statement: aryan.pdf
        tables = tabula.read_pdf(pdf_path, pages='all', area=[280.5,1.1,836.2,706.3], columns=[70.2,241.6,330.8,463.4,579.1,706.3],password=passcode, pandas_options = col2str)
        cust_info=tabula.read_pdf(pdf_path, pages=1, area=[61,15,216,553],pandas_options={'header':None,'dtype': str},password=passcode)
        if tables[-1][tables[-1]['Date'] == 'Statem'].any()['Date']:
            j = tables[-1].index[tables[-1]['Date'] == 'Statem'][0]
            tables[-1] = tables[-1].iloc[:j]
            tables[-1].reset_index(drop=True, inplace=True)
        for i in range(len(tables)):
            for j in tables[i].index :
                if type(tables[i]['Balance'][j]) == str:
                    isCR=tables[i]['Balance'][j][-4:]
                    if isCR=="(Cr)":
                        tables[i]['Balance'][j] = tables[i]['Balance'][j][:-4]
                    elif isCR=="(Dr)":
                        tables[i]['Balance'][j] = '-'+str(tables[i]['Balance'][j][:-4])
        for i in range(1,len(tables)):
            tables[0]=pd.concat([tables[0],tables[i]])
        tables[0].reset_index(inplace=True,drop=True)
        for j in range(1,len(tables[0])):
            prev_row=j-1
            while j<len(tables[0]) and pd.isna(tables[0]['Date'][j]):
                if not pd.isna(tables[0]['Chq/Ref No'][j]):
                    if pd.isna(tables[0]['Chq/Ref No'][prev_row]):
                        tables[0]['Chq/Ref No'][prev_row]=str(tables[0]['Chq/Ref No'][j])
                    else:
                        tables[0]['Chq/Ref No'][prev_row]=str(tables[0]['Chq/Ref No'][prev_row])+str(tables[0]['Chq/Ref No'][j])
                j+=1
        master_table2=tables[0]
        master_table2.rename(columns={'Narration':'Description','Withdrawal (Dr)':'Debit','Deposit(Cr)':'Credit','Chq/Ref No':'Cheque Number'},inplace=True)
        master_table2=master_table2[master_table2['Description']!="B/F"]
        master_table2.reset_index(drop=True,inplace=True)
        #concat_desc
        for j in range(1,len(master_table2)):
            prev_row=j-1
            while j<len(master_table2) and pd.isna(master_table2['Date'][j]):
                if not pd.isna(master_table2['Description'][j]):
                    master_table2['Description'][prev_row]=str(master_table2['Description'][prev_row])+str(master_table2['Description'][j])
                j+=1
        master_table2.dropna(subset=['Date'],inplace=True)
        master_table2.reset_index(inplace=True,drop=True)
        
        
        #standarising cust_info for further processing
        i=2
        while i<len(cust_info[0].columns):
            for j in range(len(cust_info[0])):
                if pd.isna(cust_info[0][cust_info[0].columns[i]][j]):
                    continue
                cust_info[0][cust_info[0].columns[1]][j]=str(cust_info[0][cust_info[0].columns[1]][j])+str(cust_info[0][cust_info[0].columns[i]][j])
            i+=1
        cust_info[0]=cust_info[0][[cust_info[0].columns[0],cust_info[0].columns[1]]]
        account_name=cust_info[0].iloc[0,0]
        for i in range(len(cust_info[0])):
            if type(cust_info[0].iloc[i,1])==str and cust_info[0].iloc[i,1].find("Account No")!=-1:
                account_no="'{}'".format(cust_info[0].iloc[i][1].split(':')[-1].strip())
        
        
    elif 'Sl. No.' in (tables[0].columns[0]):
        #format 1
        ##['Sl. No.', 'Date', 'Description', 'Chq / Ref number', 'Amount','Dr / Cr', 'Balance', 'Dr / Cr.1']
        #sample statement: HARITOSH KUMAR KOTAK BANKING
        tables = tabula.read_pdf(pdf_path, pages='1', area=[326.6, 43.1, 826.1, 844.1], columns=[83.6, 226.1, 381.3, 510.3, 623.6, 671.6, 783.3, 844.1],password=passcode)
        b = tabula.read_pdf(pdf_path, pages='all', area=[19.8, 42.3, 826.1, 844.1], columns=[83.6, 226.1, 381.3, 510.3, 623.6, 671.6, 783.3, 844.1],password=passcode)
        tables.extend(b[1:])
        del b
        cust_info=tabula.read_pdf(pdf_path, pages=1, area=[130, 34, 291, 807],pandas_options={'header':None},password=passcode)
        
        if tables[-1].columns[0] != 'Sl. No.':
            tables.pop(-1)
        if tables[-1][tables[-1]['Sl. No.'] == 'Opening'].any()['Sl. No.']:
            j = tables[-1].index[tables[-1]['Sl. No.'] == 'Opening'][0]
            tables[-1] = tables[-1].iloc[:j]
            tables[-1].reset_index(drop=True, inplace=True)
        for i in range(len(tables)):
            if len(tables[i].columns) == 8 :
                tables[i]['Debit'] = tables[i].loc[tables[i]['Dr / Cr'] == "DR" , 'Amount']
                tables[i]['Credit'] = tables[i].loc[tables[i]['Dr / Cr'] == "CR" , 'Amount']
            else:
                continue
        for i in range(1,len(tables)):
            tables[0]=pd.concat([tables[0],tables[i]])
        tables[0].reset_index(inplace=True,drop=True)
        for j in range(1,len(tables[0])):
            prev_row=j-1
            while j<len(tables[0]) and pd.isna(tables[0]['Date'][j]):
                if not pd.isna(tables[0]['Chq / Ref number'][j]):
                    if pd.isna(tables[0]['Chq / Ref number'][prev_row]):
                        tables[0]['Chq / Ref number'][prev_row]=str(tables[0]['Chq / Ref number'][j])
                    else:
                        tables[0]['Chq / Ref number'][prev_row]=str(tables[0]['Chq / Ref number'][prev_row])+str(tables[0]['Chq / Ref number'][j])
                j+=1
        master_table2=tables[0][['Date','Description','Chq / Ref number','Balance','Debit','Credit']]
        master_table2.rename(columns={'Chq / Ref number':'Cheque Number'},inplace=True)
        master_table2.reset_index(inplace=True,drop=True)
        master_table2['Date']=master_table2[['Date']].fillna(method='pad')
        #concat_desc
        for j in range(1,len(master_table2)):
            prev_row=j-1
            while j<len(master_table2) and pd.isna(master_table2['Balance'][j]):
                if not pd.isna(master_table2['Description'][j]):
                    master_table2['Description'][prev_row]+=''+str(master_table2['Description'][j])
                j+=1
        master_table2.dropna(subset=['Balance'],inplace=True)
        master_table2 = master_table2.iloc[::-1]
        master_table2.reset_index(drop=True,inplace=True)
        account_name=cust_info[0].iloc[0,0]
        for i in range(len(cust_info[0])):
            if type(cust_info[0].iloc[i,1])==str and cust_info[0].iloc[i,1]=="Account No.":
                account_no="'{}'".format(cust_info[0].iloc[i][2])
    
    else:
        #format 2
        #['Date', 'Unnamed: 0', 'Narration Chq/Ref No', 'Unnamed: 1','Withdrawal (Dr)/', 'Balance']
        #sample pdf: deepak banking
        tables = tabula.read_pdf(pdf_path, pages='all', area=[223.8, 28.8, 821.6, 565], columns=[88.8, 274.8, 360, 482.6, 565],password=passcode)
        cust_info=tabula.read_pdf(pdf_path, pages=1, area=[61,22,216,553],pandas_options={'header':None},password=passcode)
        
        if 'Date' in tables[0].columns[0]:
            for i in range(len(tables)):
                tables[i] = tables[i].iloc[1:]
                tables[i].reset_index(drop=True, inplace=True)
            if tables[-1].columns[0] != 'Date':
                tables.pop(-1)
            if tables[-1][tables[-1]['Date'] == 'Statement  Su'].any()['Date']:
                j = tables[-1].index[tables[-1]['Date'] == 'Statement  Su'][0]
                tables[-1] = tables[-1].iloc[:j]
                tables[-1].reset_index(drop=True, inplace=True)
            #standarising cust_info for further processing
            i=2
            while i<len(cust_info[0].columns):
                for j in range(len(cust_info[0])):
                    if pd.isna(cust_info[0][cust_info[0].columns[i]][j]):
                        continue
                    cust_info[0][cust_info[0].columns[1]][j]=str(cust_info[0][cust_info[0].columns[1]][j])+str(cust_info[0][cust_info[0].columns[i]][j])
                i+=1
            cust_info[0]=cust_info[0][[cust_info[0].columns[0],cust_info[0].columns[1]]]
    
        else:
            #old format exception
            #pushpendra sen banking
            tables = tabula.read_pdf(pdf_path, pages='all', area=[210.9,27.3,755.7,533.1], columns=[82.5, 258.3, 347.7, 460.5, 533],password=passcode)
            if 'Date' in tables[0].columns[0]:
                for i in range(len(tables)):
                    tables[i] = tables[i].iloc[1:]
                    tables[i].reset_index(drop=True, inplace=True)
                if tables[-1].columns[0] != 'Date':
                    tables.pop(-1)
                if tables[-1][tables[-1]['Date'] == 'Statement  S'].any()['Date']:
                    j = tables[-1].index[tables[-1]['Date'] == 'Statement  S'][0]
                    tables[-1] = tables[-1].iloc[:j]
                    tables[-1].reset_index(drop=True, inplace=True)
                #standarising cust_info for further processing
                i=2
                while i<len(cust_info[0].columns):
                    for j in range(len(cust_info[0])):
                        if pd.isna(cust_info[0][cust_info[0].columns[i]][j]):
                            continue
                        cust_info[0][cust_info[0].columns[1]][j]=str(cust_info[0][cust_info[0].columns[1]][j])+str(cust_info[0][cust_info[0].columns[i]][j])
                    i+=1
                cust_info[0]=cust_info[0][[cust_info[0].columns[0],cust_info[0].columns[1]]]
            
            else:
                #anil.pdf
                tables = tabula.read_pdf(pdf_path, pages='all', area=[284,7.5,838.9,709], columns=[73.7,330,451,595.0],password=passcode)
                cust_info=tabula.read_pdf(pdf_path, pages=1, area=[80,13.7,264.4,702.8],pandas_options={'header':None},password=passcode)
                if 'Withdrawal (Dr)/' in tables[0].columns:
                    #print("\n")
                    #standarising dfs for furhter processing
                    for i in range(len(tables)):
                        tables[i]=tables[i][2:]
                        tables[i].reset_index(drop=True, inplace=True)
                        if(len(tables[i].columns))!=5:
                            print("check tables["+i+"]")
                            continue
                        tables[i].columns=['Date', 'Narration', 'Chq/Ref No','Withdrawal (Dr)/', 'Balance']
                    if tables[-1][tables[-1]['Date'] == 'Statemen'].any()['Date']:
                        j = tables[-1].index[tables[-1]['Date'] == 'Statemen'][0]
                        tables[-1] = tables[-1].iloc[:j]
                        tables[-1].reset_index(drop=True, inplace=True)
                        
                    #standarising cust_info for further processing
                    i=2
                    while i<len(cust_info[0].columns):
                        for j in range(len(cust_info[0])):
                            if pd.isna(cust_info[0][cust_info[0].columns[i]][j]):
                                continue
                            cust_info[0][cust_info[0].columns[1]][j]=str(cust_info[0][cust_info[0].columns[1]][j])+str(cust_info[0][cust_info[0].columns[i]][j])
                        i+=1
                    cust_info[0]=cust_info[0][[cust_info[0].columns[0],cust_info[0].columns[1]]]
                
                else:
                    print('Unidentified Structure')
                    return
    
    
        # splitting 'Withdrawal/Deposit' column in two separate columns                
        for i in range(len(tables)):
            if len(tables[i].columns) == 5 and not tables[i].empty:
                for j in range(len(tables[i])) :
                    if pd.notna(tables[i]['Date'][j]) and pd.isna(tables[i]['Balance'][j]) :
                        k = tables[i].loc[j+1:,'Balance'].first_valid_index()
                        tables[i]['Balance'][j] = tables[i]['Balance'][k]
                        tables[i]['Withdrawal (Dr)/'][j] = tables[i]['Withdrawal (Dr)/'][k]
                tables[i][['Amount','CreditOrDebit']] = tables[i]['Withdrawal (Dr)/'].str.split('(',1,expand=True)
                tables[i].drop(['Withdrawal (Dr)/'] ,axis=1,inplace=True)
                tables[i]['Debit'] = tables[i].loc[tables[i]['CreditOrDebit'] == "Dr)" , 'Amount']
                tables[i]['Credit'] = tables[i].loc[tables[i]['CreditOrDebit'] == "Cr)" , 'Amount']
                tables[i].drop(['Amount','CreditOrDebit'],axis=1,inplace=True)
        
            else:
                continue
        
        # removing CR/DR from Balance column
        for i in range(len(tables)):
            for j in tables[i].index :
                if type(tables[i]['Balance'][j]) == str:
                    isCR=tables[i]['Balance'][j][-4:]
                    if isCR=="(Cr)":
                        tables[i]['Balance'][j] = tables[i]['Balance'][j][:-4]
                    elif isCR=="(Dr)":
                        tables[i]['Balance'][j] = '-'+str(tables[i]['Balance'][j][:-4])
        
        for i in range(1,len(tables)):
            if tables[i].empty:
                continue
            tables[0]=pd.concat([tables[0],tables[i]])
        tables[0].reset_index(inplace=True,drop=True)
        for j in range(1,len(tables[0])):
            prev_row=j-1
            while j<len(tables[0]) and pd.isna(tables[0]['Date'][j]):
                if not pd.isna(tables[0]['Chq/Ref No'][j]):
                    if pd.isna(tables[0]['Chq/Ref No'][prev_row]):
                        tables[0]['Chq/Ref No'][prev_row]=str(tables[0]['Chq/Ref No'][j])
                    else:
                        tables[0]['Chq/Ref No'][prev_row]=str(tables[0]['Chq/Ref No'][prev_row])+str(tables[0]['Chq/Ref No'][j])
                j+=1
        master_table2=tables[0][1:][['Date','Narration','Chq/Ref No','Balance','Debit','Credit']]
        master_table2.rename(columns={'Narration':'Description','Chq/Ref No':'Cheque Number'},inplace=True)
        master_table2.reset_index(inplace=True,drop=True)
        
        #concat_desc
        for j in range(len(master_table2)):
            prev_row=j-1
            while j<len(master_table2) and pd.isna(master_table2['Date'][j]):
                if not pd.isna(master_table2['Description'][j]):
                    master_table2['Description'][prev_row]=str(master_table2['Description'][prev_row])+str(master_table2['Description'][j])
                j+=1
        master_table2.dropna(subset=['Date'],inplace=True)
        master_table2.reset_index(inplace=True,drop=True)
        
        account_name=cust_info[0].iloc[0,0]
        for i in range(len(cust_info[0])):
            if type(cust_info[0].iloc[i,1])==str and cust_info[0].iloc[i,1].find("Account No")!=-1:
                account_no="'{}'".format(cust_info[0].iloc[i][1].split(':')[-1].strip())
                
    
    #common parts
    master_table2['Account Name'] = account_name
    master_table2['Account Number'] = account_no
    master_table2.rename(columns={'Date':'Txn Date'}, inplace=True)
    
    master_table2['Txn Date'] = [dt.strftime(pd.to_datetime(x,dayfirst=True),"%d-%m-%Y") for x in master_table2['Txn Date']]
    master_table2 = master_table2[['Txn Date', 'Description','Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number']]
    last_trans_date = master_table2['Txn Date'].iat[-1]

    ## NOW PERFORMING FEW LOGICAL CHECKS TO CHECK DIGITIZATION HAS NO ISSUE
    
    df = pd.DataFrame(master_table2)
    column_names=['Statement_name','Wrong Credit', 'Wrong Debit', 'Remark']
    result=pd.DataFrame(index=[1],columns=column_names)
    
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
        
    #df['Balance_changed'] = df['Balance_changed'].replace(0,np.nan)
    #df['Debit_changed'] = df['Debit_changed'].replace(0,np.nan)
    #df['Credit_changed'] = df['Credit_changed'].replace(0,np.nan)        
    
    col_credit=df.columns.get_loc('Credit_changed')
    col_debit=df.columns.get_loc('Debit_changed')
    col_bal=df.columns.get_loc('Balance_changed')
    #col_desc=df.columns.get_loc('Description')
    
    for i in range(1,len(df)):
        #check 1 having, both debit and credit values
        if  (pd.isna(df.iloc[i,col_debit]) and pd.isna(df.iloc[i,col_credit])) or (pd.notna(df.iloc[i,col_debit]) and pd.notna(df.iloc[i,col_credit])) :
            data=pd.DataFrame({'Statement_name':pdf_file,'Wrong Credit': (i+2),'Wrong Debit':(i+2), 'Remark':'Only one of Debit/Credit should be filled'},index=[0])
            result=pd.concat([result,data])                
    
        #check 2, balance check
        else:
            #debited
            if pd.isna(df.iloc[i,col_credit]):
                if df.iloc[i,col_debit]>0:
                    if df.iloc[i-1,col_bal]<df.iloc[i,col_bal]:
                        data=pd.DataFrame({'Statement_name':pdf_file,'Wrong Credit': np.nan,'Wrong Debit':(i+2), 'Remark':'Balance should be less than previous since debit>0'},index=[0])
                        result=pd.concat([result,data])
                else:
                    if df.iloc[i-1,col_bal]>df.iloc[i,col_bal]:
                        data=pd.DataFrame({'Statement_name':pdf_file,'Wrong Credit': np.nan,'Wrong Debit':(i+2),'Remark':'Balance should be more than previous since debit<0'},index=[0])
                        result=pd.concat([result,data])
                  
    
            #credited
            elif pd.isna(df.iloc[i,col_debit]):
                if df.iloc[i,col_credit]>0:
                    if df.iloc[i-1,col_bal]>df.iloc[i,col_bal]:
                        data=pd.DataFrame([{'Statement_name':pdf_file,'Wrong Credit': (i+2),'Wrong Debit':np.nan,'Remark':'Balance should be more than previous since credit>0'}],index=[0])
                        result=pd.concat([result,data])
                else:
                    if df.iloc[i-1,col_bal]<df.iloc[i,col_bal]:
                        data=pd.DataFrame([{'Statement_name':pdf_file,'Wrong Credit': (i+2),'Wrong Debit':np.nan,'Remark':'Balance should be less than previous since credit<0'}],index=[0])
                        result=pd.concat([result,data])    
    
    result = result.dropna(how='all')
    
    # will continue only if 'result' is an empty dataframe
    if len(result)==0:
        print("go ahead")
        pass
    else:
        print("\nThere are issues found after the Logical checks.\nThe digtitized output and the issues have been exported in CSVs.\n")
        #master_table2.to_csv("{}/{}_Digitized.csv".format(out_path,pdf_file),index=False)        
        #result.to_csv("{}/{}_LogicalChecks.csv".format(out_path,pdf_file),index=False)
        return

    # NOW THE ENTITY EXTRACTION PART
    import warnings
    warnings.simplefilter(action='ignore', category=FutureWarning)

    def get_printable(s):
        res=''.join([i for i in s if i.isprintable()])
        return res
    
    
    kotak = pd.DataFrame(master_table2)
    
    kotak["Description"]=kotak["Description"].str.lstrip()
    kotak['Description']=[i  if i.isprintable() else get_printable(i) for i in kotak['Description'].astype(str)]
    pd.options.mode.chained_assignment = None
    
    kotak["Description"]=kotak["Description"].str.lstrip()
    #Converting string into float 
    kotak["Debit"] = kotak["Debit"].apply(lambda x: float(str(x).replace(",","")))
    kotak["Credit"] = kotak["Credit"].apply(lambda x: float(str(x).replace(",","")))
    kotak["Balance"] = kotak["Balance"].apply(lambda x: float(str(x).replace(",","")))

    #Converting list to string
    def listToString(s):  
        str1 = " " 
        return (str1.join(s))

    #UPI 

    try:
        kotak["Description"]=kotak["Description"].astype(str)
        df1=kotak[kotak["Description"].str.startswith("UPI/")]
        df1["new"]=df1["Description"].str.split("/")
        df1["sub-mode"]=df1["new"].apply(lambda x: x[0])
        df1['entity'] = df1["new"].apply(lambda x: x[1])
        df1['entity_bank'] = "NA" 
        df1['source_of_trans']='Self Initiated'
        df1['mode']="Mobile App"  
        df1.drop([ 'new'], axis=1, inplace=True)
    except:
        pass

    try:
        df1a=kotak[kotak["Description"].str.startswith("UPI-")]
        df1a["new"]=df1a["Description"].str.split("-")
        df1a["sub-mode"]=df1a["new"].apply(lambda x: x[0])
        df1a['entity'] = df1a["new"].apply(lambda x: x[1])
        df1a['entity_bank'] = "NA" 
        df1a['source_of_trans']='Self Initiated'
        df1a['mode']="Mobile App"  
        df1a.drop([ 'new'], axis=1, inplace=True)
    except:
        pass


    #ATM 
    try:
        df2=kotak[kotak["Description"].str.startswith("ATL")]
        df2["new"]=df2["Description"].str.split("/")
        df2["sub-mode"]=df2["new"].apply(lambda x: x[0])
        df2['entity'] = "NA"
        df2['entity_bank'] = "NA" 
        df2['source_of_trans']='Self Initiated'
        df2['mode']="Cash" 
        df2.drop([ 'new'], axis=1, inplace=True)
    except:
        pass
    
    try:
        df2a=kotak[kotak["Description"].str.startswith("ATW")]
        df2a["new"]=df2a["Description"].str.split("/")
        df2a["sub-mode"]=df2a["new"].apply(lambda x: x[0])
        df2a['entity'] = "NA"
        df2a['entity_bank'] = "NA" 
        df2a['source_of_trans']='Self Initiated'
        df2a['mode']="Cash" 
        df2a.drop([ 'new'], axis=1, inplace=True)
    except:
        pass
    
    #subsetting Mobile Banking transactions 
    try:
        df3=kotak[kotak["Description"].str.startswith("MB")]
        df3a=df3[~df3["Description"].str.startswith("MB:")]
        df3a=df3a[~df3a["Description"].str.contains(pat="IMPS")]
        df3a=df3a[~df3a["Description"].str.contains(pat="NEFT")]
        df3a=df3a[~df3a["Description"].str.contains(pat="TRRef")]
        df3a["new"]=df3a["Description"].str.split("I")
        df3a["new"]=df3a["new"].apply(lambda x: x[0])
        df3a["new"]=df3a["new"].str.split(" ")
        df3a["sub-mode"]="Mobile Banking"
        df3a['entity'] = df3a["new"].apply(lambda x: x[1:])
        df3a['entity'] = df3a["entity"].apply(listToString)
        df3a['entity_bank'] = "NA" 
        df3a['source_of_trans']='Self Initiated'
        df3a['mode']="Mobile App" 
        df3a.drop([ 'new'], axis=1, inplace=True)
    except:
        pass
    
    try:
        df3b=df3[~df3["Description"].isin(df3a["Description"])] 
        df3b=df3b[~df3b["Description"].str.startswith("MB:")]
        df3b["sub-mode"]="MB"
        df3b['entity'] = "NA"
        df3b['entity_bank'] = "NA" 
        df3b['source_of_trans']='Self Initiated'
        df3b['mode']="Mobile App"
    except:
        pass
    #MB:    
    try:
        df3_1=df3[df3["Description"].str.startswith("MB:")]
    except:
        pass
    
    try: 
        df3c=df3_1[~df3_1["Description"].str.contains(pat="IMPS")]
        df3c=df3c[~df3c["Description"].str.contains(pat="NEFT")]
        df3c=df3c[~df3c["Description"].str.contains(pat="PAID CARD")]
        
        df3c_to=df3c[df3c["Description"].str.contains(pat="SENT")]
        df3c_to["new"]=df3c_to["Description"].str.split("TO")
        df3c_to['new'] = df3c_to["new"].apply(lambda x: x[1])
        df3c_to["new"]=df3c_to["new"].str.split(" ")
        df3c_to['entity'] = df3c_to["new"].apply(lambda x: x[:-1])
        df3c_to['entity'] = df3c_to["entity"].apply(listToString)
        
        df3_from=df3c[df3c["Description"].str.contains(pat="RECEIVED")]
        df3_from["new"]=df3_from["Description"].str.split("RECEIVED FROM")
        df3_from['new'] = df3_from["new"].apply(lambda x: x[1])
        df3_from["new"]=df3_from["new"].str.split(" ")
        df3_from['entity'] = df3_from["new"].apply(lambda x: x[:-1])
        df3_from['entity'] = df3_from["entity"].apply(listToString)
        
        df3c = pd.concat([df3c_to,df3_from], axis=0)
        df3c["sub-mode"]="MB"
        df3c['entity_bank'] = "NA" 
        df3c['source_of_trans']='Self Initiated'
        df3c['mode']="Mobile App" 
        df3c.drop([ 'new'], axis=1, inplace=True)
    except:
        pass
    
    try:
        df3d=df3_1[~df3_1["Description"].isin(df3c["Description"])] 
        df3d["sub-mode"]="MB"
        df3d['entity'] = "NA"
        df3d['entity_bank'] = "NA" 
        df3d['source_of_trans']='Self Initiated'
        df3d['mode']="Mobile App"       
    except:
        pass
    
    
    #Card     
    try:
        df4=kotak[kotak["Description"].str.startswith("PCD")]
        df4["new"]=df4["Description"].str.split("/")
        df4["sub-mode"]=df4["new"].apply(lambda x: x[0])
        df4['entity'] = df4["new"].apply(lambda x: x[2])
        df4['entity_bank'] = "NA" 
        df4['source_of_trans']='Self Initiated'
        df4['mode']="Card"
        df4.drop([ 'new'], axis=1, inplace=True)
    except:
        pass   
    
    #ECS transactions    
    try:
        df5=kotak[kotak["Description"].str.startswith("ECSI")]
        df5["new"]=df5["Description"].str.split("-")
        df5["sub-mode"]=df5["new"].apply(lambda x: x[0])
        df5['entity'] = df5["new"].apply(lambda x: x[1])
        df5['entity_bank'] = "NA" 
        df5['source_of_trans']='Self Initiated'
        df5['mode']="Loan/MF"
        df5.drop([ 'new'], axis=1, inplace=True)
    except:
        pass      
    #IMPS transactions    
    try:
        df6=kotak[kotak["Description"].str.startswith("Received from")]
        df6["new"]=df6["Description"].str.split(" ")
        df6["sub-mode"]="IMPS"
        df6['entity'] = df6["new"].apply(lambda x: x[2]+" "+x[3])
        df6['entity_bank'] = "NA" 
        df6['source_of_trans']='Self Initiated'
        df6['mode']="Net Banking"
        df6.drop([ 'new'], axis=1, inplace=True)
    except:
        pass      
 
    try:
        df6a=kotak[kotak["Description"].str.startswith("IMPS")]
        df6a["new"]=df6a["Description"].str.split(" ")
        df6a["sub-mode"]=df6a["new"].apply(lambda x: x[0])
        df6a['entity'] = df6a["new"].apply(lambda x: x[2]+" "+x[3])
        df6a['entity_bank'] = "NA" 
        df6a['source_of_trans']='Self Initiated'
        df6a['mode']="Net Banking"
        df6a.drop([ 'new'], axis=1, inplace=True)
    except:
        pass

    #Interest transactions    
    try:
        df7=kotak[kotak["Description"].str.startswith("Int.Pd")]
        df7["sub-mode"]="Int.Pd"
        df7['entity'] = "NA"
        df7['entity_bank'] = "NA" 
        df7['source_of_trans']='Automated'
        df7['mode']="Interest"
    except:
        pass      
    #By Clg and To Clg  
    try:
        df8_by=kotak[kotak["Description"].str.startswith("BY CLG")]
        df8_by["Description"]=df8_by["Description"].str.replace("/",":")
        df8_by["new"]=df8_by["Description"].str.split(":",1)
        df8_by["sub-mode"]=df8_by["new"].apply(lambda x: x[0])
        df8_by['entity_bank'] = df8_by["new"].apply(lambda x: x[1].split()[0])
        df8_by['new'] = df8_by["Description"].str.split("CLG",1)
        df8_by['entity'] = df8_by["new"].apply(lambda x: x[1].split(":")[0])
        df8_to=kotak[kotak["Description"].str.startswith("TO CLG")]
        df8_to["new"]=df8_to["Description"].str.split("CMS")
        df8_to["sub-mode"]=df8_to["new"].apply(lambda x: x[0])
        df8_to['entity'] = df8_to["new"].apply(lambda x: x[-1])
        df8_to['entity_bank'] = "NA" 
        
        df8 = pd.concat([df8_by,df8_to], axis=0)
        df8['source_of_trans']='Self Initiated'
        df8['mode']="Cheque"
        df8.drop([ 'new'], axis=1, inplace=True)
    except:
        pass
    #NEFT transactions    
    try:
        df9=kotak[kotak["Description"].str.startswith("NEFT")]
        df9=df9[~df9["Description"].str.contains(pat="Salary", case=False)]
        df9["new"]=df9["Description"].str.split(" ")
        df9["sub-mode"]="NEFT"
        df9['entity'] = df9["new"].apply(lambda x: x[2:]) 
        df9['entity'] = df9['entity'].apply(listToString)
        df9['entity_bank'] = "NA" 
        df9['source_of_trans']='Self Initiated'
        df9['mode']="Net Banking"
        df9.drop([ 'new'], axis=1, inplace=True)
    except:
        pass

    #REV     
    try:
        df10=kotak[kotak["Description"].str.startswith("REV")]
        df10["sub-mode"]="REV"
        df10['entity'] = "NA"
        df10['entity_bank'] = "NA" 
        df10['source_of_trans']='Self Initiated'
        df10['mode']="Reversal"
    except:
        pass
    
    #Salary  
    try:
        df11=kotak[kotak["Description"].str.contains(pat="SAL")]
        df11["sub-mode"]="Salary"
        df11['entity'] = "NA"
        df11['entity_bank'] = "NA" 
        df11['source_of_trans']='Automated'
        df11['mode']="Salary"
    except:
        pass  

#Charge
    try:
        df12=kotak[kotak["Description"].str.contains(pat="Chrg")]
        df12["sub-mode"]="Charge"
        df12['entity'] = "NA"
        df12['entity_bank'] = "NA" 
        df12['source_of_trans']='Automated'
        df12['mode']="Charge"
    except:
        pass
    
#Internet Banking
        
    try:
        df13=kotak[kotak["Description"].str.startswith("IB")] 
        df13["new"]=df13["Description"].str.split(" ")
        df13["sub-mode"]=df13["new"].apply(lambda x: x[0])
        df13['entity'] = df13["new"].apply(lambda x: x[1:-2])
        df13['entity'] = df13['entity'].apply(listToString)
        df13['entity_bank'] = "NA" 
        df13['source_of_trans']='Self Initiated'
        df13['mode']="Net Banking" 
        df13.drop([ 'new'], axis=1, inplace=True)
    except:
        pass

#OS: Online Shopping done using net banking gateway
        
    try:
        df14=kotak[kotak["Description"].str.startswith("OS")]
        df14["new"]=df14["Description"].str.split(" ")
        df14["sub-mode"]=df14["new"].apply(lambda x: x[0])
        df14['entity'] = df14["new"].apply(lambda x: x[1])
        df14['entity_bank'] = "NA" 
        df14['source_of_trans']='Self Initiated'
        df14['mode']="Net Banking"
        df14.drop([ 'new'], axis=1, inplace=True)
    except:
        pass
        
 #Fund Transfer Debit
        
    try:
        df15=kotak[kotak["Description"].str.startswith("FUND TRANSFER")]
        df15=df15[~df15["Description"].str.startswith("FUND TRANSFERRED")]
        df15["new"]=df15["Description"].str.split("-")
        df15["sub-mode"]=df15["new"].apply(lambda x: x[0])
        df15['entity'] = df15["new"].apply(lambda x: x[-1])
        df15['entity_bank'] = "NA" 
        df15['source_of_trans']='Self Initiated'
        df15['mode']="Net Banking"
        df15.drop([ 'new'], axis=1, inplace=True)
    except:
        pass
        
    
 #Fund Transfer Credit
        
    try:
        df15a=kotak[kotak["Description"].str.startswith("FUND TRANSFERRED")]
        df15a["new"]=df15a["Description"].str.split("TO")
        df15a["sub-mode"]=df15a["new"].apply(lambda x: x[0])
        df15a['entity'] = df15a["new"].apply(lambda x: x[-1])
        df15a['entity_bank'] = "NA" 
        df15a['source_of_trans']='Self Initiated'
        df15a['mode']="Net Banking"
        df15a.drop([ 'new'], axis=1, inplace=True)
    except:
        pass
    
 #RTGS
        
    try:
        df16=kotak[kotak["Description"].str.startswith("RTGS")]
        df16["new"]=df16["Description"].str.split(" ")
        df16["sub-mode"]="RTGS"
        df16['entity'] = df16["new"].apply(lambda x: x[2:])
        df16['entity'] = df16["entity"].apply(listToString)
        df16['entity_bank'] = "NA" 
        df16['source_of_trans']='Self Initiated'
        df16['mode']="Net Banking"
        df16.drop([ 'new'], axis=1, inplace=True)
    except:
        pass
    
    #TD premat
    try:
        df17 =kotak[kotak["Description"].str.startswith("TD PREMAT")]
        df17 ["new"]=df17 ["Description"].str.split(":")
        df17 ['entity'] = df17 ["new"].apply(lambda x: x[1])
        df17 ["sub-mode"]="NA"
        df17 ["entity_bank"]="Kotak Bank"
        df17 ["source_of_trans"]="Automated"
        df17 ["mode"]="Term Deposit"
        df17 .drop([ 'new'], axis=1, inplace=True)
    except:
        pass
        
    
    #incentive
    try:
        df18 =kotak[kotak["Description"].str.contains("INCENTIVE")]
        df18 ['entity'] = "NA"
        df18 ["entity_bank"]="NA"
        df18 ["sub-mode"]="NA"
        df18 ["source_of_trans"]='Automated'
        df18 ["mode"]="Salary"
    except:
        pass
    
    #TD int and tax
    try:
        df19 =kotak[kotak["Description"].str.contains("TD Int")]
        df19 ["new"]=df19 ["Description"].str.split("-")
        df19 ['entity'] = df19 ["new"].apply(lambda x: x[1])
        df19 ["entity_bank"]="Kotak Bank"
        df19 ["source_of_trans"]="Automated"
        df19 ["sub-mode"]="NA"
        df19 ["mode"]="Interest"
        df19 .drop([ 'new'], axis=1, inplace=True)
    except:
        pass
    
    #Payment towards
    try:
        df20 =kotak[kotak["Description"].str.contains("Payment towards")]
        df21 =kotak[kotak["Description"].str.contains("PAYMENT TOWARDS")]
        df20 =pd.concat([df20 ,df21 ])
        df20 ['entity'] = "NA"
        df20 ["entity_bank"]="NA"
        df20 ["sub-mode"]="Credit Card"
        df20 ["source_of_trans"]="Self Initiated"
        df20 ["mode"]="Card"
    except:
        pass
    
    #i/w chq rtn
    try:
        df21 =kotak[kotak["Description"].str.contains("I/W CHQ RTN")]
        df21 ['entity'] = "NA"
        df21 ["entity_bank"]="NA"
        df21 ["sub-mode"]="NA"
        df21 ["source_of_trans"]="Automated"
        df21 ["mode"]="Failed"
    except:
        pass
    
    #PCI
    try:
        df22 =kotak[kotak["Description"].str.startswith("PCI")]
        df22 ["new"]=df22 ["Description"].str.split("/")
        df22 ['entity'] = df22 ["new"].apply(lambda x: x[2])
        df22 ["entity_bank"]="NA"
        df22 ["sub-mode"]="NA"
        df22 ["source_of_trans"]="Self Initiated"
        df22 ["mode"]="Card"
        df22 .drop(['new'], axis=1, inplace=True)
    except:
        pass
    
    #"charges
    try:
        df23 =kotak[kotak["Description"].str.startswith("CHGS")]
        df_t=kotak[kotak["Description"].str.startswith("CHRS")]
        df23=pd.concat([df23,df_t])
        del df_t
        df23 ['entity'] = "NA"
        df23 ["entity_bank"]="NA"
        df23 ["source_of_trans"]="Automated"
        df23 ["sub-mode"]="Charges"
        df23 ["mode"]="NA"
    except:
        pass
    
    #DIFF IN SETT
    try:
        df24 =kotak[kotak["Description"].str.startswith("DIFF IN SETT")]
        df24 ['entity'] = "NA"
        df24 ["entity_bank"]="NA"
        df24 ["source_of_trans"]="NA"
        df24 ["sub-mode"]="NA"
        df24 ["mode"]="NA"
    except:
        pass
    
    #VMT
    try:
        df25 =kotak[kotak["Description"].str.startswith("VMT")]
        df25 ["new"]=df25 ["Description"].str.split("/")
        df25 ["entity"] = df25 ["new"].apply(lambda x: x[2])
        df25 ["entity_bank"]="NA"
        df25 ["sub-mode"]="NA"
        df25 ["source_of_trans"]="Self Initiated"
        df25 ["mode"]="Card"
        df25 .drop(['new'], axis=1, inplace=True)
    except:
        pass
    
    #O/W RTN
    try:
        df26 =kotak[kotak["Description"].str.startswith("O/W RTN")]
        df26 ['entity'] = "NA"
        df26 ["entity_bank"]="NA"
        df26 ["sub-mode"]="NA"
        df26 ["source_of_trans"]="Automated"
        df26 ["mode"]="Failed"
    except:
        pass
    
    #CC Payment FUND TRf
    try:
        df27 =kotak[kotak["Description"].str.startswith("CC PAYMENT")]
        df27 ['entity'] = "NA"
        df27 ["entity_bank"]="NA"
        df27 ["sub-mode"]="NA"
        df27 ['source_of_trans']='Self Initiated'
        df27 ['mode']="Net Banking"
    except:
        pass
    
    #FUND TRf
    try:
        df28 =kotak[kotak["Description"].str.startswith("FUND TRF TO")]
        df28 ["new"]=df28 ["Description"].str.split("TO")
        df28 ["entity"] = df28 ["new"].apply(lambda x: x[1])
        df28 ["entity_bank"]="NA"
        df28 ["sub-mode"]="Mutual Funds/SIP"
        df28 ['source_of_trans']='Automated'
        df28 ['mode']="NA"
        df28 .drop(['new'], axis=1, inplace=True)
        
        df29 =kotak[kotak["Description"].str.startswith("FUND TRF FROM")]
        df29 ["new"]=df29 ["Description"].str.split("FROM")
        df29 ["entity"] = df29 ["new"].apply(lambda x: x[1])
        df29 ["entity_bank"]="NA"
        df29 ["sub-mode"]="Mutual Funds/SIP"
        df29 ['source_of_trans']='Automated'
        df29 ['mode']="NA"
        df29 .drop(['new'], axis=1, inplace=True)
    except:
        pass
    
    #sent rtgs
    try:
        df30 =kotak[kotak["Description"].str.startswith("Sent RTGS")]
        df30 ["new"]=df30 ["Description"].str.split("/")
        df30 ["entity"] = df30 ["new"].apply(lambda x: x[1])
        df30 ["entity_bank"]="NA"
        df30 ["sub-mode"]="RTGS"
        df30 ['source_of_trans']='Self Initiated'
        df30 ['mode']="Net Banking"
        df30 .drop(['new'], axis=1, inplace=True)
    except:
        pass
    
    #Loan amt
    try:
        df31 =kotak[kotak["Description"].str.startswith("LOAN AMT")]
        df31 ["entity"] = "NA"
        df31 ["entity_bank"]="NA"
        df31 ["sub-mode"]="EMI"
        df31 ['source_of_trans']='Automated'
        df31 ['mode']="NA"
    except:
        pass
    
    #ins debit
    try:
        df32 =kotak[kotak["Description"].str.startswith("Ins Debit A\c")]
        df32 ["new"]=df32 ["Description"].str.split(" ")
        df32 ["entity"]=df32 ["new"].apply(lambda x: x[3]+" "+x[4])
        df32 ["entity_bank"]="NA"
        df32 ["sub-mode"]="Insurance"
        df32 ['source_of_trans']='Automated'
        df32 ['mode']="NA"
        df32 .drop(['new'], axis=1, inplace=True)
    except:
        pass
    
    #DD Issued
    try:
        df33 =kotak[kotak["Description"].str.startswith("DD ISSUED")]
        df33 ["new"]=df33 ["Description"].str.split("OF")
        df33 ["entity"]=df33 ["new"].apply(lambda x: x[1])
        df33 ["entity_bank"]="NA"
        df33 ["sub-mode"]="DD"
        df33 ['source_of_trans']='Self Initiated'
        df33 ['mode']="Demand Draft"
        df33 .drop(['new'], axis=1, inplace=True)
    except:
        pass
    
    #fee
    try:
        df34 =kotak[kotak["Description"].str.contains("ANNUAL FEE")]
        df34 ["entity"]="NA"
        df34 ["entity_bank"]="NA"
        df34 ["sub-mode"]="Service Charges"
        df34 ['source_of_trans']='Automated'
        df34 ['mode']="Charges"
    except:
        pass
    
    #INT coll
    try:
        df35 =kotak[kotak["Description"].str.contains("Int.Coll")]
        df35 ["entity"]="NA"
        df35 ["entity_bank"]="NA"
        df35 ["sub-mode"]="Interest Collected"
        df35 ['source_of_trans']='Automated'
        df35 ['mode']="Charge"
    except:
        pass
    
    #PF refund
    try:
        df36 =kotak[kotak["Description"].str.contains("PF REFUND")]
        df36 ["entity"]="NA"
        df36 ["entity_bank"]="NA"
        df36 ["sub-mode"]="Salary"
        df36 ['source_of_trans']='Automated'
        df36 ['mode']="Salary"
    except:
        pass
    
    #FT to/Frm
    try:
        df38 =kotak[kotak["Description"].str.startswith("FT TO")]
        df38 ["new"]=df38 ["Description"].str.split("TO")
        df38 ["entity"] = df38 ["new"].apply(lambda x: x[1])
        df38 ["entity_bank"]="NA"
        df38 ["sub-mode"]="Mutual Funds/SIP"
        df38 ['source_of_trans']='Automated'
        df38 ['mode']="NA"
        df38 .drop(['new'], axis=1, inplace=True)
        
        df39 =kotak[kotak["Description"].str.startswith("FT FRM")]
        df39 ["new"]=df39 ["Description"].str.split("FRM")
        df39 ["entity"] = df39 ["new"].apply(lambda x: x[1])
        df39 ["entity_bank"]="NA"
        df39 ["sub-mode"]="Mutual Funds/SIP"
        df39 ['source_of_trans']='Automated'
        df39 ['mode']="NA"
        df39 .drop(['new'], axis=1, inplace=True)
        
        df37 =kotak[kotak["Description"].str.startswith("FT FROM")]
        df_t=kotak[kotak["Description"].str.startswith("FTR FROM")]
        df37 =pd.concat([df37 ,df_t])
        del df_t
        df37 ["new"]=df37["Description"].str.split("FROM")
        df37 ["entity"] = df37["new"].apply(lambda x: x[1])
        df37 ["entity_bank"]="NA"
        df37 ["sub-mode"]="Mutual Funds/SIP"
        df37 ['source_of_trans']='Automated'
        df37 ['mode']="NA"
        df37 .drop(['new'], axis=1, inplace=True)
    except:
        pass
    
    #Loan from
    try:
        df40 =kotak[kotak["Description"].str.startswith("LOAN FROM")]
        df40 ["new"]=df40 ["Description"].str.split("FROM")
        df40 ["entity"] = df40 ["new"].apply(lambda x: x[1])
        df40 ["entity_bank"]="NA"
        df40 ["sub-mode"]="Loan"
        df40 ['source_of_trans']='Automated'
        df40 ['mode']="NA"
        df40 .drop(['new'], axis=1, inplace=True)
    except:
        pass
    
 #BONUS
    try:
        df42=kotak[kotak["Description"].str.startswith("BONUS")]
        df42["sub-mode"]="Salary"
        df42['entity'] = "NA"
        df42['entity_bank'] = "NA" 
        df42['source_of_trans']='Automated'
        df42['mode']="Salary"
    except:
          pass
      
  #VISA REFUND
    try:
        df43=kotak[kotak["Description"].str.startswith("VISA-")]
        df43["new"]=df43["Description"].str.split("/")
        df43["sub-mode"]=df43["new"].apply(lambda x: x[0])
        df43['entity'] = df43["new"].apply(lambda x: x[3])
        df43['entity'], df43['B'] = df43['entity'].str.split('(', 1).str
        df43['entity_bank'] = "NA" 
        df43['source_of_trans']='Automated'
        df43['mode']="Net Banking"
        df43.drop([ 'new','B'], axis=1, inplace=True)
    except:
           pass
       
  #MICR INWARD 
    try:
        df44=kotak[kotak["Description"].str.contains("MICR INWARD")]
        df44["new"]=df44["Description"].str.split(":")
        df44["sub-mode"]=df44["new"].apply(lambda x: x[1])
        df44['entity'] = df44["new"].apply(lambda x: x[2])
        df44['entity_bank'] = "NA" 
        df44['source_of_trans']='Self Initiated'
        df44['mode']="Net Banking"
        df44.drop([ 'new'], axis=1, inplace=True)
    except:
        pass
    
    
    #CLG TO
    try:
        df45=kotak[kotak["Description"].str.startswith("CLG TO")]
        df45["new"]=df45["Description"].str.split("TO")
        df45["sub-mode"]=df45["new"].apply(lambda x: x[0])
        df45['entity'] = df45["new"].apply(lambda x: x[1])
        df45['entity_bank'] = "NA" 
        df45['source_of_trans']='Automated'
        df45['mode']="Net Banking"
        df45.drop([ 'new'], axis=1, inplace=True)
    except:
        pass
    
    #SWEEP TRANSFER
    try:
        df46=kotak[kotak["Description"].str.startswith("SWEEP TRANSFER")]
        df46["new"]=df46["Description"].str.split("TO")
        df46["sub-mode"]=df46["new"].apply(lambda x: x[0])
        df46['entity'] = df46["new"].apply(lambda x: x[1])
        df46['entity_bank'] = "NA" 
        df46['source_of_trans']='Self Initiated'
        df46['mode']="Net Banking"
        df46.drop([ 'new'], axis=1, inplace=True)
    except:
        pass
    
    
    
    
     #CASH DEPOSIT
     
    try:
        df47=kotak[kotak["Description"].str.startswith("CASH DEPOSIT")]
        df47["new"]=df47["Description"].str.split("BY")
        df47["sub-mode"]=df47["new"].apply(lambda x: x[0])
        df47['entity'] = "SELF"
        df47['entity_bank'] = "KOTAK"
        df47['source_of_trans']='Self Initiated'
        df47['mode']="Cash"
        df47['sub-mode'], df47['B'] = df47['sub-mode'].str.split(' ', 1).str
        df47['B'], df47['A'] = df47['B'].str.split(' ', 1).str
        df47["sub-mode"] = df47["sub-mode"] +' ' + df47["B"]
        df47.drop(['new'], axis=1, inplace=True)
        df47.drop(['A'], axis=1, inplace=True)
        df47.drop(['B'], axis=1, inplace=True)
        
    except:
        pass
     
      #Cash Deposit
    try:
        df48=kotak[kotak["Description"].str.startswith("Cash Deposit")]
        df48["new"]=df48["Description"].str.split("at")
        df48["sub-mode"]=df48["new"].apply(lambda x: x[0])
        df48['entity'] = "SELF"
        df48['entity_bank'] = "Kotak"
        df48['source_of_trans']='Self Initiated'
        df48['mode']="Cash"
        df48.drop(['new'], axis=1, inplace=True)
    except:
        pass
    
    
    #CASH WITHDRAWAL
    try:
        df49=kotak[kotak["Description"].str.startswith("CASH WITHDRAWAL")]
        df49["new"]=df49["Description"].str.split("BY")
        df49["sub-mode"]=df49["new"].apply(lambda x: x[0])
        df49['entity'] = "SELF"
        df49['entity_bank'] = "KOTAK"
        df49['source_of_trans']='Self Initiated'
        df49['mode']="Cash"
        df49['sub-mode'], df49['B'] = df49['sub-mode'].str.split(' ', 1).str
        df49['B'], df49['A'] = df49['B'].str.split(' ', 1).str
        df49["sub-mode"] = df49["sub-mode"] +' ' + df49["B"]
        df49.drop(['new'], axis=1, inplace=True)
        df49.drop(['A'], axis=1, inplace=True)
        df49.drop(['B'], axis=1, inplace=True)
        
        
    except:
        pass
    
    #Sweep Trf
    try:
        df50=kotak[kotak["Description"].str.startswith("Sweep Trf ")]
        df50["new"]=df50["Description"].str.split("From")
        df50["sub-mode"]=df50["new"].apply(lambda x: x[0])
        df50['entity'] = df50["new"].apply(lambda x: x[1])
        df50['entity_bank'] = "NA" 
        df50['source_of_trans']='Self Initiated'
        df50['mode']="Net Banking"
        df50.drop([ 'new'], axis=1, inplace=True)
    except:
        pass
    
    t1 = pd.concat([df1,df1a,df2,df2a,df3a,df3b,df3c,df3d,df4,df5,df6,df6a,df7,
                    df8,df9,df10,df11,df12,df13,df14,df15,df15a,df16,df17 ,df18 ,
                    df19 ,df20 ,df21 ,df22 ,df23 ,df24 ,df25 ,df26 ,df27 ,
                    df28 ,df29 ,df30 ,df31 ,df32 ,df33 ,df34 ,df35 ,df36 ,
                    df37 ,df38 ,df39 ,df40 ,df42,df43,df44,df45,df46,df47,
                    df48,df49,df50], axis=0)

    t2 = kotak[~kotak["Description"].isin(t1["Description"])]
    t2['sub-mode']='Others'
    t2['entity']='NA'
    t2['source_of_trans']='NA'
    t2['entity_bank']='NA'
    t2['mode']='NA'
    final = pd.concat([t1,t2], axis=0)
    
    final = final.sort_index()
    final.rename(columns={'sub-mode':'sub_mode'}, inplace=True)
    final['entity'].fillna('Other', inplace=True)
    final['entity'].replace('NA', 'Other', inplace=True)
    final['entity'].replace('', 'Other', inplace=True)
    final['Cheque Number']=final['Cheque Number'].fillna("NA.")
    final=final[['Txn Date', 'Description','Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number','mode','entity','source_of_trans','entity_bank','sub_mode']]
    return final
    # exporting the master table to a csv - this is final having complete transactions table appended and essential account information
    #final.to_csv("{}\\{}_{}_{}.csv".format(out_path,pdf_file,account_no, last_trans_date),index=False)

#try :
 #   kotak_digitization(r".\input_files\PUSHPENDAR SEN BANKING.pdf", r".\output_files")
#except Exception as e:
 #   print(e)
 #   print("\nThis statement cannot be digitized.\n")

