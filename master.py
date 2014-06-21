#!/usr/bin/python

from flask import Flask
from flask import request
import yaml, commonFunc

armedZones = []
tmpStatus = {}
pinStatus = {}
app = Flask(__name__)

#Get the list of pins from yaml file
pinYaml = open('./pins.yaml','r')
yamlPins = yaml.load(pinYaml.read())
allPins = yamlPins['pins']

statusYaml = open('status.yaml','r')
tmpStatus = yaml.load(statusYaml.read())
if tmpStatus > 0:
    try:
        tmpStatus['pins']
    except KeyError:
        pinStatus = {}
    else:
        pinStatus = tmpStatus['pins']
    
    try:
        tmpStatus['armed']
    except KeyError:
        armedZones = []
    else:
        armedZones = tmpStatus['armed']
statusYaml.close()

#return the pins for the request pi serial number
@app.route("/getpins", methods=['GET'])
def getpins():
    global allPins

    serialNum = request.args.get('serNum')

    return yaml.dump(allPins[serialNum])

#recieve the status of the pins
@app.route("/pinstatus",methods=['GET'])
def recievePinStatus():
    global allPins
    global pinStatus

    serialNum = str(request.args.get('serNum'))
    pin = int(request.args.get('pin'))
    status = int(request.args.get('status'))
    setStatus(serialNum,pin,status)
    if isArmed(allPins[serialNum][pin]['zones'])  == True and status==1:
        email = commonFunc.email('Pin: '+str(pin)+'\nStatus: '+str(status))
    return "Ok" 

#arm the alarm
@app.route("/arm",methods=['GET'])
def arm():
    global armedZones
    zone = str(request.args.get('zone'))
    armedZones.append(zone)
    writeStatus()
    return "Armed Zone" 

def isArmed(zones):
    global armedZones

    if len(armedZones) == 0:
        return False 
    for zone in zones:
        if zone in armedZones:
            return True
    return False 

def setStatus(serNum,pin,status):
    global pinStatus
    try:
        pinStatus[serNum]
    except KeyError:
        pinStatus[serNum] = {}
    pinStatus[serNum][pin] = status
    writeStatus()
    return

def writeStatus():
    global armedZones
    global pinStatus

    statusYaml = open('status.yaml','r+')
    statusYaml.write(yaml.dump({'armed':armedZones,'pins':pinStatus}))
    statusYaml.close
    return

if __name__ == "__main__":
   app.run(debug=True) 
