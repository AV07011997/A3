import webbrowser
import json
import boto3
import io
from io import BytesIO
import sys
from pprint import pprint
import glob
import pandas as pd
import os




def get_rows_columns_map(table_result, blocks_map):
    rows = {}
    for relationship in table_result['Relationships']:
        if relationship['Type'] == 'CHILD':
            for child_id in relationship['Ids']:
                cell = blocks_map[child_id]
                if cell['BlockType'] == 'CELL':
                    row_index = cell['RowIndex']
                    col_index = cell['ColumnIndex']
                    if row_index not in rows:
                        # create new row
                        rows[row_index] = {}
                        
                    # get the text value
                    rows[row_index][col_index] = get_text(cell, blocks_map)
    return rows


def get_text(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] =='SELECTED':
                            text +=  'X '    
    return text


def get_table_csv_results(file_name):

    with open(file_name, 'rb') as file:
        img_test = file.read()
        bytes_test = bytearray(img_test)
        print('Image loaded', file_name)

    # process using image bytes
    # get the results
    client = boto3.client('textract', region_name='us-south-1')

    response = client.analyze_document(Document={'Bytes': bytes_test}, FeatureTypes=['TABLES'])

    # Get the text blocks
    blocks=response['Blocks']
    #pprint(blocks)

    blocks_map = {}
    table_blocks = []
    for block in blocks:
        blocks_map[block['Id']] = block
        if block['BlockType'] == "TABLE":
            table_blocks.append(block)

    if len(table_blocks) <= 0:
        return "<b> NO Table FOUND </b>"

    csv = ''
    for index, table in enumerate(table_blocks):
        csv += generate_table_csv(table, blocks_map, index +1)
        csv += '\n\n'

    return csv

def generate_table_csv(table_result, blocks_map, table_index):
    rows = get_rows_columns_map(table_result, blocks_map)

    table_id = 'Table_' + str(table_index)
    
    # get cells.
    csv = 'Table: {0}\n\n'.format(table_id)

    for row_index, cols in rows.items():
        
        for col_index, text in cols.items():
            csv += '{}'.format(text) + "|"
        csv += '\n'
        
    csv += '\n\n\n'
    return csv

def main(file_name):
    table_csv = get_table_csv_results(file_name)
   
    output_file = '{}.csv'.format(file_name.replace('.jpg',''))

    # replace content
    with open(output_file, "wt") as fout:
        fout.write(table_csv)

    # show the results
    print('CSV OUTPUT FILE: ', output_file)
    return table_csv



def append_files(folder_name, type):
    
    
    folders = folder_name
    
   
    
    files = glob.glob(folders+'\\*.jpg')
    
    for j in files:
        main(j)

    if type == 'bank':
        csv_files = glob.glob(folders+'\\*.csv')
        
        df1 = []
        df = []
        append = ''
        for j in csv_files:
           
            try:
                df.append(pd.read_csv(j, dtype='str', sep='|', skiprows=1, header=None))
                append='true'
            except:
                bucket = 'bankindividualcsvupload'
                s3 = boto3.resource('s3')
                append='false'
                for file in csv_files:
                    response = s3.Bucket(bucket).upload_file(file, Key=os.path.basename(file))
                    response = s3.Bucket(bucket).upload_file(file.replace('.csv','.jpg'), Key=os.path.basename(file).replace('.csv','.jpg'))
                break

        if append == 'true':
            df[0] = df[0].iloc[:, :-1]
            #print(df[0])
            new_header = [x.strip() for x in df[0].iloc[0]] #grab the first row for the header
       
            #df[0].columns =  new_header
        
            df[0].columns = new_header 
            df[0] = df[0][1:] #take the data less the header row
          
            df1.append(df[0])

            for k in range(1,len(df)):
           
                try:   
                    df[k] = df[k].iloc[:, :-1]
                    df[k].columns = new_header
                    df1.append(df[k])
                except:pass
            df = pd.concat(df1)

            #for num in range(len(df.columns)):
            #    df[new_header[num]] = "'" + df[new_header[num]]

        
            df.to_csv('{}{}_consolidated.csv'.format(folders+'\\',os.path.basename(folders)), index=False)
        
            s3 = boto3.resource('s3')
            bucket = 'bankappendedcsvupload'
            response = s3.Bucket(bucket).upload_file(folders+'\\{}_consolidated.csv'.format(os.path.basename(folders)), Key=os.path.basename(folders)+'.csv')
            response = s3.Bucket(bucket).upload_file('D:\\bank\\' + os.path.basename(folders)+'.pdf', Key=os.path.basename(folders)+'.pdf')

    else:
        csv_files = glob.glob(folders+'\\*.csv')
        jpg_files = glob.glob(folders+'\\*.jpg')
        s3 = boto3.resource('s3')
        bucket = 'a3itrupload'
        for file in csv_files:
            response = s3.Bucket(bucket).upload_file(file, Key=os.path.basename(file))
        for file in jpg_files:
            response = s3.Bucket(bucket).upload_file(file, Key=os.path.basename(file))

