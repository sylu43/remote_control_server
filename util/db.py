import sqlite3
import os
import datetime
import jwt
import hmac
import binascii
import random
from math import floor
from threading import Timer

class DB():

    con = None
    cur = None
    otpList = {}
    autoDestroyTime = 1800

    def __init__(self):
        DB = 'files/remote_control.db'

        self.con = sqlite3.connect(DB, check_same_thread=False)
        self.cur = self.con.cursor()

        #check users table
        self.cur.execute('''select count(name) from sqlite_master where type='table' and name='users' ''')
        if self.cur.fetchone()[0] == 0:
            self.cur.execute('''create table users(name text, zone text, activated int2, expireDate real, token text, secret text)''')

        #check logs table
        self.cur.execute('''select count(name) from sqlite_master where type='table' and name='logs' ''')
        if self.cur.fetchone()[0] == 0:
            self.cur.execute('''create table logs(event text, user text, op text, time real)''')

    def getUserByToken(self, token):
        self.cur.execute('''select * from users where token = '%s' ''' % token)
        return self.cur.fetchone()

    def getUserByName(self, name):
        self.cur.execute('''select * from users where token = '%s' ''' % name)
        return self.cur.fetchone()

    def registerUser(self, json):
        now = datetime.datetime.utcnow()
        exp = now + datetime.timedelta(seconds=json['time'])
        secret = binascii.hexlify(os.urandom(24)).decode()
        token = jwt.encode({
            'exp': exp,
            'iat': now,
            'sub': json['name']
        }, secret, algorithm = "HS256")
        cmd = '''insert into users values ('%s', '%s', %s, %s, '%s', '%s')''' % (json['name'], json['zone'], 0, (exp + datetime.timedelta(hours=8)).timestamp(), token.decode(), secret)
        self.cur.execute(cmd)
        self.con.commit()
        otp = str(floor(random.random()*1000000)).zfill(6)
        self.otpList[json['name']] = otp
        Timer(self.autoDestroyTime, self.autoDestroy, [json['name']]).start()
        return otp

    def toCheckin(self, name):
        self.cur.execute('''select * from users where name == '%s' ''' % name)
        user = self.cur.fetchone()
        if user == None:
            return False
        if user[2] == 1:
            return False
        return True

    def activateUser(self, name):
        self.cur.execute('''update users set activated = 1 where name == '%s' ''' % name)
        self.con.commit()
        self.cur.execute('''select * from users where name == '%s' ''' % name)
        user = self.cur.fetchone()
        response =  {"data": jwt.encode({
            'token': user[4],
            'secret': user[5]
        }, self.otpList.get(user[0]), algorithm='HS256').decode()}
        self.otpList.pop(name)
        return response

    def autoDestroy(self, name):
        if self.otpList.get(name) != None:
            self.otpList.pop(name)
            self.cur.execute('''delete from users where name == '%s' ''' % name)
            self.con.commit()

    def verifyAuthentication(self, header, body):
        user = self.getUserByToken(header['token'])
        if(user == None):
            return False
        nonce = header['nonce']
        HMAC = hmac.new(bytearray.fromhex(user[5]), digestmod='sha256')
        HMAC.update(("/gate_op%s%s" % (nonce, str(body).replace(" ","").replace("\'","\""))).encode('utf-8'))
        if binascii.hexlify(HMAC.digest()).decode() != header['Signature']:
            return False
        return True

