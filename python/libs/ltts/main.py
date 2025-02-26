"""
Synthesizes speech from the input string of text.
Initialize this application before running and connect to a google cloud account using:

gcloud init
gcloud auth application-default login
"""

import argparse

from google.cloud import texttospeech
from flask_cors import CORS
from flask import Flask, request, jsonify, Response

tts_client = texttospeech.TextToSpeechClient()
app = Flask(__name__)
CORS(app)


def tts(text: str, language: str = "en-GB", voice: str = "en-GB-Chirp-HD-D"):
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language,
        name=voice,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16, speaking_rate=1
    )
    response = tts_client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )
    return response.audio_content


@app.route("/tts", methods=["POST"])
def tts_api_endpoint():
    try:
        request_data = request.get_json()
        if not request_data or "text" not in request_data:
            return jsonify({"error": "Invalid request data"}), 400
        text = request_data["text"]
        audio_data = tts(text)
        return Response(audio_data, mimetype="audio/l16")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=9502,
        help="Which port to run the server on.",
    )
    parser.add_argument(
        "--debug",
        "-d",
        type=bool,
        default=True,
        help="Which mode to run the server in.",
    )
    args = parser.parse_args()
    app.run(debug=args.debug, host="127.0.0.1", port=args.port)
