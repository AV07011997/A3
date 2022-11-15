import pytesseract
import pandas as pd
# from kraken import binarization
# import fitz
# import cv2
import numpy as np
import os
import re
from PIL import Image
import unittest
from django.conf import settings
from common.scripts import generate_random_file_name


def get_pancard_data(file_location):
    try:
        ##converting pdf to image
        doc = fitz.open(file_location)
        page = doc.loadPage(0) #number of page
        pix = page.getPixmap()
        media_root = settings.MEDIA_ROOT
        upload_dir = os.path.join(media_root, 'pan')
        random_file_name = generate_random_file_name()
        image_path = os.path.join(upload_dir, random_file_name + ".png")
        # print("into pancard class (pdf).")
        # print("image path:", image_path)
        # image_path=r"D:\Kavyant\lokesh_loan_documents_verification_project\a3-kit\a3_kit\media\image\PAN_card.png"
        pix.writePNG(image_path)
    except:
        image_path=file_location

    image = cv2.imread(image_path)

    pytesseract.pytesseract.tesseract_cmd = 'tesseract'
    # pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'


    try:
        newdata=pytesseract.image_to_osd(image)
        angle=re.search('(?<=Rotate: )\d+', newdata).group(0)
                
        def rotate_bound(image, angle):
            # grab the dimensions of the image and then determine the
            # center
            (h, w) = image.shape[:2]
            (cX, cY) = (w // 2, h // 2)
            # grab the rotation matrix (applying the negative of the
            # angle to rotate clockwise), then grab the sine and cosine
            # (i.e., the rotation components of the matrix)
            M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
            cos = np.abs(M[0, 0])
            sin = np.abs(M[0, 1])
            # compute the new bounding dimensions of the image
            nW = int((h * sin) + (w * cos))
            nH = int((h * cos) + (w * sin))
            # adjust the rotation matrix to take into account translation
            M[0, 2] += (nW / 2) - cX
            M[1, 2] += (nH / 2) - cY
            # perform the actual rotation and return the image
            return cv2.warpAffine(image, M, (nW, nH))
        
        if angle != 0:
            rotated = rotate_bound(image, int(angle))
        #cv2.imshow("Rotated", image)
        #cv2.waitKey(0)
        #cv2.imshow("Rotated", rotated)
        #cv2.waitKey(0)
            cv2.imwrite(image_path,rotated)
    except:
        cv2.imwrite(image_path,image)
        

    # binarization using kraken
    im = Image.open(image_path)
    bw_im = binarization.nlbin(im)
    text = pytesseract.image_to_string(bw_im)
    im.close()
    text
    name=[]
    relative_name=[]
    dob=[]
    pan_number=[]
    data=pd.DataFrame()

    import re
    try:
        matches = re.findall('(\d{2}[\/ ](\d{2}|January|Jan|February|Feb|March|Mar|April|Apr|May|May|June|Jun|July|Jul|August|Aug|September|Sep|October|Oct|November|Nov|December|Dec)[\/ ]\d{2,4})', text)
        for match in matches:
            dob.append(match[0])
    except:
        pass
    try:    
        temp=re.findall("([a-zA-Z0-9]{10,})", text)
        temp=list(temp)
        def num(s):
            return any(i.isdigit() for i in s)
        for i in temp:
            if num(i)==True:
                pan_number.append(i)  
    except:
        pass
    text2=[]
    text3=[]
    text4=[]
    text5=[]
    text6=[]
    try:
        def convert(text): 
            return (text.split("\n"))
        text1=convert(text)

        for i in text1:
            if len(i)>2:
                text2.append(i)
        for i in text2:
            if "TAX" in i or "INCOME" in i or "DEPARTMENT" in i :
                text2=text2[(text2.index(i)+1):]
        text3=text2
        for i in text3:
            if "GOVT" not in i or "INDIA" not in i:
                text4.append(i)
        
        try:
            for i in text4:
                if dob[0] in i:
                    text5=text4[:text4.index(i)]
        except:
            pass
        if len(text5)==0:
                text5=text4
        #text6=[]
        for i in text5:
            temp=re.findall(r"[A-Z]+,?\s+(?:[A-Z]*\.?\s*)?[A-Z]+", i)
            text6.extend(temp) 
        if len(text6)==0:
            for i in text5:
                temp=re.findall(r"[A-Z]+", i)
                text6.extend(temp) 
        if len(text6)>2:
            res = min(len(ele) for ele in text6)
            for i in text6:
                if len(i)==res:
                    text6.remove(i)
                    
        
        name.append(text6[0])
        relative_name.append(text6[1])
    except:
        pass
        


    try:
        data['name']=name
    except:
        data['name']=""
    try:
        data['relative_name']=relative_name
    except:
        data['relative_name']=""
    try:
        data['dob']=dob
    except:
        data['dob']=None
    try:
        data['pan_number']=pan_number
    except:
        data['pan_number']=""

    return data, image_path

#data.to_csv(r"D:\User DATA\Documents\A3\Codes_pan_adhaar_with_samples/Pan Card Copy (1).csv")
