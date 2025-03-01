import redis
import pickle
import whisper
import argparse
import tempfile
import requests

from google.cloud import texttospeech
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

tts_client = texttospeech.TextToSpeechClient()
model_cache = {}
redis_client = None


def tts(text: str, language: str = "en-GB", voice: str = "en-GB-Chirp-HD-D") -> bytes:
    """
    Generates a voice from text using google clouds text-to-speech engine.

    Args:
        text: the speech to generate.
        language: the target language of the spoken voice.
        voice: the specific voice model to use.

    Returns:
        LINEAR16 Audio Bytes
    """
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


def load_chat_model(model: str = "dexter-0.5b") -> requests.Response:
    """
    Sends a message to the model server to load and cache the target model.

    Args:
        model: the name of the chat model to load.

    Return:
        None
    """
    return requests.post(
        "http://localhost:11434/api/chat",
        headers={"Content-Type": "application/json"},
        json={
            "model": model,
            "keep_alive": (86400 * 7),
        },
    )


def generate_chat_response(chat_history: list, model: str = "dexter-0.5b") -> str:
    """
    Generates a chat response from the Ollama server.

    Args:
      model: The name of the chat model on the model server.
      chat_history: A list of dictionaries representing the chat history.
                     Each dictionary should have "role" and "content" keys.

    Returns:
      The generated text response from the model, or an error message if there was an error.
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            headers={"Content-Type": "application/json"},
            json={
                "model": model,
                "messages": chat_history,
                "stream": False,
            },
        )

        response.raise_for_status()
        response_json = response.json()
        response_message = response_json["message"]
        response_message_content = response_message["content"]
        return str(response_message_content)

    except requests.exceptions.RequestException as e:
        return f"Error: {e}"


def load_stt_model(size: str = "tiny.en") -> whisper.model:
    """
    Handles the loading, caching, and invalidation of the speech-to-text model.

    Args:
        size: the name (and size) of the model to load.

    Return:
        the cached or newly loaded model.
    """
    model = None

    if redis_client is not None:
        try:
            redis_client.ping()
            cached_model = redis_client.get(f"stt_model:{size}")

            if cached_model:
                model = pickle.loads(cached_model)
            else:
                model = whisper.load_model(size)
                redis_client.set(
                    f"stt_model:{size}",
                    pickle.dumps(model),
                    ex=(86400 * 7),
                )
            return model

        except redis.exceptions.ConnectionError as e:
            print(f"Redis connection error: {e}")

    if size not in model_cache:
        model_cache[size] = whisper.load_model(size)

    return model_cache[size]


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


@app.route("/llm", methods=["POST"])
def prompt_api_endpoint():
    request_data = request.get_json()
    session_data = request_data.get("session", "")

    try:
        llm_response = generate_chat_response(chat_history=session_data["history"])
        return jsonify({"response": llm_response}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error communicating with Ollama server: {e}"}), 500

    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid request data: {e}"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/stt", methods=["POST"])
def transcription_api_endpoint():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file part"}), 400

    audio_file = request.files["audio"]
    if audio_file.filename == "":
        return jsonify({"error": "No selected audio file"}), 400

    try:
        model = load_stt_model()
        with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp:
            audio_file.save(temp.name)
            result = model.transcribe(temp.name, language=None)

        return jsonify(
            {"text": result["text"].strip(), "language": result["language"].strip()}
        ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=9500,
        help="Which port to run the server on.",
    )
    parser.add_argument(
        "--debug",
        "-d",
        type=bool,
        default=True,
        help="Which mode to run the server in.",
    )
    parser.add_argument(
        "--chat", "-c", type=str, default="", help="Inference the llm directly."
    )
    parser.add_argument(
        "--use_redis",
        "-r",
        type=bool,
        default=False,
        help="Which caching mechanism to use.",
    )
    parser.add_argument(
        "--redis_host",
        type=str,
        default="localhost",
        help="Redis host parameter.",
    )
    parser.add_argument(
        "--redis_port",
        type=int,
        default=6379,
        help="Redis port parameter.",
    )
    args = parser.parse_args()

    if args.use_redis or not args.debug:
        redis_client = redis.Redis(host=args.redis_host, port=args.redis_port, db=0)

    if len(args.chat) == 0:
        app.run(debug=args.debug, host="127.0.0.1", port=args.port)

    else:
        r = generate_chat_response([{"role": "user", "content": args.prompt}])
        print(r)
