#!/usr/bin/python

from flask import Flask, make_response
import yaml, commonFunc, time, random, StringIO, os, socket
#from yaml import CLoader, CDumper
os.environ['MPLCONFIGDIR'] = "/home/pi/"
from flask import request
#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#from matplotlib.figure import Figure
from datetime import datetime
sysStatus = {}
app = Flask(__name__)
app.debug=True
settings = commonFunc.getYaml('settings')
#Get the list of pins from yaml file
pins = commonFunc.getYaml('pins')
allPins = pins['pins']
allTemps = pins['temps']
sysStatus = commonFunc.getYaml('status')
if type(sysStatus) is not dict:
    sysStatus = {}
    sysStatus['pins'] ={}
    sysStatus['armed'] = []
    sysStatus['checkIn'] = {}
    sysStatus['triggered'] = []

@app.route("/getstatus")
def getStatus():
    global sysStatus
    global pins

    get = str(request.args.get('get'))
    if get == 'zones':
        result = yaml.dump(pins['zones'])
    else:
        result = yaml.dump(sysStatus)
    return result

#return the pins for the request pi serial number
@app.route("/getpins", methods=['GET'])
def getpins():
    global allPins
    global sysStatus

    serialNum = str(request.args.get('serNum'))
    sysStatus['checkIn'][serialNum] = time.time()
    writeStatus()
    return yaml.dump(allPins[serialNum])

#return the temperature sensors for the request pi serial number
@app.route("/gettempsensors", methods=['GET'])
def getTempSensors():
    global allPins
    global allTemps
    global sysStatus

    serialNum = str(request.args.get('serNum'))
    sysStatus['checkIn'][serialNum] = time.time()
    writeStatus()
    return yaml.dump(allTemps[serialNum])

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

#recieve the temps
@app.route("/updatetemp",methods=['GET'])
def updateTemp():
    global allPins
    global sysStatus

    serialNum = str(request.args.get('serNum'))
    sensor = request.args.get('sensor')
    temp = int(request.args.get('temp'))
    sysStatus['checkIn'][serialNum] = time.time()
    setTemp(serialNum,sensor,temp)
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
    global allPins
    zone = str(request.args.get('zone'))
    code = int(request.args.get('code'))

    if zone in pins['codes'][code]['zones']:
        sysStatus['armed'].remove(zone)
        if zone in sysStatus['triggered']:
            sysStatus['triggered'].remove(zone)
        writeStatus()
        return "OK"
    else:
        return "Error: "+yaml.dump(pins['codes'].keys())

##show the temp history
#@app.route("/temp.png")
#def plot():
#    fig = Figure(figsize=(40,40))
#    axis = fig.add_subplot(1, 1, 1)
#
#    temps = getTempLists()
##    ys = [50,50.4,20,60,50]
##    xs = [datetime(2014,8,14,23,50),datetime(2014,8,14,23,55),datetime(2014,8,15,0,0),datetime(2014,8,15,0,5),datetime(2014,8,15,0,10)]
#    ys = temps[1]
#    xs = temps[2]
#
# 
#    axis.plot(xs, ys)
#    canvas = FigureCanvas(fig)
#    output = StringIO.StringIO()
#    canvas.print_png(output)
#    response = make_response(output.getvalue())
#    response.mimetype = 'image/png'
#    return response

def isArmed(zones):
    global sysStatus
    if len(sysStatus['armed']) == 0:
        return False 
    for zone in zones:
        if zone in sysStatus['armed']:
            if zone not in sysStatus['triggered']:
                sysStatus['triggered'].append(zone)
            return True
    return False 
@app.route("/temps.test")
def getTempLists():

    global allTemps

    cel = []
    fer = []
    ttime = []
    sensors = []
    temps = []

    for ser in allTemps:
        for sensor in allTemps[ser]:
            sensors.append(sensor)
#    f = open('./'+str(sensors[0])+'.yaml','r')
#    content = f.read()
#    f.close()
#    content = content.split('\n')
    i = 0
    with open('./'+str(sensors[0])+'.yaml','r') as f:
        for line in f:
            thisLine = yaml.load(line, Loader=CLoader)
            cel.append(thisLine['c'])
            fer.append(thisLine['f'])
            #ttime.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(thisLine['time'])))
            ttime.append(datetime.fromtimestamp(thisLine['time']))
            i = i+1

#    for temp in temps:
#        cel.append(temp['c'])
#        fer.append(temp['f'])
#        time.append(temp['time'])


    return [cel,fer,ttime]

def setStatus(serNum,pin,status):
    global sysStatus 
    try:
        sysStatus['pins'][serNum]
    except KeyError:
        sysStatus['pins'][serNum] = {}
    sysStatus['pins'][serNum][pin] = status
    writeStatus()
    return

def setTemp(serNum,sensor,temp):
    temp = float(temp)
    tempData = {}
    tempData['time'] = time.time()
    tempData['r'] = temp
    tempData['c'] = temp/1000
    tempData['f'] = 9.0/5.0 * tempData['c'] + 32
    tFile = "./"+str(sensor)+".yaml"
    print tFile
    myFile = open(tFile,"a+")
    myFile.write(yaml.dump(tempData))
    myFile.close()
    message = "raspberrypi.temp." + str(sensor) +".raw" + " " + str(tempData['r']) + " " + str(tempData['time']) +"\n"
    message += "raspberrypi.temp." + str(sensor) +".celcius" + " " + str(tempData['c']) + " " + str(tempData['time']) +"\n"
    message += "raspberrypi.temp." + str(sensor) +".fahrenheit" + " " + str(tempData['f']) + " " + str(tempData['time']) +"\n"
    sock = socket.socket()
    sock.connect(('192.168.22.109',2003))
    while message:
        bytes = sock.send(message)
        message = message[bytes:]
    sock.close()
    return

def writeStatus():
    global sysStatus

    statusYaml = open('./status.yaml','r+')
    statusYaml.write(yaml.dump(sysStatus))
    statusYaml.close
    return

if __name__ == "__main__":
   app.run(debug=True,host='0.0.0.0') 
