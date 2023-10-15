"""
`qtpy_knob_midi_cc.py` -- Mount a rotary encoder directly to an Adafruit QT Py,
                          add some neopixels and get a USB scrolling knob
                          Turning knob scrolls vertically,
                          pressing & turning scrolls horizontally

 NOTE:  This is different from other qtpy_knob programs in that you will need to
        delete the 'adafruit_hid' library and install the 'adafruit_midi' library

 https://github.com/todbot/qtpy-knob/
 2021-2023 @todbot / Tod Kurt
"""
# pylint: disable=invalid-name, consider-using-enumerate

import os
import time
import board
from digitalio import DigitalInOut, Pull
import neopixel
import usb_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange

if os.uname().machine.find("rp2040") > 0:  # RP2040
    from fakerotaryio import IncrementalEncoder
else:
    from rotaryio import IncrementalEncoder

cc_num = 44        # what control change number to send on
cc_mult_fine = 4   # how much to multiply raw value by
cc_mult_coarse = 8 # how much to multiply raw value by when button pressed
cc_val = 0         # starting (and current) value of the control change value

# 16 position neopixel ring
ring = neopixel.NeoPixel(board.MISO, 16, brightness=0.2, auto_write=False)

# button of rotary encoder
button = DigitalInOut(board.MOSI)
button.switch_to_input(pull=Pull.UP)

# Use pin A2 as a fake ground for the rotary encoder
fakegnd = DigitalInOut(board.A2)
fakegnd.switch_to_output( value=False )

encoder = IncrementalEncoder( board.A3, board.A1 )

midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

print("hello from qtpy_knob_midi_cc!")

# standard colorwheel
def colorwheel(pos):
    """Emulate rainbowio.colorwheel, sorta"""
    if pos < 0 or pos > 255:
        (r,g,b) = (0,0,0)
    elif pos < 85:
        (r,g,b) = (int(pos * 3), int(255 - pos * 3), 0)
    elif pos < 170:
        pos -= 85
        (r,g,b) = (int(255 - pos * 3), 0, int(pos * 3))
    else:
        pos -= 170
        (r,g,b) = (0, int(pos * 3), int(255 - pos * 3))
    return (r, g, b)


last_encoder_val = encoder.position
ring_pos = 0
rainbow_pos = 0

cc_mult = cc_mult_fine

while True:
    diff = last_encoder_val - encoder.position  # encoder clicks since last read
    last_encoder_val = encoder.position
    ring_pos = (ring_pos + diff) % len(ring)    # position on LED ring
    hue = colorwheel( encoder.position*4 % 255 )     # fun hue change based on pos

    if not button.value:                        # button pressed
        cc_mult = cc_mult_coarse
        for i in range(len(ring)):          # spin the rainbow while held
            pixel_index = (i*256 // len(ring)) + rainbow_pos
            ring[i] = colorwheel( pixel_index & 255 )
            ring.show()
            rainbow_pos = (rainbow_pos + 1) % 256
    else:
        cc_mult = cc_mult_fine

        ring.fill( [int(i/4) for i in hue] ) # make it 1/4 dimmer
        ring[ring_pos] = (255,255,255)
        ring[(ring_pos-1)%len(ring)] = (67,67,67)
        ring[(ring_pos+1)%len(ring)] = (67,67,67)
        ring.show()

    if diff != 0:  # only send if there's a change
        print("sending")
        cc_val = cc_val - (diff*cc_mult)
        cc_val = max(min(127,cc_val), 0)  # clamp to 0-127
        #cc_val = 0 if n < 0 else 127 if n > 127 else cc_val  # clamp to 0-127

        midi.send([ControlChange(44, cc_val)])

    print(encoder.position,diff,button.value,ring_pos,cc_val)
    time.sleep(0.05)
