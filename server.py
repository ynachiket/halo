import json
from itertools import islice
from ledStrip import ledstrip
from threading import Thread
import Queue
from collections import deque
from time import sleep
from klein import Klein
from twisted.internet import reactor

BRIGHTNESS=50
SHIFTTIME = 5*60

#app = Flask(__name__)
app = Klein()

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/webhook", methods=["POST"])
def webhook(request):
    global states
    try:
        payload = json.loads(request.content.read())
        state = payload.get('details', {}).get('state')

        print 'got state: ', state
        states.append(state.lower())
        states.popleft()
        turnOnTheLights(states, timeoutFlag = True)
        return "Success"
    except Exception, e:
        print "Exception: %s" % e.message

    return "All Good"

def unknown(pixel):
    leds.setPixelColorRGB(pixel=pixel, red=0, green=0, blue=0)
    leds.show()

def ok(pixel, timeoutFlag = False):
    leds.setPixelColorRGB(pixel=pixel, red=0, green=BRIGHTNESS, blue=0)
    leds.show()
    if timeoutFlag:
        timeout.reset(SHIFTTIME) 

def warning(pixel, timeoutFlag = False):
    leds.setPixelColorRGB(pixel=pixel, red=BRIGHTNESS, green=(BRIGHTNESS/3), blue=0)
    leds.show()
    if timeoutFlag:
        timeout.reset(SHIFTTIME) 

def critical(pixel, timeoutFlag = False):
    leds.setPixelColorRGB(pixel=pixel, red=BRIGHTNESS, green=0, blue=0)
    leds.show()
    if timeoutFlag:
        timeout.reset(SHIFTTIME)

def all_red():
    for x in xrange(32):
        leds.setPixelColorRGB(pixel=x, red=0, green=BRIGHTNESS, blue=0)
        leds.show()


def shiftOne():
    global timeout
    states.append('iamgonnapopsome')
    states.popleft()
    turnOnTheLights(states)
    timeout = reactor.callLater(SHIFTTIME,shiftOne)

def turnOnTheLights(states, timeoutFlag = False):
    for pixel in xrange(len(states)):
        current_state = states[pixel]
        if current_state.lower() == 'ok':
            ok(pixel, timeoutFlag)
        elif current_state.lower() == 'warning':
            warning(pixel, timeoutFlag)
        elif current_state.lower() == 'critical':
            critical(pixel, timeoutFlag)
        else:
            unknown(pixel) 
   
def init():
    global states
    global leds
    global timeout
    number_of_lights = 32
    timeout = reactor.callLater(SHIFTTIME,shiftOne)

    states = deque(['unknown']*number_of_lights)

    spidev = file("/dev/spidev0.0", "wb")
    leds = ledstrip.LEDStrip(pixels=number_of_lights, spi=spidev)

if __name__ == "__main__":
    #app.config['DEBUG'] = True
    init()
    app.run(host='::', port=5000)

