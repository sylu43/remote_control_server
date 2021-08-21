from flask import Flask, request, jsonify
import util.db as db
import util.util as util
import util.gpio as gpio
import jwt
import hmac
import binascii

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

'''
{
    'op': ${op}
}
'''
@app.post("/gate_op")
def gateOp():
    if request.is_json:
        data = request.get_json()
        headers = request.headers
        user = DB.getUser(headers['token'])
        nonce = headers['nonce']
        HMAC = hmac.new(bytearray.fromhex(user[5]), digestmod='sha256')
        HMAC.update(("/gate_op%s%s" % (nonce, str(request.json).replace(" ","").replace("\'","\""))).encode('utf-8'))
        if binascii.hexlify(HMAC.digest()).decode() != headers['Signature']:
            return {"error": "not authenticated"}, 403
        pin = gpioDict[data['op']]
        if pin != None:
            gpio.gateOp(pin)
            return {"OK": data['op']}, 200
        else:
            return {"error": "Unknown operation"}, 400
    return {"error": "Request must be JSON"}, 415

'''
{
    'name': ${name},
    'zone': ${zone},
    'time': ${time in seconds}
}
'''
@app.post("/register")
def register():
    if request.is_json:
        data = request.get_json()
        if DB.findUser(data['name']):
            return {"error": "user exists"}, 409
        try:
            otp = DB.registerUser(data)
        except:
            return {"error": "sqlite error"}, 500
        return {"info": "registerd", "otp": otp}, 201
    return {"error": "Request must be JSON"}, 415

'''
{
    'name': ${name}
}
'''
@app.post("/checkin")
def checkin():
    if request.is_json:
        data = request.get_json()
        if DB.toCheckin(data['name']):
            try:
                response = DB.activateUser(data['name'])
            except:
                return {"error": "sqlite error"}, 500
            return response, 201
        return {"info": "not register or activated"}, 403
    return {"error": "Request must be JSON"}, 415




