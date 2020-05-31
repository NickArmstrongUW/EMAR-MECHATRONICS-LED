#!/usr/bin/env python

import time
import serial

ser = serial.Serial(
        port = '/dev/ttyS0',
        baudrate = 9600
)
print("Begin")
while 1:
    x = ser.readline()
    print(x)
    sleep(1000)
