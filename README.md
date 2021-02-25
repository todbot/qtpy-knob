# QTPy-Knob

QT Py USB Media Knob using rotary encoder &amp; neopixel ring

<img width=400 src="./docs/qtpyknob-pic1.jpg" />


The QTPy-Knob features:
- Media knob for volume up/down/mute with "qtpy-knob.py" CircuitPython program
- Stylish design reminiscent of Griffin Powermate
- Recessed USB-C connector to for safety
- No screws needed for assembly
- Only 3 wires needed to solder (none if you want to forgo LED lighting)
- Reprogrammable for any USB macro key action via CircuitPython

This is an attempt to make a minimal and easy-to-build version of similar, previous projects like:
- https://learn.adafruit.com/trinket-usb-volume-knob
- https://learn.adafruit.com/media-dial

## Components

Parts needed:

- Adafruit QT Py (https://www.adafruit.com/product/4600)
- Adafruti Neopixel Ring (https://www.adafruit.com/product/1463 or equiv)
- Rotary encoder (https://www.adafruit.com/product/377 or equiv)
- 3D printed enclosure (see "cad" folder)

## Software

Installation is:
- Install CircuitPython on your QT Py
- Install required CircuitPython libraries to QT Py
- Copy qtpy-knob.py to QT Py

The last two steps can be accomplished with the below

```
git clone https://github.com/todbot/qtpy-knob
cd qtpy-knob
pip3 install circup
circup install -r requirements.txt
cp qtpy-knob.py /Volumes/CIRCUITPY/code.py

```

## Assembly

[tbd, but basically...]

<img width=325 src="./docs/qtpyknob-wiring-diag.jpg" /><img width=325 src="./docs/qtpyknob-cad-animation.gif" />

<img width=325 src="./docs/qtpyknob-encoder-mount.jpg" /><img width=325 src="./docs/qtpyknob-wiring1.jpg" />

