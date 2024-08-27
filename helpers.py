import sys

from dataclasses import dataclass
from pydub.generators import Sine


def get_fret_frequencies(open_freq):
    """
    Calculates the frequency for each fret based on the base frequency
    and the relationship between frets (semitone steps).

    :param base_freq: The frequency of the open string (e.g. 82Hz for E2)
    :return: A list of frequencies for each fret (The 0th fret will be the open string)
    """

    frequencies = []

    # Iterate over each fret position
    for i in range(20):
        # Calculate the frequency for the current fret using the semitone formula
        frequency = open_freq * (2 ** (i / 12))
        frequencies.append(frequency)

    # TODO: understand the semitone formula

    return frequencies


def show_help():
    print(f"""
  Usage Examples:
    {sys.argv[0]} --show-frets
    {sys.argv[0]} --string 1 --fret 3
    {sys.argv[0]} --string 1 --fret 3 --overtones
    {sys.argv[0]} --string 1 --fret 3 --scale
    {sys.argv[0]} --string 1 --fret 3 --scale --overtones
""")


def parse_args(args, fret_string_frequencies):
    """
    Analyze the user's command and determine what to do.
    """

    # There are nicer ways to do this, but they involve learning other third
    # party libraries I'm trying to stick with just the standard library + pydub
    # here.
    if "--show-frets" in args:
        for i, string_frequencies in enumerate(fret_string_frequencies):
            print("string", i + 1)
            for j, freq in enumerate(string_frequencies):
                print("    fret:", j, "frequency:", freq)
        exit(0)

    if ("--string" not in args) or ("--fret" not in args):
        # the user doesn't seem to know what they're doing
        # provide some useful, then exit
        show_help()
        exit(0)
    else:
        string_num_index = args.index("--string") + 1
        string_num = int(args[string_num_index])
        if not (1 <= string_num <= 6):
            raise ValueError(f"Invalid string: {string_num}")

        # internally, strings use 0-based indexing (so they can be list indexes)
        # but when talking to the user, use 1-based
        string_num -= 1

        fret_num_index = args.index("--fret") + 1
        fret_num = int(args[fret_num_index])
        if not (0 <= fret_num <= 20):
            raise ValueError(f"Invalid Fret: {fret_num}")

        overtones = "--overtones" in args
        scale = "--scale" in args

        return string_num, fret_num, overtones, scale


def apply_volume_gain(segment, volume):
    """
    Apply volume gain to an AudioSegment.

    :param segment: The AudioSegment to which gain is applied.
    :param volume: The volume level (0.0 to 1.0).
    :return: The AudioSegment with the applied gain.
    """
    # Calculate the gain in dB relative to the volume level
    gain = 20 * (volume - 1)
    return segment.apply_gain(gain)


def pluck(
    frequency_hz, duration_seconds=0.5, sample_rate=44100, volume=1, overtones=False
):
    """
    Create an AudioSegment object containing a sine wave of the specified frequency
    with optional overtones to simulate a plucked guitar string.

    :param frequency_hz: The fundamental frequency of the sine wave (in Hz)
    :param duration_seconds: The duration of the sine wave (in seconds)
    :param sample_rate: The sample rate (in samples per second)
    :param volume: The volume of the sine wave (0.0 to 1.0)
    :param overtones: A boolean indicating whether to apply overtones
    :return: An AudioSegment containing the sine wave with overtones
    """

    # Define overtone harmonic amplitudes if overtones are enabled
    overtone_harmonic_amplitude = (
        {2: 0.3, 3: 0.3, 4: 0.2, 5: 0.2, 6: 0.1} if overtones else {}
    )

    # Create the fundamental tone
    base_tone = Sine(frequency_hz, sample_rate=sample_rate)
    base_segment = apply_volume_gain(
        base_tone.to_audio_segment(duration=duration_seconds * 1000), volume
    )

    # Initialize the output segment with the fundamental tone
    output_segment = base_segment

    # Overlay the overtones
    for overtone, overtone_volume in overtone_harmonic_amplitude.items():
        overtone_freq = frequency_hz * overtone
        overtone_tone = Sine(overtone_freq, sample_rate=sample_rate)
        overtone_segment = apply_volume_gain(
            overtone_tone.to_audio_segment(duration=duration_seconds * 1000),
            overtone_volume,
        )
        output_segment = output_segment.overlay(overtone_segment)

    return output_segment


@dataclass
class Note:
    string: int
    fret: int


def minor_pentatonic(note):
    first_fret = note.fret

    # this function is nested so that it can refer to the first fret
    # without requring the caller to specify it over and over again
    def add_semitones(note, num_semitones):

        # mostly you can add a string and subtract 5 frets and be back where you
        # started, except when the next string is string 4
        # note: this will break for certain nonstandard tunings
        if note.string + 1 == 4:
            fret_offset = -4
        else:
            fret_offset = -5

        # if we're too far down the neck from where we started
        # jump to the next string, but only if ther *is* a next string
        if (note.fret + num_semitones) - first_fret > 4 and note.string < 5:
            return Note(note.string + 1, note.fret + fret_offset + num_semitones)

        # otherwise just walk up the string
        else:
            new_fret = note.fret + num_semitones
            if new_fret > 20:
                raise ValueError(f"There is no fret {new_fret}")
            return Note(note.string, new_fret)

    one = note
    two = add_semitones(one, 3)
    three = add_semitones(two, 2)
    four = add_semitones(three, 2)
    five = add_semitones(four, 3)
    six = add_semitones(five, 2)

    return [one, two, three, four, five, six]
