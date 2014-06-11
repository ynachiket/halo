import json
from flask import Flask
from flask import request
from ledStrip import ledstrip

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        payload = json.loads(request.data)
        state = payload.get('details', {}).get('state')
        
        if state.lower() == 'critical':
            all_red()
        return "Success"
    except Exception, e:
        print "Broke"
        print e
    return "bahsds"

def all_red():
    spidev = file("/dev/spidev0.0", "wb")
    leds = ledstrip.LEDStrip(pixels=32, spi=spidev)
    leds.setPixelColorRGB(pixel=0, red=255, green=0, blue=0)
    leds.show()

if __name__ == "__main__":
    app.config['DEBUG'] = True
    app.run(host='0.0.0.0', port=5000)
