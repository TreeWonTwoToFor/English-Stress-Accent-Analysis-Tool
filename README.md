# English-Stress-Accent-Analysis-Tool
English Stress Accent Analysis Tool (or ESAAT), is a tool which takes in an audio file, along with a transcript of the spoken English in the audio file, and will return details to the user about qualities about their spoken English.

# Used libraries
* librosa for sound analysis
* whisperx for syncing up transcriptions to the audio. 
* syllabify for identifying syllables + stress accent pattern
* General utility Libraries
  * pathlib, tgt, numpy, matplotlib
* The Montreal Forced Aligner (MFA) is also used for detecting phoneme boundaries
