import pandas as pd
import numpy as np
import tabula
from datetime import datetime as dt
import glob

def corporation_digitization(pdf_path):
    file_name=pdf_path.split('\\')[-1][:-4]
    passcode=''
    tables =  tabula.read_pdf(pdf_path, pages=1,password=passcode, area=[0,0,576,775],pandas_options={'header':None})
    print("xx")
    # print(tables)

    if len(tables)!=0 and len(tables[0])!=10 and len(tables[0])!=12 and len(tables[0])!=18 and len(tables[0])>11:
        Ifcs=tables[0][2][12][0:4]
        bankname=""
        if Ifcs=="CORP":
            bankname="Corporation Bank"
            print(bankname)
            return 1
    return 0





def sbi_digitization(pdf_path):
    passwrd=''
    tables = tabula.read_pdf(pdf_path, pages='1', password=passwrd, area=[0,0,330,565], pandas_options={'header':None})
    print("zz")


    if len(tables)!=0 and len(tables[0])!=0 and len(tables[0])!=10 and len(tables[0])!=15 and len(tables[0][0])>6:

        if len(str(tables[0][0][0]))>20:
            if tables[0][0][0][10:]=="State Bank of India":
                bankname="State Bank of India"
                print(bankname)
                return 3

        Ifcs7=tables[0][0][3]


        Ifcs7=str(Ifcs7)
        # print(Ifcs7[0:3] + " SS")
        if Ifcs7[0:3]=="IFS":
            print("xxx")
            Ifcs7=Ifcs7.split(":")[1][0:4]
            if Ifcs7=="SBIN":
                bankname="State Bank of India"
                print(bankname)
                return 3


        Ifcs2=tables[0][0][13]


        Ifcs2=str(Ifcs2)

        if Ifcs2[0:3]=="IFS":
            print("xxx")
            Ifcs2=Ifcs2.split(":")[1][0:4]
            if Ifcs2=="SBIN":
                bankname="State Bank of India"
                print(bankname)
                return 3


        Ifcs1=tables[0][0][13]

        Ifcs1=str(Ifcs1)
        if Ifcs1[0:3]=="IFS":
            Ifcs1=Ifcs1.split(":")[1][1:5]
        if Ifcs1=="SBIN":
            bankname="State Bank of India"
            print(bankname)
            return 3




        bankname=""
        Ifcs=tables[0][0][14]


        Ifcs=str(Ifcs) + ":"
        if Ifcs[0:3]=="IFS":

            Ifcs=Ifcs.split(":")[1][0:4]
        if Ifcs=="SBIN":
            bankname="State Bank of India"
            print(bankname)
            return 3


        Ifcs4=tables[0][0][14]

        Ifcs4=str(Ifcs4)
        if Ifcs4[0:3]=="IFS":
            Ifcs4=tables[0][1][14]
            Ifcs4=str(Ifcs4)
            Ifcs4=Ifcs4.split(":")[1][0:4]
        if Ifcs4=="SBIN":
            bankname="State Bank of India"
            print(bankname)
            return 3

        Ifcs5=tables[0][0][15]

        Ifcs5=str(Ifcs5)
        if Ifcs5[0:3]=="IFS":
            Ifcs5=tables[0][1][15]
            Ifcs5=str(Ifcs5)
            Ifcs5=Ifcs5.split(":")[1][0:4]
        if Ifcs5=="SBIN":
            bankname="State Bank of India"
            print(bankname)
            return 3

        Ifcs6=tables[0][2][7]

        Ifcs6=str(Ifcs6)
        if Ifcs6[0:3]=="IFS":
            Ifcs6=Ifcs6.split(":")[1][1:5]
        if Ifcs6=="SBIN":
            bankname="State Bank of India"
            print(bankname)
            return 3

    return 0

