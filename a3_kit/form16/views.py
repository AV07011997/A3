import os
import time
from django.http import HttpResponse
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from common.scripts import normalize_date
from .data_extraction.form16 import get_form16_data
from .models import Info
from .models import Quarters
from .models import Challans
from .models import Partb
from django.http import JsonResponse
from mysite.models import Uploaded_itrv_form16_form26as_details



@login_required
def home(request):
    status = {}
    
    if "deal_id" not in request.session or "customer_id" not in request.session:
        status["type"] = "other"
        status["message"] = "Please select a deal first to procceed further!"

    if request.method == 'POST' and not status:
        if 'file_upload' not in request.FILES:
            status["type"] = "other"
            status["message"] = "Field name is missing, can not procceed further!"
        
        if not status:
            # upload_file = request.FILES['pdf']
            print("form16 views clicked")
            document_type = request.POST['document_type']
            year = request.POST['year']
            print("form16 views document type: ",document_type)
            print("form16 views year: ",year)

            upload_file = request.FILES['file_upload']
            file_name = request.session["customer_id"] + "_" + str(time.time())
            file_name_type = file_name + '.' + upload_file.name.split('.')[-1]
            fs = FileSystemStorage()
            fs.save('form16/'+file_name_type, upload_file)
            media_root = settings.MEDIA_ROOT
            file_dir = os.path.join(media_root, 'form16')
            file_path = os.path.join(file_dir, file_name_type)
            try:
                info_df, quaters_df, challans_df, part_b_df = get_form16_data(file_path)
            except Exception as e:
                print(e)
                status["type"] = "fail"
                status["message"] = "We are unable to process the uploaded document. Do you want to process it manually through knowlvers?"

            if not status:
                status["type"] = "success"
                status["message"] = "File upload successful!"
            
            if status["type"] == "success":
                try:
                    if info_df is not None:
                        Info.objects.create(
                            certification_no = info_df.iloc[0,1],
                            last_updated_on = normalize_date(info_df.iloc[1,1]),
                            pan_of_the_deductor = info_df.iloc[2,1],
                            tan_of_the_deductor = info_df.iloc[3,1],
                            pan_of_the_employee = info_df.iloc[4,1],
                            assessment_year = info_df.iloc[5,1],
                            period_with_the_employer_from = normalize_date(info_df.iloc[6,1]),
                            period_with_the_employer_to = normalize_date(info_df.iloc[7,1]),
                            employer_name = info_df.iloc[8,1],
                            employer_address = info_df.iloc[9,1],
                            employee_name = info_df.iloc[10,1],
                            employee_address = info_df.iloc[11,1],
                            created_by=request.user,
                            deal_id=request.session["deal_id"],
                            customer_id=request.session["customer_id"],
                            image_name=file_name_type
                            
                        )
                    
                    if challans_df is not None:
                        for index, data in challans_df.iterrows():
                            Challans.objects.create(
                                tax_deposited = data['Tax deposited'] if 'Tax deposited' in challans_df else '',
                                bsr_code = data['BSR Code'] if 'BSR Code' in challans_df else '',
                                tax_deposited_date = normalize_date(data['Tax deposited Date'] if 'Tax deposited Date' in challans_df else ''),
                                challan_serial_no = data['Challan Serial No'] if 'Challan Serial No' in challans_df else '',
                                status_match_oltas = data['Status Match OLTAS'] if 'Status Match OLTAS' in challans_df else '',
                                assessment_year = data['Assessment Year'] if 'Assessment Year' in challans_df else '',
                                deal_id=request.session["deal_id"],
                                customer_id=request.session["customer_id"],
                                created_by=request.user
                        )

                    if quaters_df is not None:
                        for index, data in quaters_df.iterrows():
                            Quarters.objects.create(
                                quater = data['Quarter'] if 'Quarter' in quaters_df else '',
                                reciept_number = data['Receipt Number'] if 'Receipt Number' in quaters_df else '',
                                amount_credited = data['Amount paid/credited'] if 'Amount paid/credited' in quaters_df else '',
                                tax_deducted = data['Tax deducted'] if 'Tax deducted' in quaters_df else '',
                                tax_remitted = data['Tax deposited/remitted'] if 'Tax deposited/remitted' in quaters_df else '',
                                assessment_year = data['Assessment Year'] if 'Assessment Year' in quaters_df else '',
                                created_by=request.user,
                                deal_id=request.session["deal_id"],
                                customer_id=request.session["customer_id"]
                            )

                    if part_b_df is not None:
                        Partb.objects.create(
                            gross_salary_salary_as_per_provisions_contained_in_section_17_1 = part_b_df.iloc[0,1],
                            gross_salary_value_of_perquisites_under_section_17_2 = part_b_df.iloc[1,1],
                            gross_salary_profits_in_lieu_of_salary_under_section_17_3 = part_b_df.iloc[2,1],
                            gross_salary_total = part_b_df.iloc[3,1],
                            gross_salary_reported_total_amount_of_salary_received_from_other_employers = part_b_df.iloc[4,1],
                            less_allowance_to_the_extent_exempt_under_section_10 = part_b_df.iloc[5,1],
                            travel_concession_or_assistance_under_section_10_5 = part_b_df.iloc[6,1],
                            death_cum_retirement_gratuity_under_section_10_10 = part_b_df.iloc[7,1],
                            commuted_value_of_pension_under_section_10_10a = part_b_df.iloc[8,1],
                            cash_equivalent_of_leave_salary_encashment_under_section_10_10aa = part_b_df.iloc[9,1],
                            house_rent_allowance_under_section_10_13a = part_b_df.iloc[10,1],
                            amount_of_any_other_exemption_under_section_10 = part_b_df.iloc[11,1],
                            total_amount_of_any_other_exemption_under_section_10 = part_b_df.iloc[12,1],
                            total_amount_of_exemption_claimed_under_section_10 = part_b_df.iloc[13,1],
                            total_amount_of_salary_received_from_current_employer_1d_minus_2h = part_b_df.iloc[14,1],
                            standard_deduction_under_section_16_ia = part_b_df.iloc[15,1],
                            entertainment_allowance_under_section_16_ii = part_b_df.iloc[16,1],
                            tax_on_employment_under_section_16_iii = part_b_df.iloc[17,1],
                            total_amount_of_deductions_under_section_16_4a_plus_4b_plus_4c = part_b_df.iloc[18,1],
                            income_chargeable_under_the_head_salaries_3_plus_1e_minus_5 = part_b_df.iloc[19,1],
                            income_or_admissible_loss_from_house_property_reported_by_employee_offered_for_tds = part_b_df.iloc[20,1],
                            income_under_the_head_other_sources_offered_for_tds = part_b_df.iloc[21,1],
                            total_amount_of_other_income_reported_by_the_employee_7a_plus_7b = part_b_df.iloc[22,1],
                            gross_total_income_6_plus_8 = part_b_df.iloc[23,1],
                            deduction_in_respect_of_life_insurance_premia_contributions_to_provident_fund_etc_under_section_80c_gross_amount = part_b_df.iloc[24,1],
                            deduction_in_respect_of_contribution_to_certain_pension_funds_under_section_80ccc_gross_amount = part_b_df.iloc[25,1],
                            deduction_in_respect_of_contribution_by_taxpayer_to_pension_scheme_under_section_80ccd_1_gross_amount = part_b_df.iloc[26,1],
                            total_deduction_under_section_80c_80ccc_and_80ccd_1_gross_amount = part_b_df.iloc[27,1],
                            deductions_in_respect_of_amount_paid_deposited_to_notified_pension_scheme_under_section_80ccd_1b_gross_amount = part_b_df.iloc[28,1],
                            deduction_in_respect_of_contribution_by_employer_to_pension_scheme_under_section_80ccd_2_gross_amount = part_b_df.iloc[29,1],
                            deduction_in_respect_of_health_insurance_premia_under_section_80d_gross_amount = part_b_df.iloc[30,1],
                            deduction_in_respect_of_interest_on_loan_taken_for_higher_education_under_section_80e_gross_amount = part_b_df.iloc[31,1],
                            total_deduction_in_respect_of_donations_to_certain_funds_charitable_institutions_etc_under_section_80g_gross_amount = part_b_df.iloc[32,1],
                            deduction_in_respect_of_interest_on_deposits_in_savings_account_under_section_80tta_gross_amount = part_b_df.iloc[33,1],
                            amount_deductible_under_any_other_provisions_of_chapter_vi_a_gross_amount = part_b_df.iloc[34,1],
                            total_of_amount_deductible_under_any_other_provisions_of_chapter_vi_a = part_b_df.iloc[35,1],
                            aggregate_of_deductible_amount_under_chapter_vi_a = part_b_df.iloc[36,1],
                            total_taxable_income_9_minus_11 = part_b_df.iloc[37,1],
                            tax_on_total_income = part_b_df.iloc[38,1],
                            rebate_under_section_87a_if_applicable = part_b_df.iloc[39,1],
                            surcharge_wherever_applicable = part_b_df.iloc[40,1],
                            health_and_education_cess = part_b_df.iloc[41,1],
                            tax_payable_13_plus_15_plus_16_minus_14 = part_b_df.iloc[42,1],
                            relief_under_section_89 = part_b_df.iloc[43,1],
                            net_tax_payable_17_minus_18 = part_b_df.iloc[44,1],
                            assessment_year = part_b_df.iloc[45,1],
                            deal_id=request.session["deal_id"],
                            customer_id=request.session["customer_id"],
                            created_by=request.user
                        )
                        
                        Uploaded_itrv_form16_form26as_details.objects.create(
                                deal_id=request.session["deal_id"],
                                customer_id=request.session["customer_id"],
                                year=year,
                                document_type = document_type,
                                file_name = file_name_type,
                                created_by=request.user
                        )

                    
                except Exception as e:
                    print(e)
                    status["type"] = "other"
                    status["message"] = "Something went wrong! please try again!"
    
    # return JsonResponse({"status": status})
    payload = json.dumps({"upload_form_page": True, "status": status})
    return HttpResponse(payload)