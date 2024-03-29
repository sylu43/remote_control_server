from flask import Flask, request, jsonify
import util.db as db
import util.util as util
import util.gpio as gpio
import logging

app = Flask(__name__)
DB = db.DB()
conf = util.getConf()
gpioDict = conf['GPIO']
gpio.setupGPIO(conf)

app.logger.disabled = True
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

'''
{
    'name': ${name},
    'op': ${op}
}
'''
@app.route("/gate_op", methods=["POST"])
def gateOp():
    if not request.is_json:
        logging.warning("wierd stuff")
        return {"error": "Request must be JSON"}, 415
    op = request.json['op']
    if not DB.verifyActivatedUser(request, "/gate_op"):
        logging.warning("{}".format(request.json))
        return {"error": "Authentication failed or not enabled."}, 403
    pin = int(gpioDict[op])
    if pin != None:
        gpio.gateOp(pin)
        logging.info("{}".format(request.json))
        return {"OK": op}, 200
    else:
        logging.warning("{}".format(request.json))
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
@app.route("/update", methods=["POST"])
def update():
    if not request.is_json:
        logging.warning("wierd stuff")
        return {"error": "Request must be JSON"}, 415
    if not DB.verifyAdmin(request, "/update"):
        logging.warning("{}".format(request.json))
        return {'error': "not admin"}, 403
    try:
        DB.updateUser(request.json['guest'])
    except:
        logging.error("{}".format(request.json))
        return {"error": "sqlite error"}, 500
    logging.info("{}".format(request.json))
    return {"info": "updated"}, 201

'''
{
    'name': ${name},
    'zone': ${zone},
    'time': ${time in seconds}
}
'''
@app.route("/register", methods=["POST"])
def register():
    if not request.is_json:
        logging.warning("wierd stuff")
        return {"error": "Request must be JSON"}, 415
    user = request.json
    user['name'] = user['name'].replace(" ","")
    if DB.getUserByName(user['name']) != None:
        logging.warning("{}".format(request.json))
        return {"error": "user exists"}, 409
    try:
        token = DB.registerUser(user)
    except:
        logging.error("{}".format(request.json))
        return {"error": "sqlite error"}, 500
    logging.info("{}".format(request.json))
    return {"info": "registered", "token": token}, 201

'''
{
    'name': ${name}
}
'''
@app.route("/list", methods=["POST"])
def admin():
    if not request.is_json:
        logging.warning("wierd stuff")
        return {"error": "Request must be JSON"}, 415
    users = []
    if not DB.verifyAdmin(request, "/list"):
        logging.warning("{}".format(request.json))
        return {'error': "not admin"}, 403
    for user in DB.allUsers():
        users.append({
            "name": user[0],
            "zone": user[1],
            "activated": user[2],
            "expDate": user[3]
        })
    logging.info("{}".format(request.json))
    return {"users":users}, 200

'''
{
    'name': ${name},
    'guest': ${
        'name': ${name}
    }
}
'''
@app.route("/delete", methods=["POST"])
def delete():
    if not request.is_json:
        logging.warning("wierd stuff")
        return {"error": "Request must be JSON"}, 415
    if not DB.verifyAdmin(request, "/delete"):
        logging.warning("{}".format(request.json))
        return {'error': "not admin"}, 403
    try:
        DB.deleteUser(request.json['guest'])
    except:
        logging.error("{}".format(request.json))
        return {"error": "sqlite error"}, 500
    logging.info("{}".format(request.json))
    return {"info": "delete"}, 200

