from decider import Decider
from sys import argv
import RPi.GPIO as GPIO
import time
from mylog import MyLog
import datetime
from decider import Decider
from config import Configuration


pin=12 #gpio 18
multiplier = 100
sleeptime=60

config = Configuration("config.yaml")
log = MyLog("light.log")
if len(argv) == 4:
    pin=int(argv[1])
    multiplier = int(argv[2])
    sleeptime = int(argv[3])
else:
    print("Usage: light.py <pin> <multiplier> <sleeptime> - use default param")
log.info("Use following parameter: "+str(pin)+ " "+str(multiplier)+ " "+str(sleeptime))

decider = Decider(config)
log.info(decider)

log.info("Using PIN: "+str(pin))
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.OUT)

p=GPIO.PWM(pin, 50)
p.start(0)
try:
    while(True):
        value=decider.percentageByTime()
        now=datetime.datetime.now(decider.zoneinfo)
        log.info("Current time"+str(now))
        log.info("returned value is: "+str( value))
        p.ChangeDutyCycle(value*multiplier)
        time.sleep(sleeptime)
except Exception as e:
    log.error("Exception occured: "+str(e))
p.stop()
GPIO.cleanup()


