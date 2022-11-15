from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from pan.models import Pan
from aadhaar.models import Aadhaar
from itrv.models import Itrv
from form16.models import Info
from form26as.models import AsseseeDetails
from bank.models import Bank
from mysite.models import Customer_details
from salary.models import Salary
from common.scripts import previous_months_list
from .models import Table1, Table2, Table3, Table4, Table5
from django.db import connection
import pandas
from form16.models import Partb, Info
from form26as.models import PartA, PartB, PartG
from .data_extraction.display_itr_code_1 import itr_display5
from .data_extraction.display_itr_code_2 import itr_display4
from .data_extraction.display_itr_code_3_4_5 import itr_display1
from .data_extraction.inflows_different_sources import inflow_outflow
from django.http import HttpResponse
import pandas as pd
import json
from babel.numbers import format_currency
from .data_extraction.emivsautodebit import emi_vs_auto_debit


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    all_data = []
    for row in cursor.fetchall():
        data_row = dict(zip(columns, row))
        # data_row["Disbursal_date"] = data_row["Disbursal_date"].strftime('%d/%m/%Y')
        # data_row["Date_reported"] = data_row["Date_reported"].strftime('%d/%m/%Y')
        # data_row["bank_name"] = data_row["bank_name"]
        # data_row["deal_id"] = data_row["deal_id"]
        all_data.append(data_row)

    return all_data


