import math
import sys
from math import pi, sin
from struct import pack

from pydub import AudioSegment


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

def create_sine_wave_audio_segment(frequencyHz, duration_seconds, sample_rate=44100, volume=0.5):
    """
    Create an AudioSegment object containing a sine wave of the specified frequency.

    :param frequencyHz: The frequency of the sine wave (in Hz)
    :param duration_seconds: The duration of the sine wave (in seconds)
    :param sample_rate: The sample rate (in samples per second)
    :param volume: Volume of the sine wave (0.0 to 1.0)
    :return: An AudioSegment containing the sine wave
    """
    wave_data = b''
    max_vol = int((2**15 - 1) * volume)

    # Ensure the range function receives an integer value
    for i in range(int(sample_rate * duration_seconds)):
        pcm_value = sin(i * frequencyHz / sample_rate * pi * 2)
        pcm_value = int(max_vol * pcm_value)
        wave_data += pack('h', pcm_value)

    # Generate the AudioSegment object directly from the wave data
    audio_segment = AudioSegment(
        data=wave_data,
        sample_width=2,  # 2 bytes per sample (16-bit)
        frame_rate=sample_rate,
        channels=1
    )

    return audio_segment
   
