import librosa
import numpy as np
import matplotlib.pyplot as plt

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
