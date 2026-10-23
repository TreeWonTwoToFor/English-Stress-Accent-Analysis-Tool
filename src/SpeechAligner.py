import whisperx

device = "cpu"
model = whisperx.load_model("base", device, compute_type="int8")

def align_transcript(audio_file_path, transcript_file_path=None):
    audio = whisperx.load_audio(audio_file_path)

    if transcript_file_path is not None:
        with open(transcript_file_path, 'r') as file:
            text = file.read()
        segments = [
            {
                "start": 0.0,
                "end": len(audio) / 16000, # 16kHz appears to be a generalization.
                "text": text
            }
        ]
        language = "en" # this is an assumption based on my current use case
        result = {"segments": segments, "language": language}
    else:
        result = model.transcribe(audio, batch_size=4)

    align_model, metadata = whisperx.load_align_model(
        language_code=result["language"],
        device=device,
    )

    aligned = whisperx.align(
        result["segments"],
        align_model,
        metadata,
        audio,
        device,
    )

    return aligned

def print_aligned_words(aligned_words):
    for word in aligned_words:
        print(f"\t{word['word']} - [{word['start']}-{word['end']}]")
