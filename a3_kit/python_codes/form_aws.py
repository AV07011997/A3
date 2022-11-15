#import boto3

## Document
#s3BucketName = "a3itr"
#documentName = "12_0.jpg"

## Amazon Textract client
#client = boto3.client('textract', region_name='ap-south-1')

## Call Amazon Textract
#response = client.detect_document_text(
#    Document={
#        'S3Object': {
#            'Bucket': s3BucketName,
#            'Name': documentName
#        }
#    })

#print(response)

# #Print text
#print("\nText\n========")
#text = ""
#for item in response["Blocks"]:
#    if item["BlockType"] == "LINE":
#        print ('\033[94m' +  item["Text"] + '\033[0m')
#        text = text + " " + item["Text"]

### Amazon Comprehend client
#comprehend = boto3.client('comprehend', region_name='ap-south-1')

### Detect sentiment
#sentiment =  comprehend.detect_sentiment(LanguageCode="en", Text=text)
#print ("\nSentiment\n========\n{}".format(sentiment.get('Sentiment')))

### Detect entities
#entities =  comprehend.detect_entities(LanguageCode="en", Text=text)
#print("\nEntities\n========")
#for entity in entities["Entities"]:
#    print ("{}\t=>\t{}".format(entity["Type"], entity["Text"]))


import glob
import boto3
from trp import Document
import os

def form_data_itr(path):

    files = glob.glob(path+'\\*.jpg')
    print(files)
    # Document
    s3BucketName = "a3itr"

    

    # Amazon Textract client
    client = boto3.client('textract', region_name='us-east-2')

    for images in files:

        with open(images, 'rb') as file:
            img_test = file.read()
            bytes_test = bytearray(img_test)
            print('Image loaded', file)

    #    # Call Amazon Textract
        response = client.analyze_document(Document={'Bytes': bytes_test}, FeatureTypes=['FORMS'])

    #response = client.analyze_document(
    #    Document={
    #        'S3Object': {
    #            'Bucket': s3BucketName,
    #            'Name': documentName
    #        }
    #    },
    #    FeatureTypes=["FORMS"])

    #print(response)

        doc = Document(response)

        for page in doc.pages:
            # Print fields
            with open(images.replace('.jpg','') + '_form.csv', 'w') as f:
                f.write("key"+' ,' + "value\n")
                for field in page.form.fields:
                    f.write("{}".format(field.key)+ ' ,' +"{}\n".format(field.value))
        
        
                    
        s3 = boto3.resource('s3')
        bucket = 'a3itrupload'
        print(os.path.basename(images))
        response = s3.Bucket(bucket).upload_file(images.replace('.jpg','') + '_form.csv', Key=os.path.basename(images).replace('.jpg','') + '_form.csv')
            #response = s3.Bucket(bucket).upload_file(images, Key=os.path.basename(images))
        #print("Fields:")
        #for field in page.form.fields:
        #    print("Key: {}, Value: {}".format(field.key, field.value))

        ## Get field by key
        #print("\nGet Field by Key:")
        #key = "Phone Number:"
        #field = page.form.getFieldByKey(key)
        #if(field):
        #    print("Key: {}, Value: {}".format(field.key, field.value))

        ## Search fields by key
        #print("\nSearch Fields:")
        #key = "address"
        #fields = page.form.searchFieldsByKey(key)
        #for field in fields:
        #    print("Key: {}, Value: {}".format(field.key, field.value))


