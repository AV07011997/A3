import schedule
import boto3
import time
import tabula
import datetime
import mysql.connector
from pdfimage import pdf_image
from textract_python_table_parser import append_files
from hdfc import hdfc_digitization
from sbi import sbi_digitization
from letest_icici import icici_digitization
from axis import axis_digitization
from letest_corporation import corporation_digitization
## #from form_aws import form_data_itr
import os
from itrv import get_itrv_data
from form26as import get_form26as_data
from form16 import get_form16_data
from fstype_extraction_bank import bank_extraction
from bank_name_extraction import fstype_extraction
from fstype_extraction_itr import itr_extraction
import glob


bucket = 'a3bank'  ###define bucket name
bucket1 = 'a3itr'  ###define bucket name
bucket2 = 'digitizedfiles'

s3 = boto3.resource('s3')

objects_bank = s3.Bucket(bucket).objects.all()   ###get all objects in the bucket
objects_itr = s3.Bucket(bucket1).objects.all()   ###get all objects in the bucket

# objects_bank = glob.glob(r'D:\s3_bank\\*')     # manual testing
# objects_itr = glob.glob(r'D:\s3_itr\\*')       # manual testing

def job():
    print('Digitization')
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",                        ###connect to database
        password="Knowlvers@555",
        database="details"
    )

    mycursor = mydb.cursor()       

    for obj in objects_bank:

        try:

            #file = r'C:\Users\hardi\OneDrive\Documents\Project Nishchay\Digitization\{}'.format(obj.key)
            s3.Bucket(bucket).download_file(obj.key, r'/Users/hardikbhardwaj/Desktop/digitised/{}'.format(obj.key))  ###download file to bank folder

            ### chek scanned/unscanned

            passcode = ''

            try:

                tables = tabula.read_pdf(r'/Users/hardikbhardwaj/Desktop/digitised/{}'.format(obj.key), pages='all',password=passcode)

            except:

                passcode=''
                tables = tabula.read_pdf(r'/Users/hardikbhardwaj/Desktop/digitised/{}'.format(obj.key), pages='all',password=passcode)

            if len(tables)==0:
                scanned_flag = 1
                file_path = pdf_image(r'/Users/hardikbhardwaj/Desktop/digitised/{}'.format(obj.key))
                append_files(file_path, 'bank')

            else:
                scanned_flag = 0
                # fstype='HDFC'
                files = glob.glob(r"/Users/hardikbhardwaj/Desktop/digitised/*.pdf")

                for i in range(len(files)):
                    print(files[i])
                    fstype = bank_extraction(files[i])
                    if fstype == None:
                        fstype = fstype_extraction(files[i],scanned_flag)

                    if fstype == 'HDFC':
                        print('hdfc')
                        file_path = hdfc_digitization(r'/Users/hardikbhardwaj/Desktop/digitised/{}'.format(obj.key))
                        response = s3.Bucket(bucket2).upload_file(file_path, Key=os.path.basename(file_path))
                        os.remove(files[i])

                    elif fstype == 'SBI':
                        file_path = sbi_digitization(r'/Users/hardikbhardwaj/Desktop/digitised/{}'.format(obj.key),'')
                        response = s3.Bucket(bucket2).upload_file(file_path, Key=os.path.basename(file_path))
                        os.remove(files[i])

                    elif fstype == 'ICICI':
                        file_path = icici_digitization(r'/Users/hardikbhardwaj/Desktop/digitised/{}'.format(obj.key),'')
                        response = s3.Bucket(bucket2).upload_file(file_path, Key=os.path.basename(file_path))
                        os.remove(files[i])

                    elif fstype == 'AXIS':
                        file_path = axis_digitization(r'/Users/hardikbhardwaj/Desktop/digitised/{}'.format(obj.key),'')
                        response = s3.Bucket(bucket2).upload_file(file_path, Key=os.path.basename(file_path))
                        os.remove(files[i])

                    elif fstype == 'Corporation':
                        file_path = corporation_digitization(r'/Users/hardikbhardwaj/Desktop/digitised/{}'.format(obj.key),'')
                        response = s3.Bucket(bucket2).upload_file(file_path, Key=os.path.basename(file_path))
                        os.remove(files[i])

            ###  end scanned/unscanned

            ### insert document details into the table

            sql = "INSERT INTO received_file_details (lead_id, file_name, file_type, file_extension, scanned, uploaded_output, uploaded_datetime) VALUES (%s, %s, %s, %s, %s, %s, %s);"
            lid = obj.key.split('_')[0]
            spl_word = '_'
            fname = obj.key.partition(spl_word)[2]
            #fname = ''.join(obj.key.split('_')[1:])
            ftype = 'bank'

            extension=obj.key.split('.')[1]
            s=scanned_flag
            fswap='ok'
            hours = 5.5   ### add hours to match our local timezone
            hours_added = datetime.timedelta(hours = hours)
            uptime = str(obj.last_modified + hours_added).split('+')[0]
            #uptime=str(obj.last_modified).split('+')[0]


            val = (lid, fname, ftype, extension, s, fswap, uptime)

            mycursor.execute(sql, val)

            s3.Object(bucket, obj.key).delete()   ### delete downloaded file from AWS

        except Exception as e:
            print(e)

    for obj in objects_itr:
   
        try:

            #file = r'd:\itr\{}'.format(obj.key)
            s3.Bucket(bucket1).download_file(obj.key, r'd:\itr\{}'.format(obj.key))   ###download file to itr folder

            ### chek scanned/unscanned

            passcode = ''
    
            try:
                tables = tabula.read_pdf(r'd:\itr\{}'.format(obj.key), pages='all',password=passcode)
            except:
                passcode=pdf_password
                tables = tabula.read_pdf(r'd:\itr\{}'.format(obj.key), pages='all',password=passcode)

            if len(tables)==0:
                scanned_flag = 1
                path = pdf_image(r'd:\itr\{}'.format(obj.key))
                append_files(path,'itr')
                form_data_itr(path)
            else:
                scanned_flag = 0
                files = glob.glob(r"d:\itr\*.pdf")
                for j in range(len(files)):
                    fstype = itr_extraction(files[j])
                    if fstype == 'itrv':
                        file_path = get_itrv_data(r'd:\itr\{}'.format(obj.key))
                        response = s3.Bucket(bucket2).upload_file(file_path, Key=os.path.basename(file_path))
                        os.remove(files[j])
                    elif fstype == 'form26as':
                        file_path = get_form26as_data(r'd:\itr\{}'.format(obj.key))
                        for i in file_path:
                            response = s3.Bucket(bucket2).upload_file(i, Key=os.path.basename(i))
                            os.remove(i)
                        os.remove(files[j])
                    elif fstype == 'form16':
                        file_path = get_form16_data(r'd:\itr\{}'.format(obj.key))
                        for i in file_path:
                            response = s3.Bucket(bucket2).upload_file(i, Key=os.path.basename(i))
                            os.remove(i)
                        os.remove(files[j])



            ###  end scanned/unscanned

            ### insert document details into the table
            
            sql = "INSERT INTO received_file_details (lead_id, file_name, file_type, file_extension, scanned, uploaded_output, uploaded_datetime) VALUES (%s, %s, %s, %s, %s, %s, %s);"
            lid = obj.key.split('_')[0]
            spl_word = '_'
            fname = obj.key.partition(spl_word)[2]
            #fname = ''.join(obj.key.split('_')[1:])   
            ftype = 'itr'                             
                                        
            extension=obj.key.split('.')[1]           
            s=scanned_flag                            
            fswap='ok'
            hours = 5.5    ### add hours to match our local timezone
            hours_added = datetime.timedelta(hours = hours)
            uptime = str(obj.last_modified + hours_added).split('+')[0]
            #uptime=str(obj.last_modified).split('+')[0]
           

            val = (lid, fname, ftype, extension, s, fswap, uptime)

            mycursor.execute(sql, val)
            
            s3.Object(bucket1, obj.key).delete()    ### delete downloaded file from AWS
        except Exception as e:
            print(e)
            
    mydb.commit()   ### until and unless you commit table will not be updated
 
schedule.every(1).minutes.do(job)   ### frequency of code execution

while True:
    schedule.run_pending()
    time.sleep(1) 

