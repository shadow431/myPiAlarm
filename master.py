#!/usr/bin/python

from flask import Flask
from flask import request
import yaml, commonFunc, time

sysStatus = {}
app = Flask(__name__)

settings = commonFunc.getYaml('settings')
#Get the list of pins from yaml file
allPins = commonFunc.getYaml('pins')['pins']
sysStatus = commonFunc.getYaml('status')
if type(sysStatus) is not dict:
    sysStatus = {}
    sysStatus['pins'] ={}
    sysStatus['armed'] = []
    sysStatus['checkIn'] = {}

@app.route("/getstatus")
def getStatus():
    global sysStatus

    retrun yaml.dump(sysStatus)
#return the pins for the request pi serial number
@app.route("/getpins", methods=['GET'])
def getpins():
    global allPins
    global sysStatus

    serialNum = str(request.args.get('serNum'))
    sysStatus['checkIn'][serialNum] = time.time()
    writeStatus()
    return yaml.dump(allPins[serialNum])

#recieve the status of the pins
@app.route("/pinstatus",methods=['GET'])
def recievePinStatus():
    global allPins
    global sysStatus

    serialNum = str(request.args.get('serNum'))
    pin = int(request.args.get('pin'))
    status = int(request.args.get('status'))
    sysStatus['checkIn'][serialNum] = time.time()
    setStatus(serialNum,pin,status)
    if isArmed(allPins[serialNum][pin]['zones'])  == True and status==1:
        email = commonFunc.email('Pin: '+str(pin)+'\nStatus: '+str(status))
    return "Ok" 

#arm the alarm
@app.route("/arm",methods=['GET'])
def arm():
    global sysStatus
    zone = str(request.args.get('zone'))
    sysStatus['armed'].append(zone)
    writeStatus()
    return "Armed Zone" 

#arm the alarm
@app.route("/disarm",methods=['GET'])
def disarm():
    global sysStatus
    zone = str(request.args.get('zone'))
    sysStatus['armed'].remove(zone)
    writeStatus()
    return "Disarmed Zone" 

def isArmed(zones):
    global sysStatus

    if len(sysStatus['armed']) == 0:
        return False 
    for zone in zones:
        if zone in sysStatus['armed']:
            return True
    return False 

def setStatus(serNum,pin,status):
    global sysStatus 
    try:
        sysStatus['pins'][serNum]
    except KeyError:
        sysStatus['pins'][serNum] = {}
    sysStatus['pins'][serNum][pin] = status
    writeStatus()
    return

def writeStatus():
    global sysStatus

    statusYaml = open('status.yaml','r+')
    statusYaml.write(yaml.dump(sysStatus))
    statusYaml.close
    return

if __name__ == "__main__":
   app.run(debug=True,host='0.0.0.0') 
