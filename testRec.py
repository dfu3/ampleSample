import pyaudio
import wave
import subprocess
import sys
import msvcrt
import numpy as np

#uaer pre-config~~~>
print('PLEASE ENTER THE FOLLOWING')
print('|')
title = input('|-->TITLE: ')
artist = input('|-->ARTIST: ')
genre = input('|-->GENRE: ')
duration = input('|-->Duration(sec): ')
print('|')
#<~~~

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = float(duration)
FILENAME = "file.wav"

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
SAMPLE_WIDTH = audio.get_sample_size(FORMAT)
WINDOW = np.blackman(CHUNK)
frames = []

print('\nRECORDING')
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

    #taking freq of sampling~~~>
    # unpack the data and times by the hamming window
    indata = np.array(wave.struct.unpack("%dh" % ((len(data)) / SAMPLE_WIDTH),data)) * (WINDOW)
    # Take the fft and square each value
    fftData = abs(np.fft.rfft(indata)) ** 2
    # find the maximum
    which = fftData[1:].argmax() + 1
    # use quadratic interpolation around the max
    if which != len(fftData) - 1:
        y0, y1, y2 = np.log(fftData[which - 1:which + 2:])
        x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
        # find the frequency and output it
        thefreq = (which + x1) * RATE / CHUNK
        if(thefreq > 80.0 and thefreq < 180.0):
            print("~{} Hz.".format(thefreq))
    else:
        if (thefreq > 80.0 and thefreq < 180.0):
            print("~{} Hz.".format(thefreq))
    #<~~~

    # if(i % 10 == 0):
    #     sys.stdout.write("♫")
    #     sys.stdout.flush()
    # if(i % 30 == 0):
    #     sys.stdout.write('\r')

sys.stdout.write('\rDONE!\n\n')

# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()

waveFile = wave.open(FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()

newFile = title.replace(' ', '_')
cmd = 'ffmpeg  -loglevel quiet -i {} ' \
      '-metadata Title="{}" ' \
      '-metadata Artist="{}" ' \
      '-metadata Genre="{}" ' \
      '-y -codec copy {}.wav'.format(
    FILENAME, title, artist, genre, newFile
)

try:
    subprocess.call(cmd)
    print('SUCCESS!')
except:
    print('FAILED TO INSERT METADATA!')

#display file metadata
cmd = 'ffprobe -loglevel quiet -show_format {}.wav'.format(newFile)
subprocess.call(cmd)

