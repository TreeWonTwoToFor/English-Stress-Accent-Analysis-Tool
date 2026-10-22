import tgt
import librosa
import subprocess
import numpy as np
import matplotlib.pyplot as plt

# utility functions to get and manipulate audio

def get_audio(audio_file_path):
    # y is the array of samples in the audio file
    # sr is the Sample Rate
    y, sr = librosa.load(audio_file_path)
    return (y,sr)

def get_audio_segment(audio, start, end):
    y, sr = audio

    start_sample = int(start*sr)
    end_sample = int(end*sr)

    return (y[start_sample:end_sample], sr)

# audio analysis functions

"""
what kinds of functions would I want to have access to?
1. split the words into syllable audio segments
2. measure auditory information (such as volume, and pitch)
3. use that information to determine if a syllable is stressed
"""

# audio_path and output_dir are both Path objects, while transcript is just a text file
def align_audio(audio_path, transcript_path, alignment_path):
    command = [
        "mfa",
        "align_one_hf",
        audio_path,
        transcript_path,
        "english_us_arpa",
        str(alignment_path),
        "--output_format",
        "long_textgrid",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "MFA alignment failed:\n" + result.stderr
        )

    if not alignment_path.exists():
        raise FileNotFoundError(
            f"Expected alignment output: {alignment_path}"
        )

    return alignment_path

def get_phones_from_textgrid(textgrid_file_path):
    tg = tgt.io.read_textgrid(textgrid_file_path)
    tier = tg.get_tier_by_name("phones")

    phoneme_list = []
    for interval in tier:
        if interval.text:
            phoneme_list.append((interval.text, interval.start_time, interval.end_time))

    return phoneme_list

# some plotting functions to show audio waveforms

def plot_audio(audio, name="Audio Graph"):
    y, sr = audio

    fig, ax = plt.subplots()
    librosa.display.waveshow(y, sr=sr, ax=ax)
    ax.set(title=name)

    plt.show()

def plot_audios(audio_list, names_list=None):
    if names_list is None:
        names_list = [f"Audio file #{i+1}" for i in range(len(audio_list))]
    if len(audio_list) > 1:
        fig, ax = plt.subplots(nrows=len(audio_list))
        for i in range(len(audio_list)):
            y, sr = audio_list[i]
            librosa.display.waveshow(y, sr=sr, ax=ax[i])
            ax[i].set(title=names_list[i])
        plt.show()
    else:
        plot_audio(audio_list[0])

def plot_fft(audio, name="Audio Graph"):
    y, sr = audio
    y_dft = np.fft.rfft(y)
    frequencies = np.fft.rfftfreq(len(y), d=1 / sr)

    fig, ax = plt.subplots(nrows=2)
    librosa.display.waveshow(y, sr=sr, ax=ax[0])
    ax[0].set(title=name + " time domain")
    ax[1].plot(frequencies, np.abs(y_dft), color="C1")
    ax[1].set(title="Frequency domain",
              xlabel="Frequency (Hz)",
              ylabel="Magnitude")

    plt.show()
