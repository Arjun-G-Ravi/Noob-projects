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
rms_threshold = 500  # Adjust this value based on your environment

# Global variables
audio_queue = queue.Queue()
buffer = np.array([], dtype=dtype)
running_transcript = ""

def clean_up_using_llama(input_text, model="llama3-70b-8192"):
    if isinstance(input_text, str):
        messages = [
            {"role": "system", "content": "Given a string, you have to clean the string up, by changing as less as possible. Do not answer anything else."},
            {"role": "user", "content": input_text}
        ]
    else:
        messages = input_text
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
    )
    
    return response.choices[0].message.content

def calculate_rms(audio_data):
    """
    Calculate the Root Mean Square (RMS) of the audio data.
    """
    audio_data = audio_data.astype(np.float32)
    return np.sqrt(np.mean(audio_data**2))

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
            model="whisper-large-v3",
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
            rms = calculate_rms(audio_chunk)
            if rms > rms_threshold:
                transcription = transcribe_audio(audio_chunk)
                if transcription.strip():
                    running_transcript += " " + transcription.strip()
                    print(f"{transcription.strip()} ")
            else:
                # print(f"Skipping transcription: RMS={rms:.2f} (below threshold {rms_threshold})")
                pass
        except queue.Empty:
            print("No speech detected for 10 seconds.")
        except Exception as e:
            print(f"Error processing audio: {e}")

def main():
    # Start audio processing in a separate thread
    processing_thread = threading.Thread(target=process_audio, daemon=True)
    processing_thread.start()
    
    # Start recording in the main thread
    # print(clean_up_using_llama('hi'))
    record_audio()
    print('\nCleaned up result:')
    print(clean_up_using_llama(running_transcript))

if __name__ == "__main__":
    main()