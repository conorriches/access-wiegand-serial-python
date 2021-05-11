import csv
import os
import requests
import yaml


with open('config.yaml') as config_f:
    config = yaml.safe_load(config_f)

api_key = config['members']['apikey']
query_key = config['members']['querykey']

CSV_URL = "https://members.hacman.org.uk/query2.php?key=%s" % query_key


def send_heartbeat():
    try:
        url = "https://members.hacman.org.uk/acs/node/heartbeat"
        headers = {
            "ApiKey": api_key
        }
        r = requests.post(url=url, headers=headers)
        if r.status_code != 200:
            raise Exception("Heartbeat status code wasn't 200")
        print("Sent heartbeat")
    except:
        print("Couldn't sent heartbeat")
        GPIO.output(led_error_pin, GPIO.HIGH)


def main():
    try:
        with requests.Session() as s:
            download = s.get(CSV_URL)
            decoded_content = download.content.decode('utf-8')

            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            member_list = list(cr)

            with open('members.csv', 'w') as f:
                for item in member_list:
                    f.write("%s,%s\n" % (item[0], item[1]))
    except:
        print("Failed!")
        GPIO.output(led_error_pin, GPIO.HIGH)
    finally:
        send_heartbeat()


if __name__ == "__main__":
    main()
