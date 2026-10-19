import librosa
import numpy as np
import matplotlib.pyplot as plt

def plot_audio(audio_file_path):
    # y is the array of samples in the audio file
    # sr is the Sample Rate
    y, sr = librosa.load(audio_file_path)

    fig, ax = plt.subplots()
    librosa.display.waveshow(y, sr=sr, ax=ax)
    ax.set(title=audio_file_path)

    plt.show()

def plot_fft(audio_file_path):
    y, sr = librosa.load(audio_file_path)
    y_dft = np.fft.rfft(y)
    frequencies = np.fft.rfftfreq(len(y), d=1 / sr)

    fig, ax = plt.subplots(nrows=2)
    librosa.display.waveshow(y, sr=sr, ax=ax[0])
    ax[0].set(title=audio_file_path + " time domain")
    ax[1].plot(frequencies, np.abs(y_dft), color="C1")
    ax[1].set(title="Frequency domain",
              xlabel="Frequency (Hz)",
              ylabel="Magnitude")

    plt.show()
