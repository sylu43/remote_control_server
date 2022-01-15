import sqlite3
import os
import time
import jwt
import hmac
import binascii
import random
from math import floor
from threading import Lock
from operator import itemgetter

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
            self.cur.execute('''create table users(name text, zone text, activated int2, expDate real, token text)''')

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

    def registerUser(self, user):
        while True:
            token = str(floor(random.random()*1000000)).zfill(6)
            if not self.findToken(token):
                break
        cmd = '''insert into users values ('%s', '%s', %d, %d, '%s')''' % (user['name'], user['zone'], -1, int(time.time()), token)
        self.lock.acquire()
        self.cur.execute(cmd)
        self.con.commit()
        self.lock.release()
        return token

    def updateUser(self, guest):
        self.lock.acquire()
        cmd = '''update users set zone = '%s', activated = %d, expDate = %d where name == '%s' ''' % (guest['zone'], guest['activated'], guest['expDate'], guest['name'])
        self.cur.execute('''update users set zone = '%s', activated = %d, expDate = %d where name == '%s' ''' % (guest['zone'], guest['activated'], guest['expDate'], guest['name']))
        self.con.commit()
        self.lock.release()

    def verifyActivatedUser(self, request, path):
        user = self.getUserByName(request.json['name'])
        if user == None or not user[2]:
            return False
        if not self.verifyAuthentication(request, user, path):
            return False
        nonce = float(request.headers['nonce'])
        if nonce > user[3] or (time.time() - nonce) > 10:
            return False
        return True

    def verifyAdmin(self, request, path):
        user = self.getUserByName(request.json['name'])
        if user == None or user[1] != 'admin':
            return False
        return self.verifyAuthentication(request, user, path)

    def verifyAuthentication(self, request, user, path):
        nonce = request.headers['nonce']
        body = {} if request.method == 'GET' else request.json
        HMAC = hmac.new(user[4].encode('utf-8'), digestmod='sha256')
        HMAC.update(("%s%s%s" % (path, nonce, str(body).replace(" ","").replace("\'","\""))).encode('utf-8'))
        if binascii.hexlify(HMAC.digest()).decode() != request.headers['signature']:
            return False
        return True

    def allUsers(self):
        self.lock.acquire()
        self.cur.execute('''select * from users ''')
        users = self.cur.fetchall()
        self.lock.release()
        users = sorted(users, key=itemgetter(2, 3), reverse=True)
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

