#!/usr/bin/python
####################################################
# Name: Donation Box Network deamon
#
# Description:
# Syncs the local database to the online network database
#
# Author: Dimitris Koukoulakis
#
# License: GNU GPL v3.0
####################################################

import MySQLdb
import urllib2
import logging
import json
import time
from decimal import *
from time import sleep

json_data=open('/home/commonslab/donation-box/config.json')
config = json.load(json_data)
json_data.close()

logging.basicConfig(filename='Network_deamon.log', level=logging.DEBUG, format='%(levelname)s %(asctime)s: %(message)s')
logging.debug('Coop Box Network deamon started')
#DATABASE
dbserver = config["Database"]["server"]
dbuser = config["Database"]["username"]
dbpass = config["Database"]["password"]
dbname = config["Database"]["name"]
#NETWORK
net_enabled = config["Network"]["enabled"]
net_url = config["Network"]["URL"]
net_send = config["Network"]["insert"]
net_rec = config["Network"]["get"]
net_boxid = config["Network"]["boxID"]

getcontext().prec = 2

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
    logging.error('failed to fetch data')
  finally:
    cursor.close()  #close just incase it failed


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
    #logging.debug('Sending: {0}'.format(data))
    response = urllib2.urlopen(req, json.dumps(data))
    result = response.read()
    logging.debug('Response from {0}/{1}: {2}'.format(net_url,net_send,result))
    if 'created successfully' in result:
      return True
    else:
      return False


def CheckUIDs():
    dbConn = MySQLdb.connect(dbserver,dbuser,dbpass,dbname) or die ("could not connect to database")
    cursor = dbConn.cursor()
    uid = ""
    try:
        cursor.execute('SELECT ProjectID, Ammount, uid FROM donations WHERE uidStored is not True')
        numrows = cursor.rowcount

        for row in xrange(0, numrows):
            row = cursor.fetchone()
            prid = row[0]
            amount = float(row[1])
            uid = row[2]
            if uid is not None:
              logging.debug('UID to update:{0}'.format(uid))
              result = SendDonationToServer(prid,amount,uid)
              if (result == True):
                UIDStored(uid, True)
              else:
                UIDStored(uid, False)
                #Wait a few seconds to avoid sending requests too fast
              sleep(1)

        cursor.close();  #close the cursor

    except MySQLdb.IntegrityError:
        logging.error('failed to fetch data')
    finally:
        cursor.close()

CheckUIDs()
