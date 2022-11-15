# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 18:31:35 2020

@author: Vaibhav
"""

#THE FOLLOWING CODE CREATES THE ITR DISPLAY FOR TABLE3,4,5

import pandas as pd
from babel.numbers import format_currency
# import pymysql

def itr_display1(part_a, part_b):
    
    #Connect with DB
    # conn = pymysql.connect(host = '10.20.30.40', port = 3306, user = 'ABC', passwd = 'PAS8765', charset = 'utf8', db='bureau')
    
    # #Select the required columns and table from DB
    # sql1 = "SELECT e.DEAL_ID AS deal_id, e.CUSTOMER_ID AS cust_id FROM cibil_ref_dtl e  where e.DEAL_ID = "1234567" and e.CUSTOMER_ID ="12345678""
    
    # deal_details = pd.read_sql(sql1, conn)
    
    #READ THE INPUT FILES
    
    # part_a = pd.read_excel(part_a_path,sheet_name = "Part A")
    # part_b = pd.read_excel(part_a_path,sheet_name = "Part B")
    #deal_details = pd.read_csv(deal)
    # deal_id = "XXXX777"
    # customer_id = "4000700"
    # pan = part_a['pan'][0]
    temp = part_a['assessment_year'][0]
    
    
    
    #CODE FOR TABLE 3
    
    
    
    part_a_sec2 = part_a[["assessment_year","section_1",'amount_paid_credited','transaction_date']]
    part_b_sec2 = part_b[["assessment_year","section_1",'amount_paid_debited','transaction_date']]
    part_b_sec2.rename(columns = {'amount_paid_debited':'amount_paid_credited'}, inplace = True)
    Part_a_b_sec2 = pd.concat([part_a_sec2, part_b_sec2]).reset_index(drop = True) 
    
    
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
            return("Income from Commission")
        elif x in list6:
            return("Income from Contracting")
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
    
    Part_a_b_sec2["sec1_cat"]=Part_a_b_sec2.section_1.apply(func1)
        
    salary=Part_a_b_sec2[Part_a_b_sec2.sec1_cat == 'Salary']
    
    non_salary=Part_a_b_sec2[Part_a_b_sec2.sec1_cat != 'Salary']
    
        
    transaction_month=[]
    
    for i in range(len(Part_a_b_sec2)):
        transaction_month.append(Part_a_b_sec2['transaction_date'][i][3:6])
    Part_a_b_sec2["transaction_month"] = transaction_month 
    
    transaction_month=[]
    for i in range(len(salary)):
        transaction_month.append(salary['transaction_date'][i][3:6])
    salary["transaction_month"] = transaction_month
    
    transaction_month=[]
    for i in range(len(non_salary)):
        transaction_month.append(non_salary['transaction_date'][i][3:6])
    non_salary["transaction_month"] = transaction_month  
    
    Jan_Income=[]
    Feb_Income=[]
    Mar_Income=[]
    Apr_Income=[]
    May_Income=[]
    Jun_Income=[]
    Jul_Income=[]
    Aug_Income=[]
    Sep_Income=[]
    Oct_Income=[]
    Nov_Income=[]
    Dec_Income=[]
    
    for i in range(len(salary)):
            if salary['transaction_month'][i] == 'Jan':
                Jan_Income.append(salary['amount_paid_credited'][i])
                
            else:
                Jan_Income.append(0)
                
            if salary['transaction_month'][i] == 'Feb':
                Feb_Income.append(salary['amount_paid_credited'][i])
                
            else:
                Feb_Income.append(0)
                
            if salary['transaction_month'][i] == 'Mar':
                Mar_Income.append(salary['amount_paid_credited'][i])
               
            else:
                Mar_Income.append(0)
                
            if salary['transaction_month'][i] == 'Apr':
                Apr_Income.append(salary['amount_paid_credited'][i])
                
            else:
                Apr_Income.append(0)
                
            if salary['transaction_month'][i] == 'May':
                May_Income.append(salary['amount_paid_credited'][i])
                
            else:
                May_Income.append(0)
                
            if salary['transaction_month'][i] == 'Jun':
                Jun_Income.append(salary['amount_paid_credited'][i])
                
            else:
                Jun_Income.append(0)
                
            if salary['transaction_month'][i] == 'Jul':
                Jul_Income.append(salary['amount_paid_credited'][i])
                
            else:
                Jul_Income.append(0)
                
            if salary['transaction_month'][i] == 'Aug':
                Aug_Income.append(salary['amount_paid_credited'][i])
                
            else:
                Aug_Income.append(0)
                
            if salary['transaction_month'][i] == 'Sep':
                Sep_Income.append(salary['amount_paid_credited'][i])
                
            else:
                Sep_Income.append(0)
                
            if salary['transaction_month'][i] == 'Oct':
                Oct_Income.append(salary['amount_paid_credited'][i])
                
            else:
                Oct_Income.append(0) 
                
            if salary['transaction_month'][i] == 'Nov':
                Nov_Income.append(salary['amount_paid_credited'][i])
                
            else:
                Nov_Income.append(0) 
                
            if salary['transaction_month'][i] == 'Dec':
                Dec_Income.append(salary['amount_paid_credited'][i])
                
            else:
                Dec_Income.append(0) 
    
    salary["April"] = Apr_Income 
    salary["May"] = May_Income
    salary["June"] = Jun_Income 
    salary["July"] = Jul_Income
    salary["August"] = Aug_Income 
    salary["September"] = Sep_Income
    salary["October"] = Oct_Income 
    salary["November"] = Nov_Income
    salary["December"] = Dec_Income 
    salary["January"] = Jan_Income
    salary["February"] = Feb_Income 
    salary["March"] = Mar_Income
    
    income_by_month_sal = salary.groupby(['assessment_year'])[["April","May","June",
                                                                      "July","August","September",
                                                                      "October","November","December",
                                                                      "January","February","March"
                                                                     ]].agg('sum').reset_index()
    
    
    
    income_by_month_sal = income_by_month_sal[["April","May","June","July","August","September","October","November",
                                                       "December","January","February","March"]]
    
    Jan_Income=[]
    Feb_Income=[]
    Mar_Income=[]
    Apr_Income=[]
    May_Income=[]
    Jun_Income=[]
    Jul_Income=[]
    Aug_Income=[]
    Sep_Income=[]
    Oct_Income=[]
    Nov_Income=[]
    Dec_Income=[]
    
    for i in range(len(non_salary)):
            if non_salary['transaction_month'][i] == 'Jan':
                Jan_Income.append(non_salary['amount_paid_credited'][i])
                
            else:
                Jan_Income.append(0)
                
            if non_salary['transaction_month'][i] == 'Feb':
                Feb_Income.append(non_salary['amount_paid_credited'][i])
                
            else:
                Feb_Income.append(0)
                
            if non_salary['transaction_month'][i] == 'Mar':
                Mar_Income.append(non_salary['amount_paid_credited'][i])
               
            else:
                Mar_Income.append(0)
                
            if non_salary['transaction_month'][i] == 'Apr':
                Apr_Income.append(non_salary['amount_paid_credited'][i])
                
            else:
                Apr_Income.append(0)
                
            if non_salary['transaction_month'][i] == 'May':
                May_Income.append(non_salary['amount_paid_credited'][i])
                
            else:
                May_Income.append(0)
                
            if non_salary['transaction_month'][i] == 'Jun':
                Jun_Income.append(non_salary['amount_paid_credited'][i])
                
            else:
                Jun_Income.append(0)
                
            if non_salary['transaction_month'][i] == 'Jul':
                Jul_Income.append(non_salary['amount_paid_credited'][i])
                
            else:
                Jul_Income.append(0)
                
            if non_salary['transaction_month'][i] == 'Aug':
                Aug_Income.append(non_salary['amount_paid_credited'][i])
                
            else:
                Aug_Income.append(0)
                
            if non_salary['transaction_month'][i] == 'Sep':
                Sep_Income.append(non_salary['amount_paid_credited'][i])
                
            else:
                Sep_Income.append(0)
                
            if non_salary['transaction_month'][i] == 'Oct':
                Oct_Income.append(non_salary['amount_paid_credited'][i])
                
            else:
                Oct_Income.append(0) 
                
            if non_salary['transaction_month'][i] == 'Nov':
                Nov_Income.append(non_salary['amount_paid_credited'][i])
                
            else:
                Nov_Income.append(0) 
                
            if non_salary['transaction_month'][i] == 'Dec':
                Dec_Income.append(non_salary['amount_paid_credited'][i])
                
            else:
                Dec_Income.append(0) 
    
    non_salary["April"] = Apr_Income 
    non_salary["May"] = May_Income
    non_salary["June"] = Jun_Income 
    non_salary["July"] = Jul_Income
    non_salary["August"] = Aug_Income 
    non_salary["September"] = Sep_Income
    non_salary["October"] = Oct_Income 
    non_salary["November"] = Nov_Income
    non_salary["December"] = Dec_Income 
    non_salary["January"] = Jan_Income
    non_salary["February"] = Feb_Income 
    non_salary["March"] = Mar_Income
    
    non_salary.amount_paid_credited = non_salary.amount_paid_credited.astype(float)
    non_salary.April = non_salary.April.astype(float)
    non_salary.May = non_salary.May.astype(float)
    non_salary.June = non_salary.June.astype(float)
    non_salary.July = non_salary.July.astype(float)
    non_salary.August = non_salary.August.astype(float)
    non_salary.September = non_salary.September.astype(float)
    non_salary.October = non_salary.October.astype(float)
    non_salary.November = non_salary.November.astype(float)
    non_salary.December = non_salary.December.astype(float)
    non_salary.January = non_salary.January.astype(float)
    non_salary.February = non_salary.February.astype(float)
    non_salary.March = non_salary.March.astype(float)
    income_by_month_non_sal = non_salary.groupby(['assessment_year'])[["April","May","June",
                                                                      "July","August","September",
                                                                      "October","November","December",
                                                                      "January","February","March"
                                                                     ]].agg('sum').reset_index()
    
    
    
    income_by_month_non_sal = income_by_month_non_sal[["April","May","June","July","August","September","October","November",
                                                       "December","January","February","March"]]
    
    Jan_Income=[]
    Feb_Income=[]
    Mar_Income=[]
    Apr_Income=[]
    May_Income=[]
    Jun_Income=[]
    Jul_Income=[]
    Aug_Income=[]
    Sep_Income=[]
    Oct_Income=[]
    Nov_Income=[]
    Dec_Income=[]
    Jan_Trans_Count=[]
    Feb_Trans_Count=[]
    Mar_Trans_Count=[]
    Apr_Trans_Count=[]
    May_Trans_Count=[]
    Jun_Trans_Count=[]
    Jul_Trans_Count=[]
    Aug_Trans_Count=[]
    Sep_Trans_Count=[]
    Oct_Trans_Count=[]
    Nov_Trans_Count=[]
    Dec_Trans_Count=[]
    
    for i in range(len(Part_a_b_sec2)):
            if Part_a_b_sec2['transaction_month'][i] == 'Jan':
                Jan_Income.append(Part_a_b_sec2['amount_paid_credited'][i])
                Jan_Trans_Count.append(1)
            else:
                Jan_Income.append(0)
                Jan_Trans_Count.append(0)
            if Part_a_b_sec2['transaction_month'][i] == 'Feb':
                Feb_Income.append(Part_a_b_sec2['amount_paid_credited'][i])
                Feb_Trans_Count.append(1)
            else:
                Feb_Income.append(0)
                Feb_Trans_Count.append(0)
            if Part_a_b_sec2['transaction_month'][i] == 'Mar':
                Mar_Income.append(Part_a_b_sec2['amount_paid_credited'][i])
                Mar_Trans_Count.append(1)
            else:
                Mar_Income.append(0)
                Mar_Trans_Count.append(0)
            if Part_a_b_sec2['transaction_month'][i] == 'Apr':
                Apr_Income.append(Part_a_b_sec2['amount_paid_credited'][i])
                Apr_Trans_Count.append(1)
            else:
                Apr_Income.append(0)
                Apr_Trans_Count.append(0)
            if Part_a_b_sec2['transaction_month'][i] == 'May':
                May_Income.append(Part_a_b_sec2['amount_paid_credited'][i])
                May_Trans_Count.append(1)
            else:
                May_Income.append(0)
                May_Trans_Count.append(0)
            if Part_a_b_sec2['transaction_month'][i] == 'Jun':
                Jun_Income.append(Part_a_b_sec2['amount_paid_credited'][i])
                Jun_Trans_Count.append(1)
            else:
                Jun_Income.append(0)
                Jun_Trans_Count.append(0)
            if Part_a_b_sec2['transaction_month'][i] == 'Jul':
                Jul_Income.append(Part_a_b_sec2['amount_paid_credited'][i])
                Jul_Trans_Count.append(1)
            else:
                Jul_Income.append(0)
                Jul_Trans_Count.append(0)
            if Part_a_b_sec2['transaction_month'][i] == 'Aug':
                Aug_Income.append(Part_a_b_sec2['amount_paid_credited'][i])
                Aug_Trans_Count.append(1)
            else:
                Aug_Income.append(0)
                Aug_Trans_Count.append(0)
            if Part_a_b_sec2['transaction_month'][i] == 'Sep':
                Sep_Income.append(Part_a_b_sec2['amount_paid_credited'][i])
                Sep_Trans_Count.append(1)
            else:
                Sep_Income.append(0)
                Sep_Trans_Count.append(0)
            if Part_a_b_sec2['transaction_month'][i] == 'Oct':
                Oct_Income.append(Part_a_b_sec2['amount_paid_credited'][i])
                Oct_Trans_Count.append(1)
            else:
                Oct_Income.append(0) 
                Oct_Trans_Count.append(0)
            if Part_a_b_sec2['transaction_month'][i] == 'Nov':
                Nov_Income.append(Part_a_b_sec2['amount_paid_credited'][i])
                Nov_Trans_Count.append(1)
            else:
                Nov_Income.append(0) 
                Nov_Trans_Count.append(0)
            if Part_a_b_sec2['transaction_month'][i] == 'Dec':
                Dec_Income.append(Part_a_b_sec2['amount_paid_credited'][i])
                Dec_Trans_Count.append(1)
            else:
                Dec_Income.append(0) 
                Dec_Trans_Count.append(0)             
                
                
    
    Part_a_b_sec2["Apr_Income"] = Apr_Income 
    Part_a_b_sec2["May_Income"] = May_Income
    Part_a_b_sec2["Jun_Income"] = Jun_Income 
    Part_a_b_sec2["Jul_Income"] = Jul_Income
    Part_a_b_sec2["Aug_Income"] = Aug_Income 
    Part_a_b_sec2["Sep_Income"] = Sep_Income
    Part_a_b_sec2["Oct_Income"] = Oct_Income 
    Part_a_b_sec2["Nov_Income"] = Nov_Income
    Part_a_b_sec2["Dec_Income"] = Dec_Income 
    Part_a_b_sec2["Jan_Income"] = Jan_Income
    Part_a_b_sec2["Feb_Income"] = Feb_Income 
    Part_a_b_sec2["Mar_Income"] = Mar_Income
    Part_a_b_sec2["Apr_Trans_Count"] = Apr_Trans_Count 
    Part_a_b_sec2["May_Trans_Count"] = May_Trans_Count
    Part_a_b_sec2["Jun_Trans_Count"] = Jun_Trans_Count 
    Part_a_b_sec2["Jul_Trans_Count"] = Jul_Trans_Count
    Part_a_b_sec2["Aug_Trans_Count"] = Aug_Trans_Count 
    Part_a_b_sec2["Sep_Trans_Count"] = Sep_Trans_Count
    Part_a_b_sec2["Oct_Trans_Count"] = Oct_Trans_Count 
    Part_a_b_sec2["Nov_Trans_Count"] = Nov_Trans_Count
    Part_a_b_sec2["Dec_Trans_Count"] = Dec_Trans_Count
    Part_a_b_sec2["Jan_Trans_Count"] = Jan_Trans_Count
    Part_a_b_sec2["Feb_Trans_Count"] = Feb_Trans_Count 
    Part_a_b_sec2["Mar_Trans_Count"] = Mar_Trans_Count 
    
    Part_a_b_sec2.amount_paid_credited = Part_a_b_sec2.amount_paid_credited.astype(float)
    Part_a_b_sec2.Apr_Income = Part_a_b_sec2.Apr_Income.astype(float)
    Part_a_b_sec2.May_Income = Part_a_b_sec2.May_Income.astype(float)
    Part_a_b_sec2.Jun_Income = Part_a_b_sec2.Jun_Income.astype(float)
    Part_a_b_sec2.Jul_Income = Part_a_b_sec2.Jul_Income.astype(float)
    Part_a_b_sec2.Aug_Income = Part_a_b_sec2.Aug_Income.astype(float)
    Part_a_b_sec2.Sep_Income = Part_a_b_sec2.Sep_Income.astype(float)
    Part_a_b_sec2.Oct_Income = Part_a_b_sec2.Oct_Income.astype(float)
    Part_a_b_sec2.Nov_Income = Part_a_b_sec2.Nov_Income.astype(float)
    Part_a_b_sec2.Dec_Income = Part_a_b_sec2.Dec_Income.astype(float)
    Part_a_b_sec2.Jan_Income = Part_a_b_sec2.Jan_Income.astype(float)
    Part_a_b_sec2.Feb_Income = Part_a_b_sec2.Feb_Income.astype(float)
    Part_a_b_sec2.Mar_Income = Part_a_b_sec2.Mar_Income.astype(float)
    income_trans_by_month = Part_a_b_sec2.groupby(['assessment_year'])[["Apr_Income","May_Income","Jun_Income",
                                                                      "Jul_Income","Aug_Income","Sep_Income",
                                                                      "Oct_Income","Nov_Income","Dec_Income",
                                                                      "Jan_Income","Feb_Income","Mar_Income",
                                                                      "Apr_Trans_Count","May_Trans_Count","Jun_Trans_Count",
                                                                      "Jul_Trans_Count","Aug_Trans_Count","Sep_Trans_Count",
                                                                      "Oct_Trans_Count","Nov_Trans_Count","Dec_Trans_Count",
                                                                      'Jan_Trans_Count',"Feb_Trans_Count","Mar_Trans_Count"]].agg('sum').reset_index()
    
    tot_income_by_mon = income_trans_by_month[["Apr_Income","May_Income","Jun_Income","Jul_Income","Aug_Income","Sep_Income",
                                               "Oct_Income","Nov_Income","Dec_Income","Jan_Income","Feb_Income","Mar_Income"]]
    
    tot_income_by_mon.columns=["April","May","June","July","August","September",
                              "October","November","December","January","February","March"]
      
    tot_trans_by_mon=income_trans_by_month[["Apr_Trans_Count","May_Trans_Count","Jun_Trans_Count","Jul_Trans_Count","Aug_Trans_Count","Sep_Trans_Count",
                                          "Oct_Trans_Count","Nov_Trans_Count","Dec_Trans_Count",'Jan_Trans_Count',"Feb_Trans_Count","Mar_Trans_Count"]]
    
    tot_trans_by_mon.columns=["April","May","June","July","August","September",
                              "October","November","December","January","February","March"]
    
    
    dict = {'April':[0], 'May':[0], 'June':[0], 'July':[0], 'August':[0], 'September':[0], 
            'October':[0], 'November':[0], 'December':[0], 'January':[0], 'February':[0], 'March':[0], 
            }
    temp1 = pd.DataFrame(dict)
    
    if len(income_by_month_sal)==0:
        income_by_month_sal=pd.concat([income_by_month_sal, temp1]).reset_index(drop = True)
        
    if len(income_by_month_non_sal)==0:
        income_by_month_non_sal=pd.concat([income_by_month_non_sal, temp1]).reset_index(drop = True)
    
    if len(tot_income_by_mon)==0:
        tot_income_by_mon=pd.concat([tot_income_by_mon, temp1]).reset_index(drop = True)
    
    if len(tot_trans_by_mon)==0:
        tot_trans_by_mon=pd.concat([tot_trans_by_mon, temp1]).reset_index(drop = True)
    
    tot_trans_by_mon['measures'] = 'Number of credits'
    income_by_month_sal['measures'] = 'Salary'
    income_by_month_non_sal['measures'] = 'Non Salary'
    tot_income_by_mon['measures'] = 'Total Income'
    
    
    
    income_by_month_sal=pd.concat([income_by_month_sal, income_by_month_non_sal]).reset_index(drop = True)
    income_by_month_sal=pd.concat([income_by_month_sal, tot_income_by_mon]).reset_index(drop = True)
    income_by_month_sal=pd.concat([income_by_month_sal, tot_trans_by_mon]).reset_index(drop = True)
    
    
    import copy
    income_by_month_sal["assessment_year"] = copy.deepcopy(temp)
    income_by_month_sal["Source"] = "Form26AS"
    income_by_month_sal=income_by_month_sal.set_index(["assessment_year",'measures'],drop=True)

    table3 = income_by_month_sal[["April","May","June","July","August","September",
                              "October","November","December","January","February","March","Source"]]
    
    # def currency(x):
    #     return(format_currency(x, 'INR', locale='en_IN'))



    #temp1["Total Deductions"] = temp1["Total Deductions"].astype(float)
    for i in range(len(table3)):
        for j in range(len(table3.columns)):
            if type(table3.iloc[i,j])== str:
                pass
            else:
                #df1.iloc[i,j]=float(df1.iloc[i,j])
                table3.iloc[i,j]= table3.iloc[i,j] # currency(table3.iloc[i,j])
                
    #Export the data
    # table3.to_csv("{}\\Table3\\{}_{}_{}_Table3.csv".format(out_path,deal_id,customer_id,temp),index=True)
    

    
    
    #CODE FOR TABLE 4
    
    
    
    #part_a.drop(part_a.columns[[0, 1]], axis = 1, inplace = True)
    part_a_sec = part_a[["assessment_year","section_1",'amount_paid_credited']]
    part_b_sec = part_b[["assessment_year","section_1",'amount_paid_debited']]
    part_b_sec.rename(columns = {'amount_paid_debited':'amount_paid_credited'}, inplace = True)
    Part_a_b_sec = pd.concat([part_a_sec, part_b_sec]).reset_index(drop = True) 
     
    
    
    Part_a_b_sec["sec1_cat"]=Part_a_b_sec.section_1.apply(func1)
    
    #a=Part_a_b_sec.groupby(['assessment_year','sec1_cat'])[["amount_paid_credited"]].agg('sum').reset_index()
    
    Sec_194K=[]
    Betting=[]
    Collection_at_source = []
    Income_from_abroad = []
    Income_from_Commission=[]
    Income_from_Contracting=[]
    Income_from_investment = []
    Income_from_tech_prof_services=[]
    Orignal_investment_principal_withdrawal=[]
    Rent=[]
    Salary = []
    Sale_of_property=[]
    
    
    for i in range(len(Part_a_b_sec)):
        if Part_a_b_sec['sec1_cat'][i] == "194K":
            Sec_194K.append(Part_a_b_sec["amount_paid_credited"][i])
        else :
            Sec_194K.append(0)
        if Part_a_b_sec['sec1_cat'][i] == "Betting":
            Betting.append(Part_a_b_sec["amount_paid_credited"][i])
        else :
            Betting.append(0)
        if Part_a_b_sec['sec1_cat'][i] == "Collection at source":
            Collection_at_source.append(Part_a_b_sec["amount_paid_credited"][i])
        else :
            Collection_at_source.append(0)
        if Part_a_b_sec['sec1_cat'][i] == "Income from abroad":
            Income_from_abroad.append(Part_a_b_sec["amount_paid_credited"][i])
        else :
            Income_from_abroad.append(0)
        if Part_a_b_sec['sec1_cat'][i] == "Income from Commission":
            Income_from_Commission.append(Part_a_b_sec["amount_paid_credited"][i])
        else :
            Income_from_Commission.append(0)
        if Part_a_b_sec['sec1_cat'][i] == "Income from Contracting":
            Income_from_Contracting.append(Part_a_b_sec["amount_paid_credited"][i])
        else :
            Income_from_Contracting.append(0)
        if Part_a_b_sec['sec1_cat'][i] == "Income from investment":
            Income_from_investment.append(Part_a_b_sec["amount_paid_credited"][i])
        else :
            Income_from_investment.append(0)
        if Part_a_b_sec['sec1_cat'][i] == "Income from tech. professional services":
            Income_from_tech_prof_services.append(Part_a_b_sec["amount_paid_credited"][i])
        else :
            Income_from_tech_prof_services.append(0)
        if Part_a_b_sec['sec1_cat'][i] == "Orignal investment(principal) withdrawal":
            Orignal_investment_principal_withdrawal.append(Part_a_b_sec["amount_paid_credited"][i])
        else :
            Orignal_investment_principal_withdrawal.append(0)
        if Part_a_b_sec['sec1_cat'][i] == "Rent":
            Rent.append(Part_a_b_sec["amount_paid_credited"][i])
        else :
            Rent.append(0)
        if Part_a_b_sec['sec1_cat'][i] == "Salary":
            Salary.append(Part_a_b_sec["amount_paid_credited"][i])
        else :
            Salary.append(0)
        if Part_a_b_sec['sec1_cat'][i] == "Sale of property":
            Sale_of_property.append(Part_a_b_sec["amount_paid_credited"][i])
        else :
            Sale_of_property.append(0)
            
    
    Part_a_b_sec['194K'] = Sec_194K
    Part_a_b_sec['Betting'] = Betting
    Part_a_b_sec['Collection at source'] = Collection_at_source
    Part_a_b_sec['Income from abroad'] = Income_from_abroad
    Part_a_b_sec['Income from Commission'] = Income_from_Commission
    Part_a_b_sec['Income from Contracting'] = Income_from_Contracting
    Part_a_b_sec['Income from investment'] = Income_from_investment
    Part_a_b_sec['Income from tech prof services'] = Income_from_tech_prof_services
    Part_a_b_sec['Orignal investment principal withdrawal'] = Orignal_investment_principal_withdrawal
    Part_a_b_sec['Rent'] = Rent
    Part_a_b_sec['Salary'] = Salary
    Part_a_b_sec['Sale of property'] = Sale_of_property
    
    
    part_a_b_con = Part_a_b_sec.groupby(['assessment_year'])[['194K','Betting',
                                                              'Collection at source','Income from abroad','Income from Commission',
                                                              'Income from Contracting',
                                                              'Income from investment','Income from tech prof services',
                                                              'Orignal investment principal withdrawal',
                                                              'Rent','Salary','Sale of property'
                                                              ]].agg('sum').reset_index()
    
    
    table4 = part_a_b_con.transpose()
    table4 = table4.reset_index(drop = False)
    table4.columns = ['Section','Amount']
    
     
    table4.columns = ['Section',temp]
    
    table4=table4[table4.Section != 'assessment_year']
    
    for i in range(len(table4)):
        for j in range(len(table4.columns)):
            if type(table4.iloc[i,j])== str:
                pass
            else:
                #df1.iloc[i,j]=float(df1.iloc[i,j])
                table4.iloc[i,j]= table4.iloc[i,j] # currency(table4.iloc[i,j])
    
    
    #Export the data
    # table4.to_csv("{}\\Table4\\{}_{}_{}_Table4.csv".format(out_path,deal_id,customer_id,temp),index=False)
    
    
    
    #CODE FOR TABLE 5
    
    
    
    part_a_sec1 = part_a[["assessment_year","name_of_deductor",'total_amount_paid_credited']]
    
    part_a_deduc_amount = part_a_sec1.drop_duplicates()
    part_a_deduc_amount= part_a_deduc_amount[["name_of_deductor",'total_amount_paid_credited']]
    part_a_deduc_amount.columns = ['name_of_deductor','total_amount']
    part_a_deduc_count = part_a_sec1.groupby(['name_of_deductor'])[["total_amount_paid_credited"]].agg('count').reset_index()
    part_a_deduc_count.columns = ['name_of_deductor','number_of_transactions']
    table5 = pd.merge(part_a_deduc_count, part_a_deduc_amount, how='left', on=['name_of_deductor'])
    
    
    table5["assessment_year"]=temp
    table5=table5.set_index(["assessment_year"],drop=True)
    
    for i in range(len(table5)):
        for j in range(len(table5.columns)):
            if type(table5.iloc[i,j])== str:
                pass
            else:
                #df1.iloc[i,j]=float(df1.iloc[i,j])
                table5.iloc[i,j]= table5.iloc[i,j] # currency(table5.iloc[i,j])
    
    
    #Export the data
    # table5.to_csv("{}\\Table5\\{}_{}_{}_Table5.csv".format(out_path,deal_id,customer_id,temp),index=True)
    return table3, table4, table5
    
#Provide the input and output path     
# itr_display1(r"W:\kavyant\A3-KIT\knowlver\itr analysis table\AATPS8226K_2019-20.xlsx",
#              r"W:\kavyant\A3-KIT\knowlver\itr analysis table\output")
