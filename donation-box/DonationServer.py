#!/usr/bin/python
####################################################
# Name: Donation Box WebSockets deamon
#
# Description:
# Provides the WebSockets Server which polls data from the DB, notifies any connected clients (browsers)
# and accepts messages (donations) from clients that then writes to the DB
#
# Author: Dimitris Koukoulakis
#
# License: GNU GPL v3.0
####################################################

from __future__ import print_function
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import serial
import MySQLdb
import time
import threading
import datetime
import decimal
import json
import urllib2
import logging
import subprocess
import os
import random
from time import gmtime, strftime
import sys
sys.path.insert(0,'/home/commonslab/donation-box/resources')
from Adafruit_Thermal import *
import coopboxqr

#Init
json_data=open('/home/commonslab/donation-box/config.json')
config = json.load(json_data)
json_data.close()
logging.basicConfig(filename='DonationServer.log', level=logging.DEBUG, format='%(levelname)s %(asctime)s: %(message)s')
logging.debug('Donation Box Server started')

coin = 0
#See the config.json file for the configuration
curr = config["General"]["currency"]
init_wait_time = config["General"]["Init Wait time (sec)"]
clients = []
dbserver = config["Database"]["server"]
dbuser = config["Database"]["username"]
dbpass = config["Database"]["password"]
dbname = config["Database"]["name"]

#PRINTER
pr_enabled = config["Printer"]["enabled"]
pr_dev = config["Printer"]["dev"]
pr_baudrate = config["Printer"]["baudrate"]
pr_timeout = config["Printer"]["timeout"]
pr_feedlines = config["Printer"]["feedlines"]
pr_heattime = config["Printer"]["heattime"]

#GAME
game_enabled = config["Game"]["enabled"]
game_run = config["Game"]["run"]

#UI
ui_sendsum = config["UI"]["SendSumDonations"]

#NETWORK
net_enabled = config["Network"]["enabled"]
net_url = config["Network"]["URL"]
net_send = config["Network"]["insert"]
net_get = config["Network"]["get"]
net_getparam = config["Network"]["get_param"]
net_boxid = config["Network"]["boxID"]

#wait at start up for mySQL to load
time.sleep(init_wait_time)

#For normal Screen (No Touch) make donations automatic
#ONLY for single project!
auto_donation = False

if pr_enabled:
  printer = Adafruit_Thermal(pr_dev, pr_baudrate, timeout=pr_timeout)

def PrintMSFReceipt():
  printer.begin(pr_heattime)
  printer.setTimes(0,0) #print as fast as possible
  printer.feed(1)
  printer.printBitmap(msflogo.width, msflogo.height, msflogo.data)
  printer.feed(2)
  printer.printBitmap(msfty.width, msfty.height, msfty.data)
  printer.feed(1)
  printer.printBitmap(msfqr.width, msfqr.height, msfqr.data)
  printer.feed(1)
  printer.doubleHeightOn()
  printer.println('             msf.gr')
  printer.println('         +30 210 5200500')
  printer.feed(pr_feedlines)

def PrintCoopBoxReceipt(amount,uid):
  printer.begin(pr_heattime)
  printer.setTimes(0,0) #print as fast as possible
  printer.doubleHeightOn()
  printer.println('         CODE: {0}'.format(uid))
  printer.doubleHeightOff()
  printer.feed(1)
  printer.println('scan the QR code or go to ')
  printer.println('http://thecoopbox.commonslab.gr')
  printer.println('and register for your perk')
  printer.feed(1)
  printer.doubleHeightOn()
  printer.println('          {0} EUR'.format(amount))
  printer.doubleHeightOff()
  printer.feed(1)

  #if (amount == '0.50'):
  #  printer.printBitmap(halfeuro.width, halfeuro.height, halfeuro.data)
  #elif (amount == '1.00'):
  #  printer.printBitmap(oneeuro.width, oneeuro.height, oneeuro.data)
  #elif (amount == '2.00'):
  #  printer.printBitmap(twoeuro.width, twoeuro.height, twoeuro.data)

  printer.feed(1)
  printer.printBitmap(coopboxqr.width, coopboxqr.height, coopboxqr.data)
  printer.feed(pr_feedlines)


def Th_print(currency,value,name,email,prname,prid,donationid,uid):
  if not pr_enabled:
    logging.debug('Thermal printer is disabled')
    return
  PrintCoopBoxReceipt(value,uid)
  #os.system('/home/commonslab/donation-box/PrintCoopReceipt.py -a {0} -i {1}'.format(value,uid))
  #THREAD:Start printing receipt
  #p = threading.Thread(target=PrintCoopBoxReceipt(value,uid))
  #p.daemon = True
  #p.start()


