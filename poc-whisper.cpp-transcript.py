import time

import sounddevice as sd
import numpy as np
import requests
import io
from scipy.io import wavfile

# --- CONFIGURATION ---
SERVER_URL = "http://192.168.0.5:8888/inference"  # Note: whisper.cpp usually uses /inference
SAMPLE_RATE = 16000  # Whisper works best at 16kHz
CHANNELS = 1  # Mono audio
DURATION = 10  # Seconds of audio to capture per chunk


# ---------------------

def record_and_transcribe():
    session = requests.Session()

    print(f"Listening... (Capturing {DURATION}s chunks)")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            print(".")
            # 1. Record audio from the microphone
            # We record into a numpy array
            audio_data = sd.rec(int(DURATION * SAMPLE_RATE),
                                samplerate=SAMPLE_RATE,
                                channels=CHANNELS,
                                dtype='float32')
            sd.wait()  # Wait until recording is finished

            # 2. Convert numpy array to WAV format in memory
            # whisper.cpp expects a valid audio file (wav)
            byte_io = io.BytesIO()
            # Convert float32 to int16 (standard wav format)
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wavfile.write(byte_io, SAMPLE_RATE, audio_int16)
            byte_io.seek(0)

            # 3. Send to the whisper.cpp server
            start = time.time()
            try:
                # whisper.cpp server expects the file in a 'file' field (multipart/form-data)
                files = {'file': ('audio.wav', byte_io, 'audio/wav')}
                response = session.post(SERVER_URL, files=files)

                if response.status_code == 200:
                    text = response.text.strip()
                    if text:
                        print(f"Transcription: {text}: {time.time() - start}")
                else:
                    print(f"Error: Server returned status {response.status_code}")
                    print(response.text)

            except requests.exceptions.ConnectionError:
                print("Error: Could not connect to the server. Check the IP address.")
                break
            except Exception as e:
                print(f"An error occurred: {e}")

    except KeyboardInterrupt:
        print("\nStopped by user.")


if __name__ == "__main__":
    record_and_transcribe()
