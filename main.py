"""
1. take in as input the transcript, as well as the WAV file. [DONE]
2. split up the speech into each respective syllable. [DONE - good enough for now]
3. on each syllable, get some general informtion about it (such as loudness, pitch, etc). [DONE]
4. Then, use that information to determine whether a syllable is stressed/the quality of the stress accent. [N/A]
5. display that information back to the user [DONE]
    a. give general information about speech quality, such as average pitch, loudness, etc. [DONE]
    b. have the transcript be properly annotated for which accents are stressed
    c. maybe some visual indicators, such as a stenograph, would be valuable for the learner. [general audio graph]
"""

import sys
from src import AudioAnalyzer
from src import SpeechAligner
from src import SyllableLookup
from pathlib import Path

def get_offsets_from_aligned_audio(audio_file, syllable_timings):
    audio = AudioAnalyzer.get_audio(audio_file)
    aligned_audio = SpeechAligner.align_transcript(audio_file, transcript_file_path)
    word_segments = aligned_audio["word_segments"]
    word_start_times = [float(w["start"]) for w in word_segments]

    # uses the (presumably) more accurate word start time to offset the syllable timings
    offset_list = []
    for i in range(len(word_start_times)):
        # word start time minus first syllable start time
        offset = word_start_times[i]-syllable_timings[i][0][1]
        offset_list.append(offset)
    return offset_list

def get_phoneme_timings(audio_file, transcript_file_path):
    output_dir = Path("output").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    audio_name = audio_file.split('/')[-1].split('.')[0]
    grid = AudioAnalyzer.align_audio(
            audio_file,
            transcript_file_path, 
            output_dir/ str(audio_name + "_alignment.TextGrid")
    )
    return AudioAnalyzer.get_phones_from_textgrid(grid)

def get_vowel_timings(audio_file, transcript_file_path, printing=False):
    return get_timings_helper_func(audio_file, transcript_file_path, "vowel", printing)

def get_syllable_timings(audio_file, transcript_file_path, printing=False):
    word_times = get_timings_helper_func(audio_file, transcript_file_path, "syllable", printing)
    phones = get_phoneme_timings(audio_file, transcript_file_path)
    phones_ending_time = phones[-2][2] # a backup for if a word isn't properly caught

    # clean up timings
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

def get_timings_helper_func(audio_file, transcript_file_path, timing_type, printing):
    words_in_arpa = SyllableLookup.get_arpa_from_transcript(transcript_file_path)
    phones = get_phoneme_timings(audio_file, transcript_file_path)

    word_times = []
    for word in words_in_arpa:
        vowel_times = []
        syllable_times = []
        for syllable in word:
            syllable_text = ""
            start_time, end_time = 0, 0
            per_syllable_phoneme_list = []
            if printing: 
                print(syllable)
            searching = True
            while searching:
                if len(phones) == 0:
                    # something went wrong, so just break out
                    searching = False
                    break
                if printing: 
                    print(phones[0])
                p_arpa, p_start, p_end = phones.pop(0)
                p_old_arpa = p_arpa
                p_arpa = p_arpa[:-1] if p_arpa[-1].isdigit() else p_arpa
                if p_arpa in ['sil']:
                    continue
                syllable_text = syllable_text + p_arpa
                if syllable_text == "":
                    start_time = p_start
                if syllable_text == syllable:
                    end_time = p_end
                    searching = False
                per_syllable_phoneme_list.append((p_old_arpa, p_start, p_end))
            # this search is really ugly, but it does the job
            vowel = [x for x in per_syllable_phoneme_list if x[0][-1].isdigit()][0]
            if len(per_syllable_phoneme_list) != 0: 
                vowel_times.append(vowel)
            syllable_times.append((syllable, start_time, end_time))
        match timing_type:
            case "syllable":
                word_times.append(syllable_times)
            case "vowel":
                word_times.append(vowel_times)
    return word_times

def plot_word_from_audio_list(audio_file_list, transcript_file_path):
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
    AudioAnalyzer.plot_audio_list(word_audios, word_audio_titles)
    AudioAnalyzer.plot_show()

def read_sys_args():
    audio_file_list = []
    transcript_file_path = None
    match len(sys.argv):
        case 1:
            raise ValueError("Please input an audio file, along with a transcript for analysis.")
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
    return audio_file_list, transcript_file_path

def main(audio_file_list, transcript_file_path, show_output=False):
    for file in audio_file_list:
        print(f"Audio File: {file}")
    print(f"Transcript: {transcript_file_path}")

    vowel_grid = []
    vowel_text_grid = []
    for i in range(len(audio_file_list)):
        audio_file = audio_file_list[i]
        print(f"Analyzing {audio_file.split('/')[-1]}")

        vowel_timings = get_vowel_timings(audio_file, transcript_file_path)
        phoneme_timings = get_phoneme_timings(audio_file, transcript_file_path)

        vowel_list = []
        for phoneme in phoneme_timings:
            if phoneme[0][-1].isdigit():
                vowel_list.append(phoneme)
         
        audio = AudioAnalyzer.get_audio(audio_file)
        vowel_audio_list = AudioAnalyzer.get_phonemes_from_audio(audio, vowel_list)
        vowel_text_list = []
        for j in range(len(vowel_audio_list)):
            vowel = vowel_audio_list[j]
            rms, rms_db = AudioAnalyzer.get_volume(vowel)
            f_mean, f_median, f_min, f_max = [round(x,2) for x in AudioAnalyzer.get_fundamental_frequency(vowel)]
            vowel_text_list.append([f"Audio #{i+1} Vowel #{j+1}", str(rms), str(round(rms_db, 2)), str(f_mean), str(f_median), f"{f_min}-{f_max}"])
        vowel_grid.append(vowel_audio_list)
        vowel_text_grid.append(vowel_text_list)
    
    csv_str = ""
    for vowel_list in vowel_text_grid:
        csv_entry_list = [",", "rms,", "rms_db,", "f_mean,", "f_median,", "f_range,", ""]
        for vowel_info in vowel_list:
            for i in range(len(vowel_info)):
                csv_entry_list[i] = csv_entry_list[i] + vowel_info[i] + ','
        csv_entry_str = "\n".join(csv_entry_list)
        csv_str = csv_str + csv_entry_str + '\n'

    csv_file_name = f"./output/syllable_information.csv"
    with open(csv_file_name, 'w') as file: 
        file.write(csv_str)
    if len(audio_file_list) == 1:
        AudioAnalyzer.plot_audio_list(vowel_grid[0])
    else:
        AudioAnalyzer.plot_audio_grid(vowel_grid)
    AudioAnalyzer.plot_save()
  
    if show_output:
        print()
        print(csv_str[:-1])
        AudioAnalyzer.plot_show()

if __name__ == "__main__":
    audio_file_list, transcript_file_path = read_sys_args()
    main(audio_file_list, transcript_file_path)
