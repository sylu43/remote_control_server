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
    'op': ${op}
}
'''
@app.post("/gate_op")
def gateOp():
    if not request.is_json:
        return {"error": "Request must be JSON"}, 415
    op = request.json['op']
    if not DB.verifyEnabledUser(request, "/gate_op"):
        return {"error": "Authentication failed or not enabled."}, 403
    pin = gpioDict[op]
    if pin != None:
        gpio.gateOp(pin)
        return {"OK": op}, 200
    else:
        return {"error": "Unknown operation"}, 400

'''
{
    'name': ${name},
    'zone': ${zone},
    'time': ${time in seconds}
}
'''
@app.post("/register")
def register():
    if not request.is_json:
        return {"error": "Request must be JSON"}, 415
    json = request.json
    if DB.getUserByName(json['name']) != None:
        return {"error": "user exists"}, 409
    try:
        otp = DB.registerUser(json)
    except:
        return {"error": "sqlite error"}, 500
    return {"info": "registerd", "otp": otp}, 201

'''
{
    'name': ${name}
}
'''
@app.post("/checkin")
def checkin():
    if not request.is_json:
        return {"error": "Request must be JSON"}, 415
    name = request.json['name']
    if DB.toCheckin(name):
        try:
            response = DB.activateUser(name)
        except:
            return {"error": "sqlite error"}, 500
        return response, 201
    return {"info": "not register or activated"}, 403

@app.get("/list")
def admin():
    users = []
    if not DB.verifyAdmin(request, "/list"):
        return {'error': "not admin"}, 403
    for user in DB.allUsers():
        users.append({
            "name": user[0],
            "zone": user[1],
            "activated": user[2],
            "enabled": user[3],
            "expireDate": user[4]
        })
    return {"users":users}, 200


