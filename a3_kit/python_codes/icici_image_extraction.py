#import pytesseract
#import cv2
#from PIL import Image
#import pytesseract

image_path = r'C:\Users\PrudhviJonnalagadda\Downloads\icici.png'
#path_to_tesseract = r"D:\prudhvi\Dev\Scripts\pytesseract.exe"

#pytesseract.pytesseract.tesseract_cmd = path_to_tesseract

            
#print(pytesseract.image_to_string(Image.open(image_path)))



  

#image = cv2.imread(image_path)
    
     
     
    
#newdata=pytesseract.image_to_osd(image)

##text = pytesseract.image_to_string(image)
  
## # Displaying the extracted text
#print(newdata)


# will convert the image to text string
import pytesseract      
  
# adds image processing capabilities
from PIL import Image    
  
    
  
 # opening an image from the source path
img = Image.open(image_path)     
  
# describes image format in the output
print(img)                          
# path where the tesseract module is installed
pytesseract.pytesseract.tesseract_cmd = "C:\\Users\\PrudhviJonnalagadda\\AppData\\Local\\Tesseract-OCR\\tesseract.exe"

# converts the image to result and saves it into result variable
result = pytesseract.image_to_string(img)   
# write text in a text file and save it to source path   


print(result)