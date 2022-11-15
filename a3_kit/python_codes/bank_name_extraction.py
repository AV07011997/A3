import fitz
from PIL import Image
import io
import pytesseract
import pandas as pd
# from kraken import binarization
import cv2 
import numpy as np
import re
import base64   
from PIL import Image, ImageOps
import os


def fstype_extraction(filepath,scanned_flag):
    
    if scanned_flag == 0:

         pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

        
        #opens doc using pymupdf
         doc = fitz.open(filepath)

        #loads the first page
         page = doc.load_page(0)

        #[first image on page described thru a list][first attribute on image list: xref n], check pymupdf docs under getimagelist()
         xref = page.get_images()[0][0]

        #gets the image as a dict, check docs under extractimage 
         baseimage = doc.extract_image(xref)

        #gets the raw string image data from the dictionary and wraps it in a bytesio object before using pil to open it
         image = Image.open(io.BytesIO(baseimage['image']))
        
         image.save(r'/Users/hardikbhardwaj/Desktop/digitised/temp.png')
         img = Image.open(r'/Users/hardikbhardwaj/Desktop/digitised/temp.png')
         img = img.convert("L")
        
         result = pytesseract.image_to_string(img)
         print(result)
         if 'AXIS' in result.upper():
             return 'AXIS'
         if 'HDFC' in result:
             return 'HDFC'
         if 'SBI' in result:
             return 'SBI'
         if 'ICICI' in result.upper():
             return 'ICICI'
        



    if scanned_flag == 1:

        img = Image.open(filepath)
        #left = 10
        #top = 25
        #right = 1200
        #bottom = 250
        #img = img.crop((left, top, right, bottom))

        #img = img.convert('RGB')
        #img = cv2.bitwise_not(img)
        #img = ImageOps.invert(img)
        #img = img.convert(mode="1", dither=Image.NONE)
        img.save(r'/Users/hardikbhardwaj/Desktop/digitised/temp.png')
        pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        result = pytesseract.image_to_string(img)  
       
        if 'AXIS' in result:
            return 'AXIS'
        if 'HDFC' in result:
            return 'HDFC'
        if 'SBI' in result:
            return 'SBI'
        if 'ICICI' in result.upper():
            return 'ICICI'
        os.remove(r'/Users/hardikbhardwaj/Desktop/digitised/temp.png')
        
