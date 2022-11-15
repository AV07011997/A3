# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 12:49:58 2021

@author: PrudhviJonnalagadda
"""

import tabula
import glob

# tables = []
banknames = []
def bank_name(pdf_path):
    file_name=pdf_path.split('\\')[-1][:-4]
    passcode=''
    
    global tables
    tables = tabula.read_pdf(pdf_path, pages=1,password=passcode,area=[0,27,777,631])
    
    try:
        ifsc=tables[0].loc[15][3][:4]
        if ifsc=="HDFC":
            bankname="HDFC"
            banknames.append(bankname)
            print(bankname)
    except:
        try:
            ifsc=tables[0].loc[15][4][:4]
            if ifsc=="HDFC":
                bankname="HDFC"
                banknames.append(bankname)
                print(bankname)
        except:
            if tables[0].loc[14][2].find('HDFC') != -1:
                bankname = 'HDFC'
                banknames.append(bankname)
        
    
    
    


files = glob.glob(r"D:\prudhvi\sources-a3-kit\_Statements testing\hdfc\all\*.pdf")

for i in range(len(files)):
    bank_name(files[i])