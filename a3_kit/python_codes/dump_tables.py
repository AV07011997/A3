

import pandas as pd

cacc = pd.read_excel(r"D:\updated\bureau_data\cibil\account_segment_tl_1.xlsx")
cadd = pd.read_excel(r"D:\updated\bureau_data\cibil\address_segment.xlsx")
cname = pd.read_excel(r"D:\updated\bureau_data\cibil\cibil_name_segment.xlsx")
cscore = pd.read_excel(r"D:\updated\bureau_data\cibil\cibil_score_segment.xlsx")
cenq = pd.read_excel(r"D:\updated\bureau_data\cibil\enquiry_segment_iq.xlsx")
cref = pd.read_excel(r"D:\updated\bureau_data\cibil\ref_dtl.xlsx")

cacc = cacc.rename(columns = {'CIBIL_ID': 'BUREAU_ID', 'DATE_CIBIL_REMARK_CODE':'DATE_BUREAU_REMARK_CODE'})

cadd = cadd.rename(columns = {'CIBIL_ID': 'BUREAU_ID', 'DATE_OF_ADDR_REPORTED_TO_CIBIL':'DATE_OF_ADDR_REPORTED_TO_BUREAU'})

cenq = cenq.rename(columns = {'CIBIL_ID': 'BUREAU_ID'})

cname = cname.rename(columns = {'CIBIL_ID': 'BUREAU_ID', 'DATE_OF_ENTRY_CIBIL_REMARK_CODE':'DATE_OF_ENTRY_BUREAU_REMARK_CODE', 'CIBIL_REMARK_CODE':'BUREAU_REMARK_CODE'})

cref = cref.rename(columns = {'CIBIL_ID': 'BUREAU_ID', 'CIBIL_DATE':'BUREAU_DATE', 'CIBIL_RESULT':'BUREAU_RESULT','CIBIL_REPORT_PATH':'BUREAU_REPORT_PATH'})

cscore = cscore.rename(columns = {'CIBIL_ID': 'BUREAU_ID'})


crifacc = pd.read_excel(r"D:\updated\bureau_data\crif\account_segment_tl_1.xlsx")
crifadd = pd.read_excel(r"D:\updated\bureau_data\crif\address_segment.xlsx")
crifname = pd.read_excel(r"D:\updated\bureau_data\crif\crif_name_segment.xlsx")
crifscore = pd.read_excel(r"D:\updated\bureau_data\crif\crif_score_segment.xlsx")
crifenq = pd.read_excel(r"D:\updated\bureau_data\crif\enquiry_segment_iq.xlsx")
crifref = pd.read_excel(r"D:\updated\bureau_data\crif\ref_dtl.xlsx")


crifacc = crifacc.rename(columns = {'CRIF_ID': 'BUREAU_ID', 'DATE_CRIF_REMARK_CODE':'DATE_BUREAU_REMARK_CODE'})

crifadd = crifadd.rename(columns = {'CIBIL_ID': 'BUREAU_ID', 'DATE_OF_ADDR_REPORTED_TO_CRIF':'DATE_OF_ADDR_REPORTED_TO_BUREAU'})

crifenq = crifenq.rename(columns = {'CRIF_ID': 'BUREAU_ID'})

crifname = crifname.rename(columns = {'CRIF_ID': 'BUREAU_ID', 'DATE_OF_ENTRY_CRIF_REMARK_CODE':'DATE_OF_ENTRY_BUREAU_REMARK_CODE', 'CRIF_REMARK_CODE':'BUREAU_REMARK_CODE'})

crifref = crifref.rename(columns = {'CRIF_ID': 'BUREAU_ID', 'CRIF_DATE':'BUREAU_DATE', 'CRIF_RESULT':'BUREAU_RESULT','CRIF_REPORT_PATH':'BUREAU_REPORT_PATH'})

crifscore = crifscore.rename(columns = {'CRIF_ID': 'BUREAU_ID'})


eqacc = pd.read_excel(r"D:\updated\bureau_data\equifax\account_segment_tl_1.xlsx")
eqadd = pd.read_excel(r"D:\updated\bureau_data\equifax\address_segment.xlsx")
eqname = pd.read_excel(r"D:\updated\bureau_data\equifax\equifax_name_segment.xlsx")
eqscore = pd.read_excel(r"D:\updated\bureau_data\equifax\equifax_score_segment.xlsx")
eqenq = pd.read_excel(r"D:\updated\bureau_data\equifax\enquiry_segment_iq.xlsx")
eqref = pd.read_excel(r"D:\updated\bureau_data\equifax\ref_dtl.xlsx")


eqacc = crifacc.rename(columns = {'CRIF_ID': 'BUREAU_ID', 'DATE_CRIF_REMARK_CODE':'DATE_BUREAU_REMARK_CODE'})

eqadd = crifadd.rename(columns = {'CIBIL_ID': 'BUREAU_ID', 'DATE_OF_ADDR_REPORTED_TO_CRIF':'DATE_OF_ADDR_REPORTED_TO_BUREAU'})

eqenq = crifenq.rename(columns = {'CRIF_ID': 'BUREAU_ID'})

crifname = crifname.rename(columns = {'CRIF_ID': 'BUREAU_ID', 'DATE_OF_ENTRY_CRIF_REMARK_CODE':'DATE_OF_ENTRY_BUREAU_REMARK_CODE', 'CRIF_REMARK_CODE':'BUREAU_REMARK_CODE'})

crifref = crifref.rename(columns = {'CRIF_ID': 'BUREAU_ID', 'CRIF_DATE':'BUREAU_DATE', 'CRIF_RESULT':'BUREAU_RESULT','CRIF_REPORT_PATH':'BUREAU_REPORT_PATH'})

crifscore = crifscore.rename(columns = {'CRIF_ID': 'BUREAU_ID'})