#Generate Unique Donation ID for registering it to the DB and print it for user
def GenerateUID(amount):
    #Generate random 5 digit number
    r = random.randint(10000,99999)
    #Get a list of the digits
    l = list(str(r))
    #Get the sum of those digits
    c = int(l[0])+int(l[1])+int(l[2])+int(l[3])+int(l[4])
    #Get the modulus of that sum
    c = c%10;
    a = str(amount)[0]
    '''
    if (amount == 1):
        a = random.randint(0,2)
    elif (amount == 2):
        a = random.randint(3,5)
    elif (amount == 0.5):
        a = random.randint(6,9)
    '''
    uid = str('{0}{1}{2}').format(a,r,c)
    return uid

#Retrieve Donations from server
def RetrieveDonations(pid):
    url = net_url+"/"+net_get+"?"+net_getparam+"="+pid
    #url = "http://thecoopbox.commonslab.gr/network_output.php?idproject={0}".format(pid)
    response = urllib2.urlopen(url)
    data = json.loads(response.read())
    new_amount = data[0]['amount']
    logging.debug(json.dumps(data))
    return new_amount

#Submit Donation data to server
def SendDonationToServer(prid,value,uid):
    from time import gmtime, strftime
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    #uid = GenerateUID(value)
    #data = {"ProjectID":1,"BoxID":1,"DateTime":time.strftime('%Y-%m-%d %H:%M:%S'),"Amount":2}
    data = {}
    data['ProjectID'] = prid
    data['BoxID'] = net_boxid
    data['Amount'] = value
    data['DonationTime'] = timestamp
    data['UID'] = uid
    logging.debug(json.dumps(data))

    req = urllib2.Request(net_url+'/'+net_send)
    req.add_header('Content-Type', 'application/json')
    #print "Sending:"
    #print json.dumps(data)
    logging.debug('Sending: {0}'.format(data))
    response = urllib2.urlopen(req, json.dumps(data))
    logging.debug('Response from {0}/{1}: {2}'.format(net_url,net_send,response.read()))
    if ("successfully" in response.read()):
      return True
    else:
      return False

#Check for inserted coins and send any to the websocket clients
def UpdateCoins():
  #THREAD: This function runs inside the thread
  LastTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

  while True:
    #Connect to database
    dbConn = MySQLdb.connect(dbserver,dbuser,dbpass,dbname) or die ("could not connect to database")
    cursor = dbConn.cursor()
    try:
      cursor.execute('SELECT timeinserted, value, currency FROM coinacceptor WHERE timeinserted > "{0}" ORDER BY timeinserted ASC'.format(LastTime))
      #print('SELECT timeinserted, value, currency FROM coinacceptor WHERE timeinserted > "{0}" ORDER BY timeinserted ASC'.format(LastTime))
      for (timeinserted, value, currency) in cursor:
        LastTime = timeinserted
        global coin
        coin = value
        global curr
        curr = currency
        #logging.debug('{0}|{1}'.format(coin,curr))
        #print('{0}|{1}'.format(coin,curr))
        if coin != 0:
          #Send value to web socket clients
          SendCoins('{0}|{1}'.format(coin,curr))
          if auto_donation:
            ProcessDonation('PLAY|||0|COOP|1|{0}EUR'.format(value))
      cursor.close();  #close the cursor
    except MySQLdb.IntegrityError:
      logging.error('failed to fetch data')
    finally:
      cursor.close();  #close the cursor

    #Sleep for a while to allow other processes
    time.sleep(0.5);


#Check for money that have not been donated yet
def GetCoins():
  global dbserver
  global dbname
  global dbuser
  global dbpass
  global coin
  global curr

  #Connect to Database
  dbConn = MySQLdb.connect(dbserver,dbuser,dbpass,dbname) or die ("could not connect to database")
  cursor = dbConn.cursor()

  try:
    #See if there are coins inserted that have not been donated
    cursor.execute('SELECT currency,value,donationid FROM coinacceptor WHERE donationid < 0')
    # Get returned values
    for (currency,value,donationid) in cursor:
      #TODO: What should happen if one coin is of differenct currency?
      curr = currency
      coin += value
      logging.debug('DonationID: '+repr(donationid)+' Currency: '+repr(curr)+' Value: '+repr(coin))

    if coin != 0:
      return str('{0}|{1}'.format(coin,curr))
    else:
      return 0

    cursor.close();  #close the cursor
  except MySQLdb.IntegrityError:
    logging.error('failed to fetch data')
  finally:
    cursor.close()  #close just incase it failed

