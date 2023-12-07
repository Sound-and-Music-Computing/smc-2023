# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT
# 
# changed by Silvan Peter
# october 2023
#
# make sure boot.py contains
#
#	import usb_midi
#	import usb_hid
#
#	usb_hid.disable()
#	usb_midi.enable()
#

import rotaryio
import board
import time
import ulab.numpy as np
import storage
import os
import usb_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
import neopixel
from umidiparser import *
import time
import random

# SET LED
led = neopixel.NeoPixel(board.NEOPIXEL, 1)  # for S3 boards

# SET ENCODER
encoder = rotaryio.IncrementalEncoder(board.IO13, board.IO14)

#set MIDI ports
print("usb_midi_ports", usb_midi.ports)
port_in = usb_midi.PortIn
port_out = usb_midi.PortOut

midi = adafruit_midi.MIDI(
    midi_in=usb_midi.ports[0],
    in_channel=0,
    midi_out=usb_midi.ports[1],
    out_channel=0)

time_unit = 0.01 #s
counter = 0
last_position = encoder.position
time_start=time.monotonic()
new_note = 57
new_vel = 0
while True:
    time.sleep(time_unit)
    position = encoder.position
    if last_position != position:
        print("hey")
        midi.send(NoteOff(int(new_note), new_vel))
        new_note += (last_position - position) * random.randint(0,8)
        
        new_vel = random.randint(60,127)
        midi.send(NoteOn(int(new_note), new_vel))
        led[0] = (random.randint(0,127), random.randint(0,127), random.randint(0,127))
        last_position = position
