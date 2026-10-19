"""
1. take in as input the transcript, as well as the WAV file.
2. split up the speech into each respective syllable.
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

def main():
    # python main AUDIO_FILE TRANSCRIPT_FILE
    audio_file_path = sys.argv[1]
    transcript_file_path = sys.argv[2]
    print(f"Audio File: {audio_file_path}")
    print(f"Transcript: {transcript_file_path}")

    # AudioAnalyzer.plot_audio(audio_file_path)
    aligned_audio = SpeechAligner.align_transcript(audio_file_path, transcript_file_path)
    word_segments = aligned_audio["word_segments"]
    print(word_segments)

    SyllableLookup.get_pronunciation_from_transcript(transcript_file_path)

if __name__ == "__main__":
    main()