def InsertRegistration(name,email):
  from time import gmtime, strftime
  timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
  dbConn = MySQLdb.connect(dbserver,dbuser,dbpass,dbname) or die ("could not connect to database")
  logging.debug('Insert registration to DB')
  dbConn.set_character_set('utf8')
  cursor = dbConn.cursor()
  cursor.execute('SET NAMES utf8;')
  cursor.execute('SET CHARACTER SET utf8;')
  cursor.execute('SET character_set_connection=utf8;')

  logging.debug('Name:'+name+' Email:'+email)
  try:
    #Insert registration
    cursor.execute('INSERT INTO newsletter (email,name,timestamp) VALUES ("{0}","{1}","{2}")'.format(email,name,timestamp))
    dbConn.commit()
    cursor.close()
  except MySQLdb.IntegrityError:
    logging.error('failed to fetch data')
    for client in clients:
      client.write_message("ERROR")
  finally:
    cursor.close()  #close just incase it failed


def InsertDonation(currency,value,name,email,public, prname, prid, uid):
  from time import gmtime, strftime
  timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
  dbConn = MySQLdb.connect(dbserver,dbuser,dbpass,dbname) or die ("could not connect to database")
  logging.debug('Insert donation to DB')
  dbConn.set_character_set('utf8')
  cursor = dbConn.cursor()
  cursor.execute('SET NAMES utf8;')
  cursor.execute('SET CHARACTER SET utf8;')
  cursor.execute('SET character_set_connection=utf8;')

  logging.debug('Name:'+name+' Email:'+email+' public:'+public+' Project Name:'+prname+' ProjectID:'+prid+' Currency:'+currency+' Value:'+value)
  if (public == 'false'):
    public = 0
  else:
    public = 1
  try:
      #Insert donation
      logging.debug('INSERT INTO donations (currency,ammount,projectname,email,name,public,projectid,timestamp, uid) VALUES ("{0}",{1},"{2}","{3}","{4}",{5},{6},"{7}","{8}")'.format(currency,value,prname,email,name,public,prid,timestamp,uid))
      cursor.execute('INSERT INTO donations (currency,ammount,projectname,email,name,public,projectid,timestamp, uid) VALUES ("{0}",{1},"{2}","{3}","{4}",{5},{6},"{7}","{8}")'.format(currency,value,prname,email,name,public,prid,timestamp,uid))
      dbConn.commit()
      #Get donation ID
      donationid = cursor.lastrowid
      #Update coins inserted with donation ID
      cursor.execute('UPDATE coinacceptor SET donationid={0} WHERE donationid=-1'.format(donationid))
      dbConn.commit()
      cursor.close()
  except MySQLdb.IntegrityError:
    logging.error('failed to fetch data')
    for client in clients:
      client.write_message("ERROR")
  finally:
    cursor.close()  #close just incase it failed
    for client in clients:
      client.write_message("SUCCESS")
      #SendCoins('{0}|{1}'.format(value,currency))
      logging.info('Data written successfuly')
  return donationid;


def GetSumDonations():
    return GetDonations(-99)


#Get amount of donations for a project
def GetDonations(pid):
  #Connect to Database
  dbConn = MySQLdb.connect(dbserver,dbuser,dbpass,dbname) or die ("could not connect to database")

  cursor = dbConn.cursor()
  value = 0

  try:
    if (pid == -99):
        cursor.execute('SELECT SUM(Ammount) FROM donations')
    else:
        cursor.execute('SELECT SUM(Ammount) FROM donations WHERE ProjectID = {0}'.format(pid))
    data = cursor.fetchone()
    for row in cursor:
      if row[0] is not None:
        value = float(row[0])

    cursor.close();  #close the cursor
    logging.debug('Get project total amount donated: %s', value)
    return value
  except MySQLdb.IntegrityError:
    logging.error('failed to fetch data')
  finally:
    cursor.close()

#Send coins that have not been donated to clients
def SendCoins(msg):
  logging.debug('COINS|{0}'.format(msg))
  for client in clients:
    client.write_message('COINS|{0}'.format(msg))
  #Reset global vars
  global coin
  global curr
  coin = 0
  curr = "EUR"


def SendSumDonations(msg):
  logging.debug('PID|-99|TOTAL|{0}'.format(msg))
  for client in clients:
    client.write_message('PID|-99|TOTAL|{0}'.format(msg))


#Send donations for a specified project ID to clients
def SendDonations(pid, msg):
    if (net_enabled):
        msg = RetrieveDonations(pid)
    logging.debug('PID|{0}|TOTAL|{1}'.format(pid,msg))
    for client in clients:
        client.write_message('PID|{0}|TOTAL|{1}'.format(pid,msg))


