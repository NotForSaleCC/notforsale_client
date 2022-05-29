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

ADD_DEVICE = Template('$endpoint/devices/add/$hash')
BROKER = os.environ['BROKER']
PORT = 1883
CLIENT_ID = randomname.get_name()
PASSWORD = os.environ['PASSWORD']
URL = os.environ['WEB']
USERNAME = os.environ['USERNAME']
BUTTONS = [5,6,16,24]

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(CLIENT_ID)
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.connect(BROKER, PORT)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        data = json.loads(msg.payload.decode())
        if data["action"] == "draw":
            os.system("curl -L %s -o /tmp/original.png" % data["image"])
            resize("/tmp/original.png")
            draw("/tmp/original.png")
        elif data["action"] == "clear":
            deep_clean(1)

        print(f"Received `{userdata}` `{msg.payload.decode()}` from `{msg.topic}` topic")

    initial_boot(client)
    client.on_message = on_message

def decode_qr(image_path):
    img = Image.open(image_path)
    data = pyzbar.decode(img)
    hash = re.findall(r'add\/(.+)', data[0].data.decode('utf-8'))[0]
    topic = json.loads(base64.b64decode(hash).decode())['topic']
    return topic

def create_qr(image_path):
    topic = str(uuid.uuid4())
    data = json.dumps({"client_id": CLIENT_ID, "topic": topic}).encode("utf-8")
    image = qrcode.make(ADD_DEVICE.substitute(endpoint=URL, hash=base64.b64encode(data).decode()))
    image.save(image_path)
    resize(image_path)
    draw(image_path)
    return topic

def initial_boot(client):
    print("initial_boot is initiated")
    if os.path.isfile("./codename.png"):
        topic = decode_qr("./codename.png")
    else:
        topic = create_qr("./codename.png")
    
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

def reset(img_path):
    create_qr(img_path)

# 5 - clear
# 6 - draw existing QR code
# 16 - draw a new QR code
FEATURES = {
    5: [deep_clean, 1],
    6: [draw, "./codename.png"],
    16: [reset, "./codename.png"],
}

def handle_button(pin):
    print("button pressed %d" % pin)
    feature = FEATURES[pin]
    feature[0](feature[1])

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    for pin in BUTTONS:
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=handle_button, bouncetime=250)

    run()
