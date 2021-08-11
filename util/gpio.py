#import RPi.GPIO as gpio

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

