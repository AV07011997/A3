#THE FOLLOWING CODE CREATES THE ITR DISPLAY FOR TABLE2
import pandas as pd
import numpy as np
import pymysql


def itr2(form16_path):
    
    #Read form 16
    form16 = form16_path
    
    
    ####getting data for one customer and deal(this filter needs to be applied while pulling data from database)
    #form16=form16[(form16["customer_id"]==945) & (form16["deal_id"]==973258)]
    form16["ay"]=form16["assessment_year"].str.split("-").apply(lambda x: x[0])
    form16["ay"]=form16["ay"].astype(int)
   ####getting latest employer
    form16=form16[form16["ay"]==max(form16["ay"])]
    add=list(form16.employer_address.unique())   
    address=pd.DataFrame({"Address of latest employer for reference":add})
    
    address1=address.T
    address1 = address1.rename(columns={0:'address'})
    return address1
    
