# https://www.emqx.io/blog/how-to-use-mqtt-in-python
# You can change MQTT broker with its username and password

import paho.mqtt.client as mqttc
import random
import time

broker = 'mqtt.lunar-smart.com'
#broker = 'localhost'
port = 8883
topic1 = "/esp8266/temperature"
topic2 = "/esp8266/humidity"
topic3 = "/esp8266/kwh"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'lunar'
password = 'smartsystem'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqttc.Client(client_id)
    client.username_pw_set(username, password)    #set user pass
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client):
    msg_count = 0
    while True:
        rng1 = round(random.uniform(0,100),2)
        rng2 = round(random.uniform(0,100),2)
        rng3 = round(random.uniform(0,300),2)
        time.sleep(5)
        msg = f"messages: {msg_count}"
        result = client.publish(topic1, rng1)
        result = client.publish(topic2, rng2)
        result = client.publish(topic3, rng3)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic1}`: {rng1}")
            print(f"Send `{msg}` to topic `{topic2}`: {rng2}")
            print(F"Send '{msg}' to topic '{topic3}': {rng3}")
        else:
            print(f"Failed to send message to topic {topic1} {topic2} {topic3}")
        msg_count += 1


def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)


if __name__ == '__main__':
    run()