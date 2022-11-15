import pandas as pd
from babel.numbers import format_currency
import pymysql
import numpy as np

def itr_display345(part_a, part_b,assesse_details):

    ###############month wise salary  
    # part_a = pd.read_excel(part_a_path,sheet_name = "Part A")
    part_a = part_a
    # part_b = pd.read_excel(part_a_path,sheet_name = "Part B")
    part_b = part_b
    print(part_a)
    try:
        temp = part_a['assessment_year'][0]
    except:
        pass
    # details = pd.read_excel(part_a_path,sheet_name = "Assesee Details")
    details = assesse_details
    # details.info()
    try:
        ay_list=list(details["assessment_year"].unique())
        part_a_sec2 = part_a[["assessment_year","section_1",'amount_paid_credited','transaction_date']]
        part_b_sec2 = part_b[["assessment_year","section_1",'amount_paid_debited','transaction_date']]
        part_a_sec2['amount_paid_credited'] = part_a_sec2['amount_paid_credited'].astype('float64')
        part_b_sec2['amount_paid_debited'] = part_b_sec2['amount_paid_debited'].astype('float64')
    ####appending part a and b
        part_b_sec2.rename(columns = {'amount_paid_debited':'amount_paid_credited'}, inplace = True)
        Part_a_b_sec2 = pd.concat([part_a_sec2, part_b_sec2]).reset_index(drop = True) 
    except:
        pass
        
    # part_a_sec2 = part_a[["assessment_year","section_1",'amount_paid_credited','transaction_date']]
    # part_b_sec2 = part_b[["assessment_year","section_1",'amount_paid_debited','transaction_date']]
    

    
    #Categorise the transactions into categories
    list1=['194K']
    list2=['194B','194BB']
    list3=['206CA','206CB','206CC','206CD','206CE','206CF','206CG','206CH','206CI','206CJ','206CK','206CL','206CM','206CN']
    list4=['194E','194LC','195','196A','196B']
    list5=['194G','194H','194D']
    list6=['194C']
    list7=['193','194','194A','194LB','194LBA','194LBB','194LBC','194LD','196C','196D']
    list8=['194J']
    list9=['192A','194DA','194EE','194F']
    list10=['194I']
    list11=['192']
    list12=['194IA','194LA']
    
    
    def func1(x):
        if x in list1:
            return("194K")
        elif x in list2:
            return("Betting")
        elif x in list3:
            return("Collection at source")
        elif x in list4:
            return("Income from abroad")
        elif x in list5:
            return("Income from commission")
        elif x in list6:
            return("Income from contracting")
        elif x in list7:
            return("Income from investment")
        elif x in list8:
            return("Income from tech. professional services")
        elif x in list9:
            return("Orignal investment(principal) withdrawal")
        elif x in list10:
            return("Rent")
        elif x in list11:
            return("Salary")
        elif x in list12:
            return("Sale of property")
    try:
        Part_a_b_sec2["Sec1_Cat"]=Part_a_b_sec2.section_1.apply(func1)
        Part_a_b_sec2["Measures"]=np.where(Part_a_b_sec2["Sec1_Cat"]=="Salary","Salary","Non Salary Income")
        Part_a_b_sec2["Transaction_month"]=Part_a_b_sec2["transaction_date"].str[3:6]
    except:
        pass
    Salary=list(np.repeat("Salary",12))
    Non_Salary=list(np.repeat("Non Salary Income",12))
    Salary.extend(Non_Salary)
    months=['April','May','June','July','August','September','October',
            'November','December','January','February','March']
    months.extend(months)
    Months=pd.DataFrame({"months":months,"Measures":Salary})
    Months["m"]=Months["months"].str[0:3]
    # Months.info()
    df=Months.copy()
    try:
        for i in ay_list:
            Months["assessment_year"]=i
        # print(Months)
            df=df.append(Months)
        df.reset_index()
    
        df=df[df["assessment_year"].notnull()]
    # df.columns
        grouped=Part_a_b_sec2.groupby(["assessment_year","Measures","Transaction_month"]).agg(Value=("amount_paid_credited","sum")).reset_index()
    # grouped.columns
        merge=pd.merge(df,grouped,right_on=['assessment_year', 'Measures', 'Transaction_month'],left_on=["assessment_year","Measures","m"],how="left")
        merge["Value"]=merge["Value"].fillna(0)
    
    
    
    #####total
    # df.columns
        df1=df.drop_duplicates(['months', 'assessment_year'])
        df1["Measures"]="Total Income"
        merge1=merge.groupby(["months","assessment_year"]).agg(Value=("Value","sum")).reset_index()
        merge2=pd.merge(df1,merge1,on=["months","assessment_year"],how="left")
    
        merge2["Value"]=merge2["Value"].fillna(0)
    
    ####count
        grouped1=Part_a_b_sec2.groupby(["assessment_year","Transaction_month"]).agg(Value=("amount_paid_credited","count")).reset_index()
        df1["Measures"]="Number of credits"
    # grouped1.info()
    # df1.info()
        merge3=pd.merge(df1,grouped1,left_on=["m","assessment_year"],right_on=["Transaction_month","assessment_year"],how="left")
        merge3["Value"]=merge3["Value"].fillna(0)
    


        merge_final=merge.append(merge2).append(merge3)
        merge_final["Value"]=merge_final["Value"].fillna(0)
    except:
        pass
    
    # merge_final.columns
    def currency(x):
        return(format_currency(x, 'INR', locale='en_IN'))
    try:
        merge_final=merge_final[["months","assessment_year","Measures","Value"]].reset_index()
    
        merge_final1=pd.pivot_table(merge_final,columns=["months"], values=['Value'], index=['assessment_year', 'Measures'],)
        merge_final1.columns=merge_final1.columns.droplevel(0)
        merge_final1=merge_final1.reset_index()
    
    # merge_final1.Measures.unique()
        merge_final1["Measures"]=np.where(merge_final1["Measures"]=="Salary","a Salary",merge_final1["Measures"])
        merge_final1["Measures"]=np.where(merge_final1["Measures"]=="Non Salary Income","b Non Salary Income",merge_final1["Measures"])
        merge_final1["Measures"]=np.where(merge_final1["Measures"]=="Total Income","c Total Income",merge_final1["Measures"])
        merge_final1["Measures"]=np.where(merge_final1["Measures"]=="Number of credits","d Number of credits",merge_final1["Measures"])
        merge_final1=merge_final1.sort_values(by=["assessment_year","Measures"])
        merge_final1["Measures"]=merge_final1["Measures"].str[1:]
    # merge_final1.columns
        merge_final1["Financial_Year"]=merge_final1["assessment_year"].str.split("-").apply(lambda x: str(int(x[0])-1)+"-"+str(int(x[1])-1))
        merge_final1=merge_final1[['Financial_Year', 'Measures','April','May','June','July','August','September','October','November','December','January','February','March']]
    #merge_final1.to_csv(r"D:\User DATA\Documents\A3\KPI\ITR\month_wise_26as.csv")
    
    except:
        pass
    
    
    #############Section wise inflow of money (SELF-EMPLOYED)
    Section=['Salary','Rent','Betting','Income from investment','Income from contracting','Income from abroad','Orignal investment(principal) withdrawal','Sale of property','Income from tech. professional services','Income from commission','Collection at source','194K']
    
    df_section=pd.DataFrame({"Section":Section})
    df_section=df_section.reset_index()
    df_section1=df_section.copy()
    try:
        for i in ay_list:
            df_section["assessment_year"]=i
            df_section1=df_section1.append(df_section)
        df_section1=df_section1[df_section1["assessment_year"].notnull()]
        grouped_section=Part_a_b_sec2.groupby(["assessment_year","Sec1_Cat"]).agg(Value=("amount_paid_credited","sum")).reset_index()
        merge_section=pd.merge(df_section1,grouped_section,right_on=["assessment_year","Sec1_Cat"],left_on=["assessment_year","Section"],how="left")
        merge_section["Financial Year"]=merge_section["assessment_year"].str.split("-").apply(lambda x: str(int(x[0])-1)+"_"+str(int(x[1])-1))
        merge_section["Value"]=merge_section["Value"].fillna(0)
        merge_section1=pd.pivot_table(merge_section,columns=["Financial Year"], values=['Value'], index=['Section'])
        merge_section1.columns=merge_section1.columns.droplevel(0)
        merge_section1=merge_section1.reset_index()
        merge_section1=merge_section1.merge(df_section[["index","Section"]],on="Section",how="left")
        merge_section1=merge_section1.sort_values(by="index")
        del merge_section1["index"]
    #merge_section1.to_csv(r"D:\User DATA\Documents\A3\KPI\section_wise_inflow.csv")
    
    
    #######Number of transactions per deductor and the total amount (SELF-EMPLOYED)
        part_a_sec1 = part_a[["assessment_year","name_of_deductor",'total_amount_paid_credited']]
    
        part_a_deduc_amount = part_a_sec1.drop_duplicates()
        part_a_deduc_amount= part_a_deduc_amount[["assessment_year","name_of_deductor",'total_amount_paid_credited']]
        part_a_deduc_amount.columns = ["assessment_year",'name_of_deductor','Total Amount']
        part_a_deduc_amount["Financial Year"]=part_a_deduc_amount["assessment_year"].str.split("-").apply(lambda x: str(int(x[0])-1)+"-"+str(int(x[1])-1))
    #part_a_deduc_amount.columns
        part_a_deduc_amount=part_a_deduc_amount[['Financial Year', 'name_of_deductor', 'Total Amount']]
       
        part_a_deduc_count = part_a_sec1.groupby(["assessment_year",'name_of_deductor'])[["total_amount_paid_credited"]].agg('count').reset_index()
        part_a_deduc_count.columns = ["assessment_year",'name_of_deductor','No. of transactions']
        part_a_deduc_count["Financial Year"]=part_a_deduc_count["assessment_year"].str.split("-").apply(lambda x: str(int(x[0])-1)+"-"+str(int(x[1])-1))
        part_a_deduc_count.columns
        part_a_deduc_count=part_a_deduc_count[['Financial Year','name_of_deductor', 'No. of transactions']]
        result1 = pd.merge(part_a_deduc_count, part_a_deduc_amount, how='left', on=["Financial Year",'name_of_deductor'])
        result1 = result1.rename(columns = {'Financial Year':'financial_year','No. of transactions':'no_of_transactions','Total Amount':'total_amount'})
    #result1.to_csv(r"D:\User DATA\Documents\A3\KPI\ITR\transactions_deductor.csv")
        deductor_list = list(set(list(result1['name_of_deductor'])))
        deductor_list = pd.DataFrame(deductor_list).rename(columns={0:'name_of_deductor'})
        years = list(set(merge_final1['Financial_Year']))
    
        if (len(years)==1):
            years.append(1)
            years.append(2)
        elif (len(years)==2):
            years.append(3)

        year_wise =[]

        for i in years:
            year_wise.append(result1[result1['financial_year'] == i])
   
    # deductor_list_1 = []
        for i in range(len(year_wise)):
            deductor_list = deductor_list.merge(year_wise[i], on='name_of_deductor', how='left')
        # deductor_list['financial_year'] = deductor_list['financial_year'].fillna(years[i])
        # temp = temp.fillna('-')
        # deductor_list_1.append(temp)
    
    # deductor_list_1 = pd.concat(deductor_list_1)
    except:
        merge_final1=""
        merge_section1=""
        deductor_list=""
    print(merge_final1)
    return merge_final1,merge_section1,deductor_list
    

# monthwise_salary,section_wise_inflow,transactions_deductor=itr_display1(r"D:\User DATA\Documents\A3\KPI\ITR\26Aug2020AGUPD2668P_2018-19.xlsx")
    