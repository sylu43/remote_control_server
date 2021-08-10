#import RPi.GPIO as gpio
import configparser
import time

def jsonToTuple(j):
    return (j['name'], j['zone'], j['key'], j['secret'])

def tupleToJson(t):
    return {
        'name': t[0],
        'zone': t[1],
        'key': t[2],
        'secret': t[3]
    }

'''
comment out since not on board yet
def setupGPIO():
    for conf in gpioConf:
        gpio.setup(conf, gpio.OUT)
        gpio.output(conf, gpio.HIGH)
'''

def gateOp(pin):
    print(pin)
    #gpio.output(pin, gpio.LOW)
    #time.sleep(2)
    #gpio.output(pin , gpio.HIGH)

def getConf():
    configPath = 'files/config.txt'
    parser = configparser.ConfigParser()
    parser.read(configPath)
    return parser
