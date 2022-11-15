import pandas as pd
import numpy as np
import tabula
from datetime import datetime as dt


def union_digitization(pdf_path,pdf_password):

    col2str = {'dtype': str}
    file_name=pdf_path.split('\\')[-1][:-4]

    passcode=''
    try :
        tables = tabula.read_pdf(pdf_path,password=passcode, pages='1', guess=True, pandas_options = col2str)
    except :
        passcode=pdf_password
        tables = tabula.read_pdf(pdf_path,password=passcode, pages='1', guess=True, pandas_options = col2str)
    
    # handling scanned statements
    if len(tables)==0:
        print("This is an image-based statement, hence, cannot be digitized here")
        #return
    
    structure = ''
    if tables[0].columns[0] == 'Tran Id':
        structure = 'netbanking'
    elif tables[0].columns[0] == 'Date':
        structure = 'new'
    del tables
    
    
    ### DIGITIZING 'new' structure 
    if structure == 'new' :
    
        tables = tabula.read_pdf(pdf_path, pages='all', lattice=True, pandas_options={'header':None,'dtype': str})
        info = tabula.read_pdf(pdf_path, pages='1',area=[54,12,310,745], pandas_options={'header':None,'dtype': str})
        
        
        # appending all the dataframes
        master_table = pd.DataFrame()
        
        for i in range(len(tables)):
            master_table = pd.concat([master_table, tables[i]])
        
        master_table.reset_index(drop=True,inplace=True)
        
        # now setting the first row as header of the master_table
        master_table.columns = master_table.iloc[0]
        master_table = master_table[1:]
        
        master_table['Remarks'] = master_table['Remarks'].str.replace('\r','')
        
        # renaming the columns
        master_table.rename(columns= {'Date':'Txn Date','Remarks':'Description','Withdrawals':'Debit','Deposits':'Credit'}, inplace=True)
        
        
        ## Now extracting Name and Account no.
        
        acc_name = info[0][0][info[0][0].first_valid_index()]
        
        for i in range(len(info[0])):
            for j in range(len(info[0].columns)):
                if type(info[0].iloc[i,j])==str and info[0].iloc[i,j].find('Account No')!=-1 :
                    account_no = "'" + str(info[0].iloc[i,j+1]).strip() + "'"
        
        
        # creating a final dataframe
        master_table2 = pd.DataFrame(master_table)
        
        ## adding columns in the master table
        master_table2['Account Name'] = acc_name
        master_table2['Account Number'] = account_no
        
        #master_table2 = master_table2[['Txn Date', 'Description', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number']]
        master_table2['Txn Date'] = [dt.strftime(pd.to_datetime(x,dayfirst=True),"%d-%m-%Y") for x in master_table2['Txn Date']]
        last_trans_date = master_table2['Txn Date'].iat[-1]
    
    
    ### DIGITIZING 'netbanking' structure 
    elif structure == 'netbanking' :
    
        tables = tabula.read_pdf(pdf_path,password=passcode, pages='all', pandas_options = col2str)
        other_details_list =  tabula.read_pdf(pdf_path, pages=1, area=[0,0,420,576],columns=[288], pandas_options = col2str)
            
        other_details = other_details_list[0]
        
        no_of_columns = len(other_details.columns)
        
        column_names = []
        for i in range(1,no_of_columns+1):
            temp = 'column' + str(i)
            column_names.append(temp)
            
        other_details.columns = column_names  
        
        #fetching account name
        for j in column_names:
            for i in range(len(other_details)):
                ele = str(other_details.iloc[i][j])
                if ele.lower().startswith("name"):
                    name = ele.split(":")[1].lstrip()
        
        #fetching account number
        for j in column_names:
            for i in range(len(other_details)):
                ele = str(other_details.iloc[i][j])
                if ele.lower().startswith("account number"):
                    account_no = "'{}'".format(ele.split(":")[1].lstrip())
        
        
        #For concatinating the remarks columns which was previoulsy distributed in different rows
        for i in range(len(tables)):
            if tables[i].columns[0] == 'Tr Id' :
                tables[i].rename(columns={'Tr Id':'Tran Id'}, inplace=True)
            tables[i]['Tran Id']=list(map(str,tables[i]['Tran Id']))
            
        
        for i in range(len(tables)):
            for j in range(len(tables[i])-1):
                if tables[i]['Tran Id'][j].find('nan')==-1:
                    tables[i]=tables[i].replace(np.nan, r'')
                    tables[i]['Remarks']=list(map(str,tables[i]['Remarks']))
                    tables[i]['Remarks'][j]=tables[i]['Remarks'][j]+tables[i]['Remarks'][j+1]
                    
        for i in range(len(tables)):
            tables[i]=tables[i].replace(r'',np.nan)
            tables[i]=tables[i].replace('nan',np.nan)
        
        
        
        #Removing all the rows with nan values in the tran ID column
        for i in range(len(tables)):
            if tables[i].columns[0]=='Tran Id':
                tables[i].dropna(subset=['Tran Id'],inplace=True)
            else:
                continue
            
        #Splitting columns and creating new columns and dividing the debit and credir valu
            
        for i in range(len(tables)):
            if len(tables[i].columns)==5:
                tables[i][['Amount','CreditOrDebit']] = tables[i]['Amount (Rs.)'].str.split(' ',1,expand=True)
                tables[i].drop(['Amount (Rs.)'],axis=1,inplace=True)
                tables[i]['Debit'] = tables[i].loc[tables[i]['CreditOrDebit']=='(Dr)', 'Amount']
                tables[i]['Credit'] = tables[i].loc[tables[i]['CreditOrDebit']=='(Cr)', 'Amount']
                tables[i].drop(['Amount','CreditOrDebit'],axis=1,inplace=True)
            else:
                continue
            
            
        #Combining three columns in the last table as the values in these coulmns were all jumbled up
        for i in range(len(tables)):
            if len(tables[i].columns)!=6:
                tables[i]['Unnamed: 1']=list(map(str,tables[i]['Unnamed: 1'])) #coverting float into string
                tables[i]['y']=tables[i][['Balance (Rs.)','Unnamed: 1']].apply(lambda x:''.join(x),axis=1)
                tables[i]['y']=tables[i][['Amount (Rs.)','y']].apply(lambda x:' '.join(x),axis=1)
                
            else:
                continue
                
        #Splitting the columns in the last table accordingly 
        for i in range(len(tables)):
            if len(tables[i].columns)!=6:
                tables[i][['Amount','CreditOrDebit1']] = tables[i]['y'].str.split(' ',1,expand=True)
                tables[i].drop(['y'],axis=1,inplace=True)
                tables[i].drop(['Balance (Rs.)','Unnamed: 1','Amount (Rs.)'],axis=1,inplace=True)
            else:
                continue
            
            
        #Setting the values of credit and debit in the corresponding columns(which are created) and drop the other useless columns
        for i in range(len(tables)):
            if len(tables[i].columns)!=6:
                tables[i][['CreditOrDebit','Balance (Rs.)']] = tables[i]['CreditOrDebit1'].str.split(')',1,expand=True)
                tables[i].drop(['CreditOrDebit1'],axis=1,inplace=True)
                tables[i]['Debit'] = tables[i].loc[tables[i]['CreditOrDebit']=='(Dr', 'Amount']
                tables[i]['Credit'] = tables[i].loc[tables[i]['CreditOrDebit']=='(Cr', 'Amount']
                tables[i].drop(['Amount','CreditOrDebit'],axis=1,inplace=True)
            else:
                continue
            
        #Removing nan which was attatched with some Balance values in the Balance column
        for i in range(len(tables)):
            if len(tables[i].columns)!=6:
                for j in tables[i].index:
                    if tables[i]['Balance (Rs.)'][j].find('nan')!=-1:
                       tables[i]['Balance (Rs.)'][j] = tables[i]['Balance (Rs.)'][j][:-3]  
                    else:
                         continue
        
        #Dropping useless columns                    
        for i in range(len(tables)):
            if len(tables[i].columns)!=6:
                tables[i]['Balance (Rs.)']=tables[i]['Balance (Rs.)'].astype(float)#Changing Balance column from string to float type in the last table
                tables[i].drop(['Unnamed: 0','Unnamed: 2'],axis=1,inplace=True)
            else:
                continue
                    
        # appending all tables of a pdf
        master_table = tables[0]
            
        for i in range(len(tables)-1):
            master_table = pd.concat([master_table, tables[i+1]])
        
        ## adding twocolumns in the master table 
        master_table['Account Name'] = name
        master_table['Account Number'] = account_no
        # bring the format of HDFC like the format of SBI (after digitized)
        # so that we have a common variables creation code
        master_table.rename(columns={'Tran Date':'Txn Date','Balance (Rs.)':'Balance','Remarks':'Description'}, inplace=True)
        master_table2 = master_table.iloc[::-1]
        master_table2.reset_index(drop=True,inplace=True)
        master_table2 = master_table2[['Txn Date', 'Description', 'Instr. ID','Debit', 'Credit', 'Balance', 'Account Name','Account Number']]
        master_table2['Txn Date'] = [dt.strftime(pd.to_datetime(x,dayfirst=True),"%d-%m-%Y") for x in master_table2['Txn Date']]
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

    col_credit=df.columns.get_loc('Credit_changed')
    col_debit=df.columns.get_loc('Debit_changed')
    col_bal=df.columns.get_loc('Balance_changed')
    #col_desc=df.columns.get_loc('Description')
    
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

    ## NOW PERFORMING ENTITY EXTRACTION
    ubi_df=df
    ubi_df["Description"]=ubi_df["Description"].str.lstrip()
    
    #subsetting UPI transactions
    try:
        df1=ubi_df[ubi_df["Description"].str.startswith("UPIAB")]
        df1[['UPI','no','cr','entity','entity_bank','no2']]=df1['Description'].str.split('/',5,expand=True)
        df1['sub_mode']='UPI'
        df1['mode']='Mobile App'
        df1['source_of_trans']='Self Initiated'
        df1['df']='df1'
        df1.drop(['UPI','no','no2','cr'],axis=1,inplace=True)
        df1.drop(["df"], axis=1, inplace=True)
    except:
        pass
    try:
        df2=ubi_df[ubi_df["Description"].str.startswith("UPIAR")]
        df4=df2[df2['Description'].str.contains("/REV/")]
        df2=df2[~df2['Description'].isin(df4['Description'])]
        df2[['UPI','no','dr','entity','entity_bank','no2']]=df2['Description'].str.split('/',5,expand=True)
        df2['sub_mode']='UPI'
        df2['mode']='Mobile App'
        df2['source_of_trans']='Self Initiated'
        df2['df']='df2'
        df2['entity']=[np.nan if x==' ' else x for x in df2['entity']]
        df2.drop(['UPI','no','no2','dr'],axis=1,inplace=True)
        
        df4['entity']='NA'
        df4['entity_bank']='NA'
        df4['mode']='Reversal'
        df4['sub_mode']='NA'
        df4['source_of_trans']='Automated'
        df4['df']='df4'
        df2.drop(["df"], axis=1, inplace=True)
        df4.drop(["df"], axis=1, inplace=True)
    except:
        pass
    try:
        df3=ubi_df[ubi_df["Description"].str.startswith("UPI ")]
        df3[['UPI','entity','dt']]=df3['Description'].str.split(expand=True)
        df3['entity_bank']='NA'
        df3['mode']='Mobile App'
        df3['sub_mode']='UPI'
        df3['source_of_trans']='Self Initiated'
        df3['df']='df3'
        df3.drop(['UPI','dt'],axis=1,inplace=True)
        df3.drop(["df"], axis=1, inplace=True)
    except:
        pass
    
    
    #subsetting NEFT transactions
    try:
        df5=ubi_df[ubi_df["Description"].str.contains(pat="NEFT")]
        df6=df5[df5["Description"].str.contains(pat="NEFTO")]
        df5=df5[~df5['Description'].isin(df6['Description'])]
        df5[["mode","entity"]] = df5.Description.str.split(":", expand=True)
        df5['entity_bank'] ="NA"
        df5['sub_mode']='NEFT'
        df5['source_of_trans']="Self Initiated"
        df5['mode']="Net Banking"
        df5['df']='df5'
        
        df6[["mode","entity"]] = df6.Description.str.split("-", expand=True)
        df6['entity_bank'] ="NA"
        df6['sub_mode']='NEFT'
        df6['source_of_trans']="Self Initiated"
        df6['mode']="Net Banking"
        df6['df']='df6'
        df5.drop(["df"], axis=1, inplace=True)
        df6.drop(["df"], axis=1, inplace=True)
    except:
        pass
    
    
    #subsetting IMPSAB transactions
    try:
        df7=ubi_df[ubi_df["Description"].str.startswith(pat="IMPSAB")]
        df7[['IMPS','no',"entity_bank",'entity']] = df7.Description.str.split("/",3, expand=True)
        df7['entity']=df7['entity'].apply(lambda x: "'"+str(x)+"'")
        df7['entity_bank'] =df7['entity_bank'].apply(lambda x:x[:4])
        df7['source_of_trans']="Self Initiated"
        df7['mode']="Net Banking"
        df7['sub_mode']="IMPSAB"
        df7.drop(['IMPS','no'],axis=1,inplace=True)
        df7['df']='df7'
        df7.drop(["df"], axis=1, inplace=True)
    except:
        pass
    #subsetting IMPSAR transactions
    try:
        df8=ubi_df[ubi_df["Description"].str.startswith(pat="IMPSAR")]
        df8[['IMPS','no',"entity_bank",'entity']] = df8.Description.str.split("/",3, expand=True)
        df8['entity']=df8['entity'].apply(lambda x: "'"+str(x)+"'")
        df8['entity_bank'] =df8['entity_bank'].apply(lambda x:x[:4])
        df8['source_of_trans']="Self Initiated"
        df8['mode']="Net Banking"
        df8['sub_mode']="IMPSAR"
        df8.drop(['IMPS','no'],axis=1,inplace=True)
        df8['df']='df8'
        df8.drop(["df"], axis=1, inplace=True)
    except:
        pass
    #subsetting Salary transactions
    try:
        df9=ubi_df[ubi_df["Description"].str.startswith(pat="SALARY")]
        df9['mode']='NA'
        df9['entity']='NA'
        df9['entity_bank']='NA'
        df9['source_of_trans']="Automated"
        df9['sub_mode']="Salary"
        df9['df']='df9'
        df9.drop(["df"], axis=1, inplace=True)
    except:
        pass
    
    #subsetting Cash transactions
    try:
        df10=ubi_df[ubi_df["Description"].str.startswith(pat="BY CASH")]
        df10['mode']='Cash'
        df10['entity']='NA'
        df10['entity_bank']='NA'
        df10['source_of_trans']="Self Initiated"
        df10['sub_mode']="Cash Deposit"
        df10['df']='df10'
        df10.drop(["df"], axis=1, inplace=True)
    except:
        pass
    
    #subsetting Charges transactions
    try:
        df11=ubi_df[ubi_df["Description"].str.contains(pat="charges",case=False)]
        df_t1=ubi_df[ubi_df["Description"].str.startswith(pat="ANN.")]
        df_t2=ubi_df[ubi_df["Description"].str.startswith(pat="chrge")]
        df11=pd.concat([df11,df_t1,df_t2])
        del df_t1
        del df_t2
        df11['mode']='NA'
        df11['entity']='NA'
        df11['entity_bank']='NA'
        df11['source_of_trans']="Automated"
        df11['sub_mode']="Charges"
        df11['df']='df11'
        df11.drop(["df"], axis=1, inplace=True)
    except:
        pass
    
    #subsetting Interest transactions
    try:
        df12=ubi_df[ubi_df["Description"].str.contains(pat="Int.Pd")]
        df12['mode']='NA'
        df12['entity']='NA'
        df12['entity_bank']='NA'
        df12['source_of_trans']="Automated"
        df12['sub_mode']="Interest"
        df12['df']='df12'
        df12.drop(["df"], axis=1, inplace=True)
    except:
        pass
    
    #subsetting eTxn transactions
    try:
        df13=ubi_df[ubi_df["Description"].str.startswith(pat="eTXN")]
        df13['mode']='Net Banking'
        df13[['etxn','entity']]=df13['Description'].str.split("To:",expand=True)
        df13['entity']=df13['entity'].str.split("/").apply(lambda x:"'"+str(x[0])+"'")
        df13['entity_bank']='NA'
        df13['source_of_trans']="Self Initiated"
        df13['sub_mode']="e-Transaction"
        df13.drop(['etxn'],axis=1,inplace=True)
        df13['df']='df13'
        df13.drop(["df"], axis=1, inplace=True)
    except:
        pass
    
    #subsetting eTxn transactions
    try:
        df14=ubi_df[ubi_df["Description"].str.startswith(pat="NACH/")]
        df14['mode']='NA'
        df14[['nach','no','entity']]=df14['Description'].str.split("/",2,expand=True)
        df14['entity_bank']='NA'
        df14['source_of_trans']="Automated"
        df14['sub_mode']="Mutual Funds/SIP"
        df14.drop(['nach','no'],axis=1,inplace=True)
        df14['df']='df14'
        df14.drop(["df"], axis=1, inplace=True)
    except:
        pass
    
    #UBIN
    try:
        df15=ubi_df[ubi_df["Description"].str.startswith("UBIN")]
        df15['new']=df15['Description'].str.split("/")
        df15['entity']=df15["new"].apply(lambda x: x[1])
        df15['mode']='NA'
        df15['sub_mode']='NA'
        df15['source_of_trans']='Self Initiated'
        df15['entity_bank']='NA'
        df15.drop(["new"], axis=1, inplace=True)
    except:
        pass
    
    #pos
    try:
        df16=ubi_df[ubi_df["Description"].str.contains("POS:")]
        df16['A'], df16['new'] = df16['Description'].str.split(':', 1).str
        df16['B']=df16['new'].str.split("/")
        df16['entity']=df16["B"].apply(lambda x: x[0])
        df16['source_of_trans']='Self Initiated'
        df16['mode']='Card'
        df16['sub_mode']='Debit Card'
        df16['entity_bank']='NA'
        df16.drop(["A"], axis=1, inplace=True)
        df16.drop(["B"], axis=1, inplace=True)
        df16.drop(["new"], axis=1, inplace=True)
    except:
        pass
    
    #TRF
    
    try:
        df17=ubi_df[ubi_df["Description"].str.contains("TRF")]
        df17['new']=df17['Description'].str.split("TO")
        df17['sub_mode']=df17["new"].apply(lambda x: x[0])
        df17['entity']=df17["new"].apply(lambda x: x[1])
        df17['source_of_trans']='Auto'
        df17['mode']='Transfer'
        df17['entity_bank']='NA'
        df17.drop(["new"], axis=1, inplace=True)
        
    except:
        pass
    
    
    #AC XFR
    
    
    try:
        df18=ubi_df[ubi_df["Description"].str.contains("Ac xfr")]
        df18['sub_mode']='Acc Transfer'
        df18['mode']='NA'
        df18['source_of_trans']='Self Initiated'
        df18['entity']='NA'
        df18['entity_bank']='NA'
    except:
        pass
    
    
    #RTGS
    
    try:
        df19=ubi_df[ubi_df["Description"].str.startswith("RTGS:")]
        df19['sub_mode'], df19['entity'] = df19['Description'].str.split(':', 1).str
        df19['mode']='Branch'
        df19['source_of_trans']='Self Initiated'
        df19['entity_bank']='NA'
    except:
        pass
    
    
    #RTGS 2.0
    try:
        df20=ubi_df[ubi_df["Description"].str.startswith("RTGSO")]
        df20['sub_mode'], df20['new'] = df20['Description'].str.split('-', 1).str
        df20['new']=df20['new'].str.split(" ")
        df20['entity']=df20["new"].apply(lambda x: x[0])
        df20['mode']='Branch'
        df20['source_of_trans']='Self Initiated'
        df20['entity_bank']='NA'
        df20.drop(["new"], axis=1, inplace=True)
    except:
        pass
    
    #RTGS 3.0
    
    try:
        df21=ubi_df[ubi_df["Description"].str.startswith("Cr.")]
        df21['entity']='NA'
        df21['sub_mode']='Reversal'
        df21['mode']='Failed'
        df21['source_of_trans']='Automated'
        df21['entity_bank']='NA'
        
    except:
        pass
    
    
    #epay
    
    try:
        df22=ubi_df[ubi_df["Description"].str.startswith("ePAY")]
        df22['sub_mode'], df22['new'] = df22['Description'].str.split('/To:', 1).str
        df22['new']=df22['new'].str.split("/")
        df22['entity']=df22["new"].apply(lambda x: x[0])
        df22['source_of_trans']='Self Initiated'
        df22['mode']='Card'
        df22['entity_bank']='NA'
        df22.drop(["new"], axis=1, inplace=True)
        
    except:
        pass
    
    
    #concat all your dataframes
    t1 = pd.concat([df1,df2,df3,df4,df5,df6,df7,df8,df9,df10,df11,df12,df13,
                    df14,df15,df16,df17,df18,df19,df20,df21,df22], axis=0)
    
    t2=ubi_df[~ubi_df['Description'].isin(t1['Description'])]
    t2['mode']='NA'
    t2['sub_mode']='NA'
    t2['source_of_trans']='NA'
    t2['entity']='NA'
    t2['entity_bank']='NA'
    t2['df']='t2'
    
    final = pd.concat([t1,t2], axis=0)
    final['Txn Date']= pd.to_datetime(final['Txn Date'],dayfirst=True)
    final = final.sort_values(by= ['Txn Date'])
    final = final.sort_index()
    final['Txn Date'] = [dt.strftime(pd.to_datetime(x,dayfirst=True),"%d-%m-%Y") for x in final['Txn Date']]
    final["Cheque Number"]=final["Instr. ID"]
    final = final[['Txn Date', 'Description','Cheque Number', 'Debit', 'Credit', 'Balance', 'Account Name','Account Number','mode','entity','source_of_trans','entity_bank','sub_mode']]

    final['Debit'] = final['Debit'].astype('str')
    final['Debit'] = final['Debit'].apply(lambda x : x.replace(',',''))
    final['Debdit'] = final['Debit'].where(df['Debit'].notnull(), None)
    final['Debit'] = final['Debit'].astype('float64')
     
    final['Credit'] = final['Credit'].astype('str')
    final['Credit'] = final['Credit'].apply(lambda x : x.replace(',',''))
    final['Credit'] = final['Credit'].where(df['Credit'].notnull(), None)
    final['Credit'] = final['Credit'].astype('float64')
    
    final['Balance'] = final['Balance'].astype('str')
    final['Balance'] = final['Balance'].apply(lambda x : x.replace(',',''))
    final['Balance'] = final['Balance'].astype('float64')
    
    return final
    #final.to_csv("{}\\{}_{}_{}.csv".format(out_path,file_name,account_no, last_trans_date),index=False)

#df=union_digitization(r"D:\User DATA\Documents\A3\data_extraction\new\02-01-2020 to 19-02-2020.pdf","")
#try :
#    union_digitization(r".\input_files\1 May 2020 to 1 July 2020.pdf",
#                         r".\output_files")
#except Exception as e:
#    print(e)
#    print("\nThis statement cannot be digitized.\n")