#Process Registration
def ProcessRegistration(msg):
  logging.debug('Process registration: %s', msg)
  values = msg.split('|')
  name = values[1]
  email = values[2]
  #Insert Newsletter registration to database
  InsertRegistration(name,email)

#Flag UIDStored
def UIDStored(uid, value):
  dbConn = MySQLdb.connect(dbserver,dbuser,dbpass,dbname) or die ("could not connect to database")
  cursor = dbConn.cursor()

  try:
    #See if there are coins inserted that have not been donated
    logging.debug('UPDATE donations SET uidStored={0} WHERE uid="{1}"'.format(value,uid))
    cursor.execute('UPDATE donations SET uidStored={0} WHERE uid="{1}"'.format(value,uid))
    dbConn.commit()
    cursor.close()  #close the cursor
  except MySQLdb.IntegrityError:
    logging.error('UIDStored: failed to fetch data')
  finally:
    cursor.close()  #close just incase it failed

#Process Donation
def ProcessDonation(msg):
  logging.debug('Process donation: %s', msg)
  values = msg.split('|')
  name = values[1]
  email = values[2]
  public = values[3]
  prname = values[4]
  #This depends on the Language settings
  #projectdetails = values[4].split('?') #contains language info (e.g. 81?lang=el)
  #prid = projectdetails[0]
  prid = values[5]
  #lang = projectdetails[1]  #lang support for printer limited to ASCII
  dondata = values[6]
  l = len(dondata)
  donvalue = dondata[0:l-3]
  doncurr = dondata[l-3:]
  #Switch to Game
  if (values[0] == 'PLAY'):
      SwitchToGame();
  if net_enabled:
    uid = GenerateUID(donvalue)
    #Insert Donation to Database
    donationid = InsertDonation(doncurr,donvalue,name,email,public,prname,prid,uid)
    if (SendDonationToServer(prid,donvalue,uid)):
      UIDStored(uid, True)
    else:
      UIDStored(uid, False)
    #Print receipt
    Th_print(doncurr,donvalue,name,email,prname,prid,donationid,uid)
  else:
    #Insert Donation to Database
    donationid = InsertDonation(doncurr,donvalue,name,email,public,prname,prid,0)
    Th_print(doncurr,donvalue,name,email,prname,prid,donationid,0)


#Close window playing video loop
def CloseVideo():
 logging.debug('Close Video window')
 os.system("wmctrl -a 'Donation Box |'")

#Process Messages
def processmsg(msg):
  logging.debug('Process message: %s', msg)
  values = msg.split('|')
  if (values[0] == 'REQPROJECTTOTAL'):
    s = GetDonations(values[1])
    SendDonations(values[1],s)
  elif (values[0] == 'NEWSLETTER'):
    ProcessRegistration(msg)
  elif ( (values[0] == 'DONATION') or (values[0] == 'PLAY') ):
    ProcessDonation(msg)
  elif (values[0] == 'VIDEO_CLICK'):
    CloseVideo()

#Switch to Game Window
def SwitchToGame():
  if game_enabled:
    logging.debug('Switch to: ')
    logging.debug(game_run)
    #For Reaction game
    #os.system("wmctrl -a reflex_game")
    #For MAME or Pacman game
    os.system(game_run)


#HTTP Server Handler
class WSHandler(tornado.websocket.WebSocketHandler):
  def check_origin(self, origin):
    return True

  def open(self):
    logging.info('New connection was opened')
    clients.append(self)
    #Get inserted coins that have not been donated
    s = GetCoins()
    # Send value and currency to web socket client
    SendCoins(s)
    #Get donations
    #s = GetDonations(1) #PID=1 if we run the box as a single donation project, otherwise we need the Project ID
    #Send Donations to web socket clients
    #SendDonations(1,s)
    if (ui_sendsum):
        s = GetSumDonations()
        SendSumDonations(s)

  #Process any received messages
  def on_message(self, message):
    processmsg(message)

  def on_close(self):
    logging.info('Connection was closed...')
    clients.remove(self)

  #THREAD:Start looking for newly inserted coins
  t = threading.Thread(target=UpdateCoins)
  t.daemon = True
  t.start()

application = tornado.web.Application([
  (r'/ws', WSHandler),
])


if __name__ == "__main__":
  #Start the HTTP server and listen at port 8888
  http_server = tornado.httpserver.HTTPServer(application)
  http_server.listen(8888)
  tornado.ioloop.IOLoop.instance().start()
