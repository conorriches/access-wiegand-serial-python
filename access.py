import csv
from datetime import date, datetime as dt
import logging
import requests
from pathlib import Path
import RPi.GPIO as GPIO
import serial
import time
import yaml

# GPIO setup
errorLed = 13
exitBtn = 2
exitRelay = 6

GPIO.setmode(GPIO.BOARD)
GPIO.setup(errorLed, GPIO.OUT)
GPIO.setup(exitBtn, GPIO.IN)
GPIO.setup(exitRelay, GPIO.OUT)

# Logs
errorLog = logging.getLogger('error')
debugLog = logging.getLogger('debug')

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

errorHandler = logging.FileHandler("logs/error.log")
errorHandler.setFormatter(formatter)
errorLog.addHandler(errorHandler)

debugHandler = logging.FileHandler("logs/debug.log")
debugHandler.setFormatter(formatter)
debugLog.addHandler(debugHandler)
debugLog.setLevel(logging.DEBUG)

with open('config.yaml') as config_f:
    config = yaml.safe_load(config_f)

api_key = config['members']['apikey']
serial_cfg = config['serial']

ser1_cfg = serial_cfg.get('in', False)
ser2_cfg = serial_cfg.get('out', False)

ser1 = False
ser2 = False


def send_heartbeat():
    try:
        url = "https://members.hacman.org.uk/acs/node/heartbeat"
        headers = {
            "ApiKey": api_key
        }
        r = requests.post(url=url, headers=headers)
        debugLog.info(r.status_code)
        if r.status_code != 200:
            raise Exception("Heartbeat status code wasn't 200")
        debugLog.info("Sent heartbeat")
    except:
        errorLog.error("Couldn't sent heartbeat")


def disconnectSerial():
    global ser1, ser2
    try:
        if ser1:
            ser1.close()
            ser1 = False
        if ser2:
            ser2.close()
            ser2 = False
    except Exception as e:
        errorLog.error("Cannot disconnect serial %s", e)


def connectSerial():
    global ser1, ser2

    if (ser1_cfg and ser1 == False):
        try:
            ser1 = serial.Serial(ser1_cfg['port'], ser1_cfg['baud'], timeout=1)
            ser1.flush()
            debugLog.error("Conencted to Serial 1: %s", ser1)
        except Exception as e:
            pass

    if (ser2_cfg and ser2 == False):
        try:
            ser2 = serial.Serial(ser2_cfg['port'], ser2_cfg['baud'], timeout=1)
            ser2.flush()
            debugLog.info("Conencted to Serial 2 %s", ser2)
        except:
            pass


def report():
    debugLog.info("Sending report")
    send_heartbeat()
    if (ser1_cfg != False and ser1 == False):
        errorLog.error("No serial device SER1")
    if (ser2_cfg != False and ser2 == False):
        errorLog.error("No serial device SER2")


def checkErrors():
    size = Path('logs/error.log').stat().st_size
    if (size > 0):
        GPIO.output(errorLed, GPIO.HIGH)
    else:
        GPIO.output(errorLed, GPIO.LOW)


def validateFob(fobId):
    with open('members.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        mydict = {rows[0]: rows[1] for rows in reader}
        valid = fobId in mydict
        debugLog.info("Validation of fob ID %s was %s", fobId, valid)
        if valid:
            return valid, mydict.get(fobId)
    return False, False


def main():
    global ser1, ser2
    last_report = 0

    while True:
        connectSerial()

        try:
            if ser1:
                if ser1.in_waiting > 0:
                    line = ser1.readline().decode('utf-8').rstrip()
                    debugLog.info("Data on Ser1: %s", line)
                    valid, user = validateFob(line)
                    if(valid):
                        GPIO.output(exitRelay, GPIO.HIGH)
                        ser1.write(b'1')
                        time.sleep(0.5)
                        GPIO.output(exitRelay, GPIO.LOW)
                        print(user, "entered")
                        debugLog.info(
                            "RFID FOB SCAN: %s scanned %s with fob %s", user, "IN", line
                        )
                    else:
                        ser1.write(b'0')

            if ser2:
                if ser2.in_waiting > 0:
                    line = ser2.readline().decode('utf-8').rstrip()
                    debugLog.info("Data on Ser2: %s", line)
                    valid, user = validateFob(line)
                    if(valid):
                        GPIO.output(exitRelay, GPIO.HIGH)
                        time.sleep(0.5)
                        GPIO.output(exitRelay, GPIO.LOW)
                        print(user, "left")
                        debugLog.info(
                            "RFID FOB SCAN: %s scanned %s with fob %s", user, "OUT", line
                        )
        except Exception as e:
            disconnectSerial()
            errorLog.error("Error in main loop %s", e)
        finally:
            now = dt.now()
            if(now.minute != last_report):
                last_report = now.minute
                report()
                checkErrors()
            time.sleep(0.5)


if __name__ == "__main__":
    main()
