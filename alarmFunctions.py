#!/usr/bin/python
import time, urllib2, yaml, commonFunc
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error import RPi.GPIO!  Are you sudo?")

#Set the Pin Numbering Mode: BOARD=the pin number on the board, BCM=the channel numbers
GPIO.setmode(GPIO.BOARD)

#Warnings?
#GPIO.setwarnings(True)
startTime = time.time()
pins = {}
pinStatus = {} 
settings = {}

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
    server = "http://"+server+"/getpins?serNum="+str(getSerial())
    while True:
        try:
            pins = yaml.load(urllib2.urlopen(server))
        except urllib2.URLError,e:
            commonFunc.email("There was an error connecting to: "+server+"\nError:"+str(e))
            time.sleep((30*60))
            continue 
        break
    return pins.keys() 

def notifyHost(pin,status,server):
    server = "http://"+server+"/pinstatus?pin="+str(pin)+"&status="+str(status)+"&serNum="+str(getSerial())
    try:
        response = yaml.load(urllib2.urlopen(server))
    except urllib2.URLError,e:
        commonFunc.email("There was an error connecting to: "+server+"\nError:"+str(e))
        response = e
    return response

def start():
    global settings
    global pins

    settings = commonFunc.getYaml('settings')
    pins = getPinsFromHost(settings["master"])
    for pin in pins:
        pinSetup(pin,'in')

def main():
    start()
    restarted = False
    while True:
        mod = int((startTime-time.time())%settings['checkinTime'])
        if mod == 0 and restarted == False:
            start()
            restarted = True
        elif restarted == True and mod == 0:
            pass
        else:
            restarted = False
        result = "Ok"
        for pin in pins:
            if pinStatus.has_key(pin) == False:
                pinStatus[pin] = 0 
            current = checkPin(pin)
            if current != pinStatus[pin]:
                result = notifyHost(pin,current,settings["master"])
            pinStatus[pin] = current
            if result != "Ok":
                print "Failure to notifiy Host: "+str(result)
        time.sleep(.2)

if __name__ == '__main__':
    main()