def hdfc_digitization(pdf_path):
    file_name=pdf_path.split('\\')[-1][:-4]
    passwrd=''
    tables = tabula.read_pdf(pdf_path, password=passwrd, area=[86, 337, 193, 628], pages='1', pandas_options={'header': None})
    print("qq")
    print(tables)


    if len(tables)!=0 and len(tables[0])!=18 and len(tables[0])!=10 and len(tables[0])!=15 and len(tables[0])>9 :

        Ifcs1=tables[0][0][10].split(":")[1][1:5]


        print(Ifcs1)
        bankname=""
        if Ifcs1=="HDFC":
            bankname="Housing Development Finance Corporation Limited"
            print(bankname)
            return 4

        Ifcs=tables[0][2][10][0:4]
        bankname=""
        if Ifcs=="HDFC":
            bankname="Housing Development Finance Corporation Limited"
            print(bankname)
            return 4
        elif tables[0][2][9][0:4]=="HDFC":
            bankname = "Housing Development Finance Corporation Limited"
            print(bankname)
            return 4
    return 0


# def idfc_digitization(pdf_path):
#     passcode = ''
#     tables = tabula.read_pdf(pdf_path, pages='1', password=passcode,area=[80,46,579,535],stream=True,guess=False,pandas_options={'header':None,'dtype': str})
#     print("qq")
#     print(tables)
#
#     if len(tables) != 0 and len(tables[0]) != 18 and len(tables[0]) != 10 and len(tables[0]) != 15 and len(
#             tables[0]) > 9:
#
#         Ifcs1 = tables[0][0][10].split(":")[1][1:5]
#
#         print(Ifcs1)
#         bankname = ""
#         if Ifcs1 == "ICICI":
#             bankname = "Industrial Credit and Investment Corporation of India Limited"
#             print(bankname)
#             return 5
#
#         Ifcs = tables[0][2][10][0:4]
#         bankname = ""
#         if Ifcs == "ICICI":
#             bankname = "Industrial Credit and Investment Corporation of India Limited"
#             print(bankname)
#             return 5
#     return 0


# def icici_digitization(pdf_path):
#     passwrd = ''
#     tables = tabula.read_pdf(pdf_path, password=passwrd, pages='1',area=[4,2,270,650],pandas_options={'header': True})
#     print("qq")
#     print(tables)
#
#     if len(tables) != 0 and len(tables[0]) != 18 and len(tables[0]) != 10 and len(tables[0]) != 15 and len(
#             tables[0]) > 9:
#
#         bank_name = tables[0].iloc[2][1][18:28]
#
#         print(Ifcs1)
#         bankname = ""
#         if Ifcs1 == "ICICI":
#             bankname = "Industrial Credit and Investment Corporation of India Limited"
#             print(bankname)
#             return 5
#
#         Ifcs = tables[0][2][10][0:4]
#         bankname = ""
#         if Ifcs == "ICICI":
#             bankname = "Industrial Credit and Investment Corporation of India Limited"
#             print(bankname)
#             return 5
#     return 0

def bank_extraction(files):
    # files = glob.glob(r"d:\bank\*.pdf")

    # for i in range(len(files)):
    #     print(files[i])

    count1 = 0;
    count2 = 0;
    count3 = 0;
    count4 = 0;
    count5 = 0;
    try:
        count4 = corporation_digitization(files)
        if count4 == 1:
            return 'Corporation';

        count2 = sbi_digitization(files)
        if count2 == 3:
            return 'SBI';

        count3 = hdfc_digitization(files)
        if count3 == 4:
            return 'HDFC';
        #count5 = icici_digitization(files)
        # if count5 == 5:
        #     return 'ICICI';
        # count5 = idfc_digitization(files[0])
        # if count5 == 6:
        #     return 'IDFC';

    except Exception as e:
        print(e)
        print("\nThis statement cannot be digitized.\n")





# files = glob.glob(r"D:\bank\765604_1_aaditya banking.pdf")
# bank_extraction(files)