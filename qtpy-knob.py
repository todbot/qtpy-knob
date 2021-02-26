# qtpy-knob.py -- Mount a rotary encoder directly to an Adafruit QT Py,
#                 add some neopixels and get a USB media knob
# 2020 @todbot / Tod Kurt
#

import time
import board
from digitalio import DigitalInOut, Direction, Pull
import neopixel
import rotaryio
import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# 16 position neopixel ring
ring = neopixel.NeoPixel(board.MISO, 16, brightness=0.2, auto_write=False)

# button of rotary encoder
button = DigitalInOut(board.MOSI)
button.pull = Pull.UP

# Use pin A2 as a fake ground for the rotary encoder
fakegnd = DigitalInOut(board.A2)
fakegnd.direction = Direction.OUTPUT
fakegnd.value = False

encoder = rotaryio.IncrementalEncoder( board.A3, board.A1 ) 

cc = ConsumerControl(usb_hid.devices)

print("hello from qtpy-knob!")

# standard colorwheel
def colorwheel(pos):
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

while True: 
    diff = last_encoder_val - encoder.position  # encoder clicks since last read
    last_encoder_val = encoder.position
    ring_pos = (ring_pos + diff) % len(ring)    # position on LED ring
    hue = colorwheel( encoder.position*4 % 255 )     # fun hue change based on pos
    
    if button.value == False:                   # button pressed
        cc.send(ConsumerControlCode.MUTE)       # toggle mute
        while not button.value:                 # wait for release
            time.sleep(0.05)
            for i in range(len(ring)):          # spin the rainbow while held
                pixel_index = (i*256 // len(ring)) + rainbow_pos
                ring[i] = colorwheel( pixel_index & 255 )
                ring.show()
                rainbow_pos = (rainbow_pos + 1) % 256
    else:
        if diff > 0:
            for i in range(diff):
                cc.send(ConsumerControlCode.VOLUME_DECREMENT)
                time.sleep(0.01)
        elif diff < 0:
            for i in range(-diff):
                cc.send(ConsumerControlCode.VOLUME_INCREMENT)
                time.sleep(0.01)

        ring.fill( [int(i/4) for i in hue] ) # make it 1/4 dimmer 
        ring[ring_pos] = (255,255,255)
        ring[(ring_pos-1)%len(ring)] = (67,67,67)
        ring[(ring_pos+1)%len(ring)] = (67,67,67)
        ring.show()
        print(encoder.position,diff,button.value,ring_pos)
        time.sleep(0.05)
    
