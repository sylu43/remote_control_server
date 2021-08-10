from flask import Flask, request, jsonify
import util.db
import util.util

app = Flask(__name__)
db = util.db.DB()
conf = util.util.getConf()
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
        key
        signature
    }
}
signature is signed '/api/$path$nonce$stringify(body)'
'''

@app.post("/gate_op")
def gateOp():
    if request.is_json:
        op = request.get_json()
        pin = gpioDict[op['op']]
        if pin != None:
            util.util.gateOp()
            return {}, 200
        else:
            return {"error": "Unknown operation"}, 400
    return {"error": "Request must be JSON"}, 415

@app.post("/register")
def register():
    if request.is_json:
        info = request.get_json()
        db.addUser(util.util.jsonToTuple(info))
        return info, 201
    return {"error": "Request must be JSON"}, 415

