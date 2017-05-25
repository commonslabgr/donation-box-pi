#!/usr/bin/python

from __future__ import print_function
import coopboxqr
import halfeuro
import oneeuro
import twoeuro
from Adafruit_Thermal import *

printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)  
uid = '23287984'
amount = 2;
printer.begin(150)
printer.setTimes(0,0) #print as fast as possible
printer.doubleHeightOn()
printer.println('         CODE: {0}'.format(uid))
printer.doubleHeightOff()
printer.feed(1)
printer.println('scan the QR code or go to ')
printer.println('http://thecoopbox.commonslab.gr')
printer.println('and register for your perk')
if (amount == 0.5):
  printer.printBitmap(halfeuro.width, halfeuro.height, halfeuro.data)    
elif (amount == 1):
  printer.printBitmap(oneeuro.width, oneeuro.height, oneeuro.data)
elif (amount == 2):
  printer.printBitmap(twoeuro.width, twoeuro.height, twoeuro.data)

printer.feed(1)
printer.printBitmap(coopboxqr.width, coopboxqr.height, coopboxqr.data)
printer.feed(3)
