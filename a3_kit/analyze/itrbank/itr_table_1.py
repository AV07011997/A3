# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:31:25 2020

@author: Vaibhav
"""

#THE FOLLOWING CODE CREATES THE ITR DISPLAY FOR TABLE1

import pandas as pd
import numpy as np
import math
import pymysql

def itr_display1(form_26_a, form_16_b, form_26_g, itr_v):
    
    form16_b = form_16_b
    
    #Read itr v
    # itr_v = pd.read_csv(itr_v_path)
    itr_v = itr_v
    
    #Read form 16 part a
    # form26as_part_a = pd.read_excel(form26_as_path,sheet_name='Part A')

    form26as_part_a = form_26_a
    
    #Read form 16 part g
    # form26as_part_g = pd.read_excel(form26_as_path,sheet_name='Part G')
    form26as_part_g = form_26_g
    form16_b=form16_b.replace(np.nan,0)
    
    #Identify the required columnsfrom form 16
    
    try:
        deduc_80c = form16_b["ductn_in_rspct_of_lfe_inc_prmia_cntrbn_2_pf_undr_sec_80c_gr_amnt"]
            

        oth_7a = form16_b["incm_or_admsble_los_frm_house_prprty_rprtd_by_empyee_ofr_for_tds"]
            
        
        oth_7b = form16_b["income_under_the_head_other_sources_offered_for_tds"]
            
        
        deduc_80ccc = form16_b["ductn_in_rspct_of_ctrbtn_2_crtn_pnsn_fnds_undr_sec_80ccc_gr_amnt"]
            
        
        taxable_income = form16_b["total_taxable_income_9_minus_11"]
            
        
        deduc_80d = form16_b["dtn_in_rsp_of_hlt_insrnc_premia_ndr_sc_80d_gr_amt"]
            
        
        hra = form16_b["house_rent_allowance_under_section_10_13a"]

        deduc_80ee = 'variable not found in database'
    except:
        pass
    
    #Identify the required columnsfrom itr v        
    
        
    gross_income = itr_v["gross_total_income"]
    avg_mon_gr_inc = float(gross_income)/12
        
    total_deduc = itr_v["deductions_under_chapter_vi_a"]
    try:
            
        other_deduc = float(total_deduc)-float(deduc_80c)-float(deduc_80ccc)-float(deduc_80d)
    
        other_income_sec192_2B = float(oth_7a)-float(oth_7b)
    except:
        pass
    
    #Calculate the rent income
    try:
        rent_part=form26as_part_a[form26as_part_a.section_1 == '194I']
        rent = 0
        for i  in range(len(rent_part)):
            rent = rent + rent_part["amount_paid_credited"][i]
        try:
            temp = form26as_part_a['assessment_year'][0]
        except:
            pass
    #Identify the default if any
        if len(form26as_part_g) > 0:
            def_found = "Yes"
        else:
            def_found = "No"
    
    #Create dummy dataset
        dict1 = {'dummy':["dummy"]}
    
        temp1 = pd.DataFrame(dict1)
    
    
        temp1['Assessment_Year']= temp
        temp1['Gross_Income']= gross_income
        temp1['Average_Monthly_Gross_Income']= avg_mon_gr_inc
        temp1['Taxable_Income']= taxable_income
        temp1['HRA']= hra
        temp1['Rent_Income']= rent
        temp1['Tax_Default_Found']= def_found
        temp1['80C']= deduc_80c
        temp1['80CCC']= deduc_80ccc
        temp1['80C']= deduc_80c
        temp1['80D']= deduc_80d
        temp1['80EE'] = deduc_80ee
        temp1['Other_Income_Under_Sec_192_2B']= other_income_sec192_2B
        temp1['Other_Deductions']= other_deduc
        temp1['Total_Deductions']= total_deduc
        temp1=temp1.drop(['dummy'], axis=1)
    
        temp1=temp1.set_index(["Assessment_Year"],drop=False)
        temp1["Total_Deductions"] = temp1["Total_Deductions"].astype(float)

        temp =temp1.transpose()
    except:
        temp1 = {'Gross_Income':[gross_income],'Total_Deductions':[total_deduc] }
        temp1 = pd.DataFrame(temp1)
    return temp1
 