from flask import Flask
from flask import request
import yaml 
app = Flask(__name__)
f = open('./pins.yaml','r')
yamlarr = yaml.load(f.read())
@app.route("/getpins", methods=['GET'])
def getpins():
    serialNum = request.args.get('serNum')
    return yaml.dump(yamlarr['pins'][serialNum])

@app.route("/pinstatus",methods=['GET'])
def pinStatus():
    serialNum = request.args.get('serNum')
    pin = request.args.get('pin')
    status = request.args.get('status')
    return "recieved" 
if __name__ == "__main__":
   app.run() 
