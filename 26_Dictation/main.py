import sounddevice as sd
import numpy as np
import threading
import queue
import time
import os
import tempfile
import wave
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Audio parameters
sample_rate = 16000
channels = 1  # Adjust to 2 if your microphone is stereo
dtype = 'int16'
chunk_seconds = 5
frames_per_chunk = int(sample_rate * chunk_seconds)
buffer = np.array([], dtype=dtype)

# Queue for audio chunks
audio_queue = queue.Queue()

# Function to capture audio with buffering
def record_audio():
    global buffer
    
    def callback(indata, frame_count, time_info, status):
        global buffer
        if status:
            print(f"Status: {status}")
        
        # Debugging: Print max absolute value and RMS of incoming audio
        max_val = np.max(np.abs(indata[:, 0]))
        rms_indata = np.sqrt(np.mean(indata[:, 0].astype(np.float32)**2))
        # print(f"Max abs value: {max_val}, RMS of indata: {rms_indata:.2f}")
        
        # Append new data to buffer (mono input)
        buffer = np.append(buffer, indata[:, 0])
        
        # Process chunks when enough data is collected
        if len(buffer) >= frames_per_chunk:
            chunk = buffer[:frames_per_chunk]
            buffer = buffer[frames_per_chunk:]
            
            # Compute RMS with float32 to ensure accuracy
            rms = np.sqrt(np.mean(chunk.astype(np.float32)**2))
            print(f"Chunk RMS: {rms:.2f}")
            
            # Temporarily process every chunk for debugging
            audio_queue.put(chunk)
            # Uncomment and adjust threshold after determining typical RMS values
            # if rms > 500:
            #     print(f"Detected audio: RMS={rms:.2f}")
            #     audio_queue.put(chunk)
            # else:
            #     print("Silence detected.")
    
    try:
        with sd.InputStream(callback=callback, channels=channels, samplerate=sample_rate, dtype=dtype):
            print("Recording started... (Press Ctrl+C to stop)")
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nRecording stopped.")
    except Exception as e:
        print(f"Error in recording: {e}")

# Function to save numpy array to a temporary WAV file
def save_temp_wav(audio_data, sample_rate, channels):
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    temp_file_path = temp_file.name
    temp_file.close()
    
    with wave.open(temp_file_path, 'wb') as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)  # 2 bytes for 'int16'
        wav.setframerate(sample_rate)
        wav.writeframes(audio_data.tobytes())
    
    file_size = os.path.getsize(temp_file_path)
    print(f"Saved audio to: {temp_file_path} (size: {file_size} bytes)")
    return temp_file_path

# Function to transcribe audio using Groq's Whisper API
def transcribe_audio(audio_data):
    temp_file_path = save_temp_wav(audio_data, sample_rate, channels)
    try:
        with open(temp_file_path, 'rb') as audio_file:
            print("Sending audio to Groq API...")
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
    # File is not deleted for debugging; remove this block after verification
    # finally:
    #     if temp_file_path and os.path.exists(temp_file_path):
    #         os.unlink(temp_file_path)

# Function to process audio and get transcription
def process_audio():
    while True:
        try:
            audio_chunk = audio_queue.get(timeout=10)
            print(f"Processing chunk of length {len(audio_chunk)}...")
            transcription = transcribe_audio(audio_chunk)
            if transcription:
                print(f"Transcription: {transcription}")
            else:
                print("No transcription received.")
        except queue.Empty:
            print("No speech detected for 10 seconds.")
        except Exception as e:
            print(f"Error processing audio: {e}")

def main():
    record_thread = threading.Thread(target=record_audio)
    record_thread.daemon = True
    record_thread.start()
    
    process_thread = threading.Thread(target=process_audio)
    process_thread.daemon = True
    process_thread.start()
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting program.")

if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY not found in .env file")
        exit(1)
    
    print("Speech-to-Text Dictation Program with Whisper")
    print("============================================")
    print("Speak clearly into your microphone.")
    print("Your speech will be transcribed in chunks.")
    print("Press Ctrl+C to stop recording and exit.")
    
    main()