from pandas import isna, DataFrame
from tabula import read_pdf
from re import findall, finditer, search
from datetime import datetime as dt
from os import path
from time import time


def get_itrv_data(pdf_path):
    start = time()
    file_name=pdf_path.split("\\")[-1][:-4]
    total_income1 = 'nan'
    
    # reading only assessment year part
    tables = read_pdf(pdf_path,pages='1', area=[17.7, 487.5, 82.5, 584.1],silent=True, pandas_options= {'header': None})
    #area=[17.7, 487.5, 82.5, 584.1]; [17.7, 487.5, 82.5, 584.1]
    if len(tables)==0:
        print("This is an image-based statement, hence, cannot be digitized here")
        return
    
    a = ''.join(findall(r'\d+', ''.join(tables[0][0].to_list())))
    if len(a) == 6:
        ass_year = str(a[:-2]+"-"+a[-2:])
    else:
        ass_year = '0'
    
    
    # Now reading other parts of pdf
    tables = read_pdf(pdf_path, pages='all',stream=True)
    # setting the header as first row wherever first row of table is taken as header by tabula
    for i in range(len(tables)) :
        tables[i].loc[max(tables[i].index)+1,:] = None
        tables[i] = tables[i].shift(1,axis=0)
        tables[i].iloc[0] = tables[i].columns
    
    
    # creating a Dict of Extracted data
    out_dict = {}
    
    for i in range(len(tables)) :
        if len(tables[i]) > 2 and len(tables[i].columns) > 2 :
            for j in range(len(tables[i])) :
                for k in range(len(tables[i].columns)) :
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k] == 'Name' :
                        name = tables[i].iloc[tables[i].iloc[j+1:,k].first_valid_index(),k]
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k] == 'PAN' :
                        pan_no = tables[i].iloc[tables[i].iloc[j+1:,k].first_valid_index(),k]
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k] == 'Town/City/District State Pin/ZipCode' :
                        city = tables[i].iloc[j+1,k][: tables[i].iloc[j+1,k].rfind(' ')]
                        state = tables[i].iloc[j+1,k][tables[i].iloc[j+1,k].rfind(' ')+1 :]
                        pincode = tables[i].iloc[j+2,k]
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k] == 'Town/City/District State' :
                        city = tables[i].iloc[j+1,k][: tables[i].iloc[j+1,k].rfind(' ')]
                        state = tables[i].iloc[j+1,k][tables[i].iloc[j+1,k].rfind(' ')+1 :]
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k] == 'Pin/ZipCode' :
                        pincode = tables[i].iloc[tables[i].iloc[j+1:,k].first_valid_index(),k]
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k] == 'Town/City/District' :
                        city = tables[i].iloc[j+1,k]
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k] == 'State Pin/ZipCode' :
                        state = tables[i].iloc[j+1,k]
                        pincode = tables[i].iloc[j+2,k]
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k] == 'State Pin/ZipCode Aadhaar Number/ Enrollment ID' :
                        temp1 = tables[i].iloc[tables[i].iloc[j+1:,k].first_valid_index(),k]
                        state = temp1[ :temp1.find(' ')]
                        pincode = temp1[temp1.find(' ')+1 : [m.start() for m in finditer(r" ",temp1)][1]]
                    
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k].find('Acknowledgement Number') != -1 :
                        try:
                            ackn_no = int(''.join(filter(str.isdigit, tables[i].iloc[j,k])))
                        except:
                            ackn_no = tables[i].iloc[j,k+1]
                            try:
                                if ackn_no.isdigit() == False:
                                    ackn_no = ackn_no[ : ackn_no.find(' ')]
                            except:
                                ackn_no = tables[i].iloc[j,k+2]
                                
                            
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k].find('ITR-') != -1 and tables[i].iloc[j,k][tables[i].iloc[j,k].find('ITR-')+4].isdigit() :
                        form_no = tables[i].iloc[j,k][tables[i].iloc[j,k].find('ITR-'): ]
                    if type(tables[i].iloc[j,k]) == str and (tables[i].iloc[j,k].find('Date(DD/MM/YYYY)') != -1 or tables[i].iloc[j,k].find('Date(DD-MM-YYYY)') != -1 or tables[i].iloc[j,k].find('Filed u/s') != -1) and tables[i].iloc[j,k]!='State Pin/ZipCode Filed u/s' :
                        itr_date = tables[i].iloc[tables[i].iloc[j+1:,k].first_valid_index(),k]
                        if itr_date.find('On or before') != -1:
                            break
                        if tables[i].iloc[j,k].find('-') != -1 :
                            itr_date = tables[i].iloc[j,k][tables[i].iloc[j,k].find(' ')+1: ]
                        if itr_date.find(' ') != -1 :
                            itr_date = itr_date[itr_date.find(' ')+1 : ]
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k].find('State')!=-1:
                        if not isna(tables[i].iloc[j+1,k]):
                            temp1=tables[i].iloc[j+1,k]
                        else:
                            temp1 = tables[i].iloc[j+2,k]
                        if temp1.find(' ')==-1:
                            state=temp1
                        else:
                            state = temp1[ :temp1.find(' ')]
                        temp2 = temp1[temp1.find(' ')+1:]
                        pincode = temp2[ :temp2.find(' ')]
                        itr_date = temp2[temp2.find(' ')+1 :]
                    if type(tables[i].iloc[j,k]) == str and search('(?i)gross total income',tables[i].iloc[j,k]) :
                        try:
                            gross_total_income = str(tables[i].loc[j, tables[i].iloc[j,k+1:].last_valid_index()])
                            if gross_total_income.find(' ') != -1 :
                                gross_total_income = gross_total_income[gross_total_income.find(' ')+1: ]
                        except:
                            gross_total_income = str(tables[i].iloc[j,k][tables[i].iloc[j,k].rfind(' ')+1: ])
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k].find('Deductions under Chapter-VI-A') != -1 :
                        try:
                            deductions = str(tables[i].loc[j, tables[i].iloc[j,k+1:].last_valid_index()])
                            if deductions.find(' ') != -1 :
                                deductions = deductions[deductions.find(' ')+1: ]
                        except:
                            deductions = str(tables[i].iloc[j,k][tables[i].iloc[j,k].rfind(' ')+1: ])
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k].find('Total Income') != -1 and tables[i].iloc[j,k].find('Gross') == -1 :
                        try:
                            total_income = str(tables[i].loc[j, tables[i].iloc[j,k+1:].last_valid_index()])
                            if total_income.find(' ') != -1 :
                                total_income = total_income[total_income.find(' ')+1: ]
                        except:
                            total_income = str(tables[i].iloc[j,k][tables[i].iloc[j,k].rfind(' ')+1: ])
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k].find('Deemed Total Income') != -1 :
                        try :
                            deemed_total_income = str(tables[i].loc[j, tables[i].iloc[j,k+1:].last_valid_index()])
                            if deemed_total_income.find(' ') != -1 :
                                deemed_total_income = deemed_total_income[deemed_total_income.find(' ')+1: ]
                        except:
                            deemed_total_income = str(tables[i].iloc[j,k][tables[i].iloc[j,k].rfind(' ')+1: ])
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k].find('Current Year loss, if any') != -1 :
                        try:
                            current_year_loss = str(tables[i].loc[j, tables[i].iloc[j,k+1:].last_valid_index()])
                        except:
                            current_year_loss = str(tables[i].iloc[j,k][tables[i].iloc[j,k].rfind(' ')+1: ])
                        if current_year_loss.find(' ') != -1 :
                            current_year_loss = current_year_loss[current_year_loss.find(' ')+1: ]
                    if type(tables[i].iloc[j,k]) == str and search('(?i)Net tax payable',tables[i].iloc[j,k]) :
                        try :
                            net_tax = str(tables[i].loc[j, tables[i].iloc[j,k+1:].last_valid_index()])
                            if net_tax.find(' ') != -1 :
                                net_tax = net_tax[net_tax.find(' ')+1: ]
                        except :
                            net_tax = str(tables[i].iloc[j,k][tables[i].iloc[j,k].rfind(' ')+1: ])
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k].find('Interest and Fee Payable') != -1 and tables[i].iloc[j,k].find('Total') == -1 :
                         try :
                             interest_and_fee = str(tables[i].loc[j, tables[i].iloc[j,k+1:].last_valid_index()])
                             if interest_and_fee.find(' ') != -1 :
                                 interest_and_fee = interest_and_fee[interest_and_fee.find(' ')+1: ]
                         except :
                             interest_and_fee = str(tables[i].iloc[j,k][tables[i].iloc[j,k].rfind(' ')+1: ])                    
                    if type(tables[i].iloc[j,k]) == str and search('(?i)Total tax, interest and Fee payable',tables[i].iloc[j,k]) :
                        try :
                            total_tax_and_interest = str(tables[i].loc[j, tables[i].iloc[j,k+1:].last_valid_index()])
                            if total_tax_and_interest.find(' ') != -1 :
                                total_tax_and_interest = total_tax_and_interest[total_tax_and_interest.find(' ')+1: ]
                        except :
                            total_tax_and_interest = str(tables[i].iloc[j,k][tables[i].iloc[j,k].rfind(' ')+1: ])                    
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k].find('Advance Tax') != -1 :
                        try :
                            advance_tax = str(tables[i].loc[j, tables[i].iloc[j,k+1:].last_valid_index()])
                            if advance_tax.find(' ') != -1 :
                                advance_tax = advance_tax[advance_tax.find(' ')+1: ]
                        except :
                            advance_tax = str(tables[i].iloc[j,k][tables[i].iloc[j,k].rfind(' ')+1: ])
                        if advance_tax.isdigit() == False:
                            advance_tax = 0
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k].find('TDS') != -1 :
                        try :
                            tds = str(tables[i].loc[j, tables[i].iloc[j,k+1:].last_valid_index()])
                            if tds.find(' ') != -1 :
                                tds = tds[tds.find(' ')+1: ]
                        except :
                            tds = str(tables[i].iloc[j,k][tables[i].iloc[j,k].rfind(' ')+1: ])
                        if tds.isdigit() == False:
                            tds = 0
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k].find('TCS') != -1 :
                        try :
                            tcs = str(tables[i].loc[j, tables[i].iloc[j,k+1:].last_valid_index()])
                            if tcs.find(' ') != -1 :
                                tcs = tcs[tcs.find(' ')+1: ]
                        except :
                            tcs = str(tables[i].iloc[j,k][tables[i].iloc[j,k].rfind(' ')+1: ])
                        if tcs.isdigit() == False:
                            tcs = 0
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k].find('Self Assessment Tax') != -1 :
                        try :
                            self_assessment_tax = str(tables[i].loc[j, tables[i].iloc[j,k+1:].last_valid_index()])
                            if self_assessment_tax.find(' ') != -1 :
                                self_assessment_tax = self_assessment_tax[self_assessment_tax.find(' ')+1: ]
                        except :
                            self_assessment_tax = str(tables[i].iloc[j,k][tables[i].iloc[j,k].rfind(' ')+1: ])
                        if self_assessment_tax.isdigit() == False:
                            self_assessment_tax = 0
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k].find('Total Taxes Paid (7a+7b+7c +7d)') != -1 :
                        try :
                            total_taxes_paid = str(tables[i].loc[j, tables[i].iloc[j,k+1:].last_valid_index()])
                            if total_taxes_paid.find(' ') != -1 :
                                total_taxes_paid = total_taxes_paid[total_taxes_paid.find(' ')+1: ]
                        except :
                            total_taxes_paid = str(tables[i].iloc[j,k][tables[i].iloc[j,k].rfind(' ')+1: ])
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k].find('Tax Payable (6-7e)') != -1 :
                        try :
                            tax_payable = str(tables[i].loc[j, tables[i].iloc[j,k+1:].last_valid_index()])
                            if tax_payable.find(' ') != -1 :
                                tax_payable = tax_payable[tax_payable.find(' ')+1: ]
                        except :
                            tax_payable = str(tables[i].iloc[j,k][tables[i].iloc[j,k].rfind(' ')+1: ])
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k].find('Refund (7e-6)') != -1 :
                        try :
                            refund = str(tables[i].loc[j, tables[i].iloc[j,k+1:].last_valid_index()])
                            if refund.find(' ') != -1 :
                                refund = refund[refund.find(' ')+1: ]
                        except :
                            refund = str(tables[i].iloc[j,k][tables[i].iloc[j,k].rfind(' ')+1: ])
                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k].find('Exempt Income') != -1 :
                        try:
                            exempt_income = str(tables[i].loc[j, tables[i].iloc[j,k+1:].last_valid_index()])
                        except:
                            exempt_income = '0'
                        if exempt_income.find(' ') != -1 :
                            exempt_income = exempt_income[exempt_income.find(' ')+1: ]
                        if exempt_income == '10' :
                            exempt_income = '0'

                    if type(tables[i].iloc[j,k]) == str and tables[i].iloc[j,k] == '3Total Income':
                        total_income1 = tables[i].iloc[j,k+3]
                        total_income1 = total_income[total_income.find(' ')+1:]
                        
                        
    # if 6 digits are not extracted from AY, then we impute using ITR date
    if ass_year == '0' and len(itr_date)==10:
        itr_date_map = dt.strptime(itr_date,"%d/%m/%Y")
        if itr_date_map.month > 3 and itr_date_map.month < 12:
            ass_year = str(itr_date_map.year) +"-"+ str(int(itr_date_map.year)+1)[-2:]
        else:
            ass_year = str(int(itr_date_map.year)-1) +"-"+ str(int(itr_date_map.year))[-2:]
    try:    
        if str(total_income1) == 'nan':
            total_income1 = 0.0
    except:
        pass
    
    out_dict['assessment_year'] = ass_year
    out_dict['name'] = name
    out_dict['pan'] = pan_no
    out_dict['town_city_district_state'] = city + ' ' + state
    out_dict['pin_code'] = pincode
    out_dict['efiling_acknowledgement_number'] = ackn_no
    out_dict['form_no'] = form_no
    out_dict['date_of_itr_filed'] = itr_date
    out_dict['gross_total_income'] = gross_total_income
    out_dict['deductions_under_chapter_vi_a'] = deductions
    if str(total_income) == '0.0' or str(total_income) == '0': 
        out_dict['total_income'] = float(total_income1)+float(total_income)
    else:
        out_dict['total_income'] = total_income
    
    try:
        out_dict['total_income_deemed_total_income_under_amt_mat'] = deemed_total_income
    except:
        out_dict['total_income_deemed_total_income_under_amt_mat'] = 'NA.'
    out_dict['total_income_current_year_loss'] = current_year_loss
    out_dict['net_tax_payable'] = net_tax
    out_dict['interest_and_fee_payable'] = interest_and_fee
    out_dict['total_tax_interest_and_fee_payable'] = total_tax_and_interest
    out_dict['taxes_paid_advance_tax'] = advance_tax
    out_dict['taxes_paid_tds'] = tds
    out_dict['taxes_paid_tcs'] = tcs
    out_dict['taxes_paid_self_assessment_tax'] = self_assessment_tax
    out_dict['taxes_paid_total_taxes_paid'] = total_taxes_paid
    out_dict['tax_payable'] = tax_payable
    out_dict['refund'] = refund
    df_out = DataFrame(out_dict.items(), columns=['Parameters','Information'])
    df_out = df_out.transpose()
    df_out.columns = df_out.iloc[0]
    df_out = df_out.iloc[1:]
    df_out['lid'] = file_name.split('_')[0]
    df_out['customer_id'] = 0
    df_out['image_name'] = file_name
   
    x = file_name.split('_')[0]
    y = file_name.split('_')[1:]
    z = x + '_itr_' + '_'.join(y)

    df_out.to_csv(r'D:\digitizedfiles\{}_i.csv'.format(z), index=False)
 
  
    return r'D:\digitizedfiles\{}_i.csv'.format(z)
