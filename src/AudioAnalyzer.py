import librosa
import matplotlib.pyplot as plt

def plot_audio(audio_file_path):
    # y is the array of samples in the audio file
    # sr is the Sample Rate
    y, sr = librosa.load(audio_file_path)
    print(y)
    print(sr)
