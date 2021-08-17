import sqlite3
import os
import datetime
import jwt
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

    def getUser(self, key):
        self.cur.execute('''select * from users where key = '%s' ''' % key)
        return self.cur.fetchone()

    def registerUser(self, info):
        now = datetime.datetime.utcnow()
        exp = now + datetime.timedelta(seconds=info['time'])
        secret = binascii.hexlify(os.urandom(24)).decode()
        token = jwt.encode({
            'exp': exp,
            'iat': now,
            'sub': info['name']
        }, secret, algorithm = "HS256")
        cmd = '''insert into users values ('%s', '%s', %s, %s, '%s', '%s')''' % (info['name'], info['zone'], 0, (exp + datetime.timedelta(hours=8)).timestamp(), token.decode(), secret)
        self.cur.execute(cmd)
        self.con.commit()
        otp = str(floor(random.random()*1000000)).zfill(6)
        self.otpList[info['name']] = otp
        Timer(self.autoDestroyTime, self.autoDestroy, [info['name']]).start()
        return otp

    def findUser(self, name):
        self.cur.execute('''select count(*) from users where name == '%s' ''' % name)
        if self.cur.fetchone()[0] == 0:
            return False
        return True

    def toCheckin(self, name):
        self.cur.execute('''select * from users where name == '%s' ''' % name)
        user = self.cur.fetchone()
        if user == None:
            return False
        if user[2] == 1:
            return False
        return True


    def activateUser(self, name):
        self.cur.execute('''select * from users where name == '%s' ''' % name)
        user = self.cur.fetchone()
        self.cur.execute('''update users set activated = 1 where name == '%s' ''' % name)
        self.con.commit()
        response =  {"data": jwt.encode({
            'token': user[4],
            'secret': user[5]
        }, self.otpList.get(user[0]), algorithm='HS256').decode()}
        print(self.otpList)
        self.otpList.pop(name)

        return response

    def autoDestroy(self, name):
        if self.otpList.get(name) != None:
            otpList.pop(name)
            self.cur.execute('''delete from users where name == '%s' ''' % name)
            self.con.commit()
