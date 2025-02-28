"""
Transcribes speech from an audio file or microphone input using Google Cloud Speech-to-Text.
Initialize this application and connect to a google cloud account using:

gcloud init
gcloud auth application-default login
"""

import wave
import argparse
import sounddevice as sd

from google.cloud import speech_v1p1beta1 as speech


def record_audio(duration=5, samplerate=16000):
    """Records audio from the microphone."""
    print(f"Recording audio for {duration} seconds...")
    recording = sd.rec(
        int(duration * samplerate), samplerate=samplerate, channels=1, dtype="int16"
    )
    sd.wait()  # Wait until recording is finished
    print("Recording finished.")
    return recording, samplerate


def transcribe_audio(audio_data, samplerate, language_code="en-GB"):
    """Transcribes audio using Google Cloud Speech-to-Text."""
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(content=audio_data)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=samplerate,
        language_code=language_code,
    )

    response = client.recognize(config=config, audio=audio)

    transcription = ""
    for result in response.results:
        transcription += result.alternatives[0].transcript + " "

    return transcription.strip()


def save_wav(audio_data, samplerate, filename):
    """Saves audio data to a WAV file."""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit samples
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())
    print(f"Audio saved to {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        default="",
        help="Path to audio file (WAV). If not provided, records from microphone.",
    )
    parser.add_argument(
        "--language",
        "-l",
        type=str,
        default="en-GB",
        help="Language code for transcription.",
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=int,
        default=5,
        help="Recording duration (seconds) if recording from microphone.",
    )
    parser.add_argument(
        "--save",
        "-s",
        type=str,
        default="",
        help="Path to save recorded audio file to.",
    )
    args = parser.parse_args()

    if args.file:
        # Transcribe from file
        with open(args.file, "rb") as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)
        sample_rate = wave.open(args.file, "r").getframerate()
        transcription = transcribe_audio(content, sample_rate, args.language)

    else:
        # Record from microphone
        recording, samplerate = record_audio(args.duration)
        transcription = transcribe_audio(recording.tobytes(), samplerate, args.language)
        if args.save:
            save_wav(recording, samplerate, args.save)

    print("Transcription:", transcription)
