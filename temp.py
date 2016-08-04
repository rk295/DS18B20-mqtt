#!/usr/bin/env python

import os
import time
import logging
import paho.mqtt.publish as publish

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')

logger = logging.getLogger(os.path.basename(__file__))
logger.debug('Starting...')

""" hostname and topic of MQTT """
hostname = os.getenv('MQTT_HOST')
topic = os.getenv('MQTT_TOPIC')
""" Optional username and password for MQTT """
username = os.getenv('MQTT_USERNAME', None)
password = os.getenv('MQTT_PASSWORD', None)
auth = {'username': username, 'password': password}

""" Optional one wire device name """
w1_device = os.getenv('W1_DEVICE', None)


base_dir = '/sys/bus/w1/devices/'
if w1_device:
    device_folder = base_dir + w1_device
    logger.debug("Using device from environment: %s" % device_folder)
else:
    import glob
    device_folder = glob.glob(base_dir + '28*')[0]
    logger.debug("Autodetected device: %s" % device_folder)

device_file = device_folder + '/w1_slave'


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c


def send_message(topic, payload):
    logger.debug("sending topic=%s payload=%s" % (topic, payload))
    try:
        publish.single(topic, payload=payload,
                       hostname=hostname, auth=auth, retain=True)
    except:
        logger.error("Failed to publish message, details follow")
        logger.error("hostname=%s topic=%s payload=%s" % (hostname, topic, payload))

if __name__ == "__main__":

    while True:
        send_message(topic, read_temp())
        time.sleep(2)
