"""
1. take in as input the transcript, as well as the WAV file. [DONE]
2. split up the speech into each respective syllable. [phonetic rep., but not audio]
3. on each syllable, get some general informtion about it (such as loudness, pitch, etc).
4. Then, use that information to determine whether a syllable is stressed/the quality of the stress accent.
5. display that information back to the user
    a. give general information about speech quality, such as average pitch, loudness, etc.
    b. have the transcript be properly annotated for which accents are stressed
    c. maybe some visual indicators, such as a stenograph, would be valuable for the learner.
"""

import sys
from src import AudioAnalyzer
from src import SpeechAligner
from src import SyllableLookup
from pathlib import Path

def main():
    audio_file_list = []
    transcript_file_path = None
    match len(sys.argv):
        case 1:
            # script_name 
            print("Please input an audio file, along with a transcript for analysis.")
            return
        case 2:
            # script_name folder_name -> use the folder name to get the native recording, learner recording, and transcript
            folder_name = sys.argv[1]
            folder = Path(folder_name)
            files = [f.name for f in folder.iterdir() if f.is_file()]
            for file in files:
                if 'transcript' in file:
                    transcript_file_path = folder_name + file
                else:
                    audio_file_list.append(folder_name + file)
        case 3:
            # script_name audio_file transcript_file -> just give a single audio comparison
            audio_file_list = [sys.argv[1]]
            transcript_file_path = sys.argv[2]
        case _:
            # script_name audio_a audio_b transcript_file -> directly compare the two audios
            audio_file_list = sys.argv[1:-1]
            transcript_file_path = sys.argv[-1]
    
    for file in audio_file_list:
        print(f"Audio File: {file}")
    print(f"Transcript: {transcript_file_path}")

    syllables_arpa = SyllableLookup.get_arpa_from_transcript(transcript_file_path)
    print(syllables_arpa)

    # testing MFA
    output_dir = Path("output").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    grid = AudioAnalyzer.align_audio(audio_file_list[0], transcript_file_path, output_dir/"alignment.TextGrid")
    phones = AudioAnalyzer.get_phones_from_textgrid(grid)
    print(phones)

    syllable_times = []
    for syllable in syllables_arpa:
        print(syllable)

    return

    word_audios = []
    word_audio_titles = []
    for file in audio_file_list:
        audio = AudioAnalyzer.get_audio(file)
        aligned_audio = SpeechAligner.align_transcript(file, transcript_file_path)
        word_segments = aligned_audio["word_segments"]
        print(f"{file}:")
        SpeechAligner.print_aligned_words(word_segments)
        for word in word_segments:
            word_audio = AudioAnalyzer.get_audio_segment(audio, word['start'], word['end'])
            word_audios.append(word_audio)
            word_audio_titles.append(f"{file} - '{word["word"]}'")
    AudioAnalyzer.plot_audios(word_audios, word_audio_titles)

if __name__ == "__main__":
    main()
