import datetime
import json
import urllib2
import time
from time import gmtime, strftime

def SendDonationToServer(prid,boxid,value):
    from time import gmtime, strftime
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    #data = {"ProjectID":1,"BoxID":1,"DateTime":time.strftime('%Y-%m-%d %H:%M:%S'),"Amount":2}
    data = {}
    data['ProjectID'] = prid
    data['BoxID'] = boxid 
    data['Amount'] = value
    data['DonationTime'] = timestamp
    req = urllib2.Request('http://thecoopbox.commonslab.gr/network_input.php')
    req.add_header('Content-Type', 'application/json')
    #print "Sending:"
    print json.dumps(data)
    response = urllib2.urlopen(req, json.dumps(data))
    
SendDonationToServer(1,2,3)
