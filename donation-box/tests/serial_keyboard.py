import serial
import threading
import time
import logging
import os

logging.basicConfig(filename='Serial.log', level=logging.DEBUG, format='%(levelname)s %(asctime)s: %(message)s')

last_received = ''

def receiving(ser):
  global last_received
  buffer = ''
  while True:
    #print "waiting..."
    buffer = ser.readline()
    if buffer <> '':
      logging.info('Received: %s', buffer)
      if 'UP' in buffer:
        os.system('xdotool key Up')
      elif 'DO' in buffer:
        os.system('xdotool key Down')
      elif 'LE' in buffer:
        os.system('xdotool key Left')
      elif 'RI' in buffer:
        os.system('xdotool key Right')

class SerialData(object):
  def __init__(self, init=50):
    try:
      #check config.json file for the settings of the serial port
      self.ser = ser = serial.Serial("/dev/ttyUSB0", "9600")
      #self.ser = ser = serial.Serial(config["Serial"]["dev"], config["Serial"]["rate"])
    except serial.serialutil.SerialException:
      #no serial connection
      self.ser = None
      logging.error('Serial Connection failed')
    else:
      threading.Thread(target=receiving, args=(self.ser,)).start()

  def next(self):
    if not self.ser:
       return 100
    for i in range(40):
      raw_line = last_received
      try:
        return raw_line.strip()
      except ValueError:
        logging.error('Incorrect data: %s',raw_line)
        time.sleep(.005)
    return 0.

  def __del__(self):
    if self.ser:
      self.ser.close()


if __name__=='__main__':
  s = SerialData()
  for i in range(500):
    time.sleep(.015)