@login_required
def audit_report_page(request):
    payload = {"audit_report_page": True}
    status = {}
    audit_table_data = None

    if "deal_id" not in request.session or "customer_id" not in request.session:
        status["type"] = "other"
        status["message"] = "Please select a deal first!"
    else:
        customer_id = request.session["customer_id"]
        deal_id = request.session["deal_id"]

   

   
    if not status:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT account_number, bank_name, min(txn_date) as from_date, max(txn_date) as to_date  FROM bank_bank WHERE customer_id = " + customer_id  + " GROUP BY account_number" + ";")
                data = dictfetchall(cursor)
                
           
            data = pd.DataFrame(data)
            data['from_date'] = data['from_date'].apply(lambda x : x.strftime('%d/%m/%Y'))
            data['to_date'] = data['to_date'].apply(lambda x : x.strftime('%d/%m/%Y'))
            data['type'] = 'Bank'
        except:pass
            
   


        try:

            with connection.cursor() as cursor:
                cursor.execute("SELECT pan_of_the_employee, assessment_year  FROM form16_info WHERE customer_id = " + customer_id  + ";")
                data1 = dictfetchall(cursor)
                
            
            data1 = pd.DataFrame(data1)
       
            data1['type'] = 'ITR'
            data1['form_name'] = 'Form 16'
            data1['from_date'] = data1['assessment_year'].apply(lambda x : '01/04/20'+str(int(str(x)[2:4]) - 1))
            data1['to_date'] = data1['assessment_year'].apply(lambda x : '31/03/20'+str(int(str(x)[-2:]) - 1))
        
        
        except:pass

        try:

            with connection.cursor() as cursor:
                cursor.execute("SELECT pan, assessment_year  FROM form26as_asseseedetails WHERE customer_id = " + customer_id  + ";")
                data2 = dictfetchall(cursor)
                
            
            data2 = pd.DataFrame(data2)
            data2['type'] = 'ITR'
            data2['form_name'] = 'Form 26'
            data2['from_date'] = data2['assessment_year'].apply(lambda x : '01/04/20'+str(int(str(x)[2:4]) - 1))
            data2['to_date'] = data2['assessment_year'].apply(lambda x : '31/03/20'+str(int(str(x)[-2:]) - 1))
    
        except:pass


        try:

            with connection.cursor() as cursor:
                cursor.execute("SELECT pan, assessment_year  FROM itrv_itrv WHERE customer_id = " + customer_id  + ";")
                data3 = dictfetchall(cursor)
            

            
            data3 = pd.DataFrame(data3)
          
            data3['type'] = 'ITR'
            data3['form_name'] = 'ITR-V'
            data3['from_date'] = data3['assessment_year'].apply(lambda x : '01/04/20'+str(int(str(x)[2:4]) - 1))
            data3['to_date'] = data3['assessment_year'].apply(lambda x : '31/03/20'+str(int(str(x)[-2:]) - 1))
            data3 = data3.drop_duplicates()

        except:pass

        try:

            json_records = data.reset_index().to_json(orient ='records',date_format = 'iso') 
            data = json.loads(json_records)
        except:pass

        try:

            json_records = data1.reset_index().to_json(orient ='records',date_format = 'iso') 
            data1 = json.loads(json_records)
        except:pass

        try:

            json_records = data2.reset_index().to_json(orient ='records',date_format = 'iso') 
            data2 = json.loads(json_records)
        except:pass

        try:

            json_records = data3.reset_index().to_json(orient ='records',date_format = 'iso') 
            data3 = json.loads(json_records)
        except:pass


        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM bank_bank WHERE customer_id = " + customer_id + ";")
                bank_data = dictfetchall(cursor)

            bank_data = pd.DataFrame(bank_data)

        except:pass
        

        try:

            with connection.cursor() as cursor:
                cursor.execute("SELECT assessment_year, gross_total_income, customer_id FROM itrv_itrv WHERE customer_id = " + customer_id + ";")
                itrv_data = dictfetchall(cursor)

            itrv_data = pd.DataFrame(itrv_data)

            if itrv_data.empty:
                itrv_data['assessment_year'] = ['0-0']
                itrv_data['gross_total_income'] = ['']
                itrv_data['customer_id'] = [customer_id]
        except:pass
           
            
        # print(customer_id)

        with connection.cursor() as cursor:
            cursor.execute("SELECT assessment_year, quarter, customer_id, amount_credited FROM form16_quarters WHERE customer_id = " + customer_id + ";")
            form16_data = dictfetchall(cursor)

        form16_data = pd.DataFrame(form16_data)
        form16_data = form16_data.rename(columns = {'amount_credited':'amount_paid_credited'})

        
        with connection.cursor() as cursor:
            cursor.execute("SELECT assessment_year, quarter, customer_id, amount_credited FROM form16_quarters WHERE customer_id = " + customer_id + ";")
            form16_data = dictfetchall(cursor)

        form16_data = pd.DataFrame(form16_data)
        form16_data = form16_data.rename(columns = {'amount_credited':'amount_paid_credited'})

        with connection.cursor() as cursor:
            cursor.execute("SELECT transaction_date, customer_id, amount_paid_credited FROM form26as_parta WHERE customer_id = " + customer_id + ";")
            form26_data = dictfetchall(cursor)

        form26_data = pd.DataFrame(form26_data)
        # form16_data = form16_data.rename(columns = {'amount_credited':'amount_paid_credited'})

        
        
        

        inout = inflow_outflow(bank_data,itrv_data,form16_data,form26_data)

        form26as_return = inout[4]

        try:

            form26as_return['Form26AS'] = form26as_return['Form26AS'].apply(lambda x: x if pd.notnull(x) else 0)
            form26as_return['Form26AS'] = form26as_return['Form26AS'].apply(lambda x: round(x))
            form26as_return['Form26AS'] = form26as_return['Form26AS'].apply(lambda x: format_currency(x, 'INR', locale='en_IN'))
            form26as_return['Form26AS'] = form26as_return['Form26AS'].apply(lambda x: str(x).split('.')[0])
            form26as_return['Form26AS'] = form26as_return['Form26AS'].replace('₹0','-')

        except:pass

        form16_return = inout[3]

        try:

            form16_return['Form16'] = form16_return['Form16'].apply(lambda x: x if pd.notnull(x) else 0)
            form16_return['Form16'] = form16_return['Form16'].apply(lambda x: round(x))
            form16_return['Form16'] = form16_return['Form16'].apply(lambda x: format_currency(x, 'INR', locale='en_IN'))
            form16_return['Form16'] = form16_return['Form16'].apply(lambda x: str(x).split('.')[0])
            form16_return['Form16'] = form16_return['Form16'].replace('₹0','-')

        except:pass

        itr_return = inout[2]

        # print(itr_return)

        try:

            itr_return['ITRV'] = itr_return['ITRV'].apply(lambda x: x if pd.notnull(x) else 0)
            itr_return['ITRV'] = itr_return['ITRV'].apply(lambda x: round(x))
            itr_return['ITRV'] = itr_return['ITRV'].apply(lambda x: format_currency(x, 'INR', locale='en_IN'))
            itr_return['ITRV'] = itr_return['ITRV'].apply(lambda x: str(x).split('.')[0])
            itr_return['ITRV'] = itr_return['ITRV'].replace('₹0','-')
        # itr_return = itr_return.iloc[1:]
        except:pass

        try:
            bank_return_1 = inout[1]

            bank_return_1 = bank_return_1.iloc[1:]
            bank_return = inout[0]

            bank_return[0] = bank_return[0].apply(lambda x: x if pd.notnull(x) else 0)
            bank_return[0] = bank_return[0].apply(lambda x: round(x))
            bank_return[0] = bank_return[0].apply(lambda x: format_currency(x, 'INR', locale='en_IN'))
            bank_return[0] = bank_return[0].apply(lambda x: str(x).split('.')[0])
            bank_return[0] = bank_return[0].replace('₹0','-')
        except:
           bank_return = inout[0]

        try:
        
            bank_return[1] = bank_return[1].apply(lambda x: x if pd.notnull(x) else 0)
            bank_return[1] = bank_return[1].apply(lambda x: round(x))
            bank_return[1] = bank_return[1].apply(lambda x: format_currency(x, 'INR', locale='en_IN'))
            bank_return[1] = bank_return[1].apply(lambda x: str(x).split('.')[0])
            bank_return[1] = bank_return[1].replace('₹0','-')
        except:pass

        try:

            bank_return[2] = bank_return[2].apply(lambda x: x if pd.notnull(x) else 0)
            bank_return[2] = bank_return[2].apply(lambda x: round(x))
            bank_return[2] = bank_return[2].apply(lambda x: format_currency(x, 'INR', locale='en_IN'))
            bank_return[2] = bank_return[2].apply(lambda x: str(x).split('.')[0])
            bank_return[2] = bank_return[2].replace('₹0','-')
        except:pass

        try:
            no_of_statements = list(bank_return.columns)[1:]
            for i in range(len(no_of_statements)):
                no_of_statements[i] = '-'+str(no_of_statements[i])

            json_records = bank_return.reset_index().to_json(orient ='records',date_format = 'iso') 
            bank_return = json.loads(json_records)

            json_records = bank_return_1.reset_index().to_json(orient ='records',date_format = 'iso') 
            bank_return_1 = json.loads(json_records)

        except:pass
       
        
        try:
            json_records = itr_return.reset_index().to_json(orient ='records',date_format = 'iso') 
            itr_return = json.loads(json_records)

        except:pass
    
        try:

            json_records = form16_return.reset_index().to_json(orient ='records',date_format = 'iso') 
            form16_return = json.loads(json_records)
        except:pass

        try:
        
            json_records = form26as_return.reset_index().to_json(orient ='records',date_format = 'iso') 
            form26as_return = json.loads(json_records)
        except:pass

    #     try:
    #         pan_db_data = Pan.objects.get(customer_id=customer_id)
    #         pan_data = {"name": pan_db_data.name if pan_db_data.name else "NA", "pan": pan_db_data.pan_number if pan_db_data.pan_number else "NA", "aadhaar": "NA", "pin": "NA", "dob": pan_db_data.dob.strftime('%d/%m/%Y') if pan_db_data.dob else "NA", "contact_number": "NA", "address": "NA", "state": "NA"}
    #     except Exception as e:
    #         print(e)
    #         pan_data = {"name": "NA", "pan": "NA", "aadhaar": "NA", "pin": "NA", "dob": "NA", "contact_number": "NA", "address": "NA", "state": "NA"}
        
    #     try:
    #         aadhaaar_db_data = Aadhaar.objects.get(customer_id=customer_id)
    #         aadhaaar_data = {"name": aadhaaar_db_data.name if aadhaaar_db_data.name else "NA", "pan": "NA", "aadhaar": aadhaaar_db_data.uid if aadhaaar_db_data.uid else "NA", "pin": aadhaaar_db_data.pc if aadhaaar_db_data.pc else "NA", "dob": aadhaaar_db_data.dob.strftime('%d/%m/%Y') if aadhaaar_db_data.dob else "NA", "contact_number": "NA", "address": aadhaaar_db_data.dist if aadhaaar_db_data.dist else "NA", "state": aadhaaar_db_data.state if aadhaaar_db_data.state else "NA"}
    #     except Exception as e:
    #         print(e)
    #         aadhaaar_data = {"name": "NA", "pan": "NA", "aadhaar": "NA", "pin": "NA", "dob": "NA", "contact_number": "NA", "address": "NA", "state": "NA"}
        
    #     try:
    #         itrv_db_data = Itrv.objects.filter(customer_id=customer_id).last()
    #         form26as_db_data = AsseseeDetails.objects.filter(customer_id=customer_id).last()
    #         form16_db_data = Info.objects.filter(customer_id=customer_id).last()

    #         names = []
    #         names.append(itrv_db_data.name if itrv_db_data.name else "NA")
    #         names.append(form26as_db_data.name_of_assessee if form26as_db_data.name_of_assessee else "NA")
    #         names.append(form16_db_data.employee_name if form16_db_data.employee_name else "NA")

    #         pans = []
    #         pans.append(itrv_db_data.pan if itrv_db_data.pan else "NA")
    #         pans.append(form26as_db_data.pan if form26as_db_data.pan else "NA")
    #         pans.append(form16_db_data.pan_of_the_employee if form16_db_data.pan_of_the_employee else "NA")

    #         addresses = []
    #         addresses.append(itrv_db_data.town_city_district_state if itrv_db_data.town_city_district_state else "NA")
    #         addresses.append(form26as_db_data.address_of_assessee if form26as_db_data.address_of_assessee else "NA")
    #         addresses.append(form16_db_data.employee_address if form16_db_data.employee_address else "NA")

    #         states = []
    #         states.append(itrv_db_data.town_city_district_state if itrv_db_data.town_city_district_state else "NA")
    #         states.append(form26as_db_data.address_of_assessee if form26as_db_data.address_of_assessee else "NA")
    #         states.append(form16_db_data.employee_address if form16_db_data.employee_address else "NA")

    #         itrv_data_audit_report = {"name": ", ".join(sorted(set(names), key=names.index)) if len(names) > 0 else "NA", "pan": ", ".join(sorted(set(pans), key=pans.index)) if len(pans) > 0 else "NA", "aadhaar": "NA", "pin": itrv_db_data.pin_code if itrv_db_data.pin_code else "NA", "dob": "NA", "contact_number": "NA", "address": ", ".join(sorted(set(addresses), key=addresses.index)) if len(addresses) > 0 else "NA", "state": ", ".join(sorted(set(states), key=states.index)) if len(states) > 0 else "NA"}
    #     except Exception as e:
    #         print(e)
    #         itrv_data_audit_report = {"name": "NA", "pan": "NA", "aadhaar": "NA", "pin": "NA", "dob": "NA", "contact_number": "NA", "address": "NA", "state": "NA"}
        
    #     try:
    #         bank_db_statement_data_arr = Bank.objects.filter(customer_id=customer_id)
    #         account_names = []
    #         for bank_db_statement_data in bank_db_statement_data_arr:
    #             account_names.append(bank_db_statement_data.account_name if bank_db_statement_data.account_name else "NA")
    #         bank_statement_data = {"name": ", ".join(set(account_names)) if len(account_names) > 0 else "NA", "pan": "NA", "aadhaar": "NA", "pin": "NA", "dob": "NA", "contact_number": "NA", "address": "NA", "state": "NA"}
    #     except Exception as e:
    #         print(e)
    #         bank_statement_data = {"name": "NA", "pan": "NA", "aadhaar": "NA", "pin": "NA", "dob": "NA", "contact_number": "NA", "address": "NA", "state": "NA"}
        
    #     try:
    #         customer_db_data = Customer_details.objects.get(customer_id=customer_id)
    #         los_data = {"name": customer_db_data.customer_name if customer_db_data.customer_name else "NA", "pan": customer_db_data.customer_pan if customer_db_data.customer_pan else "NA", "aadhaar": customer_db_data.customer_uid if customer_db_data.customer_uid else "NA", "pin": customer_db_data.customer_address.pin_code if customer_db_data.customer_address.pin_code else "NA", "dob": customer_db_data.customer_dob.strftime('%d/%m/%Y') if customer_db_data.customer_dob else "NA", "contact_number": customer_db_data.customer_address.primary_phone if customer_db_data.customer_address.primary_phone else "NA", "address": customer_db_data.customer_address.address_line1 if customer_db_data.customer_address.address_line1 else "NA", "state": customer_db_data.customer_address.state if customer_db_data.customer_address.state else "NA"}
    #     except Exception as e:
    #         print(e)
    #         los_data = {"name": "NA", "pan": "NA", "aadhaar": "NA", "pin": "NA", "dob": "NA", "contact_number": "NA", "address": "NA", "state": "NA"}
        
    #     bureau_data = {"name": "NA", "pan": "NA", "aadhaar": "NA", "pin": "NA", "dob": "NA", "contact_number": "NA", "address": "NA", "state": "NA"}

    #     try:
    #         net_salary_db_data = Salary.objects.get(deal_id=deal_id,customer_id=customer_id,sal_type="net")
    #         net_salary_data = {"month1": net_salary_db_data.month7 if net_salary_db_data.month7 and net_salary_db_data.month7 != "-" else "NA", "month2": net_salary_db_data.month6 if net_salary_db_data.month6 and net_salary_db_data.month6 != "-" else "NA", "month3": net_salary_db_data.month5 if net_salary_db_data.month5 and net_salary_db_data.month5 != "-" else "NA", "month4": net_salary_db_data.month4 if net_salary_db_data.month4 and net_salary_db_data.month4 != "-" else "NA", "month5": net_salary_db_data.month3 if net_salary_db_data.month3 and net_salary_db_data.month3 != "-" else "NA", "month6": net_salary_db_data.month2 if net_salary_db_data.month2 and net_salary_db_data.month2 != "-" else "NA", "month7": net_salary_db_data.month1 if net_salary_db_data.month1 and net_salary_db_data.month1 != "-" else "NA", "month8": "NA", "month9": "NA", "month10": "NA", "month11": "NA", "month12": "NA"}
    #     except Exception as e:
    #         print(e)
    #         net_salary_data = {"month1": "NA", "month2": "NA", "month3": "NA", "month4": "NA", "month5": "NA", "month6": "NA", "month7": "NA", "month8": "NA", "month9": "NA", "month10": "NA", "month11": "NA", "month12": "NA"}

    #     # Table1
    #     income_from_different_sources_16 = "NA"
    #     try:
    #         # ITRV DATA
    #         itrv_query = str(Itrv.objects.filter(deal_id=deal_id, customer_id=customer_id).query)
    #         itrv_df = pandas.read_sql_query(itrv_query, connection)
    #         itrv_columns = ["gross_total_income",
    #                         "deductions_under_chapter_vi_a"]
    #         itrv_data = [itrv_df[label].values[0] for label in itrv_columns if label in itrv_df]
    #         itrv = []
    #         for i in itrv_data:
    #             if i == "nan" or not i:
    #                 itrv.append("0")
    #             else:
    #                 itrv.append(i)

    #         # FORM 16 PART B DATA
    #         form16_part_b_query = str(Partb.objects.filter(deal_id=deal_id, customer_id=customer_id).query)
    #         form16_part_b_df = pandas.read_sql_query(form16_part_b_query, connection)
    #         form16_part_b_columns = ["ductn_in_rspct_of_lfe_inc_prmia_cntrbn_2_pf_undr_sec_80c_gr_amnt",
    #                                 "incm_or_admsble_los_frm_house_prprty_rprtd_by_empyee_ofr_for_tds",
    #                                 "income_under_the_head_other_sources_offered_for_tds",
    #                                 "ductn_in_rspct_of_ctrbtn_2_crtn_pnsn_fnds_undr_sec_80ccc_gr_amnt",
    #                                 "total_taxable_income_9_minus_11",
    #                                 "dtn_in_rsp_of_hlt_insrnc_premia_ndr_sc_80d_gr_amt",
    #                                 "house_rent_allowance_under_section_10_13a"]
    #         form16_part_b_data = [form16_part_b_df[label].values[0] for label in form16_part_b_columns if label in form16_part_b_df]
    #         form16_part_b = []
    #         for i in form16_part_b_data:
    #             if i == "nan" or not i:
    #                 form16_part_b.append("0")
    #             else:
    #                 form16_part_b.append(i)
        
    #         # FORM 26 AS PART A DATA
    #         form26_part_a_query = str(PartA.objects.filter(deal_id=deal_id, customer_id=customer_id).query)
    #         form26_part_a_df = pandas.read_sql_query(form26_part_a_query, connection)
    #         form26_part_a = form26_part_a_df[["section_1", "assessment_year", "amount_paid_credited"]]

    #         # FORM 26 AS PART G DATA
    #         form26_part_g_query = str(PartG.objects.filter(deal_id=deal_id, customer_id=customer_id).query)
    #         form26_part_g = pandas.read_sql_query(form26_part_g_query, connection)
            
    #         table1_data_df = itr_display5(itrv, form16_part_b, form26_part_a, form26_part_g)

    #         Table1.objects.filter(deal_id=deal_id, customer_id=customer_id).delete()
    #         if table1_data_df is not None:
    #             for index, data in table1_data_df.iterrows():
    #                 Table1.objects.create(
    #                     assessment_year = data['assessment_year'] if 'assessment_year' in table1_data_df else '',
    #                     gross_income = data['gross_income'] if 'gross_income' in table1_data_df else '',
    #                     average_monthly_gross_income = data['average_monthly_gross_income'] if 'average_monthly_gross_income' in table1_data_df else '',
    #                     taxable_income = data['taxable_income'] if 'taxable_income' in table1_data_df else '',
    #                     hra = data['hra'] if 'hra' in table1_data_df else '',
    #                     rent_income = data['rent_income'] if 'rent_income' in table1_data_df else '',
    #                     tax_default_found = data['tax_default_found'] if 'tax_default_found' in table1_data_df else '',
    #                     ccc80 = data['ccc80'] if 'ccc80' in table1_data_df else '',
    #                     c80 = data['c80'] if 'c80' in table1_data_df else '',
    #                     d80 = data['d80'] if 'd80' in table1_data_df else '',
    #                     other_income_under_sec_192_2b = data['other_income_under_sec_192_2b'] if 'other_income_under_sec_192_2b' in table1_data_df else '',
    #                     other_deductions = data['other_deductions'] if 'other_deductions' in table1_data_df else '',
    #                     total_deductions = data['total_deductions'] if 'total_deductions' in table1_data_df else '',
    #                     created_by=request.user,
    #                     deal_id=deal_id,
    #                     customer_id=customer_id
    #                 )
    #                 income_from_different_sources_16 = round(data['average_monthly_gross_income'], 2) if 'average_monthly_gross_income' in table1_data_df else 'NA'
    #                 from babel.numbers import format_currency
    #                 income_from_different_sources_16 = format_currency(income_from_different_sources_16, 'INR', locale='en_IN')
    #     except Exception as e:
    #         print(e)

    #     # Table2
    #     try:
    #         # FORM 16 INFO DATA
    #         form16_info_query = str(Info.objects.filter(deal_id=deal_id, customer_id=customer_id).query)
    #         form16_info_df = pandas.read_sql_query(form16_info_query, connection)
    #         table2_data = itr_display4(form16_info_df)
    #         Table2.objects.filter(deal_id=deal_id, customer_id=customer_id).delete()
    #         if table2_data is not None:
    #             Table2.objects.create(
    #                 address_of_latest_employer_for_reference = table2_data,
    #                 created_by=request.user,
    #                 deal_id=deal_id,
    #                 customer_id=customer_id
    #             )
    #     except Exception as e:
    #         print(e)

    #     income_from_different_sources_26as_dict = {"january": "NA", "february": "NA", "march": "NA", "april": "NA", "may": "NA",
    #                 "june": "NA", "july": "NA", "august": "NA", "september": "NA", "october": "NA", "november": "NA", "december": "NA"}
    #     #dynamic_month_list = [i.lower().split(" ")[0] for i in previous_months_list(12)]
    #     dynamic_month_list = [i.lower().split("-")[0] for i in previous_months_list(12)]
    #     dynamic_month_list = pandas.to_datetime(dynamic_month_list, format='%b')
    #     dynamic_month_list = [i.strftime('%B').lower() for i in dynamic_month_list]

    #     # Table3,4,5
    #     income_from_different_sources_26as = ["NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA"]
    #     try:
    #         # FORM 26 AS PART B DATA
    #         form26_part_b_query = str(PartB.objects.filter(deal_id=deal_id, customer_id=customer_id).query)
    #         form26_part_b_df = pandas.read_sql_query(form26_part_b_query, connection)

    #         table3_data_df, table4_data_df, table5_data_df = itr_display1(form26_part_a_df, form26_part_b_df)

    #         Table3.objects.filter(deal_id=deal_id, customer_id=customer_id).delete()
    #         if table3_data_df is not None:
    #             table3_data_df.reset_index(inplace=True)
    #             for index, data in table3_data_df.iterrows():
    #                 Table3.objects.create(
    #                     assessment_year = data['assessment_year'] if 'assessment_year' in table3_data_df else '',
    #                     measures = data['measures'] if 'measures' in table3_data_df else '',
    #                     january = data['January'] if 'January' in table3_data_df else '',
    #                     february = data['February'] if 'February' in table3_data_df else '',
    #                     march = data['March'] if 'March' in table3_data_df else '',
    #                     april = data['April'] if 'April' in table3_data_df else '',
    #                     may = data['May'] if 'May' in table3_data_df else '',
    #                     june = data['June'] if 'June' in table3_data_df else '',
    #                     july = data['July'] if 'July' in table3_data_df else '',
    #                     august = data['August'] if 'August' in table3_data_df else '',
    #                     september = data['September'] if 'September' in table3_data_df else '',
    #                     october = data['October'] if 'October' in table3_data_df else '',
    #                     november = data['November'] if 'November' in table3_data_df else '',
    #                     december = data['December'] if 'December' in table3_data_df else '',
    #                     source = data['Source'] if 'Source' in table3_data_df else '',
    #                     created_by=request.user,
    #                     deal_id=deal_id,
    #                     customer_id=customer_id
    #                 )
                
    #                 if 'measures' in table3_data_df and data['measures'] == "Total Income":
    #                     income_from_different_sources_26as_dict = {"january": data['January'] if 'January' in table3_data_df else 'NA', "february": data['February'] if 'February' in table3_data_df else 'NA',
    #                             "march": data['March'] if 'March' in table3_data_df else 'NA', "april": data['April'] if 'April' in table3_data_df else 'NA',
    #                             "may": data['May'] if 'May' in table3_data_df else 'NA', "june": data['June'] if 'June' in table3_data_df else 'NA',
    #                             "july": data['July'] if 'July' in table3_data_df else 'NA', "august": data['August'] if 'August' in table3_data_df else 'NA',
    #                             "september": data['September'] if 'September' in table3_data_df else 'NA', "october": data['October'] if 'October' in table3_data_df else 'NA',
    #                             "november": data['November'] if 'November' in table3_data_df else 'NA', "december": data['December'] if 'December' in table3_data_df else 'NA'}
            
    #         Table4.objects.filter(deal_id=deal_id, customer_id=customer_id).delete()
    #         if table4_data_df is not None:
    #             Table4.objects.create(
    #                 section = list(table4_data_df)[1],
    #                 k194 = table4_data_df.iloc[0,1],
    #                 betting = table4_data_df.iloc[1,1],
    #                 collection_at_source = table4_data_df.iloc[2,1],
    #                 income_from_abroad = table4_data_df.iloc[3,1],
    #                 income_from_commission = table4_data_df.iloc[4,1],
    #                 income_from_contracting = table4_data_df.iloc[5,1],
    #                 income_from_tech_prof_services = table4_data_df.iloc[6,1],
    #                 orignal_investment_principal_withdrawal = table4_data_df.iloc[7,1],
    #                 rent = table4_data_df.iloc[8,1],
    #                 salary = table4_data_df.iloc[9,1],
    #                 sale_of_property = table4_data_df.iloc[10,1],
    #                 created_by=request.user,
    #                 deal_id=deal_id,
    #                 customer_id=customer_id
    #             )
            
    #         Table5.objects.filter(deal_id=deal_id, customer_id=customer_id).delete()
    #         if table5_data_df is not None:
    #             table5_data_df.reset_index(inplace=True)
    #             for index, data in table5_data_df.iterrows():
    #                 Table5.objects.create(
    #                     assessment_year = data['assessment_year'] if 'assessment_year' in table5_data_df else '',
    #                     name_of_deductor = data['name_of_deductor'] if 'name_of_deductor' in table5_data_df else '',
    #                     number_of_transactions = data['number_of_transactions'] if 'number_of_transactions' in table5_data_df else '',
    #                     total_amount = data['total_amount'] if 'total_amount' in table5_data_df else '',
    #                     created_by=request.user,
    #                     deal_id=deal_id,
    #                     customer_id=customer_id
    #                 )
    #     except Exception as e:
    #         print(e)

    #     income_from_different_sources_26as = []
    #     for i in dynamic_month_list:
    #         income_from_different_sources_26as.append(income_from_different_sources_26as_dict[i])

    #     audit_table_data = {"pan_data": pan_data, "aadhaaar_data": aadhaaar_data, "itrv_data": itrv_data_audit_report, "bank_statement_data": bank_statement_data, "bureau_data": bureau_data, "los_data": los_data, "net_salary_data": net_salary_data, "income_from_different_sources_26as": income_from_different_sources_26as, "income_from_different_sources_16": income_from_different_sources_16}

    # payload["audit_table_data"] = audit_table_data
    # payload["status"] = status
    # payload["previous_months_list"] = previous_months_list(12)
    
        with connection.cursor() as cursor:
            cursor.execute("select * from a3_kit.bureau where Customer_Id ="+ customer_id + ";")
            df= dictfetchall(cursor)
        df=pd.DataFrame(df)
        index=0
        for x in df['valuetype']:
            if(x=='bureau'):
                df['EMI_new'][index]=df['EMI'][index]
            elif(x=='edited'):
                df['EMI_new'][index]=df['EMI_edited'][index]
            elif(x=='recommended'):
                df['EMI_new'][index]=df['EMI_new'][index]
            index=index+1
                
            
            
        


        with connection.cursor() as cursor:
            sql_query=("select Loan_type, Disbursal_date, EMI_new from a3_kit.bureau where Customer_Id = " + customer_id + " and final_selected=1 ;")
            # print(sql_query)
            cursor.execute(sql_query)
            bureau_data = dictfetchall(cursor)
        bureau_data = pd.DataFrame(bureau_data)

        with connection.cursor() as cursor:
            cursor.execute("select * from bank_bank where customer_id = " + customer_id + ";")
            bank_1_data = dictfetchall(cursor)
        bank_1_data = pd.DataFrame(bank_1_data)

      
        
       
        if df.empty:

            bureau_data['Loan_type'] = ''
            bureau_data['Disbursal_date'] = ''
            bureau_data['EMI_new'] = ''
            bureau_data['Customer_Id'] = customer_id
        

        emi_debit_table = emi_vs_auto_debit(bank_1_data, df)
        if type(emi_debit_table) is not type(None):
            emi_debit_table = emi_debit_table.rename(columns = {'Loan Type':'loan_type', 'Next 3 Nearest Debit Entries':'next_3_debit_entries'})

           
            emi_debit_table['EMI'] = emi_debit_table['EMI'].apply(lambda x: x if pd.notnull(x) else 0)
            emi_debit_table['EMI'] = emi_debit_table['EMI'].apply(lambda x: round(x))
            emi_debit_table['EMI'] = emi_debit_table['EMI'].apply(lambda x: format_currency(x, 'INR', locale='en_IN'))
            emi_debit_table['EMI'] = emi_debit_table['EMI'].apply(lambda x: str(x).split('.')[0])
            emi_debit_table['EMI'] = emi_debit_table['EMI'].replace('₹0','-')

            emi_debit_table['debit'] = emi_debit_table['debit'].apply(lambda x: x if pd.notnull(x) else 0)
            emi_debit_table['debit'] = emi_debit_table['debit'].apply(lambda x: round(x))
            emi_debit_table['debit'] = emi_debit_table['debit'].apply(lambda x: format_currency(x, 'INR', locale='en_IN'))
            emi_debit_table['debit'] = emi_debit_table['debit'].apply(lambda x: str(x).split('.')[0])
            emi_debit_table['debit'] = emi_debit_table['debit'].replace('₹0','-')

            
            try:
                emi_debit_table['Transactions'] = emi_debit_table['Transactions'].astype('int64')

            except:pass

       
            json_records = emi_debit_table.reset_index().to_json(orient ='records',date_format = 'iso') 
            emi_debit_table = json.loads(json_records)

        





    
        payload = {"audit_report_page": True, "status": status if status else None, 'data':data, 'data1':data1, 'data2':data2, 'data3':data3, 'bank_return':bank_return, 'bank_return_1':bank_return_1, 'itr_return':itr_return, 'form16_return':form16_return, 'form26as_return':form26as_return, 'emi_debit_table':emi_debit_table,'no_of_statements':no_of_statements}
        # print(emi_debit_table)
    
        return render(request, "audit_report.html", payload)

    payload = {"audit_report_page": True, "status": status if status else None}
    return render(request, "audit_report.html", payload)

    # return render(request, "audit_report.html", {'data':data, 'data1':data1, 'data2':data2, 'data3':data3, 'bank_return':bank_return, 'bank_return_1':bank_return_1, 'itr_return':itr_return, 'form16_return':form16_return, 'form26as_return':form26as_return, 'emi_debit_table':emi_debit_table,'no_of_statements':no_of_statements})


