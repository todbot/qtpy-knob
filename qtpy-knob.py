

import board
import time
from digitalio import DigitalInOut, Direction, Pull
import neopixel
import rotaryio
import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

ring = neopixel.NeoPixel(board.MISO, 16, brightness=0.2, auto_write=False)

button = DigitalInOut(board.MOSI)
button.pull = Pull.UP

fakegnd = DigitalInOut(board.A2)
fakegnd.direction = Direction.OUTPUT
fakegnd.value = False

encoder = rotaryio.IncrementalEncoder( board.A3, board.A1 ) 

cc = ConsumerControl(usb_hid.devices)

print("hello!")

def wheel(pos):
# standard colorwheel
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
pos = 0
rainbow_pos=0

while True:
    diff = last_encoder_val - encoder.position
    last_encoder_val = encoder.position
    pos = (pos + diff) % len(ring)
    hue = wheel( encoder.position*4%255 )
    
    if button.value == False:  # pressed
        cc.send(ConsumerControlCode.MUTE)
        while not button.value: # wait for release
            time.sleep(0.05)
            for i in range(len(ring)):
                pixel_index = (i*256 // len(ring)) + rainbow_pos
                ring[i] = wheel( pixel_index & 255 )
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
        ring[pos] = (255,255,255)
        ring[(pos-1)%len(ring)] = (67,67,67)
        ring[(pos+1)%len(ring)] = (67,67,67)
        ring.show()
        print(encoder.position,diff,button.value,pos)
        time.sleep(0.05)




    
