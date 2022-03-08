from pydub import AudioSegment
from pydub.silence import split_on_silence

sentence = "Portez ce vieux whisky au juge blond qui fume"


def match_target_amplitude(aChunk, target_dBFS):
    ''' Normalize given audio chunk '''
    change_in_dBFS = target_dBFS - aChunk.dBFS
    return aChunk.apply_gain(change_in_dBFS)


song = AudioSegment.from_mp3("./Sentence/Portez.mp3")


chunks = split_on_silence(
    # Use the loaded audio.
    song,
    # Specify that a silent chunk must be at least 2 seconds or 2000 ms long.
    min_silence_len=50,
    # Consider a chunk silent if it's quieter than -16 dBFS.
    # (You may want to adjust this parameter.)
    silence_thresh=-16
)

# Process each chunk with your parameters
for i, chunk in enumerate(chunks):
    # Create a silence chunk that's 0.5 seconds (or 500 ms) long for padding.
    silence_chunk = AudioSegment.silent(duration=500)

    # Add the padding chunk to beginning and end of the entire chunk.
    audio_chunk = silence_chunk + chunk + silence_chunk

    # Normalize the entire chunk.
    normalized_chunk = match_target_amplitude(audio_chunk, -20.0)

    # Export the audio chunk with new bitrate.
    print("Exporting " + sentence[i] + ".mp3.".format(i))
    normalized_chunk.export(
        "./Test/" + sentence[i].lower() + "/" + sentence[i] + ".mp3".format(i),
        bitrate="192k",
        format="mp3"
    )
