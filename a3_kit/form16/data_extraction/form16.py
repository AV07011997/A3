import pandas as pd
import numpy as np
import tabula


def get_form16_data(pdf_path):
    pdf_file=pdf_path.split('\\')[-1][:-4]
    
    
     # PART B  of the statement  
    tables2 = tabula.read_pdf(pdf_path,pages=[3,4],guess= True,lattice=False,stream=True,area=[29,19,785,576],columns=[375,441,509],pandas_options={'header': None})
    for i in range(1,len(tables2)) :
        ####single appended file
        mtable = pd.concat([tables2[i-1], tables2[i]])
        mtable=mtable.reset_index()
        mtable=mtable.drop(columns=['index'])
        # creating the output dictionary
        ##############first type of file
    if mtable[0].iloc[0]=='PART B (Annexure)':   
        out_dict = {}
        
        for i in range(len(mtable)) :
            for j in range(len(mtable.columns)) :
                
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(a) Salary as per provisions contained in section 17(1)')!= -1:
                    out_dict['1a. Gross Salary: Salary as per provisions contained in section 17(1)'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(b) Value of perquisites under section 17(2)')!= -1:
                    out_dict['1b. Gross Salary: Value of perquisites under section 17(2)'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(c) Profits in lieu of salary under section 17(3)')!= -1:
                    out_dict['1c. Gross Salary: Profits in lieu of salary under section 17(3)'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j]=='(d) Total':
                    out_dict['1d. Gross Salary: Total'] = mtable.iloc[i,j+2]        
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(e) Reported total amount of salary received')!= -1:
                    out_dict['1e. Gross Salary: Reported total amount of salary received from other employer(s)'] = mtable.iloc[i,j+1]
        
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('2. Less: Allowance to the extent exempt under section 10')!= -1:
                    out_dict['2. Less: Allowance to the extent exempt under section 10'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(a) Travel concession or assistance under section')!= -1:
                    out_dict['2a. Travel concession or assistance under section 10(5)'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(b) Death-cum-retirement gratuity under section')!= -1:
                    out_dict['2b. Death-cum-retirement gratuity under section 10(10)'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(c) Commuted value of pension under section')!= -1:
                    out_dict['2c. Commuted value of pension under section 10(10A)'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(d) Cash equivalent of leave salary encashment')!= -1:
                    out_dict['2d. Cash equivalent of leave salary encashment under section 10(10AA)'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(e) House rent allowance under section')!= -1:
                    out_dict['2e. House rent allowance under section 10(13A)'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(f) Amount of any other exemption under section')!= -1:
                    out_dict['2f. Amount of any other exemption under section 10'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(g) Total amount of any other exemption under')!= -1:
                    out_dict['2g. Total amount of any other exemption under section 10'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(h) Total amount of exemption claimed under')!= -1:
                    out_dict['2h. Total amount of exemption claimed under section 10'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('3. Total amount of salary received from current employer')!= -1:
                    out_dict['3. Total amount of salary received from current employer [1(d)-2(h)]'] = mtable.iloc[i,j+2]
        
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(a) Standard deduction under section 16')!= -1:
                    out_dict['4a. Standard deduction under section 16(ia)'] = mtable.iloc[i,j][mtable.iloc[i,j].rfind(' ')+1: ]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(b) Entertainment allowance under section 16')!= -1:
                    out_dict['4b. Entertainment allowance under section 16(ii)'] = mtable.iloc[i,j][mtable.iloc[i,j].rfind(' ')+1: ]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(c) Tax on employment under section 16')!= -1:
                    out_dict['4c. Tax on employment under section 16(iii)'] = mtable.iloc[i,j][mtable.iloc[i,j].rfind(' ')+1: ]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('5. Total amount of deductions under section 16')!= -1:
                    out_dict['5. Total amount of deductions under section 16 [4(a)+4(b)+4(c)]'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('6. Income chargeable under the head "Salaries"')!= -1:
                    out_dict['6. Income chargeable under the head "Salaries" [(3+1(e)-5]'] = mtable.iloc[i,j+3]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(a) Income (or admissible loss) from house')!= -1:
                    out_dict['7a. Income (or admissible loss) from house property reported by employee offered for TDS'] = mtable.iloc[i,j][mtable.iloc[i,j].rfind(' ')+1: ]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(b) Income under the head Other Sources offered')!= -1:
                    out_dict['7b. Income under the head Other Sources offered for TDS'] = mtable.iloc[i,j][mtable.iloc[i,j].rfind(' ')+1: ]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('8. Total amount of other income reported by the employee')!= -1:
                    out_dict['8. Total amount of other income reported by the employee [7(a)+7(b)]'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('9. Gross total income')!= -1:
                    out_dict['9. Gross total income (6+8)'] = mtable.iloc[i,j+3]
                
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(a) Deduction in respect of life insurance premia, contributions to provident')!= -1:
                    out_dict['10a. Deduction in respect of life insurance premia, contributions to provident fund etc. under section 80C - Gross amount'] = mtable.iloc[i,j+2]
                    out_dict['10a. Deduction in respect of life insurance premia, contributions to provident fund etc. under section 80C - Deductible amount'] = mtable.iloc[i,j+3]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(b) Deduction in respect of contribution to certain pension funds')!= -1:
                    out_dict['10b. Deduction in respect of contribution to certain pension funds under section 80CCC - Gross amount'] = mtable.iloc[i,j+2]
                    out_dict['10b. Deduction in respect of contribution to certain pension funds under section 80CCC - Deductible amount'] = mtable.iloc[i,j+3]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('Deduction in respect of contribution by taxpayer to pension scheme')!= -1:
                    out_dict['10c. Deduction in respect of contribution by taxpayer to pension scheme under section 80CCD (1) - Gross amount'] = mtable.iloc[i,j+2]
                    out_dict['10c. Deduction in respect of contribution by taxpayer to pension scheme undersection 80CCD (1) - Deductible amount'] = mtable.iloc[i,j+3]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('Total deduction under section 80C, 80CCC and 80CCD(1)')!= -1:
                    out_dict['10d. Total deduction under section 80C, 80CCC and 80CCD(1) - Gross amount'] = mtable.iloc[i,j+2]
                    out_dict['10d. Total deduction under section 80C, 80CCC and 80CCD(1) - Deductible amount'] = mtable.iloc[i,j+3]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(e) Deductions in respect of amount paid/deposited to notified')!= -1:
                    out_dict['10e. Deductions in respect of amount paid/deposited to notified pension scheme under section 80CCD (1B) - Gross amount'] = mtable.iloc[i,j+2]
                    out_dict['10e. Deductions in respect of amount paid/deposited to notified pension scheme under section 80CCD (1B) - Deductible amount'] = mtable.iloc[i,j+3]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(f) Deduction in respect of contribution by Employer to pension scheme')!= -1:
                    out_dict['10f. Deduction in respect of contribution by Employer to pension scheme under section 80CCD (2) - Gross amount'] = mtable.iloc[i,j+2]
                    out_dict['10f. Deduction in respect of contribution by Employer to pension scheme under section 80CCD (2) - Deductible amount'] = mtable.iloc[i,j+3]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(g) Deduction in respect of health insurance premia under section 80D')!= -1:
                    out_dict['10g. Deduction in respect of health insurance premia under section 80D - Gross amount'] = mtable.iloc[i,j+2]
                    out_dict['10g. Deduction in respect of health insurance premia under section 80D - Deductible amount'] = mtable.iloc[i,j+3]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(h) Deduction in respect of interest on loan taken for higher education')!= -1:
                    out_dict['10h. Deduction in respect of interest on loan taken for higher education under section 80E - Gross amount'] = mtable.iloc[i,j+2]
                    out_dict['10h. Deduction in respect of interest on loan taken for higher education under section 80E - Deductible amount'] = mtable.iloc[i,j+3]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(i) Total Deduction in respect of donations to certain funds')!= -1:
                    out_dict['10i. Total Deduction in respect of donations to certain funds,charitable institutions etc. under section 80G - Gross amount'] = mtable.iloc[i,j+1]
                    out_dict['10i. Total Deduction in respect of donations to certain funds,charitable institutions etc. under section 80G - Qualifying amount'] = mtable.iloc[i,j+2]
                    out_dict['10i. Total Deduction in respect of donations to certain funds,charitable institutions etc. under section 80G - Deductible amount'] = mtable.iloc[i,j+3]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(j) Deduction in respect of interest on deposits in savings account')!= -1:
                    out_dict['10j. Deduction in respect of interest on deposits in savings account under section 80TTA - Gross amount'] = mtable.iloc[i,j+1]
                    out_dict['10j. Deduction in respect of interest on deposits in savings account under section 80TTA - Qualifying amount'] = mtable.iloc[i,j+2]
                    out_dict['10j. Deduction in respect of interest on deposits in savings account under section 80TTA - Deductible amount'] = mtable.iloc[i,j+3]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(k) Amount deductible under any other provision(s) of chapter VI-A')!= -1:
                    out_dict['10k. Amount deductible under any other provision(s) of chapter VI-A - Gross amount'] = mtable.iloc[i,j+1]
                    out_dict['10k. Amount deductible under any other provision(s) of chapter VI-A - Qualifying amount'] = mtable.iloc[i,j+2]
                    out_dict['10k. Amount deductible under any other provision(s) of chapter VI-A - Deductible amount'] = mtable.iloc[i,j+3]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('11. Aggregate of deductible amount under Chapter VI-A')!= -1:
                    out_dict['11. Aggregate of deductible amount under Chapter VI-A'] = mtable.iloc[i,j+3]
        
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('12. Total taxable income')!= -1:
                    out_dict['12. Total taxable income (9-11)'] = mtable.iloc[i,j+3]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('13. Tax on Total Income')!= -1:
                    out_dict['13. Tax on Total Income'] = mtable.iloc[i,j+3]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('14. Rebate under section 87A, if applicable')!= -1:
                    out_dict['14. Rebate under section 87A, if applicable'] = mtable.iloc[i,j+3]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('15. Surcharge, wherever applicable')!= -1:
                    out_dict['15. Surcharge, wherever applicable'] = mtable.iloc[i,j+3]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('16. Health and education cess')!= -1:
                    out_dict['16. Health and education cess'] = mtable.iloc[i,j+3]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('17. Tax payable (13+15+16-14)')!= -1:
                    out_dict['17. Tax payable (13+15+16-14)'] = mtable.iloc[i,j+3]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('18. Relief under section 89')!= -1:
                    out_dict['18. Relief under section 89'] = mtable.iloc[i,j+3]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('19. Net tax payable')!= -1:
                    out_dict['19. Net tax payable (17-18)'] = mtable.iloc[i,j+3]
    else:
        tables2 = tabula.read_pdf(pdf_path,pages='all',guess= True,lattice=False,stream=True,area=[68.5,19.3,764,575.8],columns=[394.8,498.4],pandas_options={'header': None})
###############single appended file
        mtable = pd.concat(tables2)
        mtable=mtable.reset_index()
        mtable=mtable.drop(columns=['index'])
        out_dict = {}
########################################second type of file        
        for i in range(len(mtable)) :
            for j in range(len(mtable.columns)) :
                
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(a) Salary as per provisions contained in section 17(1)')!= -1:
                    out_dict['1a. Gross Salary: Salary as per provisions contained in section 17(1)'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(b)')!= -1 and mtable.iloc[i-1,j]=="Value of perquisites under section 17(2) (as per Form No. 12BA,":
                    out_dict['1b. Gross Salary: Value of perquisites under section 17(2)'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(c)')!= -1 and mtable.iloc[i-1,j]=="Profits in lieu of salary under section 17(3) (as per Form No.":
                    out_dict['1c. Gross Salary: Profits in lieu of salary under section 17(3)'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j]=='(d) Total' and mtable.iloc[i-1,j]=="12BA, wherever applicable)":
                    out_dict['1d. Gross Salary: Total'] = mtable.iloc[i,j+2]        
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(e) Reported total amount of salary received from other employer(s)')!= -1:
                    out_dict['1e. Gross Salary: Reported total amount of salary received from other employer(s)'] = mtable.iloc[i,j+2]
        
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('2. Less: Allowances to the extent exempt under section 10')!= -1:
                    out_dict['2. Less: Allowance to the extent exempt under section 10'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(a) Travel concession or assistance under section 10(5)')!= -1:
                    out_dict['2a. Travel concession or assistance under section 10(5)'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(b) Death-cum-retirement gratuity under section 10(10)')!= -1:
                    out_dict['2b. Death-cum-retirement gratuity under section 10(10)'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(c) Commuted value of pension under section 10(10A)')!= -1:
                    out_dict['2c. Commuted value of pension under section 10(10A)'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(d)')!= -1 and mtable.iloc[i-1,j]=="Cash equivalent of leave salary encashment under section 10":
                    out_dict['2d. Cash equivalent of leave salary encashment under section 10(10AA)'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(e) House rent allowance under section 10(13A)')!= -1:
                    out_dict['2e. House rent allowance under section 10(13A)'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(f)')!= -1 and (mtable.iloc[i-1,j]=="[Note: Break-up to be prepared by employer and issued to" or mtable.iloc[i-1,j]=="[Note: Break-up to be prepared by employee and issued to"):
                    out_dict['2f. Amount of any other exemption under section 10'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(g) Total amount of any other exemption under section 10')!= -1:
                    out_dict['2g. Total amount of any other exemption under section 10'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(h)')!= -1 and mtable.iloc[i-1,j]=="Total amount of exemption claimed under section 10 [2(a)+2(b)":
                    out_dict['2h. Total amount of exemption claimed under section 10'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('3. Total amount of salary received from current employer [1(d)-2(h)]')!= -1:
                    out_dict['3. Total amount of salary received from current employer [1(d)-2(h)]'] = mtable.iloc[i,j+2]
        
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(a) Standard deduction under section 16(ia)')!= -1:
                    out_dict['4a. Standard deduction under section 16(ia)'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(b) Entertainment allowance under section 16(ii)')!= -1:
                    out_dict['4b. Entertainment allowance under section 16(ii)'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(c) Tax on employment under section 16(iii)')!= -1:
                    out_dict['4c. Tax on employment under section 16(iii)'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('5. Total amount of deductions under section 16 [4(a)+4(b)+4(c)]')!= -1:
                    out_dict['5. Total amount of deductions under section 16 [4(a)+4(b)+4(c)]'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('6. Income chargeable under the head "Salaries" [(3+1(e)-5]')!= -1:
                    out_dict['6. Income chargeable under the head "Salaries" [(3+1(e)-5]'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(a)')!= -1 and mtable.iloc[i-1,j]=="Income (or admissible loss) from house property reported by":
                    out_dict['7a. Income (or admissible loss) from house property reported by employee offered for TDS'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(b) Income under the head Other Sources offered for TDS')!= -1:
                    out_dict['7b. Income under the head Other Sources offered for TDS'] = mtable.iloc[i,j+1]
                if type(mtable.iloc[i,j])==str and j==0 and mtable.iloc[i,j].find('8.')!= -1 and mtable.iloc[i-1,j]=="Total amount of other income reported by the employee [7(a)+7":
                    out_dict['8. Total amount of other income reported by the employee [7(a)+7(b)]'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('9. Gross total income (6+8)')!= -1:
                    out_dict['9. Gross total income (6+8)'] = mtable.iloc[i,j+2]
                
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(a)')!= -1 and mtable.iloc[i-1,j]=="Deduction in respect of life insurance premia, contributions to":
                    out_dict['10a. Deduction in respect of life insurance premia, contributions to provident fund etc. under section 80C - Gross amount'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(b) under section 80CCC')!= -1:
                    out_dict['10b. Deduction in respect of contribution to certain pension funds under section 80CCC - Gross amount'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(c) scheme under section 80CCD (1)')!= -1:
                    out_dict['10c. Deduction in respect of contribution by taxpayer to pension scheme under section 80CCD (1) - Gross amount'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(d) Total deduction under section 80C, 80CCC and 80CCD(1)')!= -1:
                    out_dict['10d. Total deduction under section 80C, 80CCC and 80CCD(1) - Gross amount'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(e)')!= -1 and mtable.iloc[i-1,j]=="pension scheme under section 80CCD (1B)":
                    out_dict['10e. Deductions in respect of amount paid/deposited to notified pension scheme under section 80CCD (1B) - Gross amount'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(f) scheme under section 80CCD (2)')!= -1:
                    out_dict['10f. Deduction in respect of contribution by Employer to pension scheme under section 80CCD (2) - Gross amount'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(g)')!= -1 and mtable.iloc[i-1,j]=="Deduction in respect of health insurance premia under section":
                    out_dict['10g. Deduction in respect of health insurance premia under section 80D - Gross amount'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(h) education')!= -1:
                    out_dict['10h. Deduction in respect of interest on loan taken for higher education under section 80E - Gross amount'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(i)')!= -1 and mtable.iloc[i-1,j]=="Total Deduction in respect of donations to certain funds,":
                    out_dict['10i. Total Deduction in respect of donations to certain funds,charitable institutions etc. under section 80G - Gross amount'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(j)')!= -1 and mtable.iloc[i-1,j]=="Deduction in respect of interest on deposits in savings account":
                    out_dict['10j. Deduction in respect of interest on deposits in savings account under section 80TTA - Gross amount'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(k)')!= -1 and (mtable.iloc[i-1,j]=="[Note: Break-up to be prepared by employer and issued to" or mtable.iloc[i-1,j]=="[Note: Break-up to be prepared by employee and issued to"):
                    out_dict['10k. Amount deductible under any other provision(s) of chapter VI-A - Gross amount'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('(l)')!= -1 and mtable.iloc[i-1,j]=="Total of amount deductible under any other provision(s) of":
                    out_dict['10l. Total of amount deductible under any other provision(s) of chapter VI-A'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('11. (e)+10(f)+10(g)+10(h)+10(i)')!= -1:
                    out_dict['11. Aggregate of deductible amount under Chapter VI-A'] = mtable.iloc[i,j+2]
        
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('12. Total taxable income (9-11)')!= -1:
                    out_dict['12. Total taxable income (9-11)'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('13. Tax on total income')!= -1:
                    out_dict['13. Tax on Total Income'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('14. Rebate under section 87A, if applicable')!= -1:
                    out_dict['14. Rebate under section 87A, if applicable'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('15. Surcharge, wherever applicable')!= -1:
                    out_dict['15. Surcharge, wherever applicable'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('16. Health and education cess')!= -1:
                    out_dict['16. Health and education cess'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('17. Tax payable (13+15+16-14)')!= -1:
                    out_dict['17. Tax payable (13+15+16-14)'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('18. Less: Relief under section 89 (attach details)')!= -1:
                    out_dict['18. Relief under section 89'] = mtable.iloc[i,j+2]
                if type(mtable.iloc[i,j])==str and mtable.iloc[i,j].find('19. Net tax payable (17-18)')!= -1:
                    out_dict['19. Net tax payable (17-18)'] = mtable.iloc[i,j+2]

 

#############################Part A starts from here
    
    #list for quater attributes
    quater_no=[]
    amount_credited=[]
    reciept_id=[]
    amount_paid=[]
    tax_deducted=[]
    tax_remitted=[]
    
    #lists needed for challan
    challan_no=[]
    tax_deposited_challan=[]
    bank_branch_bsr=[]
    date=[]
    challan_serial_no=[]
    status_match_OLTAS=[]
##############################################first type of file    
    tables = tabula.read_pdf(pdf_path,pages=[1,2],stream=True,pandas_options={'header': None})
    
    if len(tables)>1:
        pass
    else:
        #################second type of file
        tables = tabula.read_pdf(pdf_path,pages=[1,2,3],stream=True,pandas_options={'header': None})
        
        
        
    if len(tables)==0:
        print("This is an image-based statement, hence, cannot be digitized here")
        return
    
        
        
    for i in range(len(tables)) :
        # print(i)
        for j in range(len(tables[i])) :
            for k in range(len(tables[i].columns)) :
                if j<(len(tables[i])):
                    if type(tables[i].iloc[j,k])==str and tables[i].iloc[j,k]=='Certificate No.':
                        cert_no=tables[i].iloc[j,k+1]
                    if type(tables[i].iloc[j,k])==str and tables[i].iloc[j,k].startswith('Last updated'):
                        last_update_date=tables[i].iloc[j,k].rsplit(' ')[-1]
                    if type(tables[i].iloc[j,k])==str and tables[i].iloc[j,k]=='PAN of the Deductor':
                        pan_deductor=tables[i].iloc[tables[i].iloc[j+1:,k].first_valid_index(),k]
                        
                    #check for (if applicable) ; couldn't use firstvalidindex      || apply isalpha()
                    if type(tables[i].iloc[j,k])==str and tables[i].iloc[j,k].startswith('TAN of the Deductor'):
                        tan_deductor = tables[i].iloc[j+2,k].split(' ')[0]
                        pan_employee=tables[i].iloc[j+2,k].split(' ')[1]
                    if type(tables[i].iloc[j,k])==str and tables[i].iloc[j,k]=='From To':
                        try:
                            assessment_year,period_from,period_to=tables[i].iloc[tables[i].iloc[j+1:,k].first_valid_index(),k].split(' ')
                        except:
                            assessment_year=tables[i].iloc[tables[i].iloc[j+1:,k].first_valid_index(),k].split(' ')[0]
                            period_from,period_to=tables[i].iloc[tables[i].iloc[j+1:,k].first_valid_index()+1,k].split(' ')
                            
                    if type(tables[i].iloc[j,k])==str and tables[i].iloc[j,k]=='Quarter(s)':
                        #q here stands for quaters
                        valid_qrow=tables[i].iloc[int(j+1):,k].first_valid_index()
                        #files being read differently
                        if len(tables[i].columns)==3:
                            while type(tables[i].iloc[valid_qrow,k])==str and tables[i].iloc[valid_qrow,k]!='Total (Rs.)':
                                details=tables[i].iloc[valid_qrow,k+2].split(' ')
                                quater_no.append(tables[i].iloc[valid_qrow,k])
                                reciept_id.append(details[0])
                                amount_credited.append(details[1])
                                tax_deducted.append(details[2])
                                tax_remitted.append(details[3])
                                valid_qrow+=1
                            total_tax_deducted=tables[i].iloc[valid_qrow,k+2].split()[1]
                        else:
                            while type(tables[i].iloc[valid_qrow,k])==str and tables[i].iloc[valid_qrow,k]!='Total (Rs.)':
                                details=tables[i].iloc[valid_qrow,k+2].split(' ')
                                quater_no.append(tables[i].iloc[valid_qrow,k])
                                reciept_id.append(details[0])
                                amount_credited.append(details[1])
                                tax_deducted.append(details[2])
                                if pd.isna(tables[i].iloc[valid_qrow,k+3])==False:
                                    tax_remitted.append(tables[i].iloc[valid_qrow,k+3])
                                else:
                                    tax_remitted.append(details[3])
                                valid_qrow+=1
                            total_tax_deducted=tables[i].iloc[valid_qrow,k+2].split()[1]
                    if type(tables[i].iloc[j,k])==str and tables[i].iloc[j,k].lower()=='Name and address of the employer'.lower():
                        employer_name=tables[i].iloc[j+1,k-1]
                        valid_row=tables[i].iloc[int(j+2):,int(k-1)].first_valid_index()
                        
                        employer_info=''
                        try:
                            while type(tables[i].iloc[valid_row,k-1])==str and tables[i].iloc[valid_row-1,k]!='The Commissioner of Income Tax (TDS)':
                                employer_info+=(tables[i].iloc[valid_row,k-1] + '\n')
                                valid_row=tables[i].iloc[int(valid_row+1):,k-1].first_valid_index()
                        except:
                            employer_info=''
                            # print("exception handling")
                            valid_row=tables[i].iloc[int(j+2):,int(k-1)].first_valid_index()
                            while type(tables[i].iloc[valid_row,k-1])==str and tables[i].iloc[valid_row-2,k]!='The Commissioner of Income Tax (TDS)':
                                employer_info+=(tables[i].iloc[valid_row,k-1] + '\n')
                                valid_row=tables[i].iloc[int(valid_row+1):,k-1].first_valid_index()
                            
                        #employer_address,employer_contact,employer_mail,_= employer_info.rsplit('\n',3)
                    if type(tables[i].iloc[j,k])==str and tables[i].iloc[j,k].lower()=='Name and address of the employee'.lower():
                        valid_row=tables[i].iloc[int(j+2):,k].first_valid_index()
                        employee_name=tables[i].iloc[valid_row,k]
                        valid_row=tables[i].iloc[int(valid_row+1):,k].first_valid_index()
                        employee_address=''
                        while type(tables[i].iloc[valid_row,k])==str and tables[i].iloc[valid_row,k].lower()!='Employee Reference No.'.lower():
                            employee_address+=(tables[i].iloc[valid_row,k] + '\n\r')
                            valid_row=tables[i].iloc[int(valid_row+1):,k].first_valid_index()
                    
                    #challans and CIN info ===> assuming min number of columns are 3 or 4
                    if type(tables[i].iloc[j,k])==str and tables[i].iloc[j,k].startswith('Branch'):
                        j+=1
        
                        if pd.isna(tables[i].iloc[j,k-1]):
                            # left column is nan ====> branch_bsr and amount are in same cell
                            if k<(len(tables[i].columns)-1):
                                #cloumn right to branch_bsr exists
                                if pd.isna(tables[i].iloc[j,k+1]):
                                    #left_col nan; right column exist ; right column is nan
                                    #all four are in same cell
                                    while j<len(tables[i]) and type(tables[i].iloc[j,k])==str and tables[i].iloc[j,k-2]!='Total (Rs.)' :
                                        challan_no.append(tables[i].iloc[(j),k-2])
                                        info=tables[i].iloc[j,k].split(' ')
                                        tax_deposited_challan.append(info[0])
                                        bank_branch_bsr.append(info[1])
                                        date.append(info[2])
                                        challan_serial_no.append(info[3])
                                        status_match_OLTAS.append(info[4])
                                        j+=1
                                        # print('first')
                                
                                else:
                                    #left_col nan; right_col exists ; is not nan
                                    #amount and branch_bsr same and rest are in next cell
                                    while j<len(tables[i]) and type(tables[i].iloc[j,k])==str and tables[i].iloc[j,k-2]!='Total (Rs.)':
                                        challan_no.append(tables[i].iloc[(j),k-2])
                                        info=tables[i].iloc[j,k].split(' ')
                                        tax_deposited_challan.append(info[0])
                                        bank_branch_bsr.append(info[1])
                                        info=tables[i].iloc[j,k+1].split(' ')
                                        date.append(info[0])
                                        challan_serial_no.append(info[1])
                                        status_match_OLTAS.append(info[2])
                                        j+=1
                                        # print('second')
                                        
                        
                            else:
                                #left col nan; right column does not exits ==> all four in same cell
                                while (j<len(tables[i]) and (type(tables[i].iloc[j,k])==str) and (tables[i].iloc[j,k-2]!='Total (Rs.)')):
                                        challan_no.append(tables[i].iloc[(j),k-2])
                                        info=tables[i].iloc[j,k].split(' ')
                                        tax_deposited_challan.append(info[0])
                                        bank_branch_bsr.append(info[1])
                                        date.append(info[2])
                                        challan_serial_no.append(info[3])
                                        status_match_OLTAS.append(info[4])
                                        j+=1
                                        # print('third')
                                        
                                        
    
                                        
                                        
                              
                            
                        else:
                            # print("in the loop 1")
                            #left column is not na ===> amount and branch_bsr in different cells
                            if k<(len(tables[i].columns)-1):
                                # print("in the loop")
                                #left column not na ; right cloumn exists; 
                                if pd.isna(tables[i].iloc[j,k+1]):
                                    #left col not nan; right col exists; right column nan
                                    #
                                    while j<len(tables[i]) and type(tables[i].iloc[j,k])==str and tables[i].iloc[j,k-2]!='Total (Rs.)' :
                                        challan_no.append(tables[i].iloc[(j),k-2])
                                        tax_deposited_challan.append(tables[i].iloc[j,k-1])
                                        info=tables[i].iloc[j,k].split(' ')
                                        bank_branch_bsr.append(info[0])
                                        date.append(info[1])
                                        challan_serial_no.append(info[2])
                                        status_match_OLTAS.append(info[3])
                                        j+=1
                                        # print('fourth')
                                        
                                        
                                else:
                                    #amount , branch_bsr are in separate cells and rest info together in last column 
                                    while j<len(tables[i]) and (type(tables[i].iloc[j,k])==str) and (tables[i].iloc[j,k-2]!='Total (Rs.)'):
                                        challan_no.append(tables[i].iloc[(j),k-2])
                                        tax_deposited_challan.append(tables[i].iloc[j,k-1])
                                        bank_branch_bsr.append(tables[i].iloc[j,k])
                                        info=tables[i].iloc[j,k+1].split(' ')
                                        date.append(info[0])
                                        challan_serial_no.append(info[1])
                                        status_match_OLTAS.append(info[2])
                                        j+=1
                                        # print('fifth')
                                    
                                    
                            else:
                                #right column does not exist ==>
                                #amount in separate cell and rest info is together
                                while j<len(tables[i]) and (type(tables[i].iloc[j,k])==str) and (tables[i].iloc[j,k-2]!='Total (Rs.)') :
                                        challan_no.append(tables[i].iloc[(j),k-2])
                                        tax_deposited_challan.append(tables[i].iloc[j,k-1])
                                        info=tables[i].iloc[j,k].split(' ')
                                        bank_branch_bsr.append(info[0])
                                        date.append(info[1])
                                        challan_serial_no.append(info[1])
                                        status_match_OLTAS.append(info[3])
                                        j+=1
                                        # print('sixth')
                else:
                    # print("I was at break")
                    break
    
    
    # print(i)
    # print("ok")
    data={}
    data['Sl No']=challan_no
    data['Tax deposited']=tax_deposited_challan
    data['BSR Code']=bank_branch_bsr
    data['Tax deposited Date']=date
    data['Challan Serial No']=challan_serial_no
    data['Status Match OLTAS']=status_match_OLTAS
    data['Assessment Year'] = assessment_year
    challan=pd.DataFrame(data)
    #challan=pd.DataFrame(data.items(),columns=['parameter','values'])
    
    
    data1={}
    data1['Certification No']=cert_no
    data1['Last updated on']=last_update_date
    data1['Pan of the Deductor']=pan_deductor
    data1['Tan of the Deductor']=tan_deductor
    data1['Pan of the Employee']=pan_employee
    data1['Assessment Year']=assessment_year
    data1['Period with the Employer - From']=period_from
    data1['Period with the Employer - To']=period_to
    data1['Employer Name']=employer_name
    data1['Employer Address']=employer_info.replace('\n',' ').replace('\r',' ')
    #data1['Employer Address']=employer_address
    #data1['Employer Contact']=employer_contact
    #data1['Employer Mail']=employer_mail
    data1['Employee Name']=employee_name
    data1['Employee Address']=employee_address.replace('\n',' ').replace('\r',' ')
    #data1['Total_tax_deducted']=total_tax_deducted
    data_df=pd.DataFrame(data1.items(),columns=['parameters','values'])
    
    
    quater_dict={}
    quater_dict['Quarter']=quater_no
    quater_dict['Receipt Number']=reciept_id
    quater_dict['Amount paid/credited']=amount_credited
    quater_dict['Tax deducted']=tax_deducted
    quater_dict['Tax deposited/remitted']=tax_remitted
    quater_dict['Assessment Year'] = assessment_year
    #quater_dict['Total Tax']=total_tax_deducted
    quater_df=pd.DataFrame(quater_dict)
    #quater_df=pd.DataFrame(quater_dict.items(),columns=['parameteres','values'])
    
    
    # converting the final dictionary into a dataframe
    out_dict['Assessment Year'] = assessment_year
    df_out = pd.DataFrame(out_dict.items(), columns=['Parameters','Information'])    


    return data_df, quater_df, challan, df_out
    
