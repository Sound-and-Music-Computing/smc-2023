# MIDI euclidean pattern player with rotary encoder
# october 2023
# silvan peter
import rotaryio
import board
import time
import neopixel
import time
import random
import ulab.numpy as np
# midi lib
import usb_midi
import adafruit_midi
from adafruit_midi.timing_clock import TimingClock
from adafruit_midi.start import Start
from adafruit_midi.stop import Stop
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from umidiparser import MidiFile, NOTE_ON, NOTE_OFF, SET_TEMPO

# HELPER TO COMPUTE RHYTHM
def euclidean(cycle = 16, pulses = 4, offset= 0):
    """
    compute an Euclidean rhythm
    """
    rhythm = []
    bucket = cycle-pulses
    timepoint = 0
    for step in range(cycle):
        # print(bucket, rhythm) 
        bucket = bucket + pulses
        if (bucket >= cycle):
            bucket = bucket - cycle
            rhythm.append(timepoint)
        timepoint += 1
    
    rhythm = [rh % cycle for rh in rhythm]
    rhythm_array = np.array(rhythm)
    rhythm_array = np.sort( rhythm_array)
    return rhythm_array


# SET MIDI ports
print("usb_midi_ports", usb_midi.ports)
port_in = usb_midi.PortIn
port_out = usb_midi.PortOut
midi = adafruit_midi.MIDI(
    midi_in=usb_midi.ports[0],
    in_channel=0,
    midi_out=usb_midi.ports[1],
    out_channel=0)

# SET LED
led = neopixel.NeoPixel(board.NEOPIXEL, 1)  # for S3 boards
# SET ENCODER
encoder = rotaryio.IncrementalEncoder(board.IO13, board.IO14)

# SET RHYTHM
STEPS_rhythm_cycle = 7
PULSES_rhythm_cycle = 3
OFFSET_rhythm_cycle = 0
event_array = euclidean(STEPS_rhythm_cycle, PULSES_rhythm_cycle, OFFSET_rhythm_cycle)
STEPS_crank_cycle = 3.5
print(event_array)

PIECE_LENGTH = STEPS_rhythm_cycle
event_dict = dict()
for timepoint in range(PIECE_LENGTH):
    event_dict[timepoint] = list()
    
for event in event_array:
    event_dict[event].append(NoteOn(int(57), 70))
    event_dict[(event + 1) % PIECE_LENGTH].append(NoteOff(int(57), 0))
    
# what to do with sync signals
def sync_sender(sync_counter):
    global led, midi, STEPS_crank_cycle, PIECE_LENGTH, event_dict
    for event_msg in event_dict[sync_counter % PIECE_LENGTH]:
        midi.send(event_msg)
    if sync_counter % STEPS_crank_cycle == 0: # on quarter, change led color
        led[0] = (random.randint(0,127), random.randint(0,127), random.randint(0,127))    

# SETUP
# framerate
time_unit = 0.001 # seconds 
STOP_TIME = 600.0 # how long should it run for
position_prev = encoder.position
position = encoder.position
starting = True
print("starting")


############################################# STARTING LOOP
while starting:
    position = encoder.position
    incr_change = abs(position-position_prev)
    if incr_change > 0:
        # increments
        sec_per_incr = 5.0 # init tempo -> this is just an initial estimate and has no effect
        incr_time = time.monotonic()
        incr_time_prev = time.monotonic()
        incr_counter = 0
        position = encoder.position
        position_prev = encoder.position

        # sync
        sec_per_sync = 0.5 # init tempo -> this is the initial rate of clock B
        sync_time = time.monotonic()
        sync_time_prev = time.monotonic()
        sync_counter = 0

        # conversion -> this is the "gearbox ratio" of the clocks
        snyc_mod = STEPS_crank_cycle
        incr_mod = 20
        syncs_per_incr = snyc_mod/incr_mod # encoder has 20 increments, sync sends 24 per quarter
        
        # find the SYNC counters corresponding to the current INCR interval
        # sync_count_of_incr_count_min -> where sync count should be ~ 
        sync_count_of_incr_count_min = 0
        # sync_count_of_incr_count_max -> where sync count should stop ~
        sync_count_of_incr_count_max = 1 * syncs_per_incr
        sync_count_min = int(sync_count_of_incr_count_min // 1)
        sync_count_max = int(sync_count_of_incr_count_max // 1)

        # global time
        global_time = time.monotonic()
        global_time_elapsed = time.monotonic()

        # run the main loop
        starting = False
        running = True
    
    time.sleep(time_unit)

############################################# RUNNING LOOP
    
print("running")

while running:
    # update incr
    position = encoder.position
    incr_change = abs(position-position_prev)
    if incr_change > 0:
        incr_time = time.monotonic()
        sec_per_incr = incr_time - incr_time_prev
        incr_time_prev = incr_time
        incr_counter += 1
        # update position
        position_prev = position
        
        # find the SYNC counters corresponding to the current INCR interval
        # sync_count_of_incr_count_min -> where sync count should be ~ 
        sync_count_of_incr_count_min = incr_counter * syncs_per_incr
        # sync_count_of_incr_count_max -> where sync count should stop ~
        sync_count_of_incr_count_max = (incr_counter+1) * syncs_per_incr
        sync_count_min = int(sync_count_of_incr_count_min // 1)
        sync_count_max = int(sync_count_of_incr_count_max // 1)
        
        # convert INCR tempo to SYNC tempo
        sec_per_sync = sec_per_incr / syncs_per_incr
        # set the new sync time reference to 
        sync_time_prev = incr_time # use increment time as reference
        sync_time_prev -= (sync_count_of_incr_count_min % 1) * sec_per_sync # subtract partial cycle of sync
        
    # update SYNC: catch up
    while sync_counter < sync_count_min:
        sync_counter += 1
        sync_sender(sync_counter)

    # update SYNC: run but not too far
    sync_time = time.monotonic()
    sync_change = abs(sync_time-sync_time_prev)
    if sync_change > sec_per_sync and sync_counter < sync_count_max:
        sync_counter += 1
        sync_time_prev = sync_time
        sync_sender(sync_counter)
        
    # update time
    global_time_elapsed = sync_time - global_time
    if abs(global_time_elapsed) > STOP_TIME:
        running = False
    
    time.sleep(time_unit)
    
# send a stop signal
midi.send(Stop())
print("stopping")


