import time
import RPi.GPIO as gpio

def setupGPIO(gpioConf):
    gpio.cleanup()
    gpio.setmode(gpio.BCM)
    for (key, val) in gpioConf.items('GPIO'):
        gpio.setup(int(val), gpio.OUT)
        gpio.output(int(val), gpio.HIGH)

def gateOp(pin):
    gpio.output(pin, gpio.LOW)
    time.sleep(0.2)
    gpio.output(pin , gpio.HIGH)

