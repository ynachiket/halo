import json
from flask import Flask
from flask import request
from ledStrip import ledstrip

app = Flask(__name__)
global leds

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/webhook", methods=["POST"])
def webhook():
    global current_pixel
    try:
        payload = json.loads(request.data)
        state = payload.get('details', {}).get('state')
        
        if state.lower() == 'critical':
            critical()
        elif state.lower() == 'warning':
            warning()
        elif state.lower() == 'ok':
            ok()

        if current_pixel == 31:
            current_pixel = 0
            print "--1"
            print current_pixel
        else:
            current_pixel += 1
            print "--2"
            print current_pixel

        return "Success"
    except Exception, e:
        print "Broke"
        print e
    return "bahsds"

def ok():
    leds.setPixelColorRGB(pixel=current_pixel, red=0, green=255, blue=0)
    leds.show()

def warning():
    leds.setPixelColorRGB(pixel=current_pixel, red=255, green=153, blue=0)
    leds.show()

def critical():
    leds.setPixelColorRGB(pixel=current_pixel, red=255, green=0, blue=0)
    leds.show()

def all_red():
    for x in xrange(32):
        leds.setPixelColorRGB(pixel=x, red=0, green=255, blue=0)
        leds.show()

if __name__ == "__main__":
    spidev = file("/dev/spidev0.0", "wb")
    leds = ledstrip.LEDStrip(pixels=32, spi=spidev)
    current_pixel = 0

    app.config['DEBUG'] = True
    app.run(host='0.0.0.0', port=5000)