# python3.6

import base64
import json
import os
import pdb
import qrcode
import randomname
import re
import RPi.GPIO as GPIO
import time
import uuid

# Inky
from inky.auto import auto
from inky.inky_uc8159 import Inky, CLEAN
from paho.mqtt import client as mqtt_client
from PIL import Image
from pyzbar import pyzbar
from string import Template

# generate client ID with pub prefix randomly
add_device = Template('$endpoint/devices/add/$hash')
broker = os.environ['BROKER']
port = 1883
client_id = randomname.get_name()
password = os.environ['PASSWORD']
url = os.environ['WEB']
username = os.environ['USERNAME']

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        data = json.loads(msg.payload.decode())
        if data["action"] == "draw":
            os.system("curl -L %s -o /tmp/original.png" % data["image"])
            os.system("convert /tmp/original.png -resize 460 -gravity Center -extent 600x448 /tmp/resized.png")
            draw("/tmp/resized.png")
        elif data["action"] == "clear":
            deep_clean(1)

        print(f"Received `{userdata}` `{msg.payload.decode()}` from `{msg.topic}` topic")

    initial_boot(client)
    client.on_message = on_message

def initial_boot(client):
    print("initial_boot is initiated")
    if os.path.isfile("./codename.png"):
        img = Image.open('./codename.png')
        data = pyzbar.decode(img)
        hash = re.findall(r'add\/(.+)', data[0].data.decode('utf-8'))[0]
        topic = json.loads(base64.b64decode(hash).decode())['topic']
    else:
        topic = str(uuid.uuid4())
        data = json.dumps({"client_id": client_id, "topic": topic}).encode("utf-8")
        image = qrcode.make(add_device.substitute(endpoint=url, hash=base64.b64encode(data).decode()))
        image.save("./codename.png")
        resize("./codename.png")
        draw("./codename.png")
    
    print(f"subscribed to topic: {topic}")
    client.subscribe(topic)

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

def clear():
    inky = Inky()

    for _ in range(2):
        for y in range(inky.height - 1):
            for x in range(inky.width - 1):
                inky.set_pixel(x, y, CLEAN)

        inky.show()

def deep_clean(cycles=3):
    print("deep_clean is initiated")
    inky_display = auto(ask_user=True, verbose=True)

    colours = (inky_display.RED, inky_display.BLACK, inky_display.WHITE)
    colour_names = (inky_display.colour, "black", "white")

    # Create a new canvas to draw on

    img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))

    # Loop through the specified number of cycles and completely
    # fill the display with each colour in turn.

    for i in range(cycles):
        print("Cleaning cycle %i\n" % (i + 1))
        for j, c in enumerate(colours):
            print("- updating with %s" % colour_names[j])
            inky_display.set_border(c)
            for x in range(inky_display.WIDTH):
                for y in range(inky_display.HEIGHT):
                    img.putpixel((x, y), c)
            inky_display.set_image(img)
            inky_display.show()
            time.sleep(1)
        print("\n")

    print("Cleaning complete!")

def resize(filepath):
    os.system(f'convert {filepath} -resize 460 -gravity Center -extent 600x448 {filepath}')

def draw(image_path):
    inky = Inky()
    saturation = 0.5
    
    image = Image.open(image_path)

    inky.set_image(image, saturation=saturation)
    inky.show()

    print("drawing complete!")

def handle_button(pin):
    print("button pressed")
    deep_clean(1)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(5, GPIO.FALLING, callback=handle_button, bouncetime=250)

    run()
