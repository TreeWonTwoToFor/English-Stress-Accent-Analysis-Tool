import syllabify

def get_pronunciation_from_transcript(transcript_file_path):
    # read and clean transcript.
    with open(transcript_file_path, 'r') as file:
        transcript = file.read()
    transcript_word_list = transcript.split(' ')
    for i in range(len(transcript_word_list)):
        transcript_word_list[i] = transcript_word_list[i].strip()

    for word in transcript_word_list:
        syllables = get_syllables_from_word(word)
        for syllable in syllables:
            print(f"{syllable[1]}({syllable[2]})", end=' ')
        print()

def get_syllables_from_word(word):
    word_syllable_info = syllabify.syllabify(word)
    syllable_list = []
    for word in word_syllable_info.words:
        for syllable in word.syllables:
            syllable_text = ''.join([x.phoneme for x in syllable.phonemes])
            syllable_list.append([syllable, syllable_text, syllable.stress])
    return syllable_list
