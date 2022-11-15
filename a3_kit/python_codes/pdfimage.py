from pdf2image import convert_from_path
import os
import glob 

def pdf_image(file_path):
    # Store Pdf with convert_from_path function
    parent_dir = "D:\\prudhvi\\pdfimages"
    images = convert_from_path(file_path)
    mode = 0o666
  
    directory = str(os.path.basename(file_path.replace('.pdf','')))
    

    path = os.path.join(parent_dir, directory) 
  
    if os.path.exists(path) == False:
            os.mkdir(path, mode)

    
    for i in range(len(images)):
   
          # Save pages as images in the pdf
        images[i].save(path+'\{}_'.format(os.path.basename(path))+ str(i) +'.jpg', 'JPEG')

    return path
#def folder_path(folder):

#    files = glob.glob(folder)

#    for i in files:
#        pdf_image(i)