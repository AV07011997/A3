import tabula 
from pandas import isna, DataFrame, concat, to_datetime, options, notna, core, Series
from numpy import nan
from datetime import datetime as dt

#function to concatenate description in  different lines (email statements)
#list of keywords has been used to identify that a particular description is of the row above it or below it
def concat_desc(df):
    no_of_rows=len(df)
    keywords=['NEF','BIL','ATM','ACH','UPI','VIN','IIN','VPS','IPS','MMT','NFS','ATD','CLG']
    #fill nan
    df['PARTICULARS']=df['PARTICULARS'].ffill()
    j=0
    while j<no_of_rows:
        if isna(df['DATE'][j]) and not isna(df['PARTICULARS'][j]):
            if j+1<no_of_rows and  df['PARTICULARS'][j][:3] in keywords:
                if df['PARTICULARS'][j] not in df['PARTICULARS'][j+1]:
                    df['PARTICULARS'][j+1]=str(df['PARTICULARS'][j])+str(df['PARTICULARS'][j+1])
            elif j-1>=0:
                df['PARTICULARS'][j-1]=str(df['PARTICULARS'][j-1])+str(df['PARTICULARS'][j])
        j+=1
    df.dropna(subset=['DATE'],inplace=True)
    df.reset_index(drop=True,inplace=True)
    return df

