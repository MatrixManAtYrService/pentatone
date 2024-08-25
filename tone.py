# sys is part of the python standard library
import sys

# helpers is a module that I wrote,
# you can import it because it's in the same directory as this script
from helpers import parse_args, get_fret_frequencies, sine_wave

from pydub.playback import play

standard_tuning = [  # in Hz
    82,  # low E
    110,  # A
    147,  # D
    196,  # G
    247,  # B
    330,  # high E
]
# source https://fretsuccess.com/what-are-the-guitar-string-frequencies/

frequencies = [get_fret_frequencies(open_freq) for open_freq in standard_tuning]
# this is a list of lists of numbers (a.k.a  `list[list[int]]` )
# frequencies[0] is a list of frequecies for the first string
# frequencies[0][0] is the frequency for the first string, no fret pressed
# frequencies[0][3] is the frequency for the first string, third fret pressed

# see what the user wants us to do
string_num, fret_num, overtones, scale = parse_args(sys.argv, frequencies)

base_freq = frequencies[string_num][fret_num]
base_sample = sine_wave(base_freq, duration_seconds=0.5, volume=0.5, overtones=overtones)

play(base_sample)
    
