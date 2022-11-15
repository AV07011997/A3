import pandas as pd
import re
import numpy as np

def emi_vs_auto_debit(data, loans_data):
    if not data.empty:
        def remove_inter_acc(c1):
            c1.reset_index(drop=True, inplace=True)
            accounts = list(c1['account_number'].unique())
            for i in accounts:
                c2=c1[c1["account_number"]!=i]
                c2["acc_no_match"]=c2["description"].apply(lambda x: 1 if i in (x) else 0)
                c2=c2[c2["acc_no_match"]==1]
                try:
                    i=list(c2.index)[0]
                    c1=c1.drop(i)
                except:
                    pass
            return c1

        def creator(c, disb_date, emi):
            #disb_date=pd.to_datetime('20/01/2017', dayfirst=True)
            #emi=20500
            c["account_number"]=c["account_number"].str.replace("'","")

            c=c[pd.notna(c['account_number'])]
            c = c[['txn_date', 'description', 'debit', 'entity','credit', 'balance', 'account_number','bank_name']]
            c['txn_date'] = [pd.to_datetime(i, dayfirst=True) for i in c['txn_date']]
            c.sort_values(['txn_date'], ascending=True, inplace=True)
            c=c[pd.notna(c['debit'])]
            c1=c[c['txn_date']>disb_date]
            c1=remove_inter_acc(c1)
            c1=c1[c1.debit>0]
            c1=c1[c1['balance']>=0]

            cut_off_max=emi+(0.15*emi)
            cut_off_min=emi-(0.15*emi)
            c1=c1[(c1['debit']>=cut_off_min) & (c1['debit']<=cut_off_max)]

            c1['Diff'] = abs(c1['debit']-emi)
            c1.sort_values(by=['Diff'], ascending=True, inplace=True)
            c1.reset_index(drop=True, inplace=True)
            
            d=c1.groupby(['entity','account_number']).head(1)

            
            debit_unique=list(d['debit'].unique())
            debit_unique.sort(reverse=True)
            debit_unique[:3]
            out1=d[d["debit"].isin(debit_unique)]
            out1.columns
            out1=out1[[ 'entity','debit','bank_name','account_number']]
            out2=c[c["entity"].isin(out1["entity"])]
            out3=out2.groupby("entity")["debit"].count().reset_index()
            out3=out3.rename(columns={"debit":"Transactions"})
            out1
            out2.columns
            out4=pd.merge(out2[['debit', 'entity']],out1[['debit', 'entity']],on="entity",how="inner")
            out4["diff"]= abs(out4['debit_x']-out4['debit_y'])
            out4=out4[out4["diff"]!=0]
            out4.sort_values(by=['diff'], ascending=True, inplace=True)
            out4.reset_index(drop=True, inplace=True)
            out5=out4.groupby('entity').head(3)
            out5=out5.groupby("entity")["debit_x"].unique().reset_index()
            out5=out5.rename(columns={"debit_x":"Next 3 Nearest Debit Entries"})

            final = out1.merge(out3.merge(out5, on='entity', how='left'), on='entity', how='left')
          
            return final

        #main code
        #loans = [('Home', pd.to_datetime('20/01/2017', dayfirst=True), 20500), ('Auto', pd.to_datetime('20/10/2018', dayfirst=True), 4500), ('Personal', pd.to_datetime('20/01/2017', dayfirst=True), 10500), ('Education', pd.to_datetime('20/01/2017', dayfirst=True), 1500)]
        # print(loans_data)
        # l = [list(i.values()) for i in loans_data]
        # loans = [(i[0],pd.to_datetime(i[1], format='%Y-%m-%d'),i[2]) for i in loans_data]
        """
        conn = pymysql.connect(host = '10.20.30.40', port = 3306, user = 'ABC', passwd = 'PAS8765', charset = 'utf8', db='bureau')
        sql1 = "select bank_name, account_number,description, txn_date, credit,balance debit from bank_table where customer_id="123" and deal_id="111" "  # customer_id and deal_id will be dynamic

        data_bank = pd.read_sql(sql1, conn)
        """
        loans_data['Disbursal_date'] = pd.to_datetime(loans_data['Disbursal_date'], format='%Y-%m-%d')
        c=data
      
        df = pd.DataFrame(columns=['entity', 'EMI', 'debit', '#Transactions with Entity', 'Transactions closest to EMI(max=3)', 'Loan Type'])

        for i in range(len(loans_data)):
            d = creator(c, loans_data['Disbursal_date'][i], loans_data['EMI_new'][i])
            d['Loan Type'] = loans_data['Loan_type'][i]
            d['EMI'] = loans_data['EMI_new'][i]
            df = df.append(d)
        df.set_index(['Loan Type', 'EMI', 'entity'])

        try:
            df["account_number"]=df["account_number"].apply(lambda x: re.sub('\D', '', x))

            df["Next 3 Nearest Debit Entries"]=np.where(df["Next 3 Nearest Debit Entries"].isnull(),[""],df["Next 3 Nearest Debit Entries"])
            df["Trans1"]=df["Next 3 Nearest Debit Entries"].apply(lambda x:x[0] if len(x)>0 else None)
            df["Trans2"]=df["Next 3 Nearest Debit Entries"].apply(lambda x: x[1] if  len(x)>1 else None)
            df["Trans3"]=df["Next 3 Nearest Debit Entries"].apply(lambda x: x[2] if len(x)>2 else None)

           
        except:
            pass

        return df

    else:
        return

######this should be added to Views.py
# bank_data = pandas.DataFrame(list(Bank.objects.filter(customer_id=customer_id).values()))
# with connection.cursor() as cursor:
#       cursor.execute("select Loan_type, Disbursal_date, EMI_new from bureau where customer_id = " + customer_id + ";")
# data = dictfetchall(cursor)
# print(type(bank_data))
# emi_debit_table = emivsautodebit(bank_data, data)

    