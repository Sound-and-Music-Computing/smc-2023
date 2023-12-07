# MIDI player with rotary encoder
# october 2023
# silvan peter
import rotaryio
import board
import time
import neopixel
import time
import random
# midi lib
import usb_midi
import adafruit_midi
from adafruit_midi.timing_clock import TimingClock
from adafruit_midi.start import Start
from adafruit_midi.stop import Stop
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from umidiparser import MidiFile, NOTE_ON, NOTE_OFF, SET_TEMPO

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
# SET STEPS PER QUARTER
STEPS_PER_QUARTER = 24

# LOAD A MIDI FILE
event_array = []
absolute_time = 0
for event in MidiFile("merged_gladiators.mid"):
    absolute_time += int(event.delta_miditicks / 480 * STEPS_PER_QUARTER)
    if event.status == NOTE_ON:
        event_array.append(["ON", event.note, event.velocity, absolute_time])
    elif event.status == NOTE_OFF :
        event_array.append(["OFF", event.note, event.velocity, absolute_time])

PIECE_LENGTH = absolute_time + 1
event_dict = dict()
for timepoint in range(PIECE_LENGTH):
    event_dict[timepoint] = list()
    
for event in event_array:
    if event[0] == "ON":
        event_dict[event[-1]].append(NoteOn(int(event[1]), event[2]))
    elif event[0] == "OFF":
        event_dict[event[-1]].append(NoteOff(int(event[1]), event[2]))
    
    
# what to do with sync signals
def sync_sender(sync_counter):
    global led, midi, STEPS_PER_QUARTER, PIECE_LENGTH, event_dict
    for event_msg in event_dict[sync_counter % PIECE_LENGTH]:
        midi.send(event_msg)
    if sync_counter % STEPS_PER_QUARTER == 0: # on quarter, change led color
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
        snyc_mod = STEPS_PER_QUARTER * 4
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

