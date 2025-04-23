import sounddevice as sd
import numpy as np
import threading
import queue
import time
import os
import io
import wave
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Audio parameters
sample_rate = 16000
channels = 1
dtype = 'int16'
chunk_duration = 3  # seconds per audio chunk

# Queue for audio chunks
audio_queue = queue.Queue()

# Function to capture audio
def record_audio():
    def callback(indata, frames, time, status):
        if status:
            print(f"Status: {status}")
        audio_queue.put(indata.copy())
        
    with sd.InputStream(samplerate=sample_rate, channels=channels, dtype=dtype, callback=callback):
        print("Recording started... (Press Ctrl+C to stop)")
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nRecording stopped.")

# Function to convert numpy array to WAV file-like object
def numpy_to_wav_file(audio_data, sample_rate, channels):
    wav_file = io.BytesIO()
    with wave.open(wav_file, 'wb') as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)  # 2 bytes for 'int16'
        wav.setframerate(sample_rate)
        wav.writeframes(audio_data.tobytes())
    wav_file.seek(0)  # Rewind the file
    return wav_file

# Function to transcribe audio using Groq's Whisper API
def transcribe_audio(audio_data):
    try:
        # Convert numpy array to WAV file-like object
        wav_file = numpy_to_wav_file(audio_data, sample_rate, channels)
        
        # Use the Groq client to transcribe the audio
        transcription = client.audio.transcriptions.create(
            file=wav_file,
            model="whisper-large-v3-turbo",
            language="en",
            temperature=0.0
        )
        
        return transcription.text
    except Exception as e:
        print(f"Error during transcription: {e}")
        return ""

# Function to process audio and get transcription
def process_audio():
    while True:
        try:
            audio_chunk = audio_queue.get(timeout=5)
            
            # Check if there is actual audio content (not just silence)
            if np.abs(audio_chunk).mean() > 0.01:  # Simple threshold check
                print("\nProcessing speech...", end="", flush=True)
                transcription = transcribe_audio(audio_chunk)
                
                if transcription:
                    print(f"\r{transcription}")
                else:
                    print("\rNo speech detected or error in transcription.")
            
        except queue.Empty:
            # No new audio for 5 seconds
            pass
        except Exception as e:
            print(f"Error processing audio: {e}")

def main():
    # Start recording thread
    record_thread = threading.Thread(target=record_audio)
    record_thread.daemon = True
    record_thread.start()
    
    # Start processing thread
    process_thread = threading.Thread(target=process_audio)
    process_thread.daemon = True
    process_thread.start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting program.")

if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY not found in .env file")
        print("Make sure you have a .env file with GROQ_API_KEY='your-api-key'")
        exit(1)
    
    print("Speech-to-Text Dictation Program with Whisper")
    print("============================================")
    print("Speak clearly into your microphone.")
    print("Your speech will be transcribed in chunks.")
    print("Press Ctrl+C to stop recording and exit.")
    
    main()