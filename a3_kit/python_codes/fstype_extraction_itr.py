import pandas as pd
import numpy as np
import tabula
import glob



def form16_digitization(pdf_path):
    try:
        tables1 = tabula.read_pdf(pdf_path,pages=1,pandas_options={'header': None},multiple_tables=True)
        tables2 = tabula.read_pdf(pdf_path, pages=[3, 4], guess=True, lattice=False, stream=True, area=[29, 19, 785, 576],columns=[375, 441, 509], pandas_options={'header': None})
    except Exception as e:
        return 0
    if ((len(tables1) !='' or len(tables1)!=None) or (len(tables2)!='' or len(tables2) !=None)):
        try:
            file_type = tables1[0][0][0]
            file_sub_type_part_A = tables1[0][0][2]
            file_sub_type_part_B = tables2[0][0][0]
            if file_type == 'FORM NO. 16':
                return 1
            elif file_sub_type_part_A == 'PART A':
                return 1
            elif file_sub_type_part_B == 'PART B (Annexure)':
                return 1
            else:
                return 0
        except Exception as e:
                return 0


def form26as_digitization(pdf_path):
    try:
        tables = tabula.read_pdf(pdf_path,pages=1,area=[20,2,420,382],pandas_options={'header': True})
    except Exception as e:
        return 0
    if ((len(tables) != '' or len(tables) != None)):
        try:
            file_type = tables[0].iloc[0][0]
            if file_type == 'Form 26AS':
                return 1
            else:
                return 0
        except Exception as e:
                return 0

def itrv_digitization(pdf_path):
    try:
        tables = tabula.read_pdf(pdf_path,pages=1,area=[20,2,420,382],pandas_options={'header': True})
    except Exception as e:
        return 0
    if ((len(tables) != '' or len(tables) != None)):
        try:
            file_type = tables[0].iloc[0][0][0:25]
            if file_type == 'INDIAN INCOME TAX RETURN ':
                return 1
            else:
                return 0
        except Exception as e:
                return 0

def itr_extraction(files):
    count1 = 0;
    count2 = 0;
    count3 = 0;

    try:
        count1 = form16_digitization(files)
        if count1 == 1:
            return 'form16';

        count2 = form26as_digitization(files)
        if count2 == 1:
            return 'form26as';

        count3 = itrv_digitization(files)
        if count3 == 1:
            return 'itrv';

    except Exception as e:
        print(e)
        print("\nThis statement cannot be digitized.\n")



# try :
#     itr_extraction(r"D:\itr\765589_21_26AS_2017-18 (1).pdf")
#
# except :
#     print("\nThis statement cannot be digitized.\n")
