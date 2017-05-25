#!/usr/bin/python

import MySQLdb
import time
import json
import threading
import datetime
import os
import smtplib
from time import gmtime, strftime
from email.mime.text import MIMEText

#Init
json_data=open('/home/commonslab/donation-box/config.json')
config = json.load(json_data)
json_data.close()

coin = 0
#See the config.json file for the configuration
curr = config["General"]["currency"]

dbserver = config["Database"]["server"]
dbuser = config["Database"]["username"]
dbpass = config["Database"]["password"]
dbname = config["Database"]["name"]

#em_sender = config["Email_Reporting"]["sender"]
#em_receiver = config["Email_Reporting"]["receiver"]
#em_subject = config["Email_Reporting"]["subject"]

report = ''

#Check for inserted coins and send any to the websocket clients
def GetDonations():
  global report
  #THREAD: This function runs inside the thread
  LastTime = strftime("%Y-%m-%d %H:%M:%S", gmtime());

  #Connect to database
  dbConn = MySQLdb.connect(dbserver,dbuser,dbpass,dbname) or die ("could not connect to database")
  cursor = dbConn.cursor()
  try:
    cursor.execute('SELECT timestamp, ammount, currency FROM donations');
    for (timestamp, ammount, currency) in cursor:
      rep='Time: {0}, Donation: {1} {2}\r\n'.format(timestamp, ammount, currency)
      report += rep

    cursor.execute('SELECT currency,value,donationid FROM coinacceptor WHERE donationid < 0')
    for (currency,value,donationid) in cursor:
      rep = 'Coins: {0} {1}\r\n'.format(value, currency)  
      report += rep
    cursor.close()  #close the cursor

  except MySQLdb.IntegrityError:
    logging.error('failed to fetch data')

  cursor.close();  #close the cursor
  SendEmail()  

def SendEmail():
        msg = MIMEText(report)
        msg['Subject'] = 'Test report'
        msg['From'] = "donationbox@commonslab.gr"
        msg['To'] = "dimitris@commonslab.gr"
        
        try:
                smtpObj = smtplib.SMTP('mail.commonslab.gr')
                smtpObj.sendmail("donationbox@commonslab.gr","dimitris@commonslab.gr" ,msg.as_string())
                smtpObj.quit()
        except SMTPException:
                print "Error: unable to send email."
                
GetDonations()        


