import tgt
import librosa
import subprocess
import numpy as np
import matplotlib.pyplot as plt

"""
The 'audio' parameter is composed of y and sr.
y - array of samples
sr - sample rate
"""

# utility functions to get and manipulate audio

def get_audio(audio_file_path):
    y, sr = librosa.load(audio_file_path)
    return (y,sr)

def get_audio_segment(audio, start, end):
    y, sr = audio

    start_sample = int(start*sr)
    end_sample = int(end*sr)

    return (y[start_sample:end_sample], sr)

def get_audio_length(audio):
    y, sr = audio
    return y.shape[0]/sr

# audio analysis functions

def get_syllables_from_audio(audio, syllable_timings):
    word_list = []
    for word in syllable_timings:
        syllable_list = []
        for syllable in word:
            syllable_list.append(get_audio_segment(audio, syllable[1], syllable[2]))
        word_list.append(syllable_list)
    return word_list

def get_phonemes_from_audio(audio, phoneme_timings):
    return [get_audio_segment(audio, p[1], p[2]) for p in phoneme_timings]

def get_volume(audio):
    y, sr = audio
    rms = librosa.feature.rms(y=y)[0][0]
    rms_db = librosa.amplitude_to_db(
        np.array([rms]),
        ref=1.0
    )[0]
    return (float(rms), float(rms_db))

def get_fundamental_frequency(audio):
    y, sr = audio
    f0 = librosa.yin(
        y,
        fmin=60,
        fmax=400,
        sr=sr
    )

    # Removes invalid values, if any
    f0 = f0[np.isfinite(f0)]

    return (float(np.mean(f0)), float(np.median(f0)), float(np.min(f0)), float(np.max(f0)))

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

def plot_audio_list(audio_list, names_list=None):
    if type(audio_list) is not list:
        audio_list = [audio_list]
    if names_list is None:
        names_list = [f"Audio file #{i+1}" for i in range(len(audio_list))]
    if len(audio_list) > 1:
        fig, ax = plt.subplots(nrows=len(audio_list))
        for i in range(len(audio_list)):
            y, sr = audio_list[i]
            librosa.display.waveshow(y, sr=sr, ax=ax[i])
            ax[i].set(title=names_list[i])
    else:
        plot_audio(audio_list[0])

def plot_audio_grid(audio_grid, names_list=None):
    # names_list should have one name per 'row', aka each audio stream, where a 'stream' is just the sublist.
    # a good use case of this would be that we can compare two recordings of the same thing, split into syllbales.
    if names_list is None:
        names_list = [f"Audio file #{i+1}" for i in range(len(audio_grid))]
    # this does presume that all audios have the same number of syllables, which should be checked at some point
    fig, ax = plt.subplots(nrows=len(audio_grid), ncols=len(audio_grid[0]), sharex="col", layout='constrained')
    # rotating to make the text more clear
    for axis in ax.flat:
        axis.tick_params(axis='x', rotation=45)
    # acutal procsessing - yay
    for i in range(len(audio_grid)):
        for j in range(len(audio_grid[i])):
            y, sr = audio_grid[i][j]
            librosa.display.waveshow(y, sr=sr, ax=ax[i,j])
            ax[i,j].set(title=str(names_list[i] + f", Clip #{j+1}"))

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

def plot_line(pt_a, pt_b):
    plt.plot([pt_a[0], pt_b[0]], [pt_a[1], pt_b[1]])

def plot_save(name="./output/plot.png"):
    plt.savefig(name, dpi=600, bbox_inches='tight', pad_inches=0.2)

def plot_show():
    plt.show()
