# python3.6

import os
import json
import time
import uuid
import base64
import qrcode

from string import Template
from paho.mqtt import client as mqtt_client
# Inky
from inky.auto import auto
from PIL import Image
from inky.inky_uc8159 import Inky, CLEAN

url = os.environ['URL']
broker = os.environ['BROKER']
port = 1883
# generate client ID with pub prefix randomly
client_id = 'python-mqtt'
username = os.environ['USERNAME']
password = os.environ['PASSWORD']
add_device = Template('$endpoint/devices/add/$hash')

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

    topic=str(uuid.uuid4())
    initial_boot(topic)
    client.subscribe(topic)
    client.on_message = on_message

def initial_boot(topic):
    data = json.dumps({"client_id": client_id, "topic": topic}).encode("utf-8")
    image = qrcode.make(add_device.substitute(endpoint=url, hash=base64.b64encode(data).decode()))
    image.save("/tmp/codename.png")
    resize("/tmp/codename.png")
    draw("/tmp/codename.png")

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

if __name__ == '__main__':
    run()
