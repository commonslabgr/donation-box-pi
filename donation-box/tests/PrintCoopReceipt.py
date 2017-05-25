#!/usr/bin/python
from __future__ import print_function
import coopboxqr
import halfeuro
import oneeuro
import twoeuro
import sys, getopt
from Adafruit_Thermal import *

def main(argv):
  printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)
  amount = 0;
  uid = '123456'
  try:
    opts, args = getopt.getopt(argv,"ha:i:",["amount=","id="])
  except getopt.GetoptError:
    #print 'PrintCoopReceipt.py -a -i'
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-h':
      #print 'PrintCoopReceipt.py -a <amount> -i <uniqueid>'
      sys.exit()
    elif opt in ('-a', '--amount'):
      amount = arg
    elif opt in ('-i', '--id'):
      uid = arg

  printer.begin(150)
  printer.setTimes(0,0) #print as fast as possible
  printer.doubleHeightOn()
  printer.println('         CODE: {0}'.format(uid))
  printer.doubleHeightOff()
  printer.feed(1)
  printer.println('scan the QR code or go to ')
  printer.println('http://thecoopbox.commonslab.gr')
  printer.println('and register for your perk')
  if (amount == '0.50'):
    printer.printBitmap(halfeuro.width, halfeuro.height, halfeuro.data)
  elif (amount == '1.00'):
    printer.printBitmap(oneeuro.width, oneeuro.height, oneeuro.data)
  elif (amount == '2.00'):
    printer.printBitmap(twoeuro.width, twoeuro.height, twoeuro.data)

  printer.feed(1)
  printer.printBitmap(coopboxqr.width, coopboxqr.height, coopboxqr.data)
  printer.feed(3)

if __name__ == "__main__":
   main(sys.argv[1:])
