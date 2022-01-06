import sqlite3
import os
import datetime
import jwt
import hmac
import binascii
import random
from math import floor
from threading import Lock

class DB():

    con = None
    cur = None
    lock = Lock()

    def __init__(self):
        DB = 'files/remote_control.db'

        self.con = sqlite3.connect(DB, check_same_thread=False)
        self.cur = self.con.cursor()

        #check users table
        self.cur.execute('''select count(name) from sqlite_master where type='table' and name='users' ''')
        if self.cur.fetchone()[0] == 0:
            self.cur.execute('''create table users(name text, zone text, activated int2, expireDate real, token text)''')

        #check logs table
        self.cur.execute('''select count(name) from sqlite_master where type='table' and name='logs' ''')
        if self.cur.fetchone()[0] == 0:
            self.cur.execute('''create table logs(event text, user text, op text, time real)''')

    def getUserByName(self, name):
        self.lock.acquire()
        self.cur.execute('''select * from users where name = '%s' ''' % name)
        user = self.cur.fetchone()
        self.lock.release()
        return user

    def registerUser(self, json):
        while True:
            token = str(floor(random.random()*1000000)).zfill(6)
            if not self.findToken(token):
                break
        cmd = '''insert into users values ('%s', '%s', %d, %d, '%s')''' % (json['name'], json['zone'], 0, 0, token)
        self.lock.acquire()
        self.cur.execute(cmd)
        self.con.commit()
        self.lock.release()
        return token

    def activateUser(self, name, time):
        self.lock.acquire()
        self.cur.execute('''update users set activated = 1 where name == '%s' ''' % name)
        self.con.commit()
        self.cur.execute('''select * from users where name == '%s' ''' % name)
        user = self.cur.fetchone()
        self.lock.release()
        if user != None and user[2] == 1:
            return True
        return False

    def updateUser(self, json):
        self.lock.acquire()
        cmd = '''update users set zone = '%s', activated = %d, expireDate = %d where name == '%s' ''' % (json['zone'], json['activated'], json['expDate'], json['name'])
        self.cur.execute('''update users set zone = '%s', activated = %d, expireDate = %d where name == '%s' ''' % (json['zone'], json['activated'], json['expDate'], json['name']))
        self.con.commit()
        self.lock.release()

    def deactivateUser(self, name):
        self.lock.acquire()
        self.cur.execute('''update users set activated = 0 where name == '%s' ''' % name)
        self.con.commit()
        self.cur.execute('''select * from users where name == '%s' ''' % name)
        user = self.cur.fetchone()
        self.lock.release()
        if user != None and user[2] == 0:
            return True
        return False

    def verifyActivatedUser(self, request, path):
        user = self.getUserByName(request.json['name'])
        if user == None or not user[2]:
            return False
        #return self.verifyAuthentication(request, user, path)
        return True

    def verifyAdmin(self, request, path):
        user = self.getUserByName(request.json['name'])
        if user == None or user[1] != 'admin':
            return False
        #return self.verifyAuthentication(request, user, path)
        return True

    def verifyAuthentication(self, request, user, path):
        nonce = request.headers['nonce']
        body = {} if request.method == 'GET' else request.json
        HMAC = hmac.new(bytearray.fromhex(user[6]), digestmod='sha256')
        HMAC.update(("%s%s%s" % (path, nonce, str(body).replace(" ","").replace("\'","\""))).encode('utf-8'))
        if binascii.hexlify(HMAC.digest()).decode() != request.headers['Signature']:
            return False
        return True

    def allUsers(self):
        self.lock.acquire()
        self.cur.execute('''select * from users ''')
        users = self.cur.fetchall()
        self.lock.release()
        return users

    def deleteUser(self, name):
        self.lock.acquire()
        self.cur.execute('''delete from users where name == '%s' ''' % name)
        self.con.commit()
        self.lock.release()

    def findToken(self, token):
        self.lock.acquire()
        self.cur.execute('''select * from users where token = '%s' ''' % token)
        user = self.cur.fetchone()
        self.lock.release()
        if user == None:
            return False
        return True

