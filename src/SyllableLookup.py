import syllabify

def get_pronunciation_from_transcript(transcript_file_path):
    # read and clean transcript.
    with open(transcript_file_path, 'r') as file:
        transcript = file.read()
    transcript_word_list = transcript.split(' ')
    for i in range(len(transcript_word_list)):
        transcript_word_list[i] = transcript_word_list[i].strip()

    words_in_syllables_list = []
    for word in transcript_word_list:
        syllables = get_syllables_from_word(word)
        words_in_syllables_list.append(syllables)

    return words_in_syllables_list

def get_arpa_from_transcript(transcript_file_path):
    arpa_list = []
    syllable_list = get_pronunciation_from_transcript(transcript_file_path)
    for word in syllable_list:
        arpa_list.append([syllable[1] for syllable in word])
    return arpa_list

def get_stress_from_transcript(transcript_file_path):
    arpa_list = []
    syllable_list = get_pronunciation_from_transcript(transcript_file_path)
    for word in syllable_list:
        arpa_list.append([syllable[2] for syllable in word])
    return arpa_list

def get_syllables_from_word(word):
    word_syllable_info = syllabify.syllabify(word)
    syllable_list = []
    for word in word_syllable_info.words:
        for syllable in word.syllables:
            syllable_text = ''.join([x.phoneme for x in syllable.phonemes])
            syllable_list.append([syllable, syllable_text, syllable.stress])
    return syllable_list
