import board
from digitalio import DigitalInOut, Direction, Pull
import busio
import sdcardio
import audiobusio
import storage
import audiocore
import os
import random
import time


## Fair random file selection
def getRanges(list):
    acc = 0
    ranges = []
    for i in list:
        ranges.append((acc, acc + i))
        acc += i

    return ranges
# fair random number generator
class FRand:
    def __init__(self, values, incrementor=lambda x: x + 1, reset=lambda x: 0):
        self.lastPicked = [1] * len(values)
        self.values = values
        self.incrementor = incrementor
        self.reset = reset

    
    def next(self):
        # get the sum of the last picked values
        # the chance of picking a value is lastPicked[i]/sum(lastPicked)

        # we emulate this by creating a list of ranges
        # picking a random number between 0 and the sum of the values
        # and then finding the index of the range that the random number falls in

        # get the sum
        s = sum(self.lastPicked)

        ranges = getRanges(self.lastPicked)

        # pick a random number between 0 and s - 1
        r = random.randrange(s)

        # increase all lastPicked values by a certain amount (defaulted to (+1))
        self.lastPicked = list(map(self.incrementor, self.lastPicked))

        # find the index of the range that the random number falls in
        for i, range in enumerate(ranges):
            if r >= range[0] and r < range[1]:
                self.lastPicked[i] = self.reset(self.lastPicked[i])
                return self.values[i]            
            

        # if we get here, something went wrong
        print("Error: random number not found in range")
        print("Random number: " + str(r))
        print("Ranges: " + str(ranges))
        print("sum: " + str(s))

def get_fair_random_file(rand):
    return open("/sd/" + rand.next(), "rb")

# Opens and returns a random file from a list of files
def get_random_file(files):
    random_name = "/sd/" + files[random.randrange(len(files))]
    return open(random_name, "rb")

# SPI for the SD card
spi = busio.SPI(board.GP10, board.GP11, board.GP12)
cs = board.GP13

# Button
button = DigitalInOut(board.GP6)
button.direction = Direction.INPUT
button.pull = Pull.UP

sdcard = sdcardio.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")
# All the .wav files in the root directory
files = list(filter(lambda f: f.endswith(".wav"), os.listdir("/sd")))
rand = FRand(files, incrementor=lambda x: x + 1, reset=lambda x: 0)

file = get_fair_random_file(rand)#get_random_file(files)

# Open the I2S device
speaker = audiobusio.I2SOut(board.GP0, board.GP1, board.GP2)

# Time in seconds
DEBOUNCE_DELAY = 0.02
HOLD_DELAY = 1.0
last_time = time.monotonic()
previous_button_value = True
hold_triggered = False
while True:
    current_time = time.monotonic()
    current_button_value = button.value

    if current_button_value != previous_button_value:
        # Check for button release
        if current_time - last_time > DEBOUNCE_DELAY and current_button_value:
            if current_time - last_time < HOLD_DELAY:
                # Close the file that is currently open to avoid IOError
                file.close()

                file = get_fair_random_file(rand)

                # Process the wav file
                file_playback = audiocore.WaveFile(file)

                speaker.play(file_playback)

            # Button now is up. We can reset the hold trigger state
            hold_triggered = False

        # Update previous values on every state change
        previous_button_value = current_button_value
        last_time = current_time

    # Check whether the hold was triggered before to avoid triggering it on the next loop
    if not hold_triggered and not current_button_value and current_time - last_time > HOLD_DELAY:
        hold_triggered = True
        speaker.stop()
