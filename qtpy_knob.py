# qtpy_knob.py -- Mount a rotary encoder directly to an Adafruit QT Py,
#                 add some neopixels and get a USB media knob
# https://github.com/todbot/qtpy-knob
# 2021-2023 @todbot / Tod Kurt

# pylint: disable=invalid-name
#
"""
qtpy_knob

"""
import os
import time
import board
from digitalio import DigitalInOut, Direction, Pull
import neopixel
import usb_hid
from rainbowio import colorwheel
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

if os.uname().machine.find("rp2040") > 0:  # RP2040
    from fakerotaryio import IncrementalEncoder
else:
    from rotaryio import IncrementalEncoder


# config: number of seconds to keep LED ring on, 0 == keep on forever
ring_on_time = 0

# config: print out qtpy_knob state to REPL
debug = False

# 16 position neopixel ring
ring = neopixel.NeoPixel(board.MISO, 16, brightness=0.2, auto_write=False)

# button of rotary encoder
button = DigitalInOut(board.MOSI)
button.pull = Pull.UP

# Use pin A2 as a fake ground for the rotary encoder
fakegnd = DigitalInOut(board.A2)
fakegnd.direction = Direction.OUTPUT
fakegnd.value = False

encoder = IncrementalEncoder( board.A3, board.A1 )

cc = ConsumerControl(usb_hid.devices)

last_encoder_val = encoder.position
ring_pos = 0
rainbow_pos = 0
last_time = 0
ring_on = True

def color_int_to_tuple(val):
    """Convert a 24-bit color int to a 3-int tuple"""
    return (val >> 16 & 0xff, val >> 8 & 0xff, val >> 0 & 0xff)

print("hello from qtpy-knob!")

while True:
    encoder_pos = encoder.position
    encoder_diff = last_encoder_val - encoder_pos  # encoder clicks since last read
    last_encoder_val = encoder_pos
    ring_pos = (ring_pos + encoder_diff) % len(ring)    # position on LED ring
    fun_color = colorwheel( (20 + encoder_pos*4) % 255 )     # fun hue change based on pos
    fun_color = color_int_to_tuple(fun_color)  # convert to tuple for down below

    # LED ring goes off after a time of no activity
    if encoder_diff !=0 or button.value is False:
        last_time = time.monotonic()

    ring_on = (ring_on_time==0 or time.monotonic() - last_time < ring_on_time)

    if button.value is False:                   # button pressed
        cc.send(ConsumerControlCode.MUTE)       # toggle mute
        while not button.value:                 # wait for release
            time.sleep(0.05)
            # spin the rainbow while held
            for i in range(len(ring)):   # pylint: disable=consider-using-enumerate
                pixel_index = (i*256 // len(ring)) + rainbow_pos
                ring[i] = colorwheel( pixel_index & 255 )
                ring.show()
                rainbow_pos = (rainbow_pos + 1) % 256
    else:
        if encoder_diff > 0:
            for i in range(encoder_diff):
                cc.send(ConsumerControlCode.VOLUME_DECREMENT)
                time.sleep(0.01)
        elif encoder_diff < 0:
            for i in range(-encoder_diff):
                cc.send(ConsumerControlCode.VOLUME_INCREMENT)
                time.sleep(0.01)

        if ring_on:
            ring.fill( [int(i/2) for i in fun_color] ) # make it 1/2 dimmer
            ring[ring_pos] = (255,255,255)  # 'pointer' of where knob is
            ring[(ring_pos-1)%len(ring)] = (37,37,37) # and some surrounds for pointer
            ring[(ring_pos+1)%len(ring)] = (37,37,37)
        else:  # fade out LED ring if past ring_on_time
            ring[:] = [[max(i-10,0) for i in l] for l in ring]
        ring.show()

        if debug:
            print(ring_on,encoder_pos,encoder_diff,button.value,ring_pos)
        time.sleep(0.01)
