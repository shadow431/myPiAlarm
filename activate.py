#!/usr/bin/python
import time
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error import RPi.GPIO!  Are you sudo?")

#Set the Pin Numbering Mode: BOARD=the pin number on the board, BCM=the channel numbers
GPIO.setmode(GPIO.BOARD)

#Warnings?
#GPIO.setwarnings(True)

pinStatus = {} 

def getserial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"

  return cpuserial

def pinSetup(pin,type):
    if type == 'in':
        GPIO.setup(pin, GPIO.IN)
    elif type == 'out':
        GPIO.setup(pin, GPIO.OUT)

def checkPin(pin):
    return GPIO.input(pin)

def getPinsFromHost():
    return [12]

def notifyHost(pin,status):
    return str(pin)+": "+str(status) 

if __name__ == '__main__':
    pins = getPinsFromHost()
    for pin in pins:
        pinSetup(pin,'out')

        for pin in pins:
            GPIO.output(pin,1)
            time.sleep(.2)
            GPIO.output(pin,0)
