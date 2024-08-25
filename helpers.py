import math
import sys
from math import pi, sin
from struct import pack

from pydub import AudioSegment
from pydub.generators import Sine


def get_fret_frequencies(open_freq):
    """
    Calculates the frequency for each fret based on the base frequency
    and the relationship between frets (semitone steps).

    :param base_freq: The frequency of the open string (e.g., 82 Hz for E2)
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

def fill_gaps(hints):
    """
    Interpolates missing fret positions using logarithmic interpolation,
    and extrapolates past the last known fret.
    """
    
    # Find the indices and values of the known fractions
    known_frets = [i for i, v in enumerate(hints) if v is not None]
    known_values = [v for v in hints if v is not None]

    # Logarithm of the known values
    log_known_values = [math.log(v) for v in known_values]

    interpolated_values = []

    # Interpolate for each fret
    for i in range(len(hints)):
        if hints[i] is not None:
            interpolated_values.append(hints[i])
        else:
            if i < known_frets[0]:  # Extrapolate before the first known value
                next_index = known_frets[0]
                prev_index = next_index - (next_index - i)
                t = (i - prev_index) / (next_index - prev_index)
                log_interpolated_value = (
                    log_known_values[0] - (log_known_values[1] - log_known_values[0]) * t
                )
            elif i > known_frets[-1]:  # Extrapolate past the last known value
                prev_index = known_frets[-1]
                # The difference in log space between the last two known values
                log_diff = log_known_values[-2] - log_known_values[-1]
                log_interpolated_value = log_known_values[-1] - (i - prev_index) * log_diff
            else:  # Interpolate between known values
                prev_index = max([idx for idx in known_frets if idx < i])
                next_index = min([idx for idx in known_frets if idx > i])
                t = (i - prev_index) / (next_index - prev_index)
                log_interpolated_value = (
                    log_known_values[known_frets.index(prev_index)] * (1 - t)
                    + log_known_values[known_frets.index(next_index)] * t
                )
                
            interpolated_value = math.exp(log_interpolated_value)
            interpolated_values.append(interpolated_value)
    
    return interpolated_values


def show_help():
    print(f"""
  Usage Examples:
    {sys.argv[0]} --show-frets
    {sys.argv[0]} --string 0 --fret 3
    {sys.argv[0]} --string 0 --fret 3 --overtones
    {sys.argv[0]} --string 0 --fret 3 --scale
    {sys.argv[0]} --string 0 --fret 3 --scale --overtones
""")

def parse_args(args, fret_string_frequencies):
    """
    Analyze the user's command and determine what to do.
    """

    # the user might want to see which fret fractions we came up with
    if "--show-frets" in args:
        for i, string_frequencies in enumerate(fret_string_frequencies):
            print("string", i)
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
        if not (0 <= string_num <= 5):
            raise ValueError(f"Invalid string: {string_num}")

        fret_num_index = args.index("--fret") + 1
        fret_num = int(args[fret_num_index])
        if not (0 <= fret_num <= 20):
            raise ValueError(f"Invalid Fret: {fret_num}")

        overtones = ("--overtones" in args)
        scale = ("--scale" in args)

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


def sine_wave(frequency_hz, duration_seconds=.5, sample_rate=44100, volume=0.5, overtones=False):
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
    overtone_harmonic_amplitude = {2: 0.5, 3: 0.4, 4: 0.3, 5: 0.2, 6: 0.1} if overtones else {}

    # Create the fundamental tone
    base_tone = Sine(frequency_hz, sample_rate=sample_rate)
    base_segment = apply_volume_gain(
        base_tone.to_audio_segment(duration=duration_seconds * 1000),
        volume
    )

    # Initialize the output segment with the fundamental tone
    output_segment = base_segment

    # Overlay the overtones
    for overtone, overtone_volume in overtone_harmonic_amplitude.items():
        overtone_freq = frequency_hz * overtone
        overtone_tone = Sine(overtone_freq, sample_rate=sample_rate)
        overtone_segment = apply_volume_gain(
            overtone_tone.to_audio_segment(duration=duration_seconds * 1000),
            overtone_volume
        )
        output_segment = output_segment.overlay(overtone_segment)

    return output_segment
