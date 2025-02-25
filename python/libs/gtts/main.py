"""
Synthesizes speech from the input string of text.
Initialize this application and connect to a google cloud account using:

gcloud init
gcloud auth application-default login
"""

import argparse
import numpy as np
import sounddevice as sd

from google.cloud import texttospeech

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--list_voices",
        "-lv",
        type=bool,
        default=False,
        help="list all available voices.",
    )
    parser.add_argument(
        "--text",
        "-t",
        type=str,
        default="Hello World!",
        help="Text to synthesize.",
    )
    parser.add_argument(
        "--language",
        "-l",
        type=str,
        default="en-GB",
        help="Selected language option to use.",
    )
    parser.add_argument(
        "--voice",
        "-v",
        type=str,
        default="en-GB-Chirp-HD-D",
        help="Selected voice option to use.",
    )
    parser.add_argument(
        "--save",
        "-s",
        type=str,
        default="",
        help="Path to save audio file to.",
    )
    parser.add_argument(
        "--print",
        "-p",
        type=bool,
        default=False,
        help="Weather or not to print the audio data.",
    )
    args = parser.parse_args()

    # Init Google Cloud TTS Client
    tts_client = texttospeech.TextToSpeechClient()

    # List & Exit
    if args.list_voices:
        tts_client.list_voices()
        exit()

    # Run TTS /w Google Cloud
    input_text = texttospeech.SynthesisInput(text=args.text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=args.language,
        name=args.voice,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16, speaking_rate=1
    )
    response = tts_client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )
    audio_data = np.frombuffer(response.audio_content, dtype=np.int16)

    # Save or Play Audio Data
    if args.print:
        print(response.audio_content)
    elif len(args.save) > 0:
        with open(args.save, "wb") as out:
            out.write(response.audio_content)
            print(f'Audio content written to file "{args.save}"')
    else:
        try:
            sd.play(audio_data, samplerate=24000)
            sd.wait()
        except sd.PortAudioError as e:
            print(f"Error playing audio: {e}")
