#!/usr/bin/env python

import time
from neopixel import *
import argparse
import board
import threading
import serial

# ----- GLOBAL CONSTANT VARIABLES -----------------
# LED strip configuration:
LED_COUNT      = 110      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
setColor = (0, 0, 0)
ORDER = GRB
R_WHITE = 161
B_WHITE = 255
G_WHITE = 202
START_STATE = "IDLE_BREATHING"
START_GRB = (G_WHITE, R_WHITE, B_WHITE)
state_lock = threading.Lock()

class LEDController():
    
    def __init__(self, strip):
        self.STATE = START_STATE
        self.grb = START_GRB
        self.strip = strip
        self.state_lock = threading.Lock()
        self.strip_lock = threading.Lock()

    def set_state(self, STATE):
        self.state_lock.acquire()
        self.STATE = STATE
        self.state_lock.release()
    
    def get_state(self):
        self.state_lock.acquire()
        ret = self.STATE
        self.state_lock.release()
        return ret

    def colorWipe(self, color, wait_ms=50):
        self.strip_lock.acquire()
        """Wipe color across display a pixel at a time."""
        for i in range(0, 110):
            self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms/1000.0)
        self.strip_lock.release()

    def glow(self, color,wait_ms = 50):
        self.strip_lock.acquire()
    # for i in range(strip.numPixels()):
        for i in range(0, 110):
            self.strip.setPixelColor(i, color)
        j = 255
        for j in range(0, 255):
            self.strip.setBrightness(j)
            self.strip.show()
            time.sleep(wait_ms/1000)
            j = j - 2
        strip_lock.release()

    def glowout(self):
        strip_lock.acquire()
        for j in range(0, 255):
            self.strip.setBrightness(255 - j)
            self.strip.show()
            time.sleep(50/1000)
            j = j + 2
        for i in range(strip.numPixels()):
            self.strip.setPixelColor(i, Color(0, 0, 0))
        self.strip.setBrightness(255)
        self.strip.show()
        self.strip_lock.release()

    # Cycle_period (s) is equivelant to the time it takes to go from white to the color
    # The full animation is 3 cycle_periods
    def idleBreathing(self, input, cycle_period):
        self.strip_lock.acquire()
        print("starting idlebreathing")
        strip.brightness = 255
        cycle_ms = cycle_period * 1000
        wait_ms = cycle_ms / 100
        input_int = (int(input[1]), int(input[0]), int(input[2]))
        delta_r = (R_WHITE - input[0]) / 100
        delta_g = (G_WHITE - input[1]) / 100
        delta_b = (B_WHITE - input[2]) / 100
        self.grb = (G_WHITE, R_WHITE, B_WHITE)
        up = True
        while self.get_state() is "IDLE_BREATHING":
            # calculate new values 
            if up: # decrement values
                g = self.grb[0] - delta_g
                r = self.grb[1] - delta_r
                b = self.grb[2] - delta_b
                if g < 0 or g < input[1]:
                    g = input[1]
                if r < 0 or r < input[0]:
                    r = input[0]
                if b < 0 or b < input[2]:
                    b = input[2]
            else: # Increment values
                g = self.grb[0] + delta_g
                r = self.grb[1] + delta_r
                b = self.grb[2] + delta_b
                if g > G_WHITE:
                    g = G_WHITE
                if r > R_WHITE:
                    r = R_WHITE
                if b > B_WHITE:
                    b = B_WHITE
            self.grb = (g, r, b)
            # print("grb: ", grb)

            # directional check
            grb_print = (int(self.grb[0]), int(self.grb[1]), int(self.grb[2]))
            if grb_print == input_int or grb_print == (G_WHITE, R_WHITE, B_WHITE):
                up = not up
                for i in range(1000):
                    time.sleep(cycle_period / 1000)
                    if self.get_state() is not "IDLE_BREATHING":
                        print("exiting")
                        self.strip_lock.release()
                        return 0
        
            # display color
            self.strip.fill(grb_print)
            self.strip.show()
            time.sleep(wait_ms/1000)
        print("exiting")
        self.strip_lock.release()
        return 0

    def greeting(self, cycle_period):
        self.strip_lock.acquire()
        print("starting greeting")
        strip.brightness = 255
        cycle_ms = cycle_period * 1000
        wait_ms = cycle_ms / 255
        delta_r = (255 - self.grb[0]) / 255
        delta_g = (255 - self.grb[1]) / 255
        delta_b = (0 - self.grb[2]) / 255

        while self.get_state() is "GREETING":
            # calculate new values
            g = self.grb[0] - delta_g
            r = self.grb[1] - delta_r
            b = self.grb[2] - delta_b
            if g > 255: 
                g = 255
            if r > 255: 
                r = 255
            if b < 0: 
                b = 0
            self.strip.fill(g, r, b)
            self.strip.show()
            time.sleep(wait_ms/1000)
            print(g, r, b)
        self.strip_lock.release()

def getInput(ser): # TODO: return next state and color, NULL if no color is sent
    burnLine = False
    x = ser.readline().decode('utf-8')
    if not burnLine:
        if "idleBreath" in x:
            return "IDLE_BREATHING"
        elif "shutdown" in x:
            return "SHUTOWN"
        elif "greeting" in x:
            return "GREETING"
        elif "setLED" in x: # Will most likely be removed, but a good example of parsing input for parameters
            x = x.replace('setLED','')
            r = x[:2]
            g = x[3:5]
            b = x[6:8]
            setColor = (int(g), int(r), int(b))
        else:
            burnLine = False
            return None
    return None

if __name__ == '__main__':
    
    # Process arguements
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    parser.add_argument('-u', '--user', action='store_true', help='sets code to run based on keyboard input from user rather than sensor feedback')
    args = parser.parse_args()

    #Create NeoPixel object
    strip = NeoPixel(board.D18, LED_COUNT, auto_write = False, pixel_order = ORDER)#, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # strip.begin()

    # setup serial connection
    ser = serial.Serial(
        port = '/dev/ttyAMA0',
        baudrate = 115200,
        parity = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE,
        bytesize = serial.EIGHTBITS,
        timeout = 1
    )

    con = LEDController(strip)
    state = START_STATE
    next_state = START_STATE
    while state is not "SHUTDOWN":
        # get next state
        next_state = getInput(ser)
        if next_state is not None:
            state = new_state
            con.set_state(new_state)
            
        # set thread for the correct state
        if state is "IDLE_BREATHING":
            c = threading.Thread(target=con.idleBreathing, args=(((0, 100, 255), 2)))
            c.start()
        if state is "GREETING":
            c = threading.Thread(target=con.greeting, args=[2])
            c.start()

        # continously execute state until a new one is set
        while state is next_state:
            time.sleep(.1)
    
    print("exiting")

    # except KeyboardInterrupt:
    #     if args.clear:
    #         colorWipe(strip, Color(0, 0, 0), 10)
