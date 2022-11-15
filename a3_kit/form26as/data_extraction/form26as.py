# from IPython import get_ipython;   
# get_ipython().magic('reset -sf')
import pandas as pd
import numpy as np
import tabula
import re



def get_form26as_data(pdf_path):
    
    # reading the pdf table
    tables = tabula.read_pdf(pdf_path, pages='all',stream=True)
    type(tables)
    out_path=''
    len(tables)
    if len(tables)==0:
        print("Cannot be digitized")
    else:
        ########digitizing assesse details table on top
        try:
            df1=tables[0]
            
            columns=list(df1.columns)
            type(columns)
            
            PAN=[]
            Financial_Year=[]
            Assessment_Year=[]
            Current_pan_status=[]
            for i in columns:
                if "Unnamed" in i:
                    del df1[i]   
                temp=re.findall("([a-zA-Z0-9]{10,})", i)
                temp=list(temp)
                def num(s):
                    return any(j.isdigit() for j in s)
                for k in temp:
                    if num(k)==True:
                        PAN.append(k)    
                if "Financial" in i:
                    Financial_Year.append(columns[columns.index(i)+1])  
            columns=list(df1.columns)
            type(columns)   
            for i in columns:
                if "Assessment" in i:
                    Assessment_Year.append(columns[columns.index(i)+1])
                if "Status" in i:
                    Current_pan_status.append(columns[columns.index(i)+1])
                
            
            Name_of_Assessee=[]
            Address_of_Assessee=[]
            for j in range(len(df1)) :
                for k in range(len(df1.columns)) :
                    if "Name" in str(df1.iloc[j,k]) :
                        #print(df1.iloc[j,k])
                        Name_of_Assessee.append(df1.iloc[j,k+1])
                    if "Address" in str(df1.iloc[j,k]) :
                        add=(df1.iloc[j,k+1])
                        if df1.iloc[j+1,k+1] is None:
                            pass
                        else:
                            add=add+str(df1.iloc[j+1,k+1])
                            #print(add)
                            Address_of_Assessee.append(add)
            data1=pd.DataFrame({"PAN":PAN,
                                "Financial_Year":Financial_Year,
                               "Assessment_Year":Assessment_Year,
                               "Current_pan_status":Current_pan_status,
                               "Name_of_Assessee":Name_of_Assessee,
                               "Address_of_Assessee":Address_of_Assessee})
        except:
            pass
        
        
        ########digitizing Part A table 
        try:
            df2=tables[1]
            
            ###########other tables
            Name_of_Deductor=[]
            TAN_of_Deductor=[]
            Total_Amount_Paid_Credited=[]
            Total_Tax_Deducted=[]
            Total_TDS_Deposited=[]
            df2=tables[1]
            len(tables)
            columns2=list(df2.columns)
            type(columns)
            
            for j in range(len(df2)) :
                for k in range(len(df2.columns)) :
                    if "Section" in str(df2.iloc[j,k]) :
                        l1=list(df2.iloc[j-1,:])
                        #print(l1)
                        l1=l1[1:]
                        l2=[]
                        for p in l1:
                            #print(p)
                            if "nan" not in str(p):
                                l2.append(p)
                                
                        if len(l2)>1:
                            Name_of_Deductor.append(l2[0])
                            TAN_of_Deductor.append(l2[1])
                            Total_Amount_Paid_Credited.append(l2[2])
                            Total_Tax_Deducted.append(l2[3])
                            Total_TDS_Deposited.append(l2[4])
            data2=pd.DataFrame({"Name_of_Deductor":Name_of_Deductor,
            "TAN_of_Deductor":TAN_of_Deductor,
            "Total_Amount_Paid_Credited":Total_Amount_Paid_Credited,
            "Total_Tax_Deducted":Total_Tax_Deducted,
            "Total_TDS_Deposited":Total_TDS_Deposited})
            
            ###getting all the transactions
            for j in list(df2.columns):
                if df2[j].isna().sum()==(list(df2.shape))[0]:
                    del df2[j]
            
            df2=df2.iloc[1:]
            
            for j in range(len(df2)) :
                for k in range(len(df2.columns)) :
                    try:
                        if "Sr. No." in str(df2.iloc[j,k]):
                            df2.drop(df2.index[[j,j+1]],axis=0,inplace=True)
                    except:
                        pass
            
            for i in df2.columns:
                if "TAN" in i:
                    df2["Remarks"]=df2[i]
            
            for i in list(df2.columns):
                if "TAN" in i:
                    k=list(df2.columns).index(i)
                    for j in range(len(df2)):
                        if len(str(df2.iloc[j,k]))<10:
                            df2.iloc[j,k]=df2.iloc[j-1,k]
                            
            for j in range(len(df2)) :
                for k in range(len(df2.columns)) :            
                    try:
                        if "nan" in str(df2.iloc[j,1]):
                            df2.drop(df2.index[[j]],axis=0,inplace=True)
                        if "nan" in str(df2.iloc[j,2]):
                            df2.drop(df2.index[[j]],axis=0,inplace=True)
                    except:
                        pass
            df2.columns 
            
            df2=df2.reset_index()
            
            for i in list(df2.columns):
                if "Name" in i:
                    list1=df2[i].str.split(" ")
                    if len(list1[0])==3:
                        df2[['Transaction_Date', 'Status_of_Booking', 'Date_of_Booking']] = pd.DataFrame([ x.split(' ') for x in df2[i].tolist() ])
                    else:
                        df2[['Transaction_Date', 'Status_of_Booking']] = pd.DataFrame([ x.split(' ') for x in df2[i].tolist() ])
                        df2['Date_of_Booking']=df2.iloc[:,(list(df2.columns)).index("Name of Deductor")+1]
                        del df2["Unnamed: 1"]
            for i in df2.columns:
                if "index" in i:
                    del df2[i]  
                if "Name" in i:
                    del df2[i]
               
            cols=['Sr_No.',
                  'Section_1',
             'TAN_of_Deductor',
             'Amount_Paid_Credited',
             'Tax_Deducted',
             'TDS_Deposited',
             'Remarks', 
             'Transaction_Date',
             'Status_of_Booking',
             'Date_of_Booking']
            
            list(df2.columns)
            df2.columns=cols
            ####
            df3=tables[2]
            cols2=[]
            columns3=[]
            for i in columns2:
                if "Unnamed" in i:
                    pass
                else:
                    columns3.append(i) 
                
            for i in columns3:
                    if type(i)!=str:
                        cols2.append(i)
                    if type(i)==str:
                        i=i.replace(" ","")
                        cols2.append(i)
            
            columns4=[]
            for i in list(df3.columns):
                if "Unnamed" in i:
                    pass
                else:
                    columns4.append(i) 
            cols3=[]
            for i in columns4:
                if type(i)!=str:
                    cols3.append(i)
                if type(i)==str:
                    i=i.replace(" ","")
                    cols3.append(i)
                if cols3==cols2:
                    df3=0
                else:
                    df3=df3
            
            if type(df3)==int:
                pass
            else:
                cols_values=list(df3.columns)
                df3.reset_index()
                cols_values1=[]
                for p in cols_values:
                    if "." in p:
                        q=p.split(".")
                        if len(q)>2:
                            q=q[:-1]
                            r=q[0]+"."+q[1]
                            cols_values1.append(r)
                        else:
                           cols_values1.append(p) 
                    else:
                        cols_values1.append(p)
                df2=df2.append({'Sr_No.':cols_values1[0],
                      'Section_1':cols_values1[1],
                 'Amount_Paid_Credited':cols_values1[6],
                 'Tax_Deducted':cols_values1[7],
                 'TDS_Deposited':(cols_values1[8]),
                 'Remarks':cols_values1[5], 
                 'Transaction_Date':cols_values1[2],
                 'Status_of_Booking':cols_values1[3],
                 'Date_of_Booking':cols_values1[4]}, ignore_index=True)
                
                df2_new=pd.DataFrame({'Sr_No.':df3.iloc[:,0],
                     'Section_1':df3.iloc[:,1],
                     'Amount_Paid_Credited':df3.iloc[:,6],
                     'Tax_Deducted':df3.iloc[:,7],
                     'TDS_Deposited':df3.iloc[:,8],
                     'Remarks':df3.iloc[:,5], 
                     'Transaction_Date':df3.iloc[:,2],
                     'Status_of_Booking':df3.iloc[:,3],
                     'Date_of_Booking':df3.iloc[:,4]})
                df2=df2.append(df2_new)
                #df2.info()
                for j in range(len(df2)) :
                    for k in range(len(df2.columns)) :
                        if str(df2.iloc[j,2])=="nan":
                            df2.iloc[j,2]=df2.iloc[j-1,2]
            
            data3=pd.merge(df2,data2,on=["TAN_of_Deductor"],how="left")
        except:
          dict = {'Sr_No.':[],"Section_1":[],"TAN_of_Deductor":[],"Amount_Paid_Credited":[],"Tax_Deducted":[],
                    "TDS_Deposited":[],"Remarks":[],"Transaction_Date":[],"Status_of_Booking":[],"Date_of_Booking":[],
                    "Name_of_Deductor":[],"Total_Amount_Paid_Credited":[],"Total_Tax_Deducted":[]
                    ,"Total_TDS_Deposited":[],"PAN":[],"Name_of_Assessee":[],"Assessment_Year":[]
                    }
          data3 = pd.DataFrame(dict)
        
        #####################################PartC########################################
        try:
            for tab in tables:
                cols=list(tab.columns)
                for i in cols:
                    if "Major" in i:
                        data5=tab
                        data5=data5.iloc[1:,:]
            for i in data5.columns:
                if data5[i].isna().sum()==list(data5.shape)[0]:
                    del data5[i]
            cols5=list(data5.columns)
            for i in cols5:
                if "Major" in i:
                    cols5[(cols5.index(i))]="Major Head"
                if "Minor" in i:
                    cols5[(cols5.index(i))]="Minor Head"
                if "Date" in i:
                    cols5[(cols5.index(i))]="Date of Deposit"
                if "Challan" in i:
                    cols5[(cols5.index(i))]="Challan Serial Number"
                if "Education" in i:
                    cols5[(cols5.index(i))]="Education Cess"
            data5.columns=cols5
            
        except:
            pass
        #####################################Part D######################################
        try:
            for tab in tables:
                cols=list(tab.columns)
                for i in cols:
                    if ("Nature of Refund" in i) or ('Amount of Refund' in i):
                        data4=tab.iloc[1:,:]
                        for j in list(data4.columns):
                            if "Unnamed" in j:
                                data4["Interest"]=data4[j]
                                del data4[j]
        except:
            pass
        
        ####################################Part B########################################
        try:
            for tab in tables:
                    cols=list(tab.columns)
                    for i in cols:
                        if "Collector" in i:
                            data6=tab
                            
            Name_of_Collector=[]
            TAN_of_Collector=[]
            Total_Amount_Paid_Debited=[]
            Total_Tax_Collected=[]
            Total_TCS_Deposited=[]
            
            for j in range(len(data6)) :
                for k in range(len(data6.columns)) :
                    if "Section" in str(data6.iloc[j,k]) :
                        l1=list(data6.iloc[j-1,:])
                        l1=l1[1:]
                        l2=[]
                        for p in l1:
                            if "nan" not in str(p):
                                l2.append(p)
                        if len(l2)>1:
                            Name_of_Collector.append(l2[0])
                            TAN_of_Collector.append(l2[1])
                            Total_Amount_Paid_Debited.append(l2[2])
                            Total_Tax_Collected.append(l2[3])
                            Total_TCS_Deposited.append(l2[4])
                            
            data7=pd.DataFrame({'Name_of_Collector':Name_of_Collector,
            'TAN_of_Collector':TAN_of_Collector,
            'Total_Amount_Paid_Debited':Total_Amount_Paid_Debited,
            'Total_Tax_Collected':Total_Amount_Paid_Debited,
            'Total_TCS_Deposited':Total_Amount_Paid_Debited})
            
            ###getting all the transactions
            for j in list(data6.columns):
                if data6[j].isna().sum()==(list(data6.shape))[0]:
                    del data6[j]
            
            data6=data6.iloc[1:]
            
            for j in range(len(data6)) :
                for k in range(len(data6.columns)) :
                    try:
                        if "Sr. No." in str(data6.iloc[j,k]):
                            data6.drop(data6.index[[j,j+1]],axis=0,inplace=True)
                    except:
                        pass
            
            for i in data6.columns:
                if "TAN" in i:
                    data6["Remarks"]=data6[i]
            
            for i in list(data6.columns):
                if "TAN" in i:
                    k=list(data6.columns).index(i)
                    for j in range(len(data6)):
                        if str(data6.iloc[j,k])=="-":
                            data6.iloc[j,k]=data6.iloc[j-1,k]
                            
            for j in range(len(data6)) :
                for k in range(len(data6.columns)) :            
                    try:
                        if "nan" in str(data6.iloc[j,1]):
                            data6.drop(data6.index[[j]],axis=0,inplace=True)
                        if "nan" in str(data6.iloc[j,2]):
                            data6.drop(data6.index[[j]],axis=0,inplace=True)
                    except:
                        pass
            data6.columns 
            
            data6=data6.reset_index()
            
            for i in list(data6.columns):
                if "Name" in i:
                    list1=data6[i].str.split(" ")
                    if len(list1[0])==3:
                        data6[['Transaction_Date', 'Status_of_Booking', 'Date_of_Booking']] = pd.DataFrame([ x.split(' ') for x in data6[i].tolist() ])
                    else:
                        data6[['Transaction_Date', 'Status_of_Booking']] = pd.DataFrame([ x.split(' ') for x in data6[i].tolist() ])
                        data6['Date_of_Booking']=data6.iloc[:,(list(data6.columns)).index(i)+1]
                        del data6["Unnamed: 1"]
                        
            for i in data6.columns:
                if "index" in i:
                    del data6[i]  
                if "Name" in i:
                    del data6[i]
               
            cols6=['Sr_No.',
                  'Section_1',
             'TAN_of_Collector',
             'Amount_Paid_Debited',
             'Tax_Collected',
             'TCS_Deposited',
             'Remarks', 
             'Transaction_Date',
             'Status_of_Booking',
             'Date_of_Booking']
        
            
            data6.columns=cols6
            data8=pd.merge(data6,data7,on=["TAN_of_Collector"],how="left")
        except:
             dict = {'Sr_No.':[],"Section_1":[],"TAN_of_Collector":[],"Amount_Paid_Debited":[],"Tax_Collected":[],
                    "TCS_Deposited":[],"Remarks":[],"Transaction_Date":[],"Status_of_Booking":[],"Date_of_Booking":[],
                    "Name_of_Collector":[],"Total_Amount_Paid_Debited":[],"Total_Tax_Collected":[]
                    ,"Total_TCS_Deposited":[],"PAN":[],"Name_of_Assessee":[],"Assessment_Year":[]
                    }
             data8 = pd.DataFrame(dict)
        
        
        ######################################digitizing Part A1######################################### 
        try:
            cols4=[]
            for tab in tables[2:]:       
                for i in list(tab.columns):
                    if type(i)!=str:
                        cols4.append(i)
                    if type(i)==str:
                        i=i.replace(" ","")
                        cols4.append(i)
                    if cols4==cols2:
                        df4=tab
                    else:
                        pass
        
            
            ###########other tables
            Name_of_Deductor=[]
            TAN_of_Deductor=[]
            Total_Amount_Paid_Credited=[]
            Total_Tax_Deducted=[]
            Total_TDS_Deposited=[]
            
            
            for j in range(len(df4)) :
                for k in range(len(df4.columns)) :
                    if "Section" in str(df4.iloc[j,k]) :
                        l1=list(df4.iloc[j-1,:])
                        #print(l1)
                        l1=l1[1:]
                        l2=[]
                        for p in l1:
                            #print(p)
                            if "nan" not in str(p):
                                l2.append(p)
                                print(l2)
                        if len(l2)>1:
                            Name_of_Deductor.append(l2[0])
                            TAN_of_Deductor.append(l2[1])
                            Total_Amount_Paid_Credited.append(l2[2])
                            Total_Tax_Deducted.append(l2[3])
                            Total_TDS_Deposited.append(l2[4])
            data9=pd.DataFrame({"Name_of_Deductor":Name_of_Deductor,
            "TAN_of_Deductor":TAN_of_Deductor,
            "Total_Amount_Paid_Credited":Total_Amount_Paid_Credited,
            "Total_Tax_Deducted":Total_Tax_Deducted,
            "Total_TDS_Deposited":Total_TDS_Deposited})
            
            ###getting all the transactions
            for j in list(df4.columns):
                if df4[j].isna().sum()==(list(df4.shape))[0]:
                    del df4[j]
            
            df4=df4.iloc[1:]
            
            for j in range(len(df4)) :
                for k in range(len(df4.columns)) :
                    try:
                        if "Sr. No." in str(df4.iloc[j,k]):
                            df4.drop(df4.index[[j,j+1]],axis=0,inplace=True)
                    except:
                        pass
            
            for i in df4.columns:
                if "TAN" in i:
                    df4["Remarks"]=df4[i]
            
            for i in list(df4.columns):
                if "TAN" in i:
                    k=list(df4.columns).index(i)
                    #print(k)
                    for j in range(len(df4)):
                        if len(str(df4.iloc[j,k]))<10:
                            df4.iloc[j,k]=df4.iloc[j-1,k]
                            
            for j in range(len(df4)) :
                for k in range(len(df4.columns)) :            
                    try:
                        if "nan" in str(df4.iloc[j,1]):
                            df4.drop(df4.index[[j]],axis=0,inplace=True)
                        if "nan" in str(df4.iloc[j,2]):
                            df4.drop(df4.index[[j]],axis=0,inplace=True)
                    except:
                        pass
            
            
            df4=df4.reset_index()
            
            for i in list(df4.columns):
                if "Name" in i:
                    list1=df4[i].str.split(" ")
                    if len(list1[0])==3:
                        df4[['Transaction_Date', 'Status_of_Booking', 'Date_of_Booking']] = pd.DataFrame([ x.split(' ') for x in df4[i].tolist() ])
                    else:
                        df4[['Transaction_Date', 'Status_of_Booking']] = pd.DataFrame([ x.split(' ') for x in df4[i].tolist() ])
                        df4['Date_of_Booking']=df4.iloc[:,(list(df4.columns)).index("Name of Deductor")+1]
                        del df4["Unnamed: 1"]
            for i in df4.columns:
                if "index" in i:
                    del df4[i]  
                if "Name" in i:
                    del df4[i]
               
            cols=['Sr_No.',
                  'Section_1',
             'TAN_of_Deductor',
             'Amount_Paid_Credited',
             'Tax_Deducted',
             'TDS_Deposited',
             'Remarks', 
             'Transaction_Date',
             'Status_of_Booking',
             'Date_of_Booking']
            
            list(df4.columns)
            df4.columns=cols
            ####
               
            data10=pd.merge(df4,data9,on=["TAN_of_Deductor"],how="left")
            for j in range(len(data10)) :
                for k in range(len(data10.columns)) :
                    try:
                        if "Sr. No." in str(data10.iloc[j,k]):
                            #print(data10.iloc[j,k])
                            data10.drop(data10.index[[j,k]],axis=0,inplace=True)
                    except:
                        pass
            
        except:
            pass
        
        PAN[0]
        Name_of_Assessee[0]
        Assessment_Year[0]
        
        
    
    data8["PAN"]=PAN[0]
    data8["Name_of_Assessee"]=Name_of_Assessee[0]
    data8["Assessment_Year"]=Assessment_Year[0]
    #out_path1=out_path+"\partB_"+PAN[0]+"_"+Assessment_Year[0]+".xlsx"
    #data8.to_excel(out_path1) 
    
    for i in range(len(tables)):
        if len(tables[i].columns) > 2:
            if tables[i].columns[2]=="Short Payment":
                part_g=tables[i]
    
    part_g = part_g.iloc[4:]
    part_g["PAN"]=PAN[0]
    part_g["Name_of_Assessee"]=Name_of_Assessee[0]
    part_g["Assessment_Year"]=Assessment_Year[0]           
    
    
    # out_path1=out_path+PAN[0]+"_"+Assessment_Year[0]+".xlsx"
    
    
    # print(out_path1)
    
    data3["PAN"]=PAN[0]
    data3["Name_of_Assessee"]=Name_of_Assessee[0]
    data3["Assessment_Year"]=Assessment_Year[0]
    #out_path1=out_path+"\partA_"+PAN[0]+"_"+Assessment_Year[0]+".xlsx"
    #data3.to_excel(out_path1) 
    
    
    data5["PAN"]=PAN[0]
    data5["Name_of_Assessee"]=Name_of_Assessee[0]
    data5["Assessment_Year"]=Assessment_Year[0]
    #out_path1=out_path+"\partC_"+PAN[0]+"_"+Assessment_Year[0]+".xlsx"
    
         
          
    data4.rename(columns={'Assessment Year':'Assessment_Year_Refund'},
             inplace=True)
    data4["PAN"]=PAN[0]
    data4["Name_of_Assessee"]=Name_of_Assessee[0]
    data4["Assessment_Year"]=Assessment_Year[0]
    #out_path1=out_path+"\partD_"+PAN[0]+"_"+Assessment_Year[0]+".xlsx"
    # print(data1[0])
    print('error in form26 python code')
    return data1, data3, data8, data5, data4, part_g
    
    # with pd.ExcelWriter(out_path1) as writer:
    #     data1.to_excel(writer, sheet_name =  "Assesee Details",index=False) 
    #     data3.to_excel(writer,sheet_name =  "Part A",index=False) 
    #     data8.to_excel(writer,sheet_name =  "Part B",index=False)
    #     data5.to_excel(writer,sheet_name =  "Part C",index=False)  
    #     data4.to_excel(writer,sheet_name =  "Part D",index=False)
    #     part_g.to_excel(writer,sheet_name =  "Part G",index=False)
    
    


####call the  function to digitize form26as
# form26as(r"C:/Users/hp/Downloads/Internship/10/Superb 26 AS_2018 (1).pdf",r"C:/Users/hp/Downloads/Internship/")


