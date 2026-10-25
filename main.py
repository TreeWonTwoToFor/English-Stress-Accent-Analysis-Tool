"""
1. take in as input the transcript, as well as the WAV file. [DONE]
2. split up the speech into each respective syllable. [DONE - but is quite inconsistent as of rn. ARPA/speech recognition both need improvement]
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
            # script_name audio_a .... audio_n transcript_file -> directly compare all audios
            audio_file_list = sys.argv[1:-1]
            transcript_file_path = sys.argv[-1]
    
    for file in audio_file_list:
        print(f"Audio File: {file}")
    print(f"Transcript: {transcript_file_path}")

    for audio_file in audio_file_list:
        # timings is a list of words, which are lists of syllables
        syllable_timings = get_syllable_timings(audio_file, transcript_file_path)

        # uses the aligned audio to get a more precise timing system
        audio = AudioAnalyzer.get_audio(audio_file)
        aligned_audio = SpeechAligner.align_transcript(audio_file, transcript_file_path)
        word_segments = aligned_audio["word_segments"]
        word_start_times = [float(w["start"]) for w in word_segments]

        # uses the (presumably) more accurate word start time to offset the syllable timings
        for i in range(len(word_start_times)):
            # word start time  minus first syllable start time
            offset = word_start_times[i]-syllable_timings[i][0][1]
            for j in range(len(syllable_timings[i])):
                word = syllable_timings[i][j]
                syllable_timings[i][j] = (word[0], word[1]+offset, word[2]+offset)

        AudioAnalyzer.plot_audios(audio)

        print(audio_file)
        for i in range(len(syllable_timings)):
            word = syllable_timings[i]
            print(word)
            for syllable in word:
                AudioAnalyzer.plot_line((syllable[1], -1), (syllable[1], 1))
        SpeechAligner.print_aligned_words(word_segments)

        AudioAnalyzer.plot_show()

def get_syllable_timings(audio_file, transcript_file_path, printing=False):
    output_dir = Path("output").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    words_in_arpa = SyllableLookup.get_arpa_from_transcript(transcript_file_path)

    audio_name = audio_file.split('/')[-1].split('.')[0]
    grid = AudioAnalyzer.align_audio(
            audio_file,
            transcript_file_path, 
            output_dir/ str(audio_name + "_alignment.TextGrid")
    )
    phones = AudioAnalyzer.get_phones_from_textgrid(grid)
    phones_ending_time = phones[-2][2] # a backup for if a word isn't properly caught

    word_times = []
    for word in words_in_arpa:
        syllable_times = []
        for syllable in word:
            syllable_text = ""
            start_time, end_time = 0, 0
            if printing: print(syllable)
            searching = True
            while searching:
                if len(phones) == 0:
                    # something went wrong, so just break out
                    searching = False
                    break
                if printing: print(phones[0])
                p_arpa, p_start, p_end = phones.pop(0)
                p_arpa = p_arpa[:-1] if p_arpa[-1].isdigit() else p_arpa
                if p_arpa in ['sil']:
                    continue
                if syllable_text == "":
                    start_time = p_start
                syllable_text = syllable_text + p_arpa
                if syllable_text == syllable:
                    end_time = p_end
                    searching = False
            syllable_times.append((syllable, start_time, end_time))
        word_times.append(syllable_times)
    for i in range(len(word_times)):
        for j in range(len(word_times[i])):
            s = word_times[i][j]
            # is the end time before the start?
            if s[1] > s[2]:
                new_end = 0
                try:
                    # start of next syllable
                    new_end = word_times[i][j+1][1]
                except:
                    try: 
                        # start of next word
                        new_end = word_times[i+1][0][1]
                    except:
                        # last recorded phoneme
                        new_end = phones_ending_time
                word_times[i][j] = (s[0], s[1], new_end)
    return word_times

def plot_audios(audio_file_list, transcript_file_path):
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
    AudioAnalyzer.plot_show()

if __name__ == "__main__":
    main()
