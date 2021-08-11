from flask import Flask, request, jsonify
import util.db as db
import util.util as util
import util.gpio as gpio

app = Flask(__name__)
DB = db.DB()
conf = util.getConf()
gpioDict = conf['GPIO']

'''
{
    'mothod':#method,
    'body':stringify({
        'op':op
    }),
    'header':{
        context_type,
        nonce
        token
        signature
    }
}
signature is signed '/api/$path$nonce$stringify(body)'
'''

#op
@app.post("/gate_op")
def gateOp():
    if request.is_json:
        op = request.get_json()
        pin = gpioDict[op['op']]
        if pin != None:
            gpio.gateOp(pin)
            return {}, 200
        else:
            return {"error": "Unknown operation"}, 400
    return {"error": "Request must be JSON"}, 415

#name zone time
@app.post("/register")
def register():
    if request.is_json:
        info = request.get_json()
        if DB.findUser(info['name']):
            return {"error": "user exists"}, 409
        try:
            DB.registerUser(info)
        except:
            return {"error": "sqlite error"}, 500
        return {"info": "registerd"}, 201
    return {"error": "Request must be JSON"}, 415


