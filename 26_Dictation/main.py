import numpy as np
import sounddevice as sd
import queue
import threading
import time
import wave
from io import BytesIO
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client (replace with your API key)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# Audio settings
sample_rate = 16000  # Hz
channels = 1
dtype = 'int16'
chunk_seconds = 3.0  # Smaller chunks for pseudo-streaming
frames_per_chunk = int(sample_rate * chunk_seconds)

# Global variables
audio_queue = queue.Queue()
buffer = np.array([], dtype=dtype)
running_transcript = ""

def record_audio():
    global buffer
    
    def callback(indata, frame_count, time_info, status):
        global buffer
        if status:
            print(f"Status: {status}")
        
        buffer = np.append(buffer, indata[:, 0])
        
        while len(buffer) >= frames_per_chunk:
            chunk = buffer[:frames_per_chunk]
            buffer = buffer[frames_per_chunk:]
            audio_queue.put(chunk)
    
    try:
        with sd.InputStream(callback=callback, channels=channels, samplerate=sample_rate, dtype=dtype):
            print("Recording started... (Press Ctrl+C to stop)")
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nRecording stopped.")
    except Exception as e:
        print(f"Error in recording: {e}")

def transcribe_audio(audio_data):
    audio_file = BytesIO()
    with wave.open(audio_file, 'wb') as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)  # 2 bytes for 'int16'
        wav.setframerate(sample_rate)
        wav.writeframes(audio_data.tobytes())
    audio_file.seek(0)
    audio_file.name = "audio.wav"
    try:
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3-turbo",
            language="en",
            temperature=0.0
        )
        return transcription.text
    except Exception as e:
        print(f"Error during transcription: {e}")
        return ""

def process_audio():
    global running_transcript
    while True:
        try:
            audio_chunk = audio_queue.get(timeout=10)
            transcription = transcribe_audio(audio_chunk)
            if transcription.strip():
                running_transcript += " " + transcription.strip()
                print(f"Current transcript: {running_transcript}")
        except queue.Empty:
            print("No speech detected for 10 seconds.")
        except Exception as e:
            print(f"Error processing audio: {e}")

def main():
    # Start audio processing in a separate thread
    processing_thread = threading.Thread(target=process_audio, daemon=True)
    processing_thread.start()
    
    # Start recording in the main thread
    record_audio()

if __name__ == "__main__":
    main()