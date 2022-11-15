# # !/usr/bin/env python3
 
import sys 
import time 
import logging 
import tabula
# from watchdog.observers import Observer 
# from watchdog.events import LoggingEventHandler 


# 	# Set the format for logging info 
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S') 


# 	# Set format for displaying path 
# path = 'D:\\prudhvi\\test-folder'

# 	# Initialize logging event handler 
# event_handler = LoggingEventHandler() 


# 	# Initialize Observer

# observer = Observer() 

# observer.schedule(event_handler, path, recursive=False) 

# 	# Start the observer 
# observer.start() 

# try: 
# 	while True: 
# 			# Set the thread sleep time 
# 		time.sleep(1) 
# except KeyboardInterrupt: 
# 	observer.stop() 
# observer.join() 



import os
import pandas as pd
import time 
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import glob

events_log = []
type_of_file = []
sub_type = []
creation_time = []
deal_id = []
cust_id = []
time_stamp = []
scanned_flag = []
def scanned(file, pdf_password):
  passcode = ''
    
  try:
    tables = tabula.read_pdf(file, pages='all',password=passcode)
  except:
    passcode=pdf_password
    tables = tabula.read_pdf(file, pages='all',password=passcode)

  if len(tables)==0:
    scanned_flag.append(1)
  else:
    scanned_flag.append(0)

  return None
def logging_func():
	
	banks=['SBI', 'HDFC', 'ICICI', 'KOTAK', 'BOB']
	ITR = ['FORM16', 'FORM26', 'ÍTR']
	

	df = pd.DataFrame({'events':events_log})
	df.to_csv("D:\\prudhvi\\events.csv",index=False)
	time.sleep(3)
	for i in df['events']:
		files = glob.glob(i+'\\*')
		for i in files:
			scanned(i,'nan')
			time_stamp.append(time.ctime(os.path.getmtime(i)))
			type_n_name = i.split('_')[0].split('\\')[-1]
			deal = i.split('_')[1]
			cust = i.split('_')[2].split('.')[0]
			print(type_n_name)
			if type_n_name in banks:

				type_of_file.append('BANK')
			else:
				type_of_file.append('ITR')
			sub_type.append(type_n_name)
			deal_id.append(deal)
			cust_id.append(cust)
			

	df1 = pd.DataFrame({'deal_id':deal_id, 'cust_id':cust_id, 'type_of_file':type_of_file, 'sub_type':sub_type, 'time_stamp':time_stamp, 'scanned_flag':scanned_flag})
	df1.to_csv("D:\\prudhvi\\events_log.csv",index=False)
	print(df1)

	return None


class ExampleHandler(FileSystemEventHandler):
    def on_created(self, event): # when file is created
        # do something, eg. call your function to process the image
        print("created %s " % event.src_path)
        events_log.append(event.src_path)

        logging_func()

observer = Observer()
event_handler = ExampleHandler() # create event handler
# set observer to use created handler in directory
observer.schedule(event_handler, path='D:\\prudhvi\\test-folder')
observer.start()

# sleep until keyboard interrupt, then stop + rejoin the observer
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()