import configparser
import time

def jsonToTuple(j):
    return (j['name'], j['zone'], j['token'], j['secret'])

def tupleToJson(t):
    return {
        'name': t[0],
        'zone': t[1],
        'token': t[2],
        'secret': t[3]
    }

def getConf():
    configPath = 'files/config.txt'
    parser = configparser.ConfigParser()
    parser.read(configPath)
    return parser
