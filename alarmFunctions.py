#!/usr/bin/python
import time, urllib2, yaml
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error import RPi.GPIO!  Are you sudo?")

#Set the Pin Numbering Mode: BOARD=the pin number on the board, BCM=the channel numbers
GPIO.setmode(GPIO.BOARD)

#Warnings?
#GPIO.setwarnings(True)

pinStatus = {} 

def getSerial():
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

def getPinsFromHost(server):
    server = "http://"+str(server)+"/getpins?serNum="+str(getSerial())
    pins = yaml.load(urllib2.urlopen(server))
    return pins.keys() 

def notifyHost(pin,status):
    return str(pin)+": "+str(status) 

if __name__ == '__main__':
    f = open('./settings.yaml','r')
    settings = yaml.load(f.read())
    print getSerial()
    pins = getPinsFromHost(settings["master"])
    for pin in pins:
        pinSetup(pin,'in')

    while True:
        for pin in pins:
            if pinStatus.has_key(pin) == False:
                pinStatus[pin] = 0 
            current = checkPin(pin)
            if current != pinStatus[pin]:
                print notifyHost(pin,current)
            pinStatus[pin] = current
        time.sleep(.2)
