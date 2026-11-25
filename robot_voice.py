# Author: Sarang R Sakhare
# Date: 24 Noveber 2026
# Description: Records the voice, convert into text string and stores it in list, then again convert text to speechand repeats the sentence in robot voice 

import numpy as np, sounddevice as sd
from faster_whisper import WhisperModel
from piper import PiperVoice

THRESHOLD = 0.02   # mic sensitivity (lower = more sensitive)
PAUSE = 25         # silence that ends a sentence, in 32 ms chunks (25 = 0.8 s)
ROBOT_HZ = 30      # robot buzz: 30 = deep, 120 = buzzy

whisper = WhisperModel("models/whisper-small.en", device="cpu", compute_type="int8", cpu_threads=6)
voice = PiperVoice.load("models/piper/en_US-ryan-medium.onnx")
RATE = voice.config.sample_rate


def listen(mic):                               # Wait until you talk, record until you pause, return the sound

    sound, quiet, talking = [], 0, False                             # 'sound' list stores the chunks recorded so far, ' quiet' counts how many quiet chunks in a row we have just seen, 'talking'  becomes True at the first loud chunk and stays True
   
    while not talking or quiet < PAUSE:
        chunk = mic.read(512)[0][:, 0]                                    # takes 512 samples from microphone. [:, 0] data is of shape (512, 1): 512 rows (one per sample) and 1 column.
        
        sound.append(chunk)
        if np.abs(chunk).mean() > THRESHOLD / (2 if talking else 1):     # loud? (quieter is ok once you started)
            talking, quiet = True, 0
        else:
            quiet += 1
        
        if not talking:
            sound = sound[-6:]                                            # not started yet: keep only the last 0.2 s
   
    if len(sound) - quiet < 10:                                           # under 0.3 s = a click, not a word
        return listen(mic)
    
    sound = np.concatenate(sound)
    return sound / max(np.abs(sound).max(), 0.01) * 0.9                   # normalise volume for whisper


with sd.InputStream(samplerate=16000, channels=1, blocksize=512, dtype="float32") as mic:       # mic stream is opened at 16000 samples per second, so 512 samples = 512 / 16000 = 0.032 s of sound is stored
    while True:
        sound = listen(mic)
        try:
            segments, _ = whisper.transcribe(sound, language="en", beam_size=1)
            text = " ".join(s.text for s in segments).strip()
        except RuntimeError:                                          # Skip if memory of PC is full
            print("out of memory - sentence skipped")
            continue
        if text:
            print("You said:", text)
            robot = np.concatenate([c.audio_float_array for c in voice.synthesize(text)])
            robot *= 0.6 + 0.4 * np.sin(2 * np.pi * ROBOT_HZ * np.arange(len(robot)) / RATE)       # robot buzz
            sd.play(np.append(robot, np.zeros(RATE // 4)).astype(np.float32), RATE, blocking=True)  # + 0.25 s tail
        mic.read(mic.read_available)                                  # drop what the mic heard while the robot talked



