#!/usr/bin/python

from flask import Flask
from flask import request
import yaml 

app = Flask(__name__)

#Get the list of pins from yaml file
f = open('./pins.yaml','r')
yamlarr = yaml.load(f.read())

#return the pins for the request pi serial number
@app.route("/getpins", methods=['GET'])
def getpins():
    serialNum = request.args.get('serNum')
    return yaml.dump(yamlarr['pins'][serialNum])

#recieve the status of the pins
@app.route("/pinstatus",methods=['GET'])
def pinStatus():
    serialNum = request.args.get('serNum')
    pin = request.args.get('pin')
    status = request.args.get('status')
    return "recieved" 

if __name__ == "__main__":
   app.run(debug=True) 
