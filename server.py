import json
from itertools import islice
from flask import Flask
from flask import request
from ledStrip import ledstrip
from threading import Thread
import Queue
from collections import deque
from time import sleep

BRIGHTNESS=50

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/webhook", methods=["POST"])
def webhook():
    global states
    try:
        payload = json.loads(request.data)
        state = payload.get('details', {}).get('state')

  print 'got state: ', state
        states.append(state.lower())
        states.popleft()

  for pixel in xrange(len(states)):
            current_state = states[pixel]
            if current_state.lower() == 'ok':
                ok(pixel)
            elif current_state.lower() == 'warning':
                warning(pixel)
            elif current_state.lower() == 'critical':
                critical(pixel)
            else:
                unknown(pixel)

        return "Success"
    except Exception, e:
        print "Exception: %s" % e.message

    return "All Good"

def unknown(pixel):
    leds.setPixelColorRGB(pixel=pixel, red=0, green=0, blue=0)
    leds.show()

def ok(pixel):
    leds.setPixelColorRGB(pixel=pixel, red=0, green=BRIGHTNESS, blue=0)
    leds.show()

def warning(pixel):
    leds.setPixelColorRGB(pixel=pixel, red=BRIGHTNESS, green=(BRIGHTNESS/3), blue=0)
    leds.show()

def critical(pixel):
    leds.setPixelColorRGB(pixel=pixel, red=BRIGHTNESS, green=0, blue=0)
    leds.show()

def all_red():
    for x in xrange(32):
        leds.setPixelColorRGB(pixel=x, red=0, green=BRIGHTNESS, blue=0)
        leds.show()

@app.before_first_request
def init():
    global states
    global leds
    number_of_lights = 32

    states = deque(['unknown']*number_of_lights)

    spidev = file("/dev/spidev0.0", "wb")
    leds = ledstrip.LEDStrip(pixels=number_of_lights, spi=spidev)

if __name__ == "__main__":
    #app.config['DEBUG'] = True
    app.run(host='::', port=5000)