#function to align the dataframes into standardized form
def icici_digitization(pdf_path,passcode):
    #extracting file name from pdf_path
    pdf_file = pdf_path.split('\\')[-1][:-4]
    passcode=''
    try:
        #if file is encrypted but with empty password
        decider = tabula.read_pdf(pdf_path,pages=1,password=passcode,area=[66,338,130,806],pandas_options={'header':None})
    except:
        passcode = input("Enter the Password : ")
        decider = tabula.read_pdf(pdf_path,pages=1,password=passcode,area=[66,338,130,806],pandas_options={'header':None})
    if len(decider)==0 or (decider[0].iloc[0,0]!="DETAILED STATEMENT" and decider[0].iloc[0,0]!="ENT"):
        #print("email_statements"+str(i))
        #code for email statements
        #differentiator for current and savings accounts
        decider = tabula.read_pdf(pdf_path,password=passcode,area=[270.0,7.0,586.2,402],pages='1',pandas_options={'header':None})
        #return if the file is image based (scanned) pdf
        if len(decider)==0:
            print("This is an image-based statement, hence, cannot be digitized here")
            return
        #snippet to recognise type of account
        current = False
        savings = False
        xx_format=False
        for i in range(len(decider[0].columns)):
            for j in range(len(decider[0])):
                if type(decider[0].iloc[j][i])==str and decider[0].iloc[j][i].lower().find("Statement of Transactions in Savings Account Number:".lower())!=-1:
                    current = False
                    savings=True
                    no=decider[0].iloc[j][i].split(":")[1].split()[0]
                    acct_number="'{}'".format(no)
                    if "XX" in acct_number:
                        xx_format=True
                    break
                if type(decider[0].iloc[j][i])==str and decider[0].iloc[j][i].lower().find("Statement of Transactions in Savings Account".lower())!=-1:
                    current = False
                    savings=True
                    no=decider[0].iloc[j][i].split("Account")[1].split()[0]
                    acct_number="'{}'".format(no)
                    if "XX" in acct_number:
                        xx_format=True
                    break
                if type(decider[0].iloc[j][i])==str and decider[0].iloc[j][i].lower().find("Statement of transactions in Current account number:".lower())!=-1:
                    current = True
                    savings = False
                    no=decider[0].iloc[j][i].split(":")[1].split()[0]
                    acct_number="'{}'".format(no)
                    break
        if current == True and savings == False:  #case for non-retail
            tables = tabula.read_pdf(pdf_path,password=passcode,pages='all',columns=[59.4,238.1,278.8,345.3,413.4,466.6,519.8,602.0])
            info = tabula.read_pdf(pdf_path,guess=True,lattice=False,password=passcode,area=[95.1,8.7,179.0,601.2],pages=1,pandas_options={'header':None})
            col_name=['Date','Particulars','Chq.No.', 'Withdrawals','Deposits', 'Autosweep', 'Reverse', 'Balance']
            master_table=DataFrame()
            #removing extra columns and concatenating particulars spitted into different columns
            for i in range(1,len(tables)):
                if len(tables[i].columns)>8:
                    tables[i].dropna(axis=1,how='all',inplace=True)
                if len(tables[i].columns)>8:
                    col_date=tables[i].columns.get_loc('Date')
                    col_chq=tables[i].columns.get_loc('Chq.No.')
                    key_p=tables[i].columns[col_date+1]
                    tables[i][key_p]=tables[i][key_p].apply(lambda x: str(x) if not isna(x) else "")
                    if col_chq-col_date!=2:
                        for j in range(col_date+2,col_chq):
                            key_extra=tables[i].columns[j]
                            tables[i][key_extra]=tables[i][key_extra].apply(lambda x: x if not isna(x) else "")
                            tables[i][key_p]+=tables[i][key_extra]
                            tables[i].drop([key_extra],inplace=True,axis=1)
                if len(tables[i].columns)==8:
                    tables[i].columns=col_name
                elif i!=0:
                    print("check for tables["+str(i)+"]")
            #removing unnecssary rows from end and concatenating into master_table
            for i in range(1,len(tables)):
                tables[i]=tables[i][['Date','Particulars', 'Withdrawals','Deposits','Balance']]
                for col in (tables[i].columns):
                    if tables[i][tables[i][col]=="Page Total:"].any()['Particulars']:
                        row=tables[i].index[tables[i][col]=="Page Total:"][0]
                        tables[i]=tables[i][:row]
                        break
                master_table=concat([master_table,tables[i]])
            master_table.reset_index(drop=True,inplace=True)
            #removing b\f
            if master_table[master_table['Particulars']=="B/F"].any()['Particulars']:
                row=master_table.index[master_table[col]=="B/F"][0]
                master_table=master_table[row+1:]
                master_table.reset_index(drop=True,inplace=True)
            #concatenating particulars split up into different rows
            for j in range(1,len(master_table)):
                if isna(master_table['Date'][j]):
                    master_table['Particulars'][j-1]+=master_table['Particulars'][j]
            master_table.dropna(subset=['Date'],inplace=True)
            master_table.reset_index(drop=True,inplace=True)
            #extracting account holder name; number is extracted along current and savings decider
            for i in range(len(info)) :
                for j in range(len(info[i])) :
                    for k in range(len(info[i].columns)):
                        if type(info[i].iloc[j,k])==str and "Your Details With Us:" in info[i].iloc[j,k]:
                            name = info[i].iloc[j+1,k]
                            break
            master_table2=master_table
            master_table2['Balance']=master_table['Balance'].apply(lambda x: x[:-3] if x[-2:]=="Cr" else ("-"+x[:-3]))
            master_table2.rename(columns={'Date':'Txn Date','Withdrawals':'Debit','Deposits':'Credit','Particulars':'Description'}, inplace=True)
            master_table2 = master_table
            #standardising dataframe according to standard schema
            master_table2['Account Name']=name
            master_table2['Account Number']=acct_number
            master_table2 = master_table2[['Txn Date','Description','Debit','Credit','Balance','Account Name','Account Number']]
            master_table2['Txn Date'] = [dt.strftime(to_datetime(x,dayfirst=True),"%d-%m-%Y") for x in master_table2['Txn Date']]
            last_trans_date = master_table2['Txn Date'].iat[-1]
            master_table2.to_csv(r"{}\{}_{}_{}.csv".format(out_path,pdf_file, acct_number, last_trans_date),index=False)
            
        elif xx_format==True:
            tables1 = tabula.read_pdf(pdf_path,guess=True,lattice=False,password=passcode,area=[100,30,900,600],pages='all',columns=[70,130,430,350,520])
            info1 = tabula.read_pdf(pdf_path,guess=True,lattice=False,password=passcode,area=[0,0,900,600],pages='1',columns=[200,200,430,350,520])
            #extracting account information (name/number)
            for i in range(len(info1)) :
                for j in range(len(info1[i])) :
                    for k in range(len(info1[i].columns)) :
                        if type(info1[i].iloc[j,k])==str:
                            if info1[i].iloc[j,k].startswith('MR.') or info1[i].iloc[j,k].startswith('MRS.') or info1[i].iloc[j,k].startswith('MS.'):
                                name = info1[i].iloc[j,k]
            for i in range(len(tables1)): 
                tables1[i].columns = ['DATE','MODE**','PARTICULARS','DEPOSITS','WITHDRAWALS','BALANCE']
                len_bf = len(tables1[i])
                for j in range(len(tables1[i]['DATE'])):
                    if tables1[i]['DATE'][j] == 'DATE':
                        tables1[i] = tables1[i].iloc[j:] 
                        tables1[i] = tables1[i].reset_index(drop=True)
                        break
            
            for i in range(len(tables1)):
                for j in range(len(tables1[i])):
                        if tables1[i]['PARTICULARS'][j] == 'Total:':
                            tables1[i] = tables1[i].iloc[:j]
                            break
                len_af = len(tables1[i])
                tables1[i] = tables1[i].iloc[1:]
                tables1[i] = tables1[i].reset_index(drop=True)
                if len_bf == len_af:
                    tables1.pop(i)
            master_table2=DataFrame()
            for i in range(len(tables1)):
                tables1[i]=tables1[i][tables1[i]['PARTICULARS']!="B/F"]
                tables1[i].reset_index(drop=True,inplace=True)
                tables1[i]=concat_desc(tables1[i])
                master_table2=concat([master_table2,tables1[i]])
            #standardising dataframe according to standard schema
            master_table2=master_table2[['DATE', 'PARTICULARS', 'DEPOSITS', 'WITHDRAWALS', 'BALANCE']]
            master_table2.rename({'DATE':'Txn Date','PARTICULARS':'Description','DEPOSITS':'Credit','WITHDRAWALS':'Debit','BALANCE':'Balance'},inplace=True,axis=1)
            master_table2['Account Name']=name
            master_table2['Account Number']=acct_number
            master_table2 = master_table2[['Txn Date','Description','Debit','Credit','Balance','Account Name','Account Number']]
            master_table2['Txn Date'] = [dt.strftime(to_datetime(x,dayfirst=True),"%d-%m-%Y") for x in master_table2['Txn Date']]
            last_trans_date = master_table2['Txn Date'].iat[-1]
            master_table2.to_csv(r"{}\{}_{}_{}.csv".format(out_path,pdf_file, acct_number, last_trans_date),index=False)
            
            
        else:
            #savings=True
            #format 2; account number all digits
            tables=tabula.read_pdf(pdf_path,password=passcode,pages='all',area=[140.0,14.5,824.7,593.2],columns=[72.8,155.9,350.3,428.9,506.7,585.3])
            info_name = tabula.read_pdf(pdf_path,password=passcode,area=[153.2,17.2,250.4,589.7],pages='1',pandas_options={'header':None})
            #extracting account name and number
            for i in range(len(info_name[0])):
                ele=info_name[0].iloc[i,0]
                if type(ele)==str and (ele.startswith("MR.") or ele.startswith("MRS.") or ele.startswith("MS.") or ele.startswith("M/S") or ele.startswith("Master")):
                    name=ele
                    break
            col_names=['DATE', 'MODE**', 'PARTICULARS', 'DEPOSITS', 'WITHDRAWALS', 'BALANCE']
            #poping out last dataframe containing extra infrmation
            if not "DATE" in tables[-1].columns:
                tables.pop()
            #removing information part from tables[0]
            key0=tables[0].columns[0]
            if tables[0][tables[0][key0]=="DATE"].any()[key0]:
                row=tables[0].index[tables[0][key0]=="DATE"][0]
                tables[0]=tables[0][row-1:]
                tables[0].reset_index(drop=True,inplace=True)
                if len(tables[0].columns==6):
                    tables[0].columns=col_names
                else:
                    print("handle extra column in tables[0]")
            #super dataframe which contains rows for all statements present in single file
            super_df=DataFrame()
            for i in range(len(tables)):
                super_df=concat([super_df,tables[i]])
            super_df.reset_index(drop=True,inplace=True)
            #splitters contains all the start index of all statements present
            splitters=super_df.index[super_df['DATE']=="Statement o"]
            for i in range(len(splitters)):
                if i==len(splitters)-1:
                    df=super_df[splitters[i]:]
                else:
                    df=super_df[splitters[i]:splitters[i+1]]
                df.reset_index(drop=True,inplace=True)
                #extract the account number
                acct_number_string=df['PARTICULARS'][0].split(":")[1]
                acct_number="'{}'".format(acct_number_string.split()[0])
                #drop extra rows:- first 3 lines (statement, date , "B\F") and after total
                df=df[3:]
                df.reset_index(drop=True,inplace=True)
                if df[df['PARTICULARS']=="OTAL"].any()['PARTICULARS']:
                    row=df.index[df['PARTICULARS']=="OTAL"][0]
                    df=df[:row]
                if df[df['PARTICULARS']=="TOTAL"].any()['PARTICULARS']:
                    row=df.index[df['PARTICULARS']=="TOTAL"][0]
                    df=df[:row]
                df.reset_index(drop=True,inplace=True)
                #concat desc
                df=concat_desc(df)
                #drop extra columns and add account  name and number
                df=df[['DATE', 'PARTICULARS', 'DEPOSITS', 'WITHDRAWALS', 'BALANCE']]
                df.rename({'DATE':'Txn Date','PARTICULARS':'Description','DEPOSITS':'Credit','WITHDRAWALS':'Debit','BALANCE':'Balance'},inplace=True,axis=1)
                df['Account Name']=name
                df['Account Number']=acct_number
                df['Txn Date'] = [dt.strftime(to_datetime(x,dayfirst=True),"%d-%m-%Y") for x in df['Txn Date']]
                last_trans_date = df['Txn Date'].iat[-1]
                df.to_csv(r"{}\{}_{}_{}.csv".format(out_path,pdf_file, acct_number, last_trans_date),index=False)

    else:
        #print("net_banking"+str(i))
        tables2 = tabula.read_pdf(pdf_path, pages=1,password = passcode)
        if len(tables2)==0:
            print("This is an image-based statement, hence, cannot be digitized here.")
            return
        if "No." in tables2[0].columns:
            #non retails
            tables=tabula.read_pdf(pdf_path, pages='all',stream=True,password=passcode,pandas_options=({'header':None}))
            cust_info=tabula.read_pdf(pdf_path,pages=1,stream=True,password=passcode,area=[171,0,221.4,907.2],pandas_options=({'header':None}))
            col_names=["No.","Txn Id","Value Date","Txn Date","Chq no","Description","Cr/Dr","Amount","Balance"]
            master_table=DataFrame(columns=col_names)
            row=0
            for i in range(len(tables)):
                #checking if description is split into multiple columns and merging
                if len(tables[i].columns)==10:
                    for j in range(len(tables[i])):
                        if not isna(tables[i][tables[i].columns[5]][j]) and not isna(tables[i][tables[i].columns[6]][j]):
                            tables[i][tables[i].columns[5]]=str(tables[i][tables[i].columns[5]][j])+str(tables[i][tables[i].columns[6]][j])
                    tables[i].drop(tables[i].columns[6],inplace=True,axis=1)
                #renaming columns to avoid non printable chars in column names
                tables[i].columns=col_names
                #concatenating description splited into multiple rows
                for j in range(len(tables[i])):
                    if not isna(tables[i]['No.'][j]) and tables[i]['No.'][j]!="No.":
                        if j>0 and not isna(tables[i]['Description'][j-1]) and isna(tables[i]['Txn Date'][j-1]) and str(tables[i]['Description'][j])!=str(tables[i]['Description'][j-1]):
                            if isna(tables[i]['Description'][j]):
                                tables[i]['Description'][j]=str(tables[i]['Description'][j-1])
                            else:
                                tables[i]['Description'][j]=str(tables[i]['Description'][j-1])+str(tables[i]['Description'][j])
                        if j+1<len(tables[i]) and not isna(tables[i]['Description'][j+1]) and isna(tables[i]['Txn Date'][j+1]) and str(tables[i]['Description'][j])!=str(tables[i]['Description'][j+1]):
                            if isna(tables[i]['Description'][j]):
                                tables[i]['Description'][j]=str(tables[i]['Description'][j+1])
                            else:
                                tables[i]['Description'][j]=str(tables[i]['Description'][j])+str(tables[i]['Description'][j+1])
                        master_table.loc[row]=tables[i].loc[j]
                        row+=1
                #spliting amount column into debit and credit resp
                master_table['Debit'] = master_table.loc[master_table['Cr/Dr'] == "DR" , 'Amount']
                master_table['Credit'] = master_table.loc[master_table['Cr/Dr'] == "CR" , 'Amount']
            #dropping off uneccesary column and extracting account info
            master_table=master_table[["Txn Date","Description","Debit","Credit","Balance"]]
            info_string=cust_info[0].iloc[0,1]
            account_name=info_string.split("-")[1][:-7].strip()
            account_no="'{}'".format(info_string.split("-")[2].strip())
            
        elif "Sr No" in tables2[0].columns:
            #new format of 2020
            tables = tabula.read_pdf(pdf_path,lattice=True,pages='all',password=passcode,pandas_options={'header':None})
            cust_info=tabula.read_pdf(pdf_path,pages=1,stream=True,area=[73.7,13.7,250.4,566.7],password=passcode,pandas_options=({'header':None}))
            #removing headers from 0th df
            tables[0] = tables[0].drop(tables[0].index[0])
            tables[0].reset_index(drop=True,inplace=True)
            master_table=DataFrame()
            #renaming columns and concatenating to master_table
            for i in range(len(tables)):
                tables[i].rename({0:"Sr. No.",1:"Value Date",2:"Txn Date",
                                  3:"ChequeNumber",4:"Description",5:"Debit",6:"Credit",7:"Balance"},axis = 1, inplace = True)
                tables[i].drop(tables[i].columns[[0,1,3]], axis=1, inplace=True)
                master_table=concat([master_table,tables[i]])
            #spliting amount column into debit and credit resp
            master_table.reset_index(drop=True,inplace=True)
            master_table['Debit'] = master_table['Debit'].replace('NA',nan)
            master_table['Credit'] = master_table['Credit'].replace('NA',nan)
            #extracting account information
            for i in range(len(cust_info[0])):
                ele=cust_info[0].iloc[i,0]
                if type(ele)==str and (ele.startswith("Account Name:")):
                    account_name=ele.split(':', 1)[-1]
                    break
                account_no="'{}'".format(cust_info[0].iloc[0,0].split()[-1])
            #changing new date format
            master_table['Txn Date']= [(i[:7]+i[10:]) for i in master_table['Txn Date']]
            master_table['Txn Date'] = [dt.strftime(to_datetime(x,dayfirst=True),"%d-%m-%Y") for x in master_table['Txn Date']]
            last_trans_date = master_table['Txn Date'].iloc[-1]
            
        else:
            #retails old formats
            tables = tabula.read_pdf(pdf_path, pages='all',stream=True,password=passcode)
            tables2 = tabula.read_pdf(pdf_path, pages='all',lattice=True,password=passcode)
            cust_info = tabula.read_pdf(pdf_path, pages=1,password=passcode,stream=True,area=[134.5,28.2,371.8,983.1],pandas_options={'header':None})
            #to extract balance correctly with decimal points and then adding back to original tables
            for i in range(len(tables2)):
                tables2[i].dropna(subset=[tables2[i].columns[1]],inplace=True)
                tables2[i].reset_index(drop=True,inplace=True)
            temp_bal=core.series.Series(dtype=float)
            for i in range(len(tables2)):
                temp_bal=temp_bal.append(tables2[i][tables2[i].columns[-1]])
            temp_bal=temp_bal.reset_index()
            for i in range(len(tables)):
                tables[i].dropna(axis=0,how='all',inplace=True)
            # setting the header as standard wherever first row of table is taken as header by tabula
            for i in range(len(tables)) :
                tables[i] = tables[i].append(Series([nan]) , ignore_index = True)
                tables[i] = tables[i].shift(1,axis=0)
                tables[i].iloc[0] = tables[i].columns
                if tables[i].columns[-1] == 0 :
                    del tables[i][0]
            #dropping extra columns
            for i in range(len(tables)) :
                if len(tables[i].columns) > 8:
                    for j in range(len(tables[i])) :
                        for k in range(1,(len(tables[i].columns)-7)):
                            tables[i].iloc[j,4] = tables[i].iloc[j,4] + tables[i].iloc[j,4+k]
                            del tables[i][tables[i].columns[4+k]]
                        if len(tables[i].columns)>8:
                            tables[i].dropna(axis=1,how='all')
                        break
            # setting the header as standard wherever first row of table is taken as header by tabula
            for i in range(len(tables)) :
                tables[i].columns = ['S No.','Value Date','Txn Date','Cheque Number','Description','Debit','Credit','Balance']
            # appending all tables of a pdf
            master_table = tables[0]
            for i in range(len(tables)-1):
                master_table = concat([master_table, tables[i+1]])
            master_table = master_table[master_table['Description'] != 'Unnamed: 4']
            master_table = master_table[master_table['S No.'] != 'S No.']
            master_table = master_table.dropna(subset=['Description'])
            master_table=master_table.replace(nan,'')
            master_table.reset_index(drop=True,inplace=True)
            master_table['Description']=list(map(str,master_table['Description']))
            #merging description
            for i in reversed(range(len(master_table))) :
                if master_table['Value Date'][i] == '' :
                    master_table['Description'][i-1] = master_table['Description'][i-1] + master_table['Description'][i]
                else :
                    continue
            #removing blank
            for i in range(len(master_table)):
                master_table=master_table.replace('',nan) 
                master_table.dropna(subset=['Value Date'],inplace=True)
            master_table.reset_index(drop=True,inplace=True)
            #correcting date where .1 is there
            for i in range(len(master_table)):
                if len(master_table['Txn Date'][i])>10:
                    master_table['Txn Date'][i]=master_table['Txn Date'][i][0:10]
                else:
                    continue
            # we have to resolve the issue where Debit/Credit/Balance column have 2 decimals
            col1=master_table.columns.get_loc('Debit')
            for i in range(len(master_table)):
                for j in range(col1,len(master_table.columns)):
                    if master_table.iloc[i,j].count('.') > 1 :
                        master_table.iloc[i,j] = master_table.iloc[i,j][:-2]
            for i in range(len(master_table)):
                master_table['Balance'][i]=temp_bal[0][i+1]
            del master_table['S No.']
            for i in range(len(cust_info[0])):
                for j in range(len(cust_info[0].columns)):
                    if type(cust_info[0].iloc[i,j])==str and cust_info[0].iloc[i,j].find("Account Number")!=-1:
                        info_string=cust_info[0].iloc[i,j].split('-',2)
                        account_name=info_string[-1].strip()
                        account_no="'{}'".format(info_string[0].split()[-1][:-5])
                        break
        ## adding the common parts
        master_table['Account Name'] = account_name
        master_table['Account Number'] = account_no
        
        master_table2 = master_table.reset_index(drop=True)
        master_table2['Txn Date'] = [dt.strftime(to_datetime(x,dayfirst=True),"%d-%m-%Y") for x in master_table2['Txn Date']]
        master_table2 = master_table2[['Txn Date', 'Description', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number']]
        last_trans_date = master_table2['Txn Date'].iat[-1]
        

        df = DataFrame(master_table2)
        options.mode.chained_assignment = None
    
        column_names=['Statement_name','Wrong Credit', 'Wrong Debit', 'Remark']
        result=DataFrame(index=[1],columns=column_names)
    
        if df['Credit'].dtype =='O':
            df['Credit_changed'] = (df['Credit'].astype(str).str.replace(',','')).str.replace('\r','').astype(float)
        else:
            df['Credit_changed']= df['Credit'].astype(float)
        if df['Debit'].dtype =='O':
            df['Debit_changed'] = (df['Debit'].astype(str).str.replace(',','')).str.replace('\r','').astype(float)
        else:
            df['Debit_changed']= df['Debit'].astype(float)
        if df['Balance'].dtype =='O':
            df['Balance_changed'] = (df['Balance'].astype(str).str.replace(',','')).str.replace('\r','').astype(float)
        else:
            df['Balance_changed']= df['Balance'].astype(float)
        
        df['Balance_changed'] = df['Balance_changed'].replace(0,nan)
        df['Debit_changed'] = df['Debit_changed'].replace(0,nan)
        df['Credit_changed'] = df['Credit_changed'].replace(0,nan)        
    
        col_credit=df.columns.get_loc('Credit_changed')
        col_debit=df.columns.get_loc('Debit_changed')
        col_bal=df.columns.get_loc('Balance_changed')
        #col_desc=df.columns.get_loc('Description')
    
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
            master_table2.to_csv("{}/{}_Digitized.csv".format(out_path,file_name),index=False)        
            result.to_csv("{}/{}_LogicalChecks.csv".format(out_path,file_name),index=False)
            return
        
        import warnings
        warnings.simplefilter(action='ignore', category=FutureWarning)

    #Converting list to string
        def listToString(s):  
            str1 = " " 
            return (str1.join(s))
        sbi_df=df
        #charges
        try:
            df_chgs=sbi_df[sbi_df["Description"].str.contains("charges",case=False)]
            sbi_df=sbi_df[~sbi_df["Description"].isin(df_chgs['Description'])]
            df_t1=sbi_df[sbi_df["Description"].str.contains("chrgs",case=False)]
            sbi_df=sbi_df[~sbi_df["Description"].isin(df_t1['Description'])]
            df_t2=sbi_df[sbi_df["Description"].str.contains("chgs",case=False)]
            sbi_df=sbi_df[~sbi_df["Description"].isin(df_t2['Description'])]
            df_t3=sbi_df[sbi_df["Description"].str.contains("charge",case=False)]
            sbi_df=sbi_df[~sbi_df["Description"].isin(df_t3['Description'])]
            df_t4=sbi_df[sbi_df["Description"].str.contains("chrg",case=False)]
            sbi_df=sbi_df[~sbi_df["Description"].isin(df_t4['Description'])]
            df_t5=sbi_df[sbi_df["Description"].str.contains("MONTHLY ave",case=False)]
            sbi_df=sbi_df[~sbi_df["Description"].isin(df_t5['Description'])]
            df_chgs=concat([df_chgs,df_t1,df_t2,df_t3,df_t4,df_t5])
            del df_t1
            del df_t2
            df_chgs['entity']="NA"
            df_chgs['mode']='NA'
            df_chgs['sub_mode']='Charges'
            df_chgs['source_of_trans']='Automated'
            #df_chgs['entity_bank']='NA'
            df_chgs['df']='36'
        
        except:
            pass
        #Salary
        try:
            df22=sbi_df[sbi_df["Description"].str.contains(pat="Revers", case=False)]
            df_t=sbi_df[sbi_df["Description"].str.contains(pat="UPI/REV", case=False)]
            df_t1=sbi_df[sbi_df["Description"].str.contains(pat="return", case=False)]
            df22=concat([df22,df_t,df_t1])
            sbi_df=sbi_df[~sbi_df["Description"].isin(df22['Description'])]
            del df_t
            del df_t1
            df22['sub_mode']='REV'
            df22['source_of_trans']='Automated'
            #df22['entity_bank']='NA'
            df22['entity']='NA'
            df22['mode']='Reversal'
            df22['df']='22'
        except:
            pass
    #subsetting upi transactions
        try:
            df1=sbi_df[sbi_df["Description"].str.contains(pat="-UPI")]
            df1=df1[~df1["Description"].str.contains(pat="REVERSAL")]
            df1=df1[~df1["Description"].str.contains(pat="REV/")]
            df1[["sub_mode", "credit/debit", "trans_id", "entity", "bank_of_entity", "entity_id", "others"]] = df1.Description.str.split("/", expand=True)
            df1['source_of_trans']='Self Initiated'
            #df1['entity_bank'] = df1['bank_of_entity'].apply(lambda x: 'SBI' if x == 'SBIN' else 'Others')
            df1['sub_mode']='UPI'
            df1['mode']='Mobile App'
            df1.drop(["others", 'credit/debit', "trans_id", "bank_of_entity", "entity_id" ], axis=1, inplace=True)
            df1['df']='1'
        except:
            pass

    #subsetting NEFT
        try:
            df2=sbi_df[sbi_df["Description"].str.contains(pat="BY TRANSFER-NEFT")]
            df2["Description"]=df2["Description"].str.lstrip()
            df2['new']=df2['Description'].str.split("*")
            df2['sub_mode']=df2['new'].apply(lambda x:x[0])
            df2['entity']=df2['new'].apply(lambda x:x[3])
            df2['entity_ifsc']=df2['new'].apply(lambda x:x[1])
            df2['entity_ifsc']=df2["entity_ifsc"].str[:4]
            df2['source_of_trans']='Self Initiated'
            #df2['entity_bank'] = df2['entity_ifsc'].apply(lambda x: 'SBI' if x == 'SBIN' else 'Others')
            df2['mode']='Net Banking'
            df2.drop(["new", "entity_ifsc" ], axis=1, inplace=True)
            df2['df']='2'
        except:
            pass

    #######subsetting deposit transfer
        try:
            df3=sbi_df[sbi_df["Description"].str.contains(pat="DEPOSIT TRANSFER")]
            df3['new']=df3['Description'].str.split("TO")
            df3['sub_mode']="DEPOSIT TRANSFER"
            df3['entity']=df3['new'].apply(lambda x:x[-1])
            df3['entity']=df3['entity'].str.replace('-','')
            df3['source_of_trans']='Self Initiated'
            df3['mode']='Net Banking'
            #df3['entity_bank']='NA'
            df3.drop(["new"], axis=1, inplace=True)
            df3['df']='3'
        except:
            pass


    #######subsetting debit card

        try:
            debit_card=sbi_df[sbi_df["Description"].str.contains(pat="debit card")]
            debit_card["Description"]=debit_card["Description"].str.lstrip()
            debit_card['new']=debit_card['Description'].str.split("-")
        except:
            pass

        try:
            df4=debit_card[debit_card["Description"].str.contains(pat="PG")]
            df4['mode_1']=df4["new"].apply(lambda x: x[0])
            df4['mode_2']=df4["new"].apply(lambda x: x[1]).str[:5]
            df4['sub_mode']="Debit Card"
            df4['entity']=df4["new"].apply(lambda x: x[1]).str[9:]
            remove_digits = str.maketrans('', '', digits) 
            df4['entity']=df4["entity"].apply(lambda x: x.translate(remove_digits))
            df4['source_of_trans']='Self Initiated'
            #df4['entity_bank'] = df4['mode_2'].apply(lambda x: 'SBI' if x == 'SBIPG' else 'Others')
            df4['mode']='Card'
            df4.drop(["new", "mode_1", 'mode_2' ], axis=1, inplace=True)
            df4['df']='4'
        except:
            pass


    #point of sale
        try:
            df5=debit_card[debit_card["Description"].str.contains(pat="POS")]
            df5["new"]=df5["new"].apply(lambda x:x[1].split("POS",1)[-1])
            df5['mode_1']=df5["new"].apply(lambda x: x[0])
            df5['mode_2']=df5["new"].apply(lambda x: x[1]).str[:6]
            df5['sub_mode']="Debit Card"
            remove_digits = str.maketrans('', '', digits) 
            df5['entity']=df5["new"].apply(lambda x: x.translate(remove_digits))
            df5['source_of_trans']='Self Initiated'
            #df5['entity_bank'] = df5['mode_2'].apply(lambda x: 'SBI' if x == 'SBIPOS' else 'Others')
            df5['mode']='Card'
            df5.drop(["new", "mode_1", 'mode_2' ], axis=1, inplace=True)
            df5['df']='5'
        except:
              pass


    #ATM WDL
        try:
            df6=sbi_df[sbi_df["Description"].str.startswith("ATM WDL")]
            df6['sub_mode']='ATM WDL'
            df6['source_of_trans']='Self Initiated'
            #df6['entity_bank']='NA'
            df6['entity']='NA'
            df6['mode']='Cash'
            df6['df']='6'
        except:
            pass


    ######substting clearing
        try:
            df7=sbi_df[sbi_df["Description"].str.contains(pat="CLEARING")]
            df7[["sub_mode","entity","cheque_no"]]=df7.Description.str.split("-",expand=True)
            df7['source_of_trans']='Self Initiated'
            #df7['entity_bank']='NA'
            df7['mode']='Cheque'
            df7.drop(["cheque_no"], axis = 1, inplace=True)
            df7['df']='7'
        except:
            pass

    ######substting INB
        try:
            df9=sbi_df[sbi_df["Description"].str.contains(pat="TRANSFER-INB")]
            df9["Description"]=df9.Description.str.lstrip()
        except:
            pass

        try:
            df9a = df9[df9["Description"].str.contains(pat="IMPS")]
            df9a = df9a[~df9a["Description"].str.contains(pat="P2A")]
            df9a = df9a[~df9a["Description"].str.contains(pat="INBCommission")]
            df9a['new']=df9a['Description'].str.split("/")
            df9a['sub_mode']="IMPS"
            df9a['source_of_trans']='Self Initiated'
            #df9a['entity_bank']='NA'
            df9a['entity']=df9a["new"].apply(lambda x:x[2])
            df9a['mode']='Net Banking'
            df9a.drop(['new'], axis=1, inplace=True)
            df9a['df']='9a'
        except :
        
            pass

        try:
            df9b = df9[df9["Description"].str.contains(pat="/P2A/")]
            df9b['new']=df9b['Description'].str.split("/")
            df9b['sub_mode']="IMPS"
            df9b['source_of_trans']='Self Initiated'
            #df9b['entity_bank']='NA'
            df9b['entity']=df9b['new'].apply(lambda x:x[-1])
            df9b['mode']='Net Banking'
            df9b.drop(['new'], axis=1, inplace=True)
            df9b['df']='9b'
        except:
            pass
    
        try:
            df9c = df9[df9["Description"].str.contains(pat="INBCommission")]
            df9c['sub_mode']="Charges"
            df9c['source_of_trans']='Automated'
            #df9c['entity_bank']='NA'
            df9c['entity']='NA'
            df9c['mode']='NA'
            df9c['df']='9c'
        except:
            pass


    ######substting cheque deposit
        try:
            df10=sbi_df[sbi_df["Description"].str.contains(pat="CHEQUE DEPOSIT")]
            df10["sub_mode"]="CHEQUE DEPOSIT"
            df10['source_of_trans']='Self Initiated'
            #df10['entity_bank']='NA'
            df10['entity']=(df10['Description'].str.split('-',1)).apply(lambda x:x[1])
            df10['entity']=df10['entity'].str.replace('-','')
            df10['mode']='Cheque'
            df10['df']='10'
        except:
            pass


    ######subsetting Interest
        try:   
            df11=sbi_df[sbi_df["Description"].str.contains(pat="INTEREST")]
            df11["Description"]=df11.Description.str.lstrip()
            df11['source_of_trans']='Automated'
            #df11['entity_bank']='NA'
            df11['entity']='NA'
            df11['sub_mode']='Interest'
            df11['mode']='Interest'
            df11['df']='11'
        except:
            pass


    ######subsetting Bulk Posting
        try:
            df12=sbi_df[sbi_df["Description"].str.contains(pat="BULK POSTING")]
            df12a=df12[df12["Description"].str.contains(pat="BULK POSTINGBY")]
            df12 = df12[~df12["Description"].str.contains(pat="BULK POSTINGBY")]
            df12=df12[~df12["Description"].str.contains(pat="SALARY")]
            df12["new"]=df12["Description"].str.split("-",1)
            df12["sub_mode"]=df12["new"].apply(lambda x: x[0])
            df12['source_of_trans']='Automated'
            #df12['entity_bank']='NA'
            df12['mode']='NA'
            df12['entity']=df12["new"].apply(lambda x: x[1])
            df12['entity']=df12['entity'].str.replace('-','')
            remove_digits = str.maketrans('', '', digits) 
            df12['entity']=df12["entity"].apply(lambda x: x.translate(remove_digits))
            df12.drop(["new"], axis = 1, inplace=True)
            df12['df']='12'
        
            df12a["new"]=df12a["Description"].str.split("BY",1)
            df12a["sub_mode"]=df12a["new"].apply(lambda x: x[0])
            df12a['source_of_trans']='Automated'
            #df12a['entity_bank']='NA'
            df12a['mode']='NA'
            df12a['entity']=df12a["new"].apply(lambda x: x[1])
            df12a.drop(["new"], axis = 1, inplace=True)
            df12a['df']='12a'
        except :
            print("df12")
            pass

        #######subsetting cash deposit
        try:
            df13=sbi_df[sbi_df["Description"].str.contains(pat="CASH DEPOSIT")]
            df13['sub_mode']="CASH DEPOSIT"
            df13['source_of_trans']='Self Initiated'
            #df13['entity_bank']='NA'
            df13['entity']='NA'
            df13['mode']='Cash'
            df13['df']='13'
        except:
            pass



    #######subsetting cash deposit through Machine
        try:
            df14=sbi_df[sbi_df["Description"].str.contains(pat="CSH DEP")]
            df14["new"]=df14["Description"].str.split("-")
            df14['sub_mode']=df14["new"].apply(lambda x: x[0])
            df14['source_of_trans']='Self Initiated'
            #df14['entity_bank']='NA'
            df14['entity']='NA'
            df14['mode']='Cash'
            df14.drop(["new"], axis = 1, inplace=True)
            df14['df']='14'
        except:
            pass


    #######subsetting cheque withdrawal
        try:
            df15=sbi_df[sbi_df["Description"].str.contains(pat="CHEQUE WDL")]
            df15a=df15[df15["Description"].str.contains(pat="CHEQUETRANSFER")]
            df15b=df15[df15["Description"].str.contains(pat="WITHDRAWALTRANSFER")]
            df15=df15[~df15['Description'].isin(df15a['Description'])]
            df15=df15[~df15['Description'].isin(df15b['Description'])]
            df15[["sub_mode","entity"]]=df15['Description'].str.split("-",1,expand=True)
            df15['source_of_trans']='Self Initiated'
            #df15['entity_bank']='NA'
            df15['mode']='Cheque'
            df15['df']='15'
        except :
            pass
        try:
            df15a[["sub_mode","entity"]]=df15a['Description'].str.split("TO",1,expand=True)
            df15a['sub_mode']='Cheque Transfer'
            df15a['source_of_trans']='Self Initiated'
            #df15a['entity_bank']='NA'
            df15a['mode']='Cheque'
            df15a['df']='15a'
        except:
            pass
        try:
            df15b[["sub_mode","entity"]]=df15b['Description'].str.split("BY",1,expand=True)
            df15b['sub_mode']='Cheque Transfer'
            df15b['source_of_trans']='Self Initiated'
            #df15b['entity_bank']='NA'
            df15b['mode']='Cheque'
            df15b['df']='15a'
        except:
            pass
    #######subsetting cash withdrawal by cheque
        try:
            df16=sbi_df[sbi_df["Description"].str.contains(pat="CASH CHEQUE-CASHWITHDRAWAL")]
            df16[["x1", "entity"]]=df16.Description.str.split("BY",1,expand=True)
            df16['source_of_trans']='Self Initiated'
            #df16['entity_bank']='NA'
            df16['sub_mode']='Cash Withdrawal'
            df16['mode']='Cheque'
            df16.drop(["x1"], axis = 1, inplace=True)
            df16['df']='16'
        except:
            pass
        try:
            df16a=sbi_df[sbi_df["Description"].str.contains(pat="CASH CHEQUE")]
            df16a=df16a[~df16a['Description'].isin(df16['Description'])]
            df16a[["x1", "entity"]]=df16a.Description.str.split("-",1,expand=True)
            df16a['source_of_trans']='Self Initiated'
            #df16a['entity_bank']='NA'
            df16a['sub_mode']='Cash Withdrawal'
            df16a['mode']='Cheque'
            df16a.drop(["x1"], axis = 1, inplace=True)
            df16a['df']='16a'
        except:
            pass


    #######subsetting cash withdrawal by cheque
        try:
            df17=sbi_df[sbi_df["Description"].str.contains(pat="CASH WITHDRAWAL")]
            df17[["sub_mode","x1","x2"]]=df17.Description.str.split("-",expand=True)
            df17['source_of_trans']='Self Initiated'
            #df17['entity_bank']='NA'
            df17['entity']='NA'
            df17['mode']='Cash'
            df17.drop(["x1", "x2"], axis = 1, inplace=True)
            df17['df']='17'
        except:
            pass


    #######subsetting YONO transactions
        try:
            df18=sbi_df[sbi_df["Description"].str.contains(pat="YONO")]
            df18[["x1","x2"]]=df18.Description.str.split(",",expand=True)
            df18['sub_mode']=df18["Description"].str[:17]
            df18['entity']=df18["Description"].str[17:]
            df18['source_of_trans']='Self Initiated'
            #df18['entity_bank']='NA'
            df18['mode']='Mobile App'
            df18.drop(["x1", "x2"], axis = 1, inplace=True)
            df18['df']='18'
        except:
            pass
    
        try:
            df19=sbi_df[sbi_df["Description"].str.startswith(pat="DEBIT-ATMCard")]
            df19['sub_mode']="DEBIT-ATMCard"
            df19['entity']="NA"
            df19['source_of_trans']='Self Initiated'
            #df19['entity_bank']='NA'
            df19['mode']='Card'
            df19['df']='19'
        except:
            pass


    #ACH
        try:
            df20=sbi_df[sbi_df["Description"].str.startswith("DEBIT-ACH")]
            df20['new']=df20['Description'].str.split("-")
            df20['sub_mode']="Debit ACH"
            df20['new_1']=df20["new"].apply(lambda x: x[1])
            #df20['entity_bank']=df20["new_1"].apply(lambda x: x[5:9])
            df20['new_1']=df20["new_1"].apply(lambda x: x[9:])
            remove_digits = str.maketrans('', '', digits) 
            df20['entity']=df20["new_1"].apply(lambda x: x.translate(remove_digits))
            df20['source_of_trans']='Automated'
            df20['mode']='Loan/MF'
            df20.drop(["new","new_1"], axis = 1, inplace=True)
            df20['df']='20'
        except :
        
            pass
    
    #Salary
        try:
            df21=sbi_df[sbi_df["Description"].str.contains(pat="SALARY", case=False)]
            df_t=sbi_df[sbi_df["Description"].str.contains(pat="CREDIT- SAL", case=False)]
            df21=df21[~df21['Description'].isin(df_t["Description"])]
            df21=concat([df21,df_t])
            del df_t
            df21['sub_mode']='Salary'
            df21['source_of_trans']='Automated'
            #df21['entity_bank']='NA'
            df21['entity']='NA'
            df21['mode']='Salary'
            df21['df']='21'
        except:
            pass

        #LIC
        try:
            df23=sbi_df[sbi_df["Description"].str.contains("LIC PREMIUM", case=False)]
            df23['new']=df23['Description'].str.split("-")
            df23['new']=df23["new"].apply(lambda x: x[1].split())
            df23['entity']=df23["new"].apply(lambda x: x[0])
            df23['sub_mode']="Insurance"
            df23['source_of_trans']='Self Initiated'
            df23['mode']='NA'
            #df23['entity_bank']='NA'
            df23['df']='23'
            df23.drop(["new"], axis = 1, inplace=True)
        except:
            pass
    
    
        try:
            df25=sbi_df[sbi_df["Description"].str.startswith("BY TRANSFER")]
            #removing upi and neft rows
            df25=df25[~df25["Description"].isin(df1["Description"])]
            df25=df25[~df25["Description"].isin(df2["Description"])]
            df25=df25[~df25["Description"].isin(df9a["Description"])]
            df25=df25[~df25["Description"].isin(df9b["Description"])]
            df27=df25[df25["Description"].str.contains("RTGS")]
            df28=df25[df25["Description"].str.contains("INB Refund")]
            df30=df25[df25["Description"].str.contains("UPI")]
            df25=df25[~df25["Description"].isin(df27["Description"])]
            df25=df25[~df25["Description"].isin(df28["Description"])]
            df25=df25[~df25["Description"].isin(df30["Description"])]
            df29=df25[df25["Description"].str.contains("-INB")]
            df29=df29[~df29["Description"].isin(df9b['Description'])]
            df31=df25[df25["Description"].str.contains("TRANSFERFROM")]
            df25=df25[~df25["Description"].isin(df29["Description"])]
            df25=df25[~df25["Description"].isin(df31["Description"])]
        
            #BY TRANSFER- ENTITY
            df25["new"]=df25["Description"].str.split("-",1)
            df25["entity"]=df25["new"].apply(lambda x : x[1])
            df25['sub_mode']='BY TRANSFER'
            df25['source_of_trans']='Self Initiated'
            df25['mode']='Net Banking'
            #df25['entity_bank']='NA'
            df25.drop(["new"], axis=1, inplace=True)
            df25['df']='25'
        
            #RTGS
            df27["new"]=df27["Description"].str.split("-")
            df27["entity"]=df27["new"].apply(lambda x : x[-1])
            df27['sub_mode']='RTGS'
            df27['source_of_trans']='Self Initiated'
            df27['mode']='Net Banking'
            #df27['entity_bank']='NA'
            df27.drop(["new"], axis=1, inplace=True)
            df27['df']='27'
        
            #INB Refund
            df28["entity"]="NA"
            df28['sub_mode']='Refund'
            df28['source_of_trans']='Automated'
            df28['mode']='Net Banking'
            #df28['entity_bank']='NA'
            df28['df']='28'
        
            #BY TRANSFER-INB-ENTITY
            df29["new"]=df29["Description"].str.split("-",1)
            df29["new"]=df29["new"].apply(lambda x : x[1].split(' ',1))
            df29["entity"]=df29["new"].apply(lambda x : x[-1])
            #df29['entity_bank']='NA'
            df29['source_of_trans']='Self Initiated'
            df29['mode']='Net Banking'
            df29['sub_mode']='BY TRANSFER'
            df29.drop(["new"], axis=1, inplace=True)
            df29['df']='29'
        
        
            #Transfer from
            df31["entity"]="NA"
            df31['sub_mode']='BY TRANSFER'
            df31['source_of_trans']='Self Initiated'
            df31['mode']='Net Banking'
            #df31['entity_bank']='NA'
            df31['df']='31'
        except:
            pass
    
        #debit sweep
        try:
            df32=sbi_df[sbi_df["Description"].str.startswith("DEBIT SWEEP")]
            df32['sub_mode']="Debit card"
            df32['entity']="NA"
            df32['source_of_trans']='Self Initiated'
            df32['mode']='Card'
            #df32['entity_bank']='NA'
            df32['df']='32'
        except:
            pass
        #transfer sweep
        try:
            df33=sbi_df[sbi_df["Description"].str.startswith("TRANSFER CREDIT")]
            df34=df33[df33["Description"].str.startswith("TRANSFER CREDIT-SWEEPFROM")]
            df35=df33[df33["Description"].str.startswith("TRANSFER CREDIT-SWEEPDEPOSIT")]
            df33=df33[~df33["Description"].isin(df34["Description"])]
            df33=df33[~df33["Description"].isin(df35["Description"])]
        
            df33['sub_mode']="NA"
            df33['entity']="NA"
            df33['source_of_trans']='Self Initiated'
            df33['mode']='Net Banking'
            #df33['entity_bank']='NA'
            df33['df']='33'
        
            df34["new"]=df34["Description"].str.rsplit(" ",1)
            df34["entity"]=df34["new"].apply(lambda x : x[-1])
            df34['sub_mode']='NA'
            df34['source_of_trans']='Self Initiated'
            df34['mode']='Net Banking'
            #df34['entity_bank']='NA'
            df34.drop(["new"], axis=1, inplace=True)
            df34['df']='34'
        
            df35['sub_mode']="NA"
            df35['entity']="NA"
            df35['source_of_trans']='Self Initiated'
            df35['mode']='Net Banking'
            #df35['entity_bank']='NA'
            df35['df']='35'
        except:
            pass
    
        try:
            df36=sbi_df[sbi_df["Description"].str.startswith("CHQ TRANSFER")]
            df36a=df36[df36['Description'].str.contains("NEFT")]
            df36b=df36[df36['Description'].str.contains("RTGS")]
            df36c=df36[df36['Description'].str.contains("DD")]
            df36d=df36[df36['Description'].str.contains("CHEQUETRANSFER")]
        
            df36=df36[~df36["Description"].isin(df36a["Description"])]
            df36=df36[~df36["Description"].isin(df36b["Description"])]
            df36=df36[~df36["Description"].isin(df36c["Description"])]
            df36=df36[~df36["Description"].isin(df36d["Description"])]
        
            df36['sub_mode']="To entity"
            df36["new"]=df36["Description"].str.split("-",1)
            df36['entity']=df36["new"].apply(lambda x: x[-1])
            df36['source_of_trans']='Self Initiated'
            df36['mode']='Cheque'
            #df36['entity_bank']='NA'
            df36.drop(["new"], axis=1, inplace=True)
            df36['df']='36'
        
            df36a["new"]=df36a["Description"].str.split(": ")
            df36a['new']=df36a['new'].apply(lambda x : x[1].split(" ",1))
            df36a['sub_mode']="NEFT"
            df36a['entity']=df36a["new"].apply(lambda x: x[-1])
            df36a['source_of_trans']='Self Initiated'
            df36a['mode']='Cheque'
            #df36a['entity_bank']='NA'
            df36a.drop(["new"], axis=1, inplace=True)
            df36a['df']='36a'
        
            df36b["new"]=df36b["Description"].str.split(":")
            df36b['new']=df36b['new'].apply(lambda x : x[1].split(" ",1))
            df36b['sub_mode']="RTGS"
            df36b['entity']=df36b["new"].apply(lambda x: x[-1])
            df36b['source_of_trans']='Self Initiated'
            df36b['mode']='Cheque'
            #df36b['entity_bank']='NA'
            df36b.drop(["new"], axis=1, inplace=True)
            df36b['df']='36b'
        
            df36c["new"]=df36c["Description"].str.split("-")
            df36c['sub_mode']="DD"
            df36c['entity']=df36c["new"].apply(lambda x: x[-1])
            df36c['source_of_trans']='Self Initiated'
            df36c['mode']='Demand Draft'
            #df36c['entity_bank']='NA'
            df36c.drop(["new"], axis=1, inplace=True)
            df36c['df']='36c'
        
            df36d["new"]=df36d["Description"].str.split("-")
            df36d['sub_mode']="To entity"
            df36d['entity']=df36d["new"].apply(lambda x: x[-1])
            df36d['source_of_trans']='Self Initiated'
            df36d['mode']='Cheque'
            #df36d['entity_bank']='NA'
            df36d.drop(["new"], axis=1, inplace=True)
            df36d['df']='36d'
        except:
            pass
    
        try:
            df37=sbi_df[sbi_df["Description"].str.startswith("WITHDRAWAL TRANSFER")]
            df37['sub_mode']="NA"
            df37['entity']="NA"
            df37['source_of_trans']='Self Initiated'
            df37['mode']='NA'
            #df37['entity_bank']='NA'
            df37['df']='37'
        except:
            pass
    
        try:
            df38=sbi_df[sbi_df["Description"].str.startswith("TO DEBIT THROUGHCHEQUE")]
            df38["new"]=df38["Description"].str.split("-")
            df38['sub_mode']="Cash Withdrawal through cheque"
            df38['entity']=df38["new"].apply(lambda x: x[-1])
            df38['source_of_trans']='Self Initiated'
            df38['mode']='Cheque'
            #df38['entity_bank']='NA'
            df38.drop(["new"], axis=1, inplace=True)
            df38['df']='38'
        except:
            pass
    
        try:
            df39=sbi_df[sbi_df["Description"].str.startswith("DEBIT-")]
            df_t=sbi_df[sbi_df["Description"].str.startswith("CREDIT-")]
            df39=concat([df39,df_t])
            del df_t
            df39=df39[~df39['Description'].isin(df20['Description'])]
            df39=df39[~df39['Description'].isin(df19['Description'])]
            df39=df39[~df39['Description'].isin(df21['Description'])]
            df39["new"]=df39["Description"].str.split("-",1)
            df39['sub_mode']="NA"
            df39['entity']=df39["new"].apply(lambda x: x[-1])
            df39['source_of_trans']='Self Initiated'
            df39['mode']='NA'
            #df39['entity_bank']='NA'
            df39.drop(["new"], axis=1, inplace=True)
            df39['df']='39'
        except:
            pass
    
        try:
            df40=sbi_df[sbi_df["Description"].str.startswith("FI Txn")]
            df40['sub_mode']="Funds"
            df40["new"]=df40["Description"].str.split("@",1)
            df40['entity']=df40["new"].apply(lambda x: x[-1])
            df40['source_of_trans']='Automated'
            df40['mode']='NA'
            #df40['entity_bank']='NA'
            df40.drop(["new"], axis=1, inplace=True)
            df40['df']='40'
        except:
            pass
    
        try:
            df41=sbi_df[sbi_df["Description"].str.startswith("TFR PART TERM")]
            df41['entity']='NA'
            df41['source_of_trans']='Self Initiated'
            df41['mode']='MOD'
            #df41['entity_bank']='NA'
            df41['df']='41'
        except:
            pass
    
    
    
            #appending dataframes
        t1 = concat([df1,df2,df3,df4,df5,df6,df7,df9a,df9b,df9c,df10,df11,df12,df12a,
                        df13,df14,df15,df15a,df15b,df16,df16a,df17,df18,df19,df20,
                        df21,df22,df23,df25,df27,df28,df29,df31,df32,df33,df34,df35,
                        df36a,df36b,df36c,df36d,df36,df37,df38,df39,df40,df41,df_chgs], axis=0)
        try:
            df24=sbi_df[sbi_df["Description"].str.startswith("TO TRANSFER")]
            df24g=df24[df24["Description"].str.contains("INB IMPS/P2A")]
            df24=df24[~df24["Description"].isin(df24g["Description"])]
        
            df24h=df24[df24["Description"].str.contains("INB IMPS")]
            df24=df24[~df24["Description"].isin(df24h["Description"])]
        
            df24i=df24[df24["Description"].str.contains("INB NEFT")]
            df24=df24[~df24["Description"].isin(df24i["Description"])]
        
            df24=df24[~df24["Description"].isin(t1["Description"])]
            df24a=df24[df24["Description"].str.startswith("TO TRANSFER-INB")]
            df_t=df24[df24["Description"].str.startswith("TO TRANSFERINB")]
            df24a=concat([df24a,df_t])
            del df_t
            df24=df24[~df24["Description"].isin(df24a["Description"])]
        
            df24b=df24[df24["Description"].str.contains("FOR")]
            df24=df24[~df24["Description"].isin(df24b["Description"])]
       
            df24c=df24[df24["Description"].str.contains("For")]
            df24=df24[~df24["Description"].isin(df24c["Description"])]
       
            df24d=df24[df24["Description"].str.startswith("TO TRANSFER-TRANSFERTO-")]
            df24=df24[~df24["Description"].isin(df24d["Description"])]
       
            df24e=df24[df24["Description"].str.startswith("TO TRANSFER-RTGS")]
            df24=df24[~df24["Description"].isin(df24e["Description"])]
        
            df24f=df24[df24["Description"].str.startswith("TO TRANSFER-NEFT")]
            df24=df24[~df24["Description"].isin(df24f["Description"])]
        
        
        except:
            pass
        try:
            df24["new"]=df24["Description"].str.split("-",1)
            df24['sub_mode']="TO TRANSFER"
            df24['entity']=df24["new"].apply(lambda x: x[1])
            df24['source_of_trans']='Self Initiated'
            df24['mode']='Net Banking'
            #df24['entity_bank']='NA'
            df24.drop(["new"], axis=1, inplace=True)
            df24['df']='24'
        except :
            pass
        try:
            df24a["new"]=df24a["Description"].str.split("INB")
            df24a['sub_mode']="Internet Banking"
            df24a['entity']=df24a["new"].apply(lambda x: x[1])
            df24a['source_of_trans']='Self Initiated'
            df24a['mode']='Net Banking'
            #df24a['entity_bank']='NA'
            df24a.drop(["new"], axis=1, inplace=True)
            df24a['df']='24a'
        except:
            pass
        try:
            df24b["new"]=df24b["Description"].str.split("FOR")
            df24b['sub_mode']="NA"
            df24b['entity']=df24b["new"].apply(lambda x: x[1])
            df24b['source_of_trans']='Self Initiated'
            df24b['mode']='NA'
            #df24b['entity_bank']='NA'
            df24b.drop(["new"], axis=1, inplace=True)
            df24b['df']='24b'
        except:
            pass
        try:
            df24c["new"]=df24c["Description"].str.split("For")
            df24c['sub_mode']="NA"
            df24c['entity']=df24c["new"].apply(lambda x: x[1])
            df24c['source_of_trans']='Self Initiated'
            df24c['mode']='NA'
            #df24c['entity_bank']='NA'
            df24c.drop(["new"], axis=1, inplace=True)
            df24c['df']='24c'
        except:
            pass
        try:
            df24d['sub_mode']="NA"
            df24d['entity']="NA"
            df24d['source_of_trans']='Self Initiated'
            df24d['mode']='NA'
            #df24d['entity_bank']='NA'
            df24d['df']='24d'
        except:
            pass
        try:
            df24e["new"]=df24e["Description"].str.split("-")
            df24e['sub_mode']="RTGS"
            df24e['entity']=df24e["new"].apply(lambda x: x[-1])
            df24e['source_of_trans']='Self Initiated'
            df24e['mode']='Net Banking'
            #df24e['entity_bank']='NA'
            df24e.drop(["new"], axis=1, inplace=True)
            df24e['df']='24e'
        except:
            pass
        try:
            df24f["new"]=df24f["Description"].str.split("-")
            df24f['sub_mode']="NEFT"
            df24f['entity']=df24f["new"].apply(lambda x: x[-1])
            df24f['source_of_trans']='Self Initiated'
            df24f['mode']='Net Banking'
            #df24f['entity_bank']='NA'
            df24f.drop(["new"], axis=1, inplace=True)
            df24f['df']='24f'
        except :
            pass
        try:
            df24g["new"]=df24g["Description"].str.split("/")
            df24g['sub_mode']="IMPS"
            df24g['entity']=df24g["new"].apply(lambda x: x[-1])
            df24g['source_of_trans']='Self Initiated'
            df24g['mode']='Net Banking'
            #df24g['entity_bank']='NA'
            df24g.drop(["new"], axis=1, inplace=True)
            df24g['df']='24g'
        except :
            pass
        try:
            df24h['sub_mode']="IMPS"
            df24h['entity']="NA"
            df24h['source_of_trans']='Self Initiated'
            df24h['mode']='Net Banking'
            #df24h['entity_bank']='NA'
            df24h['df']='24h'
        except :
            pass
        try:
            df24i["new"]=df24i["Description"].str.split("-")
            df24i['sub_mode']="NEFT"
            df24i['entity']=df24i["new"].apply(lambda x: x[-1])
            df24i['entity']=df24i["entity"].apply(lambda x: "NA" if x=='' else x)
            df24i['source_of_trans']='Self Initiated'
            df24i['mode']='Net Banking'
            #df24i['entity_bank']='NA'
            df24i.drop(["new"], axis=1, inplace=True)
            df24i['df']='24i'
        except :
            pass
        t1 = concat([t1,df24,df24a,df24b,df24c,df24d,df24e,df24f,df24g,df24h,df24i])
        try:
            t1.drop(["new", "mode_1", 'mode_2','new_1' ], axis=1, inplace=True)
        
        except:
            pass
        t2 = sbi_df[~sbi_df["Description"].isin(t1["Description"])]
        t2['sub_mode']='Others'
        t2['entity']='NA'
        t2['source_of_trans']='NA'
        t2['entity_bank']='NA'
        t2['mode']='NA'
    
        final = concat([t1,t2], axis=0)
        
        final.to_csv(r'D:\check.csv')
        final["Cheque Number"]=final['Ref No./Cheque\rNo.']
        final=final[['Txn Date', 'Description', 'Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number','mode','entity','source_of_trans','sub_mode']]
    
        final['Debit'] = final['Debit'].astype('str')
        final['Debit'] = final['Debit'].apply(lambda x : x.replace(',','').replace('\r',''))
        final['Debit'] = final['Debit'].replace('nan',0)
        final['Debit'] = final['Debit'].astype('float64')
     
        final['Credit'] = final['Credit'].astype('str')
        final['Credit'] = final['Credit'].apply(lambda x : x.replace(',','').replace('\r',''))
        final['Credit'] = final['Credit'].replace('nan',0)
        final['Credit'] = final['Credit'].astype('float64')
    
        final['Balance'] = final['Balance'].astype('str')
        final['Balance'] = final['Balance'].apply(lambda x : x.replace(',','').replace('\r',''))
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
    
        final['bank_name'] = 'ICICI'
    
        final['lid'] = file_name.split('_')[0]

        final.to_csv(r'D:\digitizedfiles\{}_b.csv'.format(file_name), index=False)

        end = time()

        print(end-start)
   
        return r'D:\digitizedfiles\{}_b.csv'.format(file_name)

   
        
            #exporting the master table to a csv - this is final having complete transactions table appended and essential account information
            #master_table2.to_csv("{}\\{}_{}_{}.csv".format(out_path,pdf_file,account_no, last_trans_date),index=False)

        #master_table2.to_csv(r'D:\icici_statement.csv',index=False)


#try:
#    icici_digitization(r".\input_files\net_banking\JULY 2019 OCT 2019.pdf",
#                       r".\output_files\net_banking")
#except:
#    print("\nThis statement cannot be digitised\n")