import mysql.connector
@login_required
def audit_entity(request):

    entity = request.GET.get('entity')
    customer_id = request.session['customer_id']

    mydb = mysql.connector.connect(
            host="localhost",
            user="root",                        ###connect to database
            password="Knowlvers@555",
            database="a3_kit"
                )

    mycursor = mydb.cursor() 

    sql = "SELECT DATE_FORMAT(txn_date, '%d/%m/%Y'), description, debit, credit, balance, cheque_number, entity FROM bank_bank WHERE customer_id = {} and entity = '{}' ;".format(customer_id,entity)

    print(mycursor.execute(sql))

    myresult = mycursor.fetchall()
    if not myresult:
        try:
            entity = "%"+entity+"%"
            sql = "SELECT DATE_FORMAT(txn_date, '%d/%m/%Y'), description, debit, credit, balance, cheque_number, entity FROM bank_bank WHERE customer_id = {} and entity like '{}' ;".format(customer_id, entity)
            # print(mycursor.execute(sql))
            myresult = mycursor.fetchall()
        except Exception as e:
            pass

    data = []
    for x in myresult:
        data.append({'txn_date':x[0], 'description':x[1], 'debit':x[2], 'credit':x[3], 'balance':x[4], 'cheque_number':x[5],'entity':x[6]})
    # print(data)
    # with connection.cursor() as cursor:

        
        
    #     cursor.execute("SELECT * FROM bank_bank WHERE customer_id = {} and entity = {} ;".format(customer_id,entity))
    #     data = dictfetchall(cursor)
    #         # for date in data:
                
    #             # date['debit']=date['debit'].apply(lambda x : format_currency( x, 'INR', locale='en_IN'))
    #             # date['credit']=format_currency(date['credit'], 'INR', locale='en_IN')
    #             # date['balance']=format_currency(date['balance'], 'INR', locale='en_IN')
        
    #     entity=""
    #     data = pd.DataFrame(data)
        
    #     data['txn_date'] = data['txn_date'].apply( lambda x : x.strftime('%d/%m/%Y'))

    #     data['debit'] = data['debit'].fillna(0)
    #     data['debit'] = data['debit'].apply(lambda x: format_currency(x, 'INR', locale='en_IN'))

    #     data['credit'] = data['credit'].fillna(0)
    #     data['credit'] = data['credit'].apply(lambda x: format_currency(x, 'INR', locale='en_IN'))

    #     data['balance'] = data['balance'].fillna(0)
    #     data['balance'] = data['balance'].apply(lambda x: format_currency(x, 'INR', locale='en_IN'))


    #     json_records = data.to_json(orient ='records') 
    #     data = json.loads(json_records)

            
    return render(request, "bank_entity.html", {'entity':data})