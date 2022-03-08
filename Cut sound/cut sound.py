from pydub import AudioSegment
from pydub.silence import split_on_silence
from pynput.keyboard import Key, Listener
import pyaudio
import wave
import os
import time

sentence = []
count = 0
boolean = True
start = time.time()

initial_count = 0
dir = "./Test"

for path in os.listdir(dir):
    if os.path.isfile(os.path.join(dir, path)):
        initial_count += 1

# the file name output you want to record into
filename = str(initial_count) + ".wav"
# set the chunk size of 1024 samples
chunk = 1024
# sample format
FORMAT = pyaudio.paInt16
# mono, change to 2 if you want stereo
channels = 2
# 44100 samples per second
sample_rate = 44100
record_seconds = 0
# initialize PyAudio object
p = pyaudio.PyAudio()


def on_press(key):
    global sentence
    global count
    global record_seconds
    if key == Key.esc:
        record_seconds = time.time() - start
        return False
    else:
        try:
            key_code = key.vk
        except AttributeError:
            key_code = key.value.vk
    sentence.append(str(key_code))
    count += 1


# Collect events until released
with Listener(on_press=on_press) as listener:
    # open stream object as input & output
    stream = p.open(format=FORMAT,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    output=True,
                    frames_per_buffer=chunk)
    frames = []
    print("Recording...")
    listener.join()

print(round(record_seconds))

for i in range(int(sample_rate / chunk * record_seconds)):
    data = stream.read(chunk)
    # if you want to hear your voice while recording
    # stream.write(data)
    frames.append(data)
print("Finished recording.")

# stop and close stream
stream.stop_stream()
stream.close()
# terminate pyaudio object
p.terminate('./Test')
# save audio file
# open the file in 'write bytes' mode
wf = wave.open(filename, "wb")
# set the channels
wf.setnchannels(channels)
# set the sample format
wf.setsampwidth(p.get_sample_size(FORMAT))
# set the sample rate
wf.setframerate(sample_rate)
# write the frames as bytes
wf.writeframes(b"".join(frames))
# close the file
wf.close()

time.sleep(5) 

for i in sentence:
    try:
        os.makedirs('./Keystrokes/' + i)
    except:
        break


def match_target_amplitude(aChunk, target_dBFS):
    ''' Normalize given audio chunk '''
    change_in_dBFS = target_dBFS - aChunk.dBFS
    return aChunk.apply_gain(change_in_dBFS)

song = AudioSegment.from_mp3("./Test/" + str(initial_count) + ".wav")

chunks = split_on_silence(
    # Use the loaded audio.
    song,
    # Specify that a silent chunk must be at least 2 seconds or 2000 ms long.
    min_silence_len = 0,
    # Consider a chunk silent if it's quieter than -16 dBFS.
    # (You may want to adjust this parameter.)
    silence_thresh= -16
)

print(len(chunks))
print(len(sentence))

# Process each chunk with your parameters
# if len(chunks) == len(sentence):
#     for i, chunk in enumerate(chunks):
#         # Create a silence chunk that's 0.5 seconds (or 500 ms) long for padding.
#         silence_chunk = AudioSegment.silent(duration=500)

#         # Add the padding chunk to beginning and end of the entire chunk.
#         audio_chunk = silence_chunk + chunk + silence_chunk

#         # Normalize the entire chunk.
#         normalized_chunk = match_target_amplitude(audio_chunk, -20.0)

#         # Export the audio chunk with new bitrate.
#         print("Exporting " + sentence[i] + ".mp3.".format(i))
#         normalized_chunk.export(
#             "./Test/" + sentence[i].lower() + "/" +
#             sentence[i] + ".mp3".format(i),
#             bitrate="192k",
#             format="mp3"
#         )
