from flask import Flask, request, jsonify
import util.db as db
import util.util as util
import util.gpio as gpio
import jwt

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
        return {"info": "registerd"}, 201
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
        if DB.findUser(data['name']):
            try:
                user = DB.activateUser(data['name'])
                print(user)
            except:
                return {"error": "sqlite error"}, 500
            s = {"data": jwt.encode({
                'token': user[4],
                'secret': user[5]
            }, DB.otpList.get(user[0]), algorithm='HS384').decode()}
            print(s)
            return s, 201
        return {"info": "not registerd"}, 201
    return {"error": "Request must be JSON"}, 415




