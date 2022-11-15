import pandas as pd
import numpy as np
#import tabula
import re
from datetime import datetime as dt
import glob
import os.path



def scanned_hdfc_digitization(dataframe):
    try:
        print('shdfc')
   
    
        #col2str = {'dtype': str}
        #file_name=pdf_path.split('\\')[-1][:-4]
        #passwrd=''
    
        #try:
        #    tables = tabula.read_pdf(pdf_path, password=passwrd, area=[226,27,777,631],pages='all',columns=[68,271,356,397,475,552], pandas_options = col2str)
        #except:
        #    # passwrd=pdf_password
        #    tables = tabula.read_pdf(pdf_path, password=passwrd, area=[226,27,777,631],pages='all',columns=[68,271,356,397,475,552], pandas_options = col2str)
    
        #if len(tables)==0:
        #    print("This is an image-based statement, hence, cannot be digitized here")
        #    return
        ##print(tabula.environment_info())
        ## setting the header as first row wherever first row of table is taken as header by tabula
        #for i in range(len(tables)) :
        #    #print(tables[i])
        #    #tables[i].to_csv('D:\prudhvi\sources-a3-kit\output{}.csv'.format(i))
        #    if tables[i].empty:
        #            continue
        #    if tables[i].columns[0] != 'Date' :
        #        tables[i].loc[max(tables[i].index)+1,:] = None
        #        tables[i] = tables[i].shift(1,axis=0)
        #        tables[i].iloc[0] = tables[i].columns
        #        if len(tables[i].columns) == 7:
        #            tables[i].columns = ['Date', 'Narration', 'Chq./Ref.No.', 'Value Dt','Withdrawal Amt.', 'Deposit Amt.','Closing Balance']
        #            #print(tables[i]['Chq./Ref.No.'])
    
        ## Dropping the rows that are originally below the table but are read into the table by Tabula
        #for i in reversed(range(len(tables))) :
        #    tables[i][tables[i].columns[1]]=list(map(str,tables[i][tables[i].columns[1]]))
        #    for j in tables[i].index :
        #        if tables[i][tables[i].columns[1]][j].startswith("STATEMENT ") :
        #            tables[i] = tables[i][0:j]
        #            try:
        #                del tables[i+1]
        #            finally:
        #                break
        #        else :
        #            continue
    
    
        #for i in range(len(tables)):
        #    for j in tables[i].index:
        #        for k in range(len(tables[i].columns)) :
        #            if type(tables[i].iloc[j,k])==str and tables[i].iloc[j,k].startswith('Unnamed:') :
        #                tables[i].iloc[j,k] = np.nan
    
    
        ##removing .1 from date
        #for i in range(len(tables)):
        #    for j in tables[i].index:
        #        if type(tables[i]['Value Dt'][j])==str and tables[i]['Value Dt'][j].endswith('.1') :
        #            tables[i]['Value Dt'][j] = tables[i]['Value Dt'][j][:-2]
        #        else:
        #            continue
    
    
        ## finally appending all tables of a pdf
        #master_table = tables[0]
    
        #for i in range(len(tables)-1) :
        #    master_table = pd.concat([master_table, tables[i+1]])
            
        #master_table=master_table.reset_index(drop=True)
        #master_table=master_table.replace(np.nan,'')
        
        #for i in reversed(range(len(master_table))) :
        #    if len(master_table['Date'][i]) ==  0 :
        #        if len(master_table['Narration'][i]) > 0 :
        #            master_table['Narration'][i-1] = master_table['Narration'][i-1] + master_table['Narration'][i]
        #    else:
        #        continue
    
        #master_table=master_table.replace('',np.nan)
        #master_table.dropna(subset=['Date'],inplace=True)
    
        #del tables
        #tables = tabula.read_pdf(pdf_path, password=passwrd, area=[80.7, 27.3,190, 311], pages='1', pandas_options={'header': None}) 
        #account_name=""
        #for i in range(len(tables[0].columns)):
        #    if type(tables[0].iloc[0,i])==str:
        #        account_name += str(tables[0].iloc[0,i])+ " "
        #del tables
        #tables = tabula.read_pdf(pdf_path, password=passwrd, area=[86, 337, 193, 628], pages='1', pandas_options={'header': None}) 
        #tables[0]['a'] = tables[0].apply(lambda x: ''.join(x.dropna()), axis=1)
    
        #tables[0]=tables[0][['a']]
        #account_no = re.findall(r'\d+', tables[0]['a'][7])[0]
        #del tables
        ## we have to extract useful information from the texts - Account No, Account holder, Cust ID
        #account_no="'"+account_no+"'"
    
        ### adding three columns in the master table 
        #master_table['Account Name'] = account_name
        #master_table['Account Number'] = account_no
        #master_table['Chq./Ref.No.']=master_table['Chq./Ref.No.'].apply(lambda x: str(x))
        
        #master_table2 = pd.DataFrame(master_table)
        master_table2 = dataframe
        master_table2.rename(columns={'Date':'Txn Date','Narration':'Description', 'Chq./Ref.No.':'Cheque Number', 'Withdrawal Amt.':'Debit', 'Deposit Amt.':'Credit', 'Closing Balance':'Balance'}, inplace=True)
        master_table2['Balance'] = master_table2['Balance'].str.replace(',', '')
        s='(\-*\d+\.\d{2})'
        master_table2["Balance"]=master_table2["Balance"].apply(lambda x: re.findall(s,x)[0])
        # Converting Amount columns into string
        master_table2 = master_table2.replace(np.nan,'')
        master_table2['Credit'] = master_table2['Credit'].astype(str)
        master_table2['Debit'] = master_table2['Debit'].astype(str)
        master_table2['Balance'] = master_table2['Balance'].astype(str)
        master_table2 = master_table2.replace('',np.nan)
    
        master_table2['Txn Date'] = [dt.strftime(pd.to_datetime(x,dayfirst=True),"%d/%m/%Y") for x in master_table2['Txn Date']]
        master_table2 = master_table2[['Txn Date', 'Description', 'Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number']]
        last_trans_date = master_table2['Txn Date'].iat[-1]
    
        ## exporting the master table to a csv - this is final having complete transactions table appended and essential account information
        ## master_table2.to_csv(r"C:\Users\Shubham\Downloads\hdfc-20210302T055600Z-001\hdfc\New folder\master2222.csv")
    
    
        ### NOW PERFORMING FEW LOGICAL CHECKS TO CHECK DIGITIZATION HAS NO ISSUE
    
        #df = pd.DataFrame(master_table2)
        #column_names=['Statement_name','Wrong Credit', 'Wrong Debit', 'Remark']
        #result=pd.DataFrame(index=[1],columns=column_names)
    
        #if df['Credit'].dtype =='O':
        #    df['Credit_changed'] = (df['Credit'].str.replace(',','')).astype(float)
        #else:
        #    df['Credit_changed']= df['Credit'].astype(float)
        #if df['Debit'].dtype =='O':
        #    df['Debit_changed'] = (df['Debit'].str.replace(',','')).astype(float)
        #else:
        #    df['Debit_changed']= df['Debit'].astype(float)
        #if df['Balance'].dtype =='O':
        #    df['Balance_changed'] = (df['Balance'].str.replace(',','')).astype(float)
        #else:
        #    df['Balance_changed']= df['Balance'].astype(float)
        
        #df['Balance_changed'] = df['Balance_changed'].replace(0,np.nan)
        #df['Debit_changed'] = df['Debit_changed'].replace(0,np.nan)
        #df['Credit_changed'] = df['Credit_changed'].replace(0,np.nan)        
    
        #col_credit=df.columns.get_loc('Credit_changed')
        #col_debit=df.columns.get_loc('Debit_changed')
        #col_bal=df.columns.get_loc('Balance_changed')
        #col_desc=df.columns.get_loc('Description')
    
        #for i in range(1,len(df)):
        #    #check 1 having, both debit and credit values
        #    if  (pd.isna(df.iloc[i,col_debit]) and pd.isna(df.iloc[i,col_credit])) or (pd.notna(df.iloc[i,col_debit]) and pd.notna(df.iloc[i,col_credit])) :
        #        data=pd.DataFrame({'Statement_name':file_name,'Wrong Credit': (i+2),'Wrong Debit':(i+2), 'Remark':'Only one of Debit/Credit should be filled'},index=[0])
        #        result=pd.concat([result,data])                
    
        #    #check 2, balance check
        #    else:
        #        #debited
        #        if pd.isna(df.iloc[i,col_credit]):
        #            if df.iloc[i,col_debit]>0:
        #                if df.iloc[i-1,col_bal]<df.iloc[i,col_bal]:
        #                    data=pd.DataFrame({'Statement_name':file_name,'Wrong Credit': np.nan,'Wrong Debit':(i+2), 'Remark':'Balance should be less than previous since debit>0'},index=[0])
        #                    result=pd.concat([result,data])
        #            else:
        #                if df.iloc[i-1,col_bal]>df.iloc[i,col_bal]:
        #                    data=pd.DataFrame({'Statement_name':file_name,'Wrong Credit': np.nan,'Wrong Debit':(i+2),'Remark':'Balance should be more than previous since debit<0'},index=[0])
        #                    result=pd.concat([result,data])
                  
    
        #        #credited
        #        elif pd.isna(df.iloc[i,col_debit]):
        #            if df.iloc[i,col_credit]>0:
        #                if df.iloc[i-1,col_bal]>df.iloc[i,col_bal]:
        #                    data=pd.DataFrame([{'Statement_name':file_name,'Wrong Credit': (i+2),'Wrong Debit':np.nan,'Remark':'Balance should be more than previous since credit>0'}],index=[0])
        #                    result=pd.concat([result,data])
        #            else:
        #                if df.iloc[i-1,col_bal]<df.iloc[i,col_bal]:
        #                    data=pd.DataFrame([{'Statement_name':file_name,'Wrong Credit': (i+2),'Wrong Debit':np.nan,'Remark':'Balance should be less than previous since credit<0'}],index=[0])
        #                    result=pd.concat([result,data])    
    
        #result = result.dropna(how='all')
    
        ## will continue only if 'result' is an empty dataframe
        #if len(result)==0:
        #    pass
        #else:
        #    print("\nThere are issues found after the Logical checks.\nThe digtitized output and the issues have been exported in CSVs.\n")
        #    # master_table2.to_csv(r"C:\Users\Shubham\Downloads\hdfc-20210302T055600Z-001\hdfc\New folder\master2.csv")        
        #    # result.to_csv(r"C:\Users\Shubham\Downloads\hdfc-20210302T055600Z-001\hdfc\New folder\result.csv")
        #    return



        ## NOW THE ENTITY EXTRACTION PART

        #hdfc = pd.DataFrame(master_table2)
        hdfc = dataframe

        hdfc["Description"]=hdfc["Description"].str.lstrip()

        #Converting list to string
        def listToString(s):  
            str1 = " " 
            return (str1.join(s))

        try:
            df1=hdfc[hdfc["Description"].str.startswith("IMPS")]
            df1['new']=df1['Description'].str.split("-")
            df1["sub_mode"] = df1['new'].apply(lambda x:x[0])
            df1['source_of_trans']='Self Initiated'
            df1['entity_bank'] = df1['new'].apply(lambda x:x[3])
            df1['entity_bank'] = df1['entity_bank'].apply(lambda x: 'HDFC' if x == 'HDFC' else 'Others')
            df1['mode'] = 'Net Banking'
            df1['entity']=df1['new'].apply(lambda x:x[2])
            df1.drop(["new"], axis=1, inplace=True)
        
        except:
                pass
    
        #subsetting .IMPS    
        try:
            df2=hdfc[hdfc["Description"].str.startswith(".IMPS")]
            df2[['sub_mode','p2p', 'trans_id', 'MIR']]=df2.Description.str.split(" ", expand = True)
            df2['source_of_trans']='Automated'
            df2['entity']='NA'
            df2['mode']='Charges'
            df2['entity_bank']='NA'
            df2.drop(['trans_id', "p2p", "MIR"], axis=1, inplace=True)
        except:
            pass
    
        #subsetting UPI
    
        try:
            df3=hdfc[hdfc["Description"].str.startswith("UPI")]
            df3['new']=df3['Description'].str.split("-")
            df3['sub_mode']=df3['new'].apply(lambda x:x[0])
            df3['entity']=df3['new'].apply(lambda x:x[2])
            df3['source_of_trans']='Self Initiated'
            df3['mode']='Mobile App'
            df3['entity_bank']=df3['entity'].str[:4]
            df3.drop('new', axis=1, inplace=True)
        except:
            pass
    
        #subsetting ATW    
        try:
            df4=hdfc[hdfc["Description"].str.startswith("ATW")]
            # df4[['sub_mode','card_no', 'atm_code', 'location']]=df4.Description.str.split("-", expand = True)
            df4["sub_mode"]="Cash Withdrawal"
            df4['new']=df4['Description'].str.split("-")
            df4['source_of_trans']='Self Initiated'
            df4['mode']='Cash'
            df4['entity_bank']='NA'
            df4['entity']='NA'
            # df4.drop(['card_no', "atm_code", "location"], axis=1, inplace=True)
            df4.drop(['new'], axis=1, inplace=True)
        except:
            pass
        
    
        #subsetting 41005995TERMINAL      
        try:
            df5=hdfc[hdfc["Description"].str.contains(pat = "TERMINAL 1 CARDS SETTL.")]
            df5['new']=df5['Description'].str.split(" ")
            df5['x1']=df5['new'].apply(lambda x:x[0]+' '+x[1])
            df5['sub_mode']=df5['new'].apply(lambda x:x[2]+' '+x[3])
            df5['date']=df5['new'].apply(lambda x:x[4])
            #df5[['x1','1', 'mode', 'date']]=df5.Description.str.split(" ", expand = True)
            df5['source_of_trans']='Automated'
            df5['mode']='Card'
            df5['entity_bank']='NA'
            df5['entity']='NA'
            df5.drop(['x1', "date", "new"], axis=1, inplace=True)
        except:
            pass
    
        #subsetting ACH
        
        try:
            df6=hdfc[hdfc["Description"].str.startswith("ACH")]
            df6['new']=df6['Description'].str.split("-")
            df6['count']=df6['new'].apply(lambda x: len(x))
        except:
            pass
        
        try:
            df6a = df6[df6['count']!=1]
            df6a['sub_mode']=df6a['new'].apply(lambda x:x[0])
            df6a['entity']=df6a['new'].apply(lambda x:x[1])
            df6a['source_of_trans']='Automated'
            df6a['mode']='Loan'
            df6a['entity_bank']='NA'
            df6a.drop(['new','count'], axis=1, inplace=True)
        except:
            pass
    
        try:
            df6b = df6[df6['count']==1]
            df6b['sub_mode']=df6b['new'].apply(lambda x:x[0])
            df6b['entity']='NA'
            df6b['source_of_trans']='Automated'
            df6b['mode']='Loan'
            df6b['entity_bank']='NA'
            df6b.drop(['new','count'], axis=1, inplace=True)
        except:
            pass
        
        #subsetting AMB CHRG INCL GST
        try:
            df7=hdfc[hdfc["Description"].str.startswith("AMB")]
            df7['new']=df7['Description'].str.split(" ")
            df7['sub_mode']=df7['new'].apply(lambda x:x[0]+' '+x[1]+' '+x[2]+' '+x[3])
            df7['source_of_trans']='Automated'
            df7['mode']='Charges'
            df7['entity_bank']='NA'
            df7['entity']='NA'
            df7.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
        #subsetting Cheque return 
        
        try:
            df8=hdfc[hdfc["Description"].str.startswith("CHQ DEP RET-")]
            df8['new']=df8['Description'].str.split("-")
            df8['sub_mode']=df8['new'].apply(lambda x:x[0])
            df8['source_of_trans']='Automated'
            df8['mode']='Cheque'
            df8['entity_bank']='NA'
            df8['entity']='NA'
            df8.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
        #subsetting Cheque return 2.0
        
        try:
            df50=hdfc[hdfc["Description"].str.startswith("CHQ DEP RET")]
            df50=df50[~df50["Description"].str.startswith("CHQ DEP RET-")]
            df50['new']=df50['Description'].str.split("CHGS")
            df50['sub_mode']=df50['new'].apply(lambda x:x[0])
            df50['source_of_trans']='Automated'
            df50['mode']='Cheque'
            df50['entity_bank']='NA'
            df50['entity']='NA'
            df50.drop(['new'], axis=1, inplace=True)
        except:
            pass
        
        #subsetting Cheque paid
        try:   
            df9 =hdfc[hdfc["Description"].str.startswith("CHQ PAID")]
            df9['new']=df9['Description'].str.split("-")
            df9['sub_mode']=df9['new'].apply(lambda x:x[0])
            df9['entity']=df9['new'].apply(lambda x:x[-1])
            df9['source_of_trans']='Automated'
            df9['mode']='Cheque'
            df9['entity_bank']='NA'
            df9.drop(['new'], axis=1, inplace=True)
        except:
            pass
        
        #subsetting debit card fee        
        try:
            df10 =hdfc[hdfc["Description"].str.startswith("DEBIT CARD ANNUAL")]
            df10['sub_mode']='DEBIT CARD ANNUAL FEE'
            df10['source_of_trans']='Automated'
            df10['mode']='Charges'
            df10['entity_bank']='NA'
            df10['entity']='NA'
        except:
            pass
    
        #ATM Cash Fee
        try:
            df11 =hdfc[hdfc["Description"].str.startswith("FEE")]
            df11['sub_mode']='ATM CASH FEE'
            df11['source_of_trans']='Automated'
            df11['mode']='Charges'
            df11['entity_bank']='NA'
            df11['entity']='NA'
        except:
            pass
    
        try:
            df12 =hdfc[hdfc["Description"].str.startswith("DEPOSITORY CHARGES")]
            df12['sub_mode']='DEPOSITORY CHARGES'
            df12['source_of_trans']='Automated'
            df12['mode']='Charges'
            df12['entity_bank']='NA'
            df12['entity']='NA'
        except:
            pass
    
    
        try:
            df13 =hdfc[hdfc["Description"].str.startswith(".ACH")]
            df13['sub_mode']='ACH DEBIT RETURN CHARGES'
            df13['source_of_trans']='Automated'
            df13['mode']='Charges'
            df13['entity_bank']='NA'
            df13['entity']='NA'
        except:
            pass
            
            
        try:
            df14 =hdfc[hdfc["Description"].str.startswith(".ECS")]
            df14['sub_mode']='ECS DEBIT RETURN CHARGES'
            df14['source_of_trans']='Automated'
            df14['mode']='Charges'
            df14['entity_bank']='NA'
            df14['entity']='NA'
        
        except:
            pass
        
    
        #subsetting CHEQUE DEP
        try:
            df15 =hdfc[hdfc["Description"].str.startswith("CHQ DEP")]
            df15=df15[~df15["Description"].str.startswith("CHQ DEP RET")]
            df15=df15[~df15["Description"].str.startswith("CHQ DEP - REV")]
            df15['new']=df15.Description.str.split("-")
            df15['sub_mode']=df15['new'].apply(lambda x:x[0])
            df15['source_of_trans']='Self Initiated'
            df15['mode']='Cheque'
            df15['entity_bank']='NA'
            df15['entity']=df15['new'].apply(lambda x:x[0])
            df15.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
    
        #Credit Interest Capitalised
        try:
        
            df16 =hdfc[hdfc["Description"].str.startswith("CREDIT INTEREST CAPITALISED")]
            df16['sub_mode']='CREDIT INTEREST CAPITALISED'
            df16['source_of_trans']='Automated'
            df16['mode']='Interest'
            df16['entity_bank']='NA'
            df16['entity']='NA'
        except:
            pass
        
        #Cash Dep
        try:
            df17 =hdfc[hdfc["Description"].str.startswith("CASH DEP")]
            df17 =df17[~df17["Description"].str.startswith("CASH DEPOSIT")]
            df17['new']=df17.Description.str.split(" ")
            df17['sub_mode']=df17['new'].apply(lambda x:x[0] +" "+ x[1])
            df17['source_of_trans']='Self Initiated'
            df17['mode']='Cash'
            df17['entity_bank']='NA'
            df17['entity']=df17['new'].apply(lambda x:x[2:])
            df17['entity']=df17["entity"].str.join(" ")
            df17.drop(['new'], axis=1, inplace=True)
        except:
            pass
        
        #cASH DEPOSIT
        try:
            df17a =hdfc[hdfc["Description"].str.startswith("CASH DEPOSIT")]
            df17a['new']=df17a.Description.str.split("-")
            df17a['sub_mode']=df17a['new'].apply(lambda x:x[0])
            df17a['source_of_trans']='Self Initiated'
            df17a['mode']='Cash'
            df17a['entity_bank']='NA'
            df17a['entity']=df17a['new'].apply(lambda x:x[-1])
            df17a.drop(['new'], axis=1, inplace=True)
        except:
            pass    
    
        #I/W Cheque Return
    
        try:
            df18 =hdfc[hdfc["Description"].str.startswith("I/W")]
            df18['new']=df18['Description'].str.split("-")
            df18['source_of_trans']='Automated'
            df18['sub_mode']='Cheque Return'
            df18['mode']='Cheque Bounce'
            df18['entity_bank']='NA'
            df18['entity']='NA'
            df18.drop(['new'], axis=1, inplace=True)
        
        except:
            pass
    
        #fund Transfer
        try:
            df19 =hdfc[hdfc["Description"].str.startswith("FT")]
            df19["new"]=df19['Description'].str.split("-")
            # df19[['sub_mode', 'dr/cr', 'entity_id', 'entity']]=df19['Description'].str.split("-", expand=True)
            df19["sub_mode"]="NA"
            df19['source_of_trans']='Self Initiated'
            df19["entity"]=df19['new'].apply(lambda x:x[3])
            df19['mode']='Fund Transfer'
            df19['entity_bank']='NA'
            df19.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
    
        #NEFT
        try:
            df20 =hdfc[hdfc["Description"].str.startswith("NEFT")]
            df20 =df20[~df20["Description"].str.startswith("NEFT CHGS")]
            df20['new']=df20["Description"].str.split("-")
            df20['sub_mode']=df20['new'].apply(lambda x:x[0])
            df20['entity']=df20['new'].apply(lambda x:x[2])
            df20['ifsc']=df20['new'].apply(lambda x:x[1]).str[:4]
            df20['source_of_trans']='Self Initiated'
            df20['mode']='Net Banking'
            df20['entity_bank'] = df20['ifsc'].apply(lambda x: 'HDFC' if x == 'HDFC' else 'Others')
            df20.drop(['new'], axis=1, inplace=True)
            df20.drop(['ifsc'], axis=1, inplace=True)
        except:
            pass
    
        #NEFT CHGS
        try:
            df20a =hdfc[hdfc["Description"].str.startswith("NEFT CHGS")]
            df20a['new']=df20a["Description"].str.split(" ")
            df20a['sub_mode']=df20a['new'].apply(lambda x:x[0:2]).str.join(" ")
            df20a['source_of_trans']='Automated'
            df20a['mode']='Charges'
            df20a['entity_bank']='NA'
            df20a['entity']='NA'
            df20a.drop(['new'], axis=1, inplace=True)
        except:
            pass
        
    
        #NWD (HDFC)
        try:
            df21 =hdfc[hdfc["Description"].str.startswith("NWD")]
            df21['sub_mode']='NWD (HDFC)'
            df21['source_of_trans']='Self Initiated'
            df21['mode']='Cash'
            df21['entity_bank']='NA'
            df21['entity']='NA'
        except:
            pass
    
    
        #EAW
        
        try:
            df22 =hdfc[hdfc["Description"].str.startswith("EAW")]
            df22['sub_mode']='EAW'
            df22['source_of_trans']='Self Initiated'
            df22['mode']='Cash'
            df22['entity_bank']='NA'
            df22['entity']='NA'
        except:
            pass
    
    
        #ECS
        try:
            df23 =hdfc[hdfc["Description"].str.startswith("ECS")]
            df23['new']=df23.Description.str.split("-")
            df23['sub_mode']='ECS'
            df23['source_of_trans']='Automated'
            df23['mode']='Loan'
            df23['entity_bank']='NA'
            df23['entity']=df23['new'].apply(lambda x:x[1])
            df23.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
        #EMI
        try:
            df24 =hdfc[hdfc["Description"].str.startswith("EMI")]
            df24['new']=df24.Description.str.split(" ")
            df24['sub_mode']='EMI'
            df24['source_of_trans']='Automated'
            df24['mode']='Loan'
            df24['entity_bank']='NA'
            df24['entity']="Loan A/C"+ " - " +df24['new'].apply(lambda x:x[1])
            df24.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
        #CRV POS
        try:
            df25 =hdfc[hdfc["Description"].str.startswith("CRV POS")]
            df25['sub_mode']='CRV POS'
            df25['source_of_trans']='Automated'
            df25['mode']='Refund'
            df25['entity_bank']='NA'
            df25['entity']='NA'
        except:
            pass
    
    
        #POS
        try:
            df26 =hdfc[hdfc["Description"].str.startswith("POS")]
            df26 =df26[~df26["Description"].str.startswith("POS REF")]
            df26 =df26[~df26["Description"].str.endswith("POS DEBIT")]
            df26 =df26[~df26["Description"].str.endswith("POSDEBIT")]
            df26['new']=df26['Description'].str.split(" ")
            df26['sub_mode']=df26['new'].apply(lambda x:x[0])
            df26['source_of_trans']='Self Initiated'
            df26['mode']='Card'
            df26['entity_bank']='NA'
            df26['entity']=df26['new'].apply(lambda x:x[2:])
            df26['entity']=df26["entity"].str.join(" ")
            df26.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
    
        try:
            df26a =hdfc[hdfc["Description"].str.endswith("POSDEBIT")]
            df26a['new']=df26a['Description'].str.split(" ")
            df26a['sub_mode']=df26a['new'].apply(lambda x:x[0])
            df26a['source_of_trans']='Self Initiated'
            df26a['mode']='Card'
            df26a['entity_bank']='NA'
            df26a['entity']=df26a['new'].apply(lambda x:x[2:-1])
            df26a['entity']=df26a["entity"].str.join(" ")
            df26a.drop(['new'], axis=1, inplace=True) 
        except:
            pass
    
    
        #POS REF
        try:
            df27 =hdfc[hdfc["Description"].str.startswith("POS REF")]
            df27['new']=df27['Description'].str.split(" ")
            df27['sub_mode']=df27['new'].apply(lambda x:x[0]+' '+x[1])
            df27['entity']=df27['new'].apply(lambda x:x[3])
            df27['source_of_trans']='Self Initiated'
            df27['mode']='Card'
            df27['entity_bank']='NA'
            df27.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
        #Ends with POS DEBIT
        try:
            df45 =hdfc[hdfc["Description"].str.endswith("POS DEBIT")]
            df45['new']=df45['Description'].str.split(" ")
            df45['sub_mode']=df45['new'].apply(lambda x:x[0])
            df45['source_of_trans']='Self Initiated'
            df45['mode']='Card'
            df45['entity_bank']='NA'
            df45['entity']=df45['new'].apply(lambda x:x[2:-2])
            df45['entity']=df45["entity"].str.join(" ")
            df45.drop(['new'], axis=1, inplace=True)
        except:
            pass    
    
            #RTGS
    
        #RTGS
        try:
            df28 =hdfc[hdfc["Description"].str.startswith("RTGS")]
            df28 =df28[~df28["Description"].str.startswith("RTGS CHGS")]
            df28['new']=df28['Description'].str.split("-")
            df28['ifsc']=df28['new'].apply(lambda x:x[1][:4])
            df28['entity_bank'] = df28['ifsc'].apply(lambda x: 'HDFC' if x == 'HDFC' else 'Others')
            df28['sub_mode']="RTGS"
            df28['entity']=df28['new'].apply(lambda x:x[2])
            df28['source_of_trans']='Self Initiated'
            df28['mode']='Bank'
            df28.drop(['new'], axis=1, inplace=True)
            df28.drop(["ifsc"],axis=1,inplace=True)
        except:
            pass
    
        #RTGS Charges
        try:
            df28a =hdfc[hdfc["Description"].str.startswith("RTGS CHGS")]
            df28a['sub_mode']="RTGS Charges"
            df28a["entity_bank"]="NA"
            df28a['entity']="NA"
            df28a['source_of_trans']='Automated'
            df28a["entity_bank"]="NA"
            df28a['mode']='Charges'
        except:
            pass
        
        #Service Charge
        try:
            df29 =hdfc[hdfc["Description"].str.startswith("SERVICE CHARGES")]
            df29['sub_mode']='SERVICE Charges'
            df29['source_of_trans']='Automated'
            df29['mode']='Charges'
            df29['entity_bank']='NA'
            df29['entity']='NA'
        except:
            pass
    
        #Settlement Charge
        try:
            df30 =hdfc[hdfc["Description"].str.startswith("SETTLEMENT CHARGE")]
            df30['sub_mode']='SETTLEMENT CHARGE'
            df30['source_of_trans']='Automated'
            df30['mode']='Charges'
            df30['entity_bank']='NA'
            df30['entity']='NA'
        except:
            pass
        
        #MC CHARGES
        try:
            df31 =hdfc[hdfc["Description"].str.startswith("MC CHARGES")]
            df31['sub_mode']='MC CHARGES'
            df31['source_of_trans']='Automated'
            df31['mode']='Charges'
            df31['entity_bank']='NA'
            df31['entity']='NA'
        except:
            pass
    
        #INST-ALERT CHARGES
        try:
            df32 =hdfc[hdfc["Description"].str.startswith("INST-ALERT")]
            df32['sub_mode']='INST ALERT CHG CHARGES'
            df32['source_of_trans']='Automated'
            df32['mode']='Charges'
            df32['entity_bank']='NA'
            df32['entity']='NA'
        except:
            pass
    
    
        try:
            df33 =hdfc[hdfc["Description"].str.startswith("IB")]
            df33['new']=df33['Description'].str.split("-")
            df33['sub_mode']=df33['new'].apply(lambda x:x[0])
            df33['source_of_trans']='Self Initiated'
            df33['mode']='NA'
            df33['entity_bank']='NA'
            df33['entity']='NA'
            df33.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
    
        #TATASKY DTH
        
        try:
            df34 =hdfc[hdfc["Description"].str.startswith("TATASKY")]
            df34['sub_mode']='TATASKY'
            df34['source_of_trans']='NA'
            df34['mode']='NA'
            df34['entity_bank']='NA'
            df34['entity']='NA'
        except:
            pass
    
        #BAJAJ FINEMI
        try:
            df35 =hdfc[hdfc["Description"].str.startswith("BAJAJ FINEMI")]
            df35['sub_mode']='BAJAJ FINEMI'
            df35['source_of_trans']='Automated'
            df35['mode']='EMI'
            df35['entity_bank']='NA'
            df35['entity']='BAJAJ FINANCE'
        except:
            pass
    
        #CASH WITHDRAWAL
        try:
            df36 =hdfc[hdfc["Description"].str.startswith("CSH WD - CHQ PAID")]
            df36['sub_mode']='CSH WD - CHQ PAID'
            df36['source_of_trans']='Self Initiated'
            df36['mode']='Cash'
            df36['entity_bank']='NA'
            df36['entity']='NA'
        except:
            pass
    
        ##HD
        try:
            df37 =hdfc[hdfc["Description"].str.startswith("HD0")]
            df37['new']=df37['Description'].str.split("-")
            df37['sub_mode']=df37['new'].apply(lambda x:x[0])
            df37['entity']=df37['new'].apply(lambda x:x[1])
            df37['source_of_trans']='Self Initiated'
            df37['mode']='NA'
            df37['entity_bank']='NA'
            df37.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
        #INTER-BRN CHARGES
        try:
            df38 =hdfc[hdfc["Description"].str.startswith("INTER-BRN")]
            df38['sub_mode']='INTER-BRN CASH CHARGES'
            df38['source_of_trans']='Automated'
            df38['mode']='Charges'
            df38['entity_bank']='NA'
            df38['entity']='INTER-BRN CASH CHG'
        except:
            pass
    
        ##Manager's Cheque        
        try:
            df39 =hdfc[hdfc["Description"].str.startswith("MC ISSUED")]
            df39['new']=df39['Description'].str.split("-")
            df39['sub_mode']=df39['new'].apply(lambda x:x[0])
            df39['entity']=df39['new'].apply(lambda x:x[4])
            df39['source_of_trans']='Self Initiated'
            df39['mode']='cheque'
            df39['entity_bank']='NA'
            df39.drop(['new'], axis=1, inplace=True)
        except:
            pass    
    
        #TPT Third Party Transfer
        try:
            df40 =hdfc[hdfc["Description"].str.contains("TPT")]
            df40['new']=df40['Description'].str.split("-")
            df40['sub_mode']='TPT'
            df40['source_of_trans']='Self Initiated'
            df40['mode']='NA'
            df40['entity_bank']='NA'
            df40['entity']=df40['new'].apply(lambda x:x[-1])
            df40.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
        #REV
        try:
            df41 =hdfc[hdfc["Description"].str.contains("REV")]
            df41 =df41[~df41["Description"].str.startswith("IMPS")]
            df41['sub_mode']='REV'
            df41['source_of_trans']='Automated'
            df41['mode']='Reversal'
            df41['entity_bank']='NA'
            df41['entity']='NA'
        except:
            pass
    
        #NET PI to HSL
        
        try:
            df42 =hdfc[hdfc["Description"].str.startswith("NET")]
            df42['new']=df42['Description'].str.split(" ")
            df42['sub_mode']=df42['new'].apply(lambda x:x[0]+" "+ x[1]+" "+x[2]+" "+ x[3]+" "+x[4])
            df42['source_of_trans']='Automated'
            df42['mode']='Trading'
            df42['entity_bank']='NA'
            df42['entity']= df42['new'].apply(lambda x:x[0]+" "+ x[1]+" "+x[2]+" "+ x[3]+" "+x[4])
            df42.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
    
        #SALARY
        try:
            df43 =hdfc[hdfc["Description"].str.startswith("SAL")]
            df43['new']=df43['Description'].str.split(" ")
            df43['sub_mode']=df43['new'].apply(lambda x:x[0])
            df43['source_of_trans']='Automated'
            df43['mode']='Salary'
            df43['entity_bank']='NA'
            df43['entity']='NA'
            df43.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
        try:
            df44 =hdfc[hdfc["Description"].str.slice(1,4,1)=='HDF']
            df44['new']=df44['Description'].str.split("/")
            df44['sub_mode']=df44['new'].apply(lambda x:x[0]).str[:4]
            df44['source_of_trans']='Self Initiated'
            df44['mode']='NA'
            df44['entity_bank']='NA'
            df44['entity']=df44['new'].apply(lambda x:x[1])
            df44.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
        #df45 exists
    
        #CC
        try:
            df46 =hdfc[hdfc["Description"].str.startswith("CC")]
            df46['new']=df46['Description'].str.split(" ")
            df46['sub_mode']=df46['new'].apply(lambda x:x[0])
            df46['source_of_trans']='Automated'
            df46['mode']='Card'
            df46['entity_bank']='NA'
            df46['entity']=df46['new'].apply(lambda x:x[-1])
            df46.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
        #MICRO ATM CASH DEP
        try:
            df47 =hdfc[hdfc["Description"].str.startswith("MICRO ATM CASH")]
            df47['new']=df47['Description'].str.split("-")
            df47['sub_mode']=df47['new'].apply(lambda x:x[0])
            df47['source_of_trans']='Self Initiated'
            df47['mode']='Cash'
            df47['entity_bank']='NA'
            df47['entity']=df47['new'].apply(lambda x:x[-1])
            df47.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
        #MICRO ATM CASH DEP
        try:
            df48 =hdfc[hdfc["Description"].str.startswith("PAYZAPP")]
            df48['new']=df48['Description'].str.split("-")
            df48['sub_mode']=df48['new'].apply(lambda x:x[0])
            df48['source_of_trans']='Self Initiated'
            df48['mode']='Mobile Apps'
            df48['entity_bank']='NA'
            df48['entity']=df48['new'].apply(lambda x:x[2])
            df48.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
            #LOAN MANUAL HOLD CHARGE
        try:
            df49 =hdfc[hdfc["Description"].str.contains("LOAN MANUAL HOLD")]
            df49['new']=df49['Description'].str.split(" ")
            df49['sub_mode']=df49['new'].apply(lambda x:x[1:])
            df49['source_of_trans']='Automated'
            df49['mode']='Charges'
            df49['entity_bank']='NA'
            df49['entity']="Loan A/C"+ " - " +df49['new'].apply(lambda x:x[0])
            df49['sub_mode'] = df49["sub_mode"].str.join(" ").str.extract('(.*)E')+"E" 
            df49.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
        #SI HGA
        try:
            df51 =hdfc[hdfc["Description"].str.contains("SI HGA")]
            df51['new']=df51['Description'].str.split(" ")
            df51['sub_mode']='NA'
            df51['source_of_trans']='Self Initiated'
            df51['mode']='Card'
            df51['entity_bank']='NA'
            df51['entity']=df51['new'].apply(lambda x:x[2])
            df51.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
        #HGAIP
        try:
            df52 =hdfc[hdfc["Description"].str.startswith("HGA")]
            df52['new']=df52['Description'].str.split("-")
            df52['sub_mode']='NA'
            df52['source_of_trans']='Automated'
            df52['mode']='NA'
            df52['entity_bank']='NA'
            df52['entity']=df52['new'].apply(lambda x:x[1])
            df52.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
        #LOw usage charges
        try:
            df53 =hdfc[hdfc["Description"].str.startswith("LOW USAGE CHARGES")]
            df53['new']=df53['Description'].str.split("-")
            df53['sub_mode']='NA'
            df53['source_of_trans']='Automated'
            df53['mode']='Charges'
            df53['entity_bank']='NA'
            df53['entity']="NA"
            df53.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
        
        t1 = pd.concat([df1,df2,df3,df4,df6a,df6b,df7,df8,df9,df10,df11,df12,df13,df14,df15,df16,df17,df17a,df18,df19,df20,df20a,df21,df22,df23,df24,df25,df26,df26a,df27,df28,df28a,df29,df30,df31,df32,df33,df34,df35,df36,df37,df38,df39,df40,df41,df42,df43,df44,df45,df46,df47,df48,df50,df49,df51,df52,df53], axis=0) #axis =0 for vertically appending
   
        t2 = hdfc[~hdfc["Description"].isin(t1["Description"])]
        t2['mode']='Others'
        t2['entity']='NA'
        t2['source_of_trans']='NA'
        t2['entity_bank']='NA'
        t2['sub_mode']='NA'
    
        final = pd.concat([t1,t2], axis=0)
    
        try:
            final.drop(['new'], axis=1, inplace=True)
        except:
            pass
    
        final = final.sort_values(by= ["Txn Date"])
        final = final.sort_index()
        final.rename(columns={'sub-mode':'sub_mode'}, inplace=True)    
        final = final[['Txn Date', 'Description', 'Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number','mode','entity','source_of_trans','entity_bank','sub_mode']]
        final['entity'].fillna('Other', inplace=True)
        final['entity'].replace('NA', 'Other', inplace=True)
        final['entity'].replace('', 'Other', inplace=True)

    
        final['Debit'] = final['Debit'].astype('str')
        final['Debit'] = final['Debit'].apply(lambda x : x.replace(',',''))
        final['Debit'] = final['Debit'].replace('nan',0)
        final['Debit'] = final['Debit'].astype('float64')
        final['Debit'] = final['Debit'].apply(lambda x : round(x,2))

     
        final['Credit'] = final['Credit'].astype('str')
        final['Credit'] = final['Credit'].apply(lambda x : x.replace(',',''))
        final['Credit'] = final['Credit'].replace('nan',0)
        final['Credit'] = final['Credit'].astype('float64')
        final['Credit'] = final['Credit'].apply(lambda x : round(x,2))
    
    
        final['Balance'] = final['Balance'].astype('str')
        final['Balance'] = final['Balance'].apply(lambda x : x.replace(',',''))
        final['Balance'] = final['Balance'].astype('float64')
        final['Balance'] = final['Balance'].apply(lambda x : round(x,2))
        #return final
        final.reset_index(drop=True,inplace=True)
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
        #exporting the file
        #final['image_name'] = os.path.basename(pdf_path)
   


        return final

    except Exception as e:
        print(e)

