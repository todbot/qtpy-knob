# qtpy_knob_simple.py -- Mount a rotary encoder directly to an Adafruit QT Py,
#                        in the simplest possible code
# https://github.com/todbot/qtpy-knob
# 2021 @todbot / Tod Kurt
#

import os
import time
import board
from digitalio import DigitalInOut, Pull
import rotaryio
import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

if os.uname().machine.find("rp2040") > 0:  # RP2040
    from fakerotaryio import IncrementalEncoder
else:
    from rotaryio import IncrementalEncoder

# button of rotary encoder
button = DigitalInOut(board.MOSI)
button.switch_to_input(pull=Pull.UP)

# Use pin A2 as a fake ground for the rotary encoder
fakegnd = DigitalInOut(board.A2)
fakegnd.switch_to_output( value=False )

encoder = IncrementalEncoder(board.A3, board.A1)

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
