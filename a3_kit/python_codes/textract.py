import random
import boto3
import time

bucket = 'a3bank'
#path = 'THE_PATH_FROM_WHERE_YOU_UPLOAD_INTO_S3'
filename = '56.pdf'

client = boto3.client('textract', region_name='ap-south-1')
response = client.start_document_text_detection(
                   DocumentLocation={'S3Object': {'Bucket': bucket, 'Name': filename} },
                   ClientRequestToken=str(random.randint(1,1e10)))

jobid = response['JobId']

response = client.get_document_text_detection(JobId=jobid)
time.sleep(180)
pages = [response]
while nextToken := response.get('NextToken'):
    response = client.get_document_text_detection(JobId=jobid, NextToken=nextToken)
    pages.append(response)

print(pages)



#import boto3

## boto3 client
#client = boto3.client(
#    'textract', 
#    region_name='us-east-2', 
    
#)

## Read image
#with open(r'D:\prudhvi\sources-a3-kit\Scanned files\HDFC\56.pdf', 'rb') as document:
#    img = bytearray(document.read())

## Call Amazon Textract
#response = client.detect_document_text(
#    Document={'Bytes': img}
#)

## Print detected text
#for item in response["Blocks"]:
#    if item["BlockType"] == "LINE":
#        print ('\033[94m' +  item["Text"] + '\033[0m')\





import boto3
from trp import Document
# Document
s3BucketName = "<Your bucket name>"
documentName = "<Image with text>"
# Amazon Textract client
textract = boto3.client('textract')
# Call Amazon Textract
response = textract.analyze_document(
 Document={
 'S3Object': {
 'Bucket': s3BucketName,
 'Name': documentName
 }
 },
 FeatureTypes=["TABLES"])
#print(response)
doc = Document(response)