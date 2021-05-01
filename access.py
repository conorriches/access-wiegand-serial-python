import datetime
import logging
import requests
import serial
import time
import yaml

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
        if r.status_code != 200:
            raise Exception("Heartbeat status code wasn't 200")
        logging.info("Sent heartbeat")
    except:
        logging.error("Couldn't sent heartbeat")
        GPIO.output(led_error_pin, GPIO.HIGH)


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
        logging.error("Cannot disconnect serial %s", e)


def connectSerial():
    global ser1, ser2

    if (ser1_cfg and ser1 == False):
        try:
            ser1 = serial.Serial(ser1_cfg['port'], ser1_cfg['baud'], timeout=1)
            ser1.flush()
            logging.info("Conencted to Serial 1: %s", ser1)
        except Exception as e:
            pass

    if (ser2_cfg and ser2 == False):
        try:
            ser2 = serial.Serial(ser2_cfg['port'], ser2_cfg['baud'], timeout=1)
            ser2.flush()
            logging.info("Conencted to Serial 2 %s", ser2)
        except:
            pass


def report():
    logging.info("Sending report")
    send_heartbeat()
    if (ser1_cfg != False and ser1 == False):
        logging.error("No serial device SER1")
    if (ser2_cfg != False and ser2 == False):
        logging.error("No serial device SER2")


def main():
    global ser1, ser2
    last_report = 0

    while True:
        connectSerial()

        try:
            if ser1:
                if ser1.in_waiting > 0:
                    line = ser1.readline().decode('utf-8').rstrip()
                    logging.info("RFID FOB SCAN - Ser1: %s", line)
                    print(line)
            if ser2:
                if ser2.in_waiting > 0:
                    line = ser2.readline().decode('utf-8').rstrip()
                    logging.info("RFID FOB SCAN - Ser2: %s", line)
                    print(line)
        except Exception as e:
            disconnectSerial()
            logging.error("Error in main loop %s", e)
        finally:
            now = datetime.datetime.now()

            if(now.minute != last_report):
                last_report = now.minute
                report()
            time.sleep(0.5)


if __name__ == "__main__":
    main()
