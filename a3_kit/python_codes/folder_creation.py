# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 14:10:50 2021

@author: PrudhviJonnalagadda
"""

import os
import mysql.connector
import schedule
import time
def job():

    cnx = mysql.connector.connect(user='root', password='u8xGEViJsNjWe9HV',
                                host='127.0.0.1',
                                database='a3_kit')

    #print(cnx)

    mycursor = cnx.cursor()

    mycursor.execute('SELECT DISTINCT(customer_id) FROM a3_kit.bureau_ref_dtl;')

    myresult = mycursor.fetchall()
    print(myresult)
    mycursor = mydb.cursor()
    for i in range(len(myresult[0])):
  
      parent_dir = "D:\\prudhvi"

      mode = 0o666
  
      directory = str(myresult[0][i])
    # Path 

      path = os.path.join(parent_dir, directory) 
  
      if os.path.exists(path) == False:
        os.mkdir(path, mode)
      else:
        pass
      
    # Create the directory 
    # 'GeeksForGeeks' in 
    # '/home / User / Documents' 
    # with mode 0o666 
   
    #print(cnx.execute('SELECT * FROM a3_kit.bureau_ref_dtl;'))



    #print("Directory '% s' created" % directory) 

schedule.every().day.at("15:52").do(job)
while True:
  schedule.run_pending()
  time.sleep(1)