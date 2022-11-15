#THE FOLLOWING CODE CREATES THE ITR DISPLAY FOR TABLE1

import pandas as pd
import numpy as np
import math
from babel.numbers import format_currency


def itr_display5(itrv, form16_part_b, form26as_part_a, form26as_part_g):    
    #Read form 16 part b
    # form16_b = pd.read_excel(form_16_path,sheet_name='Part B')
    
    #Read itr v
    # itr_v = pd.read_csv(itr_v_path)
    
    #Read form 16 part a
    # form26as_part_a = pd.read_excel(form26_as_path,sheet_name='Part A')
    
    #Read form 16 part g
    # form26as_part_g = pd.read_excel(form26_as_path,sheet_name='Part G')
    # form16_b=form16_b.replace(np.nan,0)
    
    #Identify the required columnsfrom form 16
    # for i in range(len(form16_b)):
    #     if form16_b['Parameters'][i] == "10a. Deduction in respect of life insurance premia, contributions to provident fund etc. under section 80C - Gross amount":
    #         deduc_80c = form16_b['Information'][i]
            
    #     if form16_b['Parameters'][i] == "7a. Income (or admissible loss) from house property reported by employee offered for TDS":
    #         oth_7a = form16_b['Information'][i]
            
    #     if form16_b['Parameters'][i] == "7b. Income under the head Other Sources offered for TDS":
    #         oth_7b = form16_b['Information'][i]
            
    #     if form16_b['Parameters'][i]=="10b. Deduction in respect of contribution to certain pension funds under section 80CCC - Gross amount":
    #         deduc_80ccc = form16_b['Information'][i]
            
    #     if form16_b['Parameters'][i]=="12. Total taxable income (9-11)":
    #         taxable_income = form16_b['Information'][i]
            
    #     if form16_b['Parameters'][i]=="10g. Deduction in respect of health insurance premia under section 80D - Gross amount":
    #         deduc_80d = form16_b['Information'][i]
            
    #     if form16_b['Parameters'][i]=="2e. House rent allowance under section 10(13A)":
    #         hra = form16_b['Information'][i]
    deduc_80c = form16_part_b[0]
    oth_7a = form16_part_b[1]
    oth_7b = form16_part_b[2]
    deduc_80ccc = form16_part_b[3]
    taxable_income = form16_part_b[4]
    deduc_80d = form16_part_b[5]
    hra = form16_part_b[6]

    #Identify the required columnsfrom itr v        
    # for i in range(len(itr_v)):
    #     if itr_v['Parameters'][i] == "Gross Total Income":
    #         gross_income = itr_v['Information'][i]
    #         avg_mon_gr_inc = float(gross_income)/12
    #     if itr_v['Parameters'][i] == "Deductions under Chapter-VI-A":
    #         total_deduc = itr_v['Information'][i]
    gross_income = itrv[0]
    avg_mon_gr_inc = float(gross_income)/12
    total_deduc = itrv[1]
            
    other_deduc = float(total_deduc)-float(deduc_80c)-float(deduc_80ccc)-float(deduc_80d)
    
    other_income_sec192_2B = float(oth_7a)-float(oth_7b)
    
    #Calculate the rent income
    rent_part=form26as_part_a[form26as_part_a.section_1 == '194I']
    rent = 0
    for i  in range(len(rent_part)):
        rent = rent + rent_part["amount_paid_credited"][i]
        
    temp = form26as_part_a['assessment_year'][0]
    
    #Identify the default if any
    if len(form26as_part_g) > 0:
        def_found = "Yes"
    else:
        def_found = "No"
    
    #Create dummy dataset
    dict1 = {'dummy':["dummy"]}
    
    temp1 = pd.DataFrame(dict1)
    
    
    temp1['assessment_year']= temp
    temp1['gross_income']= gross_income
    temp1['average_monthly_gross_income']= avg_mon_gr_inc
    temp1['taxable_income']= taxable_income
    temp1['hra']= hra
    temp1['rent_income']= rent
    temp1['tax_default_found']= def_found
    temp1['ccc80']= deduc_80ccc
    temp1['c80']= deduc_80c
    temp1['d80']= deduc_80d
    temp1['other_income_under_sec_192_2b']= other_income_sec192_2B
    temp1['other_deductions']= other_deduc
    temp1['total_deductions']= total_deduc
    temp1=temp1.drop(['dummy'], axis=1)
    
    # temp1=temp1.set_index(["assessment_year"],drop=True)
    
    #deal_details = pd.read_csv(deal)
    # deal_id = "XXXX777"
    # customer_id = "4000700"
    # pan = form26as_part_a['pan'][0]
    
    #Set the currency symbol for amount columns
    # def currency(x):
    #     return(format_currency(x, 'INR', locale='en_IN'))


    temp1["total_deductions"] = temp1["total_deductions"].astype(float)
    # for i in range(len(temp1)):
    #     for j in range(len(temp1.columns)):
    #         if type(temp1.iloc[i,j])== str:
    #             pass
    #         else:
    #             #df1.iloc[i,j]=float(df1.iloc[i,j])
    #             temp1.iloc[i,j]= currency(temp1.iloc[i,j])
    
    #Export the data
    # temp1.to_csv("{}\\Table1\\{}_{}_{}_Table1.csv".format(out_path,deal_id,customer_id,temp),index=True)
    return temp1
    