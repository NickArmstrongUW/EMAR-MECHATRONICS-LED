#!/usr/bin/env python

import time
from neopixel import *
import argparse
import board
import threading
#import serial

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
NEXT_STATE = "IDLE_BREATHING"
CURRENT_STATE = "IDLE_BREATHING"

#ser = serial.Serial(
#        port = '/dev/ttyS0',
#        baudrate = 115200,
#        parity = serial.PARITY_NONE,
#        stopbits = serial.STOPBITS_ONE,
#        bytesize = serial.EIGHTBITS,
#        timeout = 1
#)
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(0, 110):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def glow(strip, color,wait_ms = 50):
# for i in range(strip.numPixels()):
    for i in range(0, 110):
        strip.setPixelColor(i, color)
    j = 255
    for j in range(0, 255):
        strip.setBrightness(j)
        strip.show()
        time.sleep(wait_ms/1000)
        j = j - 2

def glowout(strip):
    for j in range(0, 255):
        strip.setBrightness(255 - j)
        strip.show()
        time.sleep(50/1000)
        j = j + 2
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.setBrightness(255)
    strip.show()

# Cycle_period (s) is equivelant to the time it takes to go from white to the color
# The full animation is 3 cycle_periods
def idleBreathing(strip, input, cycle_period):
    strip.brightness = 255
    cycle_ms = cycle_period * 1000
    wait_ms = cycle_ms / 100
    input_int = (int(input[1]), int(input[0]), int(input[2]))
    delta_r = (R_WHITE - input[0]) / 100
    delta_g = (G_WHITE - input[1]) / 100
    delta_b = (B_WHITE - input[2]) / 100
    grb = (G_WHITE, R_WHITE, B_WHITE)
    up = True
    while STATE is "IDLE_BREATHING":
        # calculate new values 
        if up: # decrement values
            g = grb[0] - delta_g
            r = grb[1] - delta_r
            b = grb[2] - delta_b
            if g < 0 or g < input[1]:
                g = input[1]
            if r < 0 or r < input[0]:
                r = input[0]
            if b < 0 or b < input[2]:
                b = input[2]
        else: # Increment values
            g = grb[0] + delta_g
            r = grb[1] + delta_r
            b = grb[2] + delta_b
            if g > G_WHITE:
                g = G_WHITE
            if r > R_WHITE:
                r = R_WHITE
            if b > B_WHITE:
                b = B_WHITE
        grb = (g, r, b)
        print("grb: ", grb)

        # directional check
        grb_print = (int(grb[0]), int(grb[1]), int(grb[2]))
        if grb_print == input_int or grb_print == (G_WHITE, R_WHITE, B_WHITE):
            up = not up
            print("going to sleep")
            for i in range(1000):
                time.sleep(cycle_period / 1000)
                if STATE is not "IDLE_BREATHING":
                    print("exiting")
                    return 0
    
        # display color
        strip.fill(grb_print)
        strip.show()
        time.sleep(wait_ms/1000)
    print("exiting")
    return 0

def setColor(x, methodName):
    x = x.replace(methodName,'')
    r = x[:2]
    g = x[3:5]
    b = x[6:8]
    return r, g, b

def getInput():
    burnLine = False
    x = ser.readline()
    if not burnLine:
        if "idleBreath" in x:
            NEXT_STATE = IDLE_BREATHING
        elif "shutdown" in x:
            NEXT_STATE = SHUTDOWN
        elif "greeting" in x:
            NEXT_STATE = GREETING
        elif "setLED" in x: # Will most likely be removed, but a good example of parsing input for parameters
            x = x.replace('setLED','')
            r = x[:2]
            g = x[3:5]
            b = x[6:8]
            setColor = (int(g), int(r), int(b))
        burnLine = True
    else:
        burnLine = False


if __name__ == '__main__':
    
    # Process arguements
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    parser.add_argument('-u', '--user', action='store_true', help='sets code to run based on keyboard input from user rather than sensor feedback')
    args = parser.parse_args()
    #Create NeoPixel object
    strip = NeoPixel(board.D18, LED_COUNT, auto_write = False, pixel_order = ORDER)#, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # strip.begin()
    # inp = thread.Thread(target=getInput)
    while NEXT_STATE is not "SHUTDOWN":
        if CURRENT_STATE is "IDLE_BREATHING"
            c = threading.Thread(target=idleBreathing, args=((strip, (0, 100, 255))
            c.start()

        while CURRENT_STATE is NEXT_STATE:

            time.sleep(.001)
        CURRENT_STATE = NEXT_STATE
    
    print("exiting")

    

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0, 0, 0), 10)
