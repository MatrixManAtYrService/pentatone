# sys is part of the python standard library
import sys

# pydub is a third-party library that you'll have to install to use this
from pydub import AudioSegment
from pydub.playback import play

# helpers is a module that I wrote,
# you can import here it because it's in the same directory as this script
# see helpers.py for more on these.
from helpers import Note, minor_pentatonic, get_fret_frequencies, parse_args, pluck

# source https://fretsuccess.com/what-are-the-guitar-string-frequencies/
standard_tuning = [  # in Hz
    82,  # low E
    110,  # A
    147,  # D
    196,  # G
    247,  # B
    330,  # high E
]

frequencies = [get_fret_frequencies(open_freq) for open_freq in standard_tuning]
# this is a list of lists of numbers (a.k.a  `list[list[int]]` )
# frequencies[0] is a list of frequecies for the first string
# frequencies[0][0] is the frequency for the first string, no fret pressed
# frequencies[0][3] is the frequency for the first string, third fret pressed

# consult the CLI to see what the user wants us to do
string_num, fret_num, overtones, scale = parse_args(sys.argv, frequencies)


if not scale:
    # play the note
    freq = frequencies[string_num][fret_num]
    print(f"String {string_num + 1}, Fret {fret_num}: {freq} Hz")
    sound = pluck(freq, duration_seconds=0.75, overtones=overtones)
    play(sound)
else:
    # play the minor pentatonic scale with the note as a base
    combined_sound = AudioSegment.silent(duration=0)  # Start with an empty AudioSegment
    silence = AudioSegment.silent(duration=100)  # 0.1 second of silence between notes

    for note in minor_pentatonic(Note(string_num, fret_num)):
        print(f"String {note.string + 1}, Fret {note.fret}:", end=" ")
        freq = frequencies[note.string][note.fret]
        print(freq, "Hz")
        sound = pluck(freq, duration_seconds=0.5, overtones=overtones)
        combined_sound += sound + silence

    # Play the entire scale
    play(combined_sound)
