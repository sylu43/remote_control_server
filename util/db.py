import sqlite3
import os

class DB():

    con = None
    cur = None

    def __init__(self):
        DB = 'files/remote_control.db'

        self.con = sqlite3.connect(DB, check_same_thread=False)
        self.cur = self.con.cursor()

        #check users table
        self.cur.execute('''select count(name) from sqlite_master where type='table' and name='users' ''')
        if self.cur.fetchone()[0] == 0:
            self.cur.execute('''create table users(name, zone, token, secret)''')

        #check registers table
        self.cur.execute('''select count(name) from sqlite_master where type='table' and name='registers' ''')
        if self.cur.fetchone()[0] == 0:
            self.cur.execute('''create table registers(name, code)''')

        #check logs table
        self.cur.execute('''select count(name) from sqlite_master where type='table' and name='logs' ''')
        if self.cur.fetchone()[0] == 0:
            self.cur.execute('''create table logs(event, user, op, time real)''')

    def getUser(self, key):
        self.cur.execute('''select * from users where key = '%s' ''' % key)
        return self.cur.fetchall()

    def addUser(self, info):
        self.cur.execute('''insert into users values (?, ?, ?, ?)''', info)
        self.con.commit()

    def getRegister(self, name, code):
        self.cur.execute('''select * from users where name = '%s' and code = '%s' ''' % (name, code))
        return self.cur.fetchall()

    def addRegister(self, name, code):
        self.cur.execute('''insert into registers (%s, %s)''' % (name, code))
        self.con.commit()


