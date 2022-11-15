import pandas as pd
# import fitz
import os
import re
import base64
# from kraken import binarization
# from PIL import Image
# from pyzbar.pyzbar import decode
# from pyzbar.pyzbar import ZBarSymbol
import unittest
from django.conf import settings
from common.scripts import generate_random_file_name


def get_aadhaarcard_data(file_location):
    try:
        doc = fitz.open(file_location)
        page = doc.loadPage(0) #number of page
        pix = page.getPixmap()
        media_root = settings.MEDIA_ROOT
        upload_dir = os.path.join(media_root, 'aadhaar')
        random_file_name = generate_random_file_name()
        image_path = os.path.join(upload_dir, random_file_name + ".png")
        pix.writePNG(image_path)
    except:
        image_path=file_location

    im = Image.open(image_path)
    bw_im = binarization.nlbin(im)

    try:
        # zbar
        decode(bw_im, symbols=[ZBarSymbol.QRCODE])
        data=decode(bw_im, symbols=[ZBarSymbol.QRCODE])
        type(data)
        data1=data[0][0]
        type(data1)
        data1=str(data1)
        type(data1)

        import re
        data2=data1.split('" ')
        for i in data2:
            if "uid" in i:
                uid=re.findall("([0-9]{12})", i)
                
        for i in data2:
            if "name" in i and "gname" not in i:
                z=data2.index(i)
                data3=data2[data2.index(i):]

        adhaar_info = dict((x.strip(), y.strip()) for x,y in (element.split('=') for element in data3))
        df = pd.DataFrame([adhaar_info], columns=adhaar_info.keys())
        for i in df.columns:
            df[i]=df[i].str.replace('"','')
            
        cols=list(df.columns)
        j=len(cols)
        df[cols[j-1]]=df[cols[j-1]].str.replace("/>'",'')
        df["uid"]=uid
        df.columns

        # n=df["co"].str.split("/O",expand=True)
        # type(n)
        # df["relative name"]=n[1]
        # df["relative name"]=df["relative name"].str.replace(":","")
        # df["relative name"]=df["relative name"].str.replace(",","")
        # df.columns
        # print(df.columns)
        return df, image_path

    except:
        ###if qr code is not found then the image is coverted to string to be saved in the database
        print("No QR code found/QR code connot be read")
        image = open(image_path, 'rb')
        image_read = image.read()
        image_64_encode = base64.encodestring(image_read)
        

