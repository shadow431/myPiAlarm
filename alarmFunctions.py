#!/usr/bin/python

#Import needed modules
import time, urllib2, yaml, commonFunc
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error import RPi.GPIO!  Are you sudo?")


#Set the Pin Numbering Mode: BOARD=the pin number on the board, BCM=the channel numbers
GPIO.setmode(GPIO.BOARD)

#Warnings?
#GPIO.setwarnings(True)

#setup needed variable and Dictionarys
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
    #configure the GPIO pin for in or out
    if type == 'in':
        GPIO.setup(pin, GPIO.IN)
    elif type == 'out':
        GPIO.setup(pin, GPIO.OUT)

def checkPin(pin):
    #what is the current GPIO pin reading
    return GPIO.input(pin)

def getPinsFromHost(server):
    #ask the Server what pins this pi should be monitoring
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
    #alert the server to a change in pin status
    server = "http://"+server+"/pinstatus?pin="+str(pin)+"&status="+str(status)+"&serNum="+str(getSerial())
    try:
        response = yaml.load(urllib2.urlopen(server))
    except urllib2.URLError,e:
        commonFunc.email("There was an error connecting to: "+server+"\nError:"+str(e))
        response = e
    return response

def start():
    #setup settings and pins from stored yaml files
    global settings
    global pins

    settings = commonFunc.getYaml('settings')
    pins = getPinsFromHost(settings["master"])
    for pin in pins:
        pinSetup(pin,'in')

def main():
    # do the work
    start()
    restarted = False

    while True:
        #Is it time to refesh settings and pins?
        mod = int((startTime-time.time())%settings['checkinTime'])
        if mod == 0 and restarted == False:
            start()
            restarted = True
        elif restarted == True and mod == 0:
            pass
        else:
            restarted = False

        #Check the pins
        result = "Ok"
        for pin in pins:
            #Do I have the last pin status
            if pinStatus.has_key(pin) == False:
                pinStatus[pin] = 0
            #Get the current status of the pin
            current = checkPin(pin)
            #if pin status has change notify the server
            if current != pinStatus[pin]:
                result = notifyHost(pin,current,settings["master"])
            #update pinStatus for later
            pinStatus[pin] = current
            #output if the connection to server failed
            if result != "Ok":
                print "Failure to notifiy Host: "+str(result)
        time.sleep(.2)

if __name__ == '__main__':
    main()
