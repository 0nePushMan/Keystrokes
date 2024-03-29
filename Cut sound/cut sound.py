from cgitb import text
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub.playback import play
from pynput.keyboard import Key, Listener
import pyaudio
import wave
import os
import time
import shutil

folders = ['Keystrokes', 'Keyboard_sound', 'Keyboard_text', 'Keyboard_timestamps']
sentence = []
periods = []
chunks = []
count = 0
start = time.time()


for i in folders:
    try:
        os.makedirs('./' + i)
    except Exception as e:
        print(e)

keyboard_sound = 0
soundDir = './Keyboard_sound'
for path in os.listdir(soundDir):
    if os.path.isfile(os.path.join(soundDir, path)):
        keyboard_sound += 1

keyboard_text = 0
textDir = './Keyboard_text'
for path in os.listdir(textDir):
    if os.path.isfile(os.path.join(textDir, path)):
        keyboard_text += 1

keyboard_timestamp = 0
timeDir = './Keyboard_text'
for path in os.listdir(timeDir):
    if os.path.isfile(os.path.join(timeDir, path)):
        keyboard_timestamp += 1

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

# Add key code to sentence list, add timestamp to periods list when key is pressed to create a pair [pressed, released]
# Add seconds to record_seconds to get the audio integrality of the key pressed
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

# Add a timestamp to periods list when key is released to create a pair [pressed, released]
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

# Save text to Keyboard_text folder
textToSave = ' '.join(sentence)
with open('./Keyboard_text/' + str(keyboard_text) + '.txt', 'w') as f:
    f.write(textToSave)

# Save text to Keyboard_timestamps folder
for i, val in enumerate(periods):
    if len(val) == 1:
        periods[i].append(periods[i + 1][0])
        periods[i +1].pop(0)
timeToSave = ''.join(str(periods))
with open('./Keyboard_timestamps/' + str(keyboard_timestamp) + '.txt', 'w') as f:
    f.write(timeToSave)

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

# Move record_keyboard to Keyboard folder and increment
shutil.move('./record_keyboard.wav', './Keyboard_sound/' + str(keyboard_sound) + '.wav')

# Create a folder for each key pressed and released
for i in sentence:
    try:
        os.makedirs('./Keystrokes/' + i)
    except Exception as e:
        continue

song = AudioSegment.from_wav("./Keyboard_sound/" + str(keyboard_sound) + ".wav")

# Slice the audio with the timestamp of key pressed/released
for i, value in enumerate(periods):
    try:
        chunks.append(song[value[0] - 50:value[1] + 50])
    except:
        chunks.append(song[value[0] - 50:periods[i + 1][0] + 50])
        periods[i + 1].pop(0)

# def match_target_amplitude(aChunk, target_dBFS):
#     ''' Normalize given audio chunk '''
#     change_in_dBFS = target_dBFS - aChunk.dBFS
#     return aChunk.apply_gain(change_in_dBFS)

# Process each chunk with your parameters
if len(chunks) == len(sentence):
    for i, chunk in enumerate(chunks):
        # Create a silence chunk that's 0.5 seconds (or 500 ms) long for padding.
        silence_chunk = AudioSegment.silent(duration=500)

        # Add the padding chunk to beginning and end of the entire chunk.
        audio_chunk = silence_chunk + chunk + silence_chunk

        # # Normalize the entire chunk.
        # normalized_chunk = match_target_amplitude(audio_chunk, -20.0)

        # Increment number of file depending on how much files is present in key code folder
        nbOfFiles = 0
        dir = './Keystrokes/' + str(sentence[i])
        for path in os.listdir(dir):
            if os.path.isfile(os.path.join(dir, path)):
                nbOfFiles += 1

        # Export the audio chunk with new bitrate.
        # print("Exporting " + sentence[i] + ".mp3.".format(i))
        audio_chunk.export(
            "./Keystrokes/" + sentence[i] + "/" +
            str(nbOfFiles + 1) + ".wav".format(i),
            format="wav"
        )
