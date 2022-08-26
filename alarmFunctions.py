#!/usr/bin/python

######
##run:
## modprobe w1-gpio
## modprobe w1-therm
######


#Import needed modules
import time, urllib.request, urllib.error, urllib.parse, yaml, commonFunc, lib16in
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
sensors = {}

def getTemp(server):
    for sensor in sensors:
        crc = 'NO'
        while crc != 'YES':
            content = readTemp(sensor)
            lines = content.split("\n")
            crc = lines[0].split("=")[1].split()[1]
            temp = lines[1].split("=")[1]
        updateTemp(sensor,temp,server)
    return temp
def readTemp(sensor):
   f = open('/sys/bus/w1/devices/'+sensor+'/w1_slave','r')
   content = f.read()
   f.close()
   return content
def getTempSensors(server):
    #ask the Server what pins this pi should be monitoring
    server = "http://"+server+"/gettempsensors?serNum="+str(getSerial())
    while True:
        try:
            sensors = yaml.load(urllib.request.urlopen(server), Loader=yaml.FullLoader)
        except urllib.error.URLError as e:
            commonFunc.email("There was an error connecting to: "+server+"\nError:"+str(e))
            time.sleep((30*60))
            continue 
        break
    return list(sensors.keys()) 

def updateTemp(sensor,temp,server):
    server = "http://"+server+"/updatetemp?serNum="+str(getSerial())+"&sensor="+sensor+"&temp="+str(temp)
    while True:
        try:
            sensors = urllib.request.urlopen(server)
        except urllib.error.URLError as e:
            commonFunc.email("There was an error connecting to: "+server+"\nEorror:"+str(e))
            time.sleep((30*60))
            continue
        break
    return
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

def pinSetup(pin,number):
    #configure the GPIO pin for in or out
    if pin['type'] in {'in', 'Dekota', 'Reed'}:
        GPIO.setup(number, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        try:
          GPIO.add_event_detect(number, GPIO.BOTH, callback=pinAction, bouncetime=200) # Set up an interrupt to look for button presses
        except:
          pass
    elif pin['type'] == 'expander':
        GPIO.setup(number, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        try:
          GPIO.add_event_detect(number, GPIO.BOTH, callback=expanderAction, bouncetime=200) # Set up an interrupt to look for button presses
        except:
          pass
    elif pin['type'] == 'out':
        GPIO.setup(number, GPIO.OUT)

def checkPin(pin):
    #what is the current GPIO pin reading
    return GPIO.input(pin)

def getPinsFromHost(server):
    #ask the Server what pins this pi should be monitoring
    server = "http://"+server+"/getpins?serNum="+str(getSerial())
    while True:
        try:
            pins = yaml.load(urllib.request.urlopen(server), Loader=yaml.FullLoader)
        except urllib.error.URLError as e:
            commonFunc.email("There was an error connecting to: "+server+"\nError:"+str(e))
            time.sleep((30*60))
            continue 
        break
    return pins 

def notifyHost(pin,status,server):
    #alert the server to a change in pin status
    server = "http://"+server+"/pinstatus?pin="+str(pin)+"&status="+str(status)+"&serNum="+str(getSerial())
    try:
        response = yaml.load(urllib.request.urlopen(server), Loader=yaml.FullLoader)
    except urllib.error.URLError as e:
        commonFunc.email("There was an error connecting to: "+server+"\nError:"+str(e))
        response = e
    return response

def start():
    #setup settings and pins from stored yaml files
    global settings
    global pins
    global sensors

    settings = commonFunc.getYaml('settings')
    pins = getPinsFromHost(settings["master"])
    sensors = getTempSensors(settings["master"])
    print(pins)
    for pin in pins:
        print(pins[pin])
        pinSetup(pins[pin],pin)

def main():
    # do the work
    start()
    restarted = False
    gotTemp = False
    firstRun = True

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

        #is it time to check the temp
        tempMod = int((startTime-time.time())%settings['tempTime'])
        if ((tempMod == 0) or (firstRun == True)) and gotTemp == False:
            getTemp(settings['master'])
            gotTemp = True
            firstRun = False
        elif gotTemp == True and mod == 0:
            pass
        else:
            gotTemp = False
        
        #Check the pins
       # result = "Ok"
       # for pin in pins:
       #     #Do I have the last pin status
       #     if pinStatus.has_key(pin) == False:
       #         pinStatus[pin] = 0
       #     #Get the current status of the pin
       #     current = checkPin(pin)
       #     #if pin status has change notify the server
       #     if current != pinStatus[pin]:
       #         result = notifyHost(pin,current,settings["master"])
       #     #update pinStatus for later
       #     pinStatus[pin] = current
       #     #output if the connection to server failed
       #     if result != "Ok":
       #         print "Failure to notifiy Host: "+str(result)
        time.sleep(.2)

def pinAction(acctedPin):
    status = checkPin(acctedPin)
    notifyHost(acctedPin,status,settings["master"])
    return

def expanderAction(acctedPin):
    print("Expander Pin!")
    status1 = checkPin(acctedPin)
    status = checkExpander()
    print("Expander Status: {0}".format(status))
    notifyHost(acctedPin,status,settings["master"])
    return

def checkExpander():
    return lib16in.readAll(0)

if __name__ == '__main__':
    main()
