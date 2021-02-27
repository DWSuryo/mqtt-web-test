# Created by Rui Santos
# Complete project details: https://randomnerdtutorials.com
#

import paho.mqtt.client as mqtt
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import eventlet
import datetime   # show date
import csv        # for storing data

eventlet.monkey_patch()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'xDsTbiULqIrqXkO_X5kcyg'
socketio = SocketIO(app, ping_interval=5, ping_timeout=10)
CORS(app)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/esp8266/temperature")
    client.subscribe("/esp8266/humidity")
    client.subscribe("/esp8266/kwh")

# The callback for when a PUBLISH message is received from the ESP8266.
def on_message(client, userdata, message):
   #socketio.emit('my variable')
   print("Received message '" + str(message.payload) + "' on topic '"
      + message.topic + "' with QoS " + str(message.qos))
   if message.topic == "/esp8266/temperature":
      global temperature1
      temperature1 = str(message.payload.decode('utf-8'))
      print("temperature update " + temperature1)
      socketio.emit('dht_temperature', {'data': message.payload})
   if message.topic == "/esp8266/humidity":
      global humidity1
      humidity1 = str(message.payload.decode('utf-8'))
      print("humidity update " +  humidity1)
      socketio.emit('dht_humidity', {'data': message.payload})
   if message.topic == "/esp8266/kwh":
      global kwh1
      kwh1 = str(message.payload.decode('utf-8'))
      print("kwh update " +  kwh1)
      socketio.emit('energy_kwh', {'data': message.payload})


# initialize mqtt broker
mqttc=mqtt.Client(client_id="capstone")
broker = 'localhost'
port = 1883

# launch mqtt
#mqttc.username_pw_set(username, password) #set user pass
#mqttc=mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv31)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect(broker,port,60)
mqttc.loop_start()



# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
   4 : {'name' : 'GPIO 4', 'board' : 'esp8266', 'topic' : 'esp8266/4', 'state' : 'False'},
   5 : {'name' : 'GPIO 5', 'board' : 'esp8266', 'topic' : 'esp8266/5', 'state' : 'False'}
   }

# Put the pin dictionary into the template data dictionary:
templateData = {
   'pins' : pins
   }

@app.route("/")
def main():
   # Pass the template data into the template main.html and return it to the user
   return render_template('main.html', async_mode=socketio.async_mode, **templateData)

# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<board>/<changePin>/<action>")
def action(board, changePin, action):
   # Convert the pin from the URL into an integer:
   changePin = int(changePin)
   # Get the device name for the pin being changed:
   devicePin = pins[changePin]['name']
   # If the action part of the URL is "on," execute the code indented below:
   if action == "1" and board == 'esp8266':
      mqttc.publish(pins[changePin]['topic'],"1")
      pins[changePin]['state'] = 'True'

   if action == "0" and board == 'esp8266':
      mqttc.publish(pins[changePin]['topic'],"0")
      pins[changePin]['state'] = 'False'

   # Along with the pin dictionary, put the message into the template data dictionary:
   templateData = {
      'pins' : pins
   }

   return render_template('main.html', **templateData)

@socketio.on('my event')
def handle_my_custom_event(json):
   print('received json data here: ' + str(json))

@socketio.on('my event1')
def handle_my_temperature(json):
   print('received json temperature here: ' + str(json))

@socketio.on('my event2')
def handle_my_humidity(json):
   print('received json humidity here: ' + str(json))

@socketio.on('my event3')
def handle_my_kwh(json):
   print('received json humidity here: ' + str(json))

if __name__ == "__main__":
   # opens and writes csv file
   with open('sensor.csv', mode='a+') as file:
      reader = csv.reader(file, delimiter=',')
      writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
      line_count = 0
      time = datetime.datetime.now()
      #way to write to csv file
      for row in reader:
         if line_count == 0:
            writer.writerow(['date','time','temperature','humidity','energy'])
         else:
            writer.writerow([time.strftime("%x"),time.strftime("%X"),temperature1,humidity1,kwh1])

   socketio.run(app, host='0.0.0.0', port=8080, debug=True)

