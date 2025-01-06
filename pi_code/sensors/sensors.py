import paho.mqtt.client as mqtt
from time import sleep
import json
from datetime import datetime
import sys
import random
from config import Configuration
import traceback
import sys
from mylog import MyLog
import smbus
from sht20 import SHT20

import weatherhat
#https://github.com/THP-JOE/Python_SI1145/tree/master/examples
import SI1145.SI1145 as SI1145
log = MyLog("sensors.log")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    log.info("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")


def startMqtt(config):
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.connect(config.mqtt_ip, config.mqtt_port, config.mqtt_keepalive)#"192.168.178.38", 1883, 60)
        return client
    except Exception as e:
        log.error(traceback.format_exc())

def dht_values():
    address = 0x38 #Put your device's address here
    data = i2cbus.read_i2c_block_data(address,0x71,1)
    if (data[0] | 0x08) == 0:
      print('Initialization error')

    i2cbus.write_i2c_block_data(address,0xac,[0x33,0x00])
    sleep(0.1)

    data = i2cbus.read_i2c_block_data(address,0x71,7)

    Traw = ((data[3] & 0xf) << 16) + (data[4] << 8) + data[5]
    temperature = 200*float(Traw)/2**20 - 50

    Hraw = ((data[3] & 0xf0) >> 4) + (data[1] << 12) + (data[2] << 4)
    humidity = 100*float(Hraw)/2**20
    return (temperature, humidity)


if __name__ == '__main__':
    try:
        config = Configuration("config.yaml")
        client=startMqtt(config)
        sensors = {}
        if client:
            client.loop_start()
        si1145=SI1145.SI1145()
        i2cbus = smbus.SMBus(1)

        sensor = weatherhat.WeatherHAT()
            
        while True:
            
            sensors['soil_moisture']=-1
            sensors['soil_temperature']=-1
            try:
                sht = SHT20(1, resolution=SHT20.TEMP_RES_14bit)
                
                sensors['soil_moisture']=sht.read_humid()
                sensors['soil_temperature']=sht.read_temp()
            except Exception as e:
                log.error(traceback.format_exc())
                sys.exit()
            
            sensors['IR']=-1
            sensors['UV']=-1
            try:
                sensors['IR']=si1145.readIR()
                sensors['UV']=si1145.readUV()/100
            except Exception as e:
                log.error(traceback.format_exc())
                
            sensors['DHT_temperature']=-1
            sensors['DHT_humidity']=-1
            try:
                temperature, humidity = dht_values()    
                sensors['DHT_temperature']=temperature
                sensors['DHT_humidity']=humidity
            except Exception as e:
                log.error(traceback.format_exc())
                
            try:
                sensor.update(interval=config.updateInterval-1)
                print(sensor.wind_speed)
                wind_direction_cardinal = sensor.degrees_to_cardinal(sensor.wind_direction)
                #obviosly the device temperature is the normal temperature, but what is temperature then?
                sensors["temperature"]= sensor.device_temperature
               # sensors['temperature'] = sensor.temperature
                sensors['humidity'] = sensor.humidity
                sensors['dew_point'] = sensor.dewpoint
                sensors['ambient_light'] = sensor.lux
                sensors['pressure'] = sensor.pressure
                sensors['wind_speed'] = sensor.wind_speed #m/sec
                sensors['rain'] = sensor.rain #mm/sec
                sensors['wind_direction_degree']=sensor.wind_direction
                sensors['wind_direction_cardinal']=wind_direction_cardinal
            except Exception as e:
                log.error(traceback.format_exc())
            
            sensors['source']=config.piname
            sensors['publisher']=config.piname
            sensors['timestamp']=str(datetime.now())
            #send them to mqtt
            log.info(sensors)
            client.publish("/environment_data", json.dumps(sensors), 0, False)
            topic = "/queen/"+config.piname
            client.publish(topic, json.dumps(sensors), 0, False)
            sleep(config.updateInterval)
    except Exception as e:
        log.error(traceback.format_exc())
        sys.exit()









