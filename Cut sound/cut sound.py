from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub.playback import play
from pynput.keyboard import Key, Listener
import pyaudio
import wave
import os
import time

sentence = []
periods = []
chunks = []
count = 0
start = time.time()

# the file name output you want to record into
filename = "record_keyboard.wav"
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
    global periods
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
    periods.append([(time.time() - start) * 1000])
    count += 1

def on_release(key):
    global periods
    periods[count - 1].append((time.time() - start) * 1000)


# Collect events until released
with Listener(on_press=on_press, on_release=on_release) as listener:
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
p.terminate()
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

print(sentence)
for i in sentence:
    print(i)
    try:
        os.makedirs('./Keystrokes/' + i)
    except Exception as e:
        print('Error')
        print(e.__class__)

song = AudioSegment.from_wav("./record_keyboard.wav")

print(periods)
for i, value in enumerate(periods):
    try:
        chunks.append(song[value[0]:value[1]])
    except:
        print(periods[i])
        print(periods[i + 1])
        chunks.append(song[value[0]:periods[i + 1][0]])
        periods[i + 1].pop(0)
        print(periods[i + 1])

def match_target_amplitude(aChunk, target_dBFS):
    ''' Normalize given audio chunk '''
    change_in_dBFS = target_dBFS - aChunk.dBFS
    return aChunk.apply_gain(change_in_dBFS)

# Process each chunk with your parameters
if len(chunks) == len(sentence):
    for i, chunk in enumerate(chunks):
        # Create a silence chunk that's 0.5 seconds (or 500 ms) long for padding.
        silence_chunk = AudioSegment.silent(duration=500)

        # Add the padding chunk to beginning and end of the entire chunk.
        audio_chunk = silence_chunk + chunk + silence_chunk

        # Normalize the entire chunk.
        normalized_chunk = match_target_amplitude(audio_chunk, -20.0)

        nbOfFiles = 0
        dir = './Keystrokes/' + str(sentence[i])
        # Export the audio chunk with new bitrate.
        # print("Exporting " + sentence[i] + ".mp3.".format(i))
        for path in os.listdir(dir):
            if os.path.isfile(os.path.join(dir, path)):
                nbOfFiles += 1

        normalized_chunk.export(
            "./Keystrokes/" + sentence[i] + "/" +
            str(nbOfFiles + 1) + ".mp3".format(i),
            bitrate="192k",
            format="mp3"
        )
