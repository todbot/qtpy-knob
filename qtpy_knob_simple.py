# qtpy_knob_simple.py -- Mount a rotary encoder directly to an Adafruit QT Py,
#                        in the simplest possible code
# https://github.com/todbot/qtpy-knob
# 2021 @todbot / Tod Kurt
#

import time
import board
from digitalio import DigitalInOut, Direction, Pull
import rotaryio
import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# button of rotary encoder
button = DigitalInOut(board.MOSI)
button.pull = Pull.UP

# Use pin A2 as a fake ground for the rotary encoder
fakegnd = DigitalInOut(board.A2)
fakegnd.direction = Direction.OUTPUT
fakegnd.value = False

encoder = rotaryio.IncrementalEncoder(board.A3, board.A1) 

cc = ConsumerControl(usb_hid.devices)

last_encoder_val = encoder.position

while True: 
    diff = last_encoder_val - encoder.position  # encoder clicks since last read
    last_encoder_val = encoder.position
    
    if button.value == False:                   # button pressed
        cc.send(ConsumerControlCode.MUTE)       # toggle mute
        while not button.value:                 # wait for release
            pass
    else:                                       # not pressed
        if diff > 0:
            cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        elif diff < 0:
            cc.send(ConsumerControlCode.VOLUME_INCREMENT)
   time.sleep(0.05)
    
