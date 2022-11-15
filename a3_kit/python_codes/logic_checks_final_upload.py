import schedule
import boto3
import time
import pandas as pd
import glob
import os
from qc_hdfc import v2_transform_qc_hdfc
from qc_sbi import v2_transform_qc_sbi
from qc_axis import v2_transform_qc_axis
from scanned_hdfc import scanned_hdfc_digitization



bucket = 'a3itrdownload'
bucket1 = 'a3itrupload'
bucket2 = 'bankappendedcsvdownload'
bucket3 = 'bankappendedcsvupload'
bucket4 = 'bankindividualcsvdownload'
bucket5 = 'digitizedfiles'


s3 = boto3.resource('s3')

objects_itr_download = s3.Bucket(bucket).objects.all()   ###get all objects in the bucket
objects_itr_upload = s3.Bucket(bucket1).objects.all()   ###get all objects in the bucket

objects_bank_appended_download = s3.Bucket(bucket2).objects.all()   ###get all objects in the bucket
objects_bank_appended_upload = s3.Bucket(bucket3).objects.all()   ###get all objects in the bucket

objects_bank_individual_download = s3.Bucket(bucket4).objects.all()   ###get all objects in the bucket

objects_digitized_files = s3.Bucket(bucket5).objects.all()

def job():

    for obj in objects_bank_appended_download:
   
        try:

            #file = r'd:\bank\{}'.format(obj.key)
            s3.Bucket(bucket2).download_file(obj.key, r'd:\bank_appended_download\{}'.format(obj.key))  ###download file to bank folder
            print('Downloaded: {}'.format(obj.key))
            s3.Object(bucket2, obj.key).delete()
            print('Deleted: {}'.format(obj.key))
        except:
            pass  
        
    try:
        b_csv_files = glob.glob(r'D:\bank_appended_download\*.csv')
        
        for file in b_csv_files:
           
            b_appended_file = pd.read_csv(file, float_precision = None)
            os.remove(file)
            if b_appended_file['bank_name'][0] == 'HDFC':
                
                test = v2_transform_qc_hdfc(b_appended_file)
               
                if test == 'ok':
                    final = scanned_hdfc_digitization(b_appended_file)
                    final.to_csv(r'D:\bank_final_digitized_files\{}'.format(os.path.basename(file)))
                    response = s3.Bucket(bucket5).upload_file(r'D:\bank_final_digitized_files\{}'.format(os.path.basename(file)), Key=os.path.basename(file))
                    os.remove(r'D:\bank_final_digitized_files\{}'.format(os.path.basename(file)))
                else:
                    response = s3.Bucket(bucket3).upload_file(file, Key=os.path.basename(file))
                    os.remove(file)
    except:pass

    for obj in objects_bank_individual_download:
        
        try:
            #file = r'd:\bank\{}'.format(obj.key)
            s3.Bucket(bucket4).download_file(obj.key, r'd:\bank_individual_download\{}'.format(obj.key))  ###download file to bank folder
            print('Downloaded: {}'.format(obj.key))
            s3.Object(bucket4, obj.key).delete()
            print('Deleted: {}'.format(obj.key))
        except:
            pass  

    csv_files = glob.glob(r'd:\bank_individual_download\*.csv')
    lead_ids = []
    for file in csv_files:
        lead_ids.append('_'.join(file.split('_')[:-1]))
    lead_ids = list(set(lead_ids))
    print(lead_ids)
    for i in lead_ids:
        csv_files = glob.glob(r'{}*.csv'.format(i))
        df = []
        for file in csv_files:
            df.append(pd.read_csv(file, float_precision=None))

        df.to_csv(r'd:\bank_appended_ind_upload\{}_consolidated.csv'.format('_'.join(os.path.basename(file).split('_')[:-1])))
        response = s3.Bucket(bucket3).upload_file(r'd:\bank_appended_ind_upload\{}_consolidated.csv'.format('_'.join(os.path.basename(file).split('_')[:-1])), Key=os.path.basename(r'd:\bank_appended_ind_upload\{}_consolidated.csv'.format('_'.join(os.path.basename(file).split('_')[:-1]))))
            
schedule.every(1).minutes.do(job)   ### frequency of code execution

while True:
    schedule.run_pending()
    time.sleep(1)