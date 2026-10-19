import pronouncing

def get_pronunciation_from_transcript(transcript_file_path):
    # read and clean transcript.
    with open(transcript_file_path, 'r') as file:
        transcript = file.read()
    transcript_word_list = transcript.split(' ')
    for i in range(len(transcript_word_list)):
        transcript_word_list[i] = transcript_word_list[i].strip()

    for word in transcript_word_list:
        pronunciations = pronouncing.phones_for_word(word)
        syllable_count = pronouncing.syllable_count(pronunciations[0])
        stress_pattern = pronouncing.stresses(pronunciations[0])
        print(word, pronunciations)
        print(syllable_count, stress_pattern)
