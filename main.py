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
    'name': ${name},
    'op': ${op}
}
'''
@app.post("/gate_op")
def gateOp():
    if not request.is_json:
        return {"error": "Request must be JSON"}, 415
    op = request.json['op']
    if not DB.verifyActivatedUser(request, "/gate_op"):
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
    'guest': ${
        'name': ${name},
        'zone': ${zone},
        'activated': ${activate},
        'expDate': ${expDate}
    }
}
'''
@app.post("/update")
def update():
    if not request.is_json:
        return {"error": "Request must be JSON"}, 415
    if not DB.verifyAdmin(request, "/update"):
        return {'error': "not admin"}, 403
    try:
        DB.updateUser(request.json['guest'])
    except:
        return {"error": "sqlite error"}, 500
    return {"info": "activated"}, 201

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
    user = request.json
    user['name'] = user['name'].replace(" ","")
    if DB.getUserByName(user['name']) != None:
        return {"error": "user exists"}, 409
    try:
        token = DB.registerUser(user)
    except:
        return {"error": "sqlite error"}, 500
    return {"info": "registered", "token": token}, 201

'''
{
    'name': ${name}
}
'''
@app.post("/list")
def admin():
    if not request.is_json:
        return {"error": "Request must be JSON"}, 415
    users = []
    if not DB.verifyAdmin(request, "/list"):
        return {'error': "not admin"}, 403
    for user in DB.allUsers():
        users.append({
            "name": user[0],
            "zone": user[1],
            "activated": user[2],
            "expDate": user[3]
        })
    return {"users":users}, 200

'''
{
    'name': ${name},
    'guest': ${
        'name': ${name}
    }
}
'''
@app.post("/delete")
def delete():
    if not request.is_json:
        return {"error": "Request must be JSON"}, 415
    if not DB.verifyAdmin(request, "/delete"):
        return {'error': "not admin"}, 403
    name = request.json['name']
    try:
        DB.deleteUser(request.json['guest']['name'])
    except:
        return {"error": "sqlite error"}, 500
    return {"info": "delete"}, 200

