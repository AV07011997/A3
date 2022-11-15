import pandas as pd
import datetime
import numpy as np
import os

import mysql.connector



def update_bank_table(file):

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Hardik@20",
        database="a3_kit"
    )

    mycursor = mydb.cursor()
    reader = pd.read_csv(file)
    reader['Txn Date']=pd.to_datetime(reader['Txn Date'])
    reader['Txn Date']=reader['Txn Date'].apply(lambda x :x.strftime('%Y-%m-%d'))
    reader['Txn Date']=reader['Txn Date'].astype('str')

    reader=reader.replace(np.nan,'NA')

    # print(reader)
    reader['creation_time']=datetime.datetime.now()

    reader['last_modification_time']=datetime.datetime.now()
    reader['image_name']="asmfbejhb"
    print(reader)
    for i in range(len(reader)):
        row = reader.iloc[i]
        print(i)
       
        mycursor.execute("insert into bank_bank(txn_date,description,cheque_number,debit,credit,balance,account_name,account_number,mode,entity,source_of_trans,entity_bank,sub_mode,transaction_type,bank_name,customer_id,deal_id,creation_time,last_modification_time,image_name) values(%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s,%s,%s,%s)", row)
    os.remove(file)           
    #return render(request,"bureauAge.html",{})

update_bank_table(r'D:\hdfc.csv')