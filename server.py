import json
from itertools import islice
from flask import Flask
from flask import request
from ledStrip import ledstrip
from threading import Thread
import Queue
from collections import deque
from time import sleep

app = Flask(__name__)

class StateThread(Thread):
    def __init__(self, pixel):
        Thread.__init__(self)
        self.pixel = pixel
        print "Creating thread for %s" % pixel

    def run(self):
        while True:
            global states
            current_state = states[self.pixel]

            consecutive_criticals = 0

            low = max(self.pixel-2, 0)
            high = min(self.pixel+3, 32)

            for state in reversed(list(islice(states,low,high))):
                if state == 'critical':
                    consecutive_criticals += 1
                else:
                    consecutive_criticals = 0

                if consecutive_criticals >= 3:
                    current_state = 'ohcrap'
                    break

            if current_state.lower() == 'ok':
                ok(self.pixel)
            elif current_state.lower() == 'warning':
                warning(self.pixel)
            elif current_state.lower() == 'critical':
                critical(self.pixel)
            elif current_state.lower() == 'ohcrap':
                leds.setPixelColorRGB(pixel=self.pixel, red=255, green=0, blue=0)
                leds.show()
                sleep(0.1)
                leds.setPixelColorRGB(pixel=self.pixel, red=0, green=0, blue=0)
                leds.show()
                sleep(0.1)
                continue
            elif current_state.lower() == 'unknown':
                unknown(self.pixel)
            #sleep(0.1)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/webhook", methods=["POST"])
def webhook():
    global states
    try:
        payload = json.loads(request.data)
        state = payload.get('details', {}).get('state')
        
        states.append(state.lower())
        states.popleft()

        return "Success"
    except Exception, e:
        print "Exception: %s" % e.message
    
    return "All Good"

def unknown(pixel):
    leds.setPixelColorRGB(pixel=pixel, red=0, green=0, blue=0)
    leds.show()

def ok(pixel):
    leds.setPixelColorRGB(pixel=pixel, red=0, green=255, blue=0)
    leds.show()

def warning(pixel):
    leds.setPixelColorRGB(pixel=pixel, red=255, green=255, blue=0)
    leds.show()

def critical(pixel):
    leds.setPixelColorRGB(pixel=pixel, red=255, green=0, blue=0)
    leds.show()

def ohcrap(pixel):
    while True:
        leds.setPixelColorRGB(pixel=pixel, red=255, green=0, blue=0)
        leds.show()

def all_red():
    for x in xrange(32):
        leds.setPixelColorRGB(pixel=x, red=0, green=255, blue=0)
        leds.show()

@app.before_first_request
def init():
    global states
    global leds
    number_of_lights = 32

    states = deque(['unknown']*number_of_lights)

    spidev = file("/dev/spidev0.0", "wb")
    leds = ledstrip.LEDStrip(pixels=number_of_lights, spi=spidev)

    threads = [ StateThread(x) for x in range(number_of_lights)]
    for thread in threads:
        thread.start()

if __name__ == "__main__":
    #app.config['DEBUG'] = True
    app.run(host='0.0.0.0', port=5000)