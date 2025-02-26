import redis
import pickle
import whisper
import argparse
import tempfile

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

model_cache = {}
redis_client = None


def load_model(size="tiny"):
    model = None

    if redis_client is not None:
        try:
            redis_client.ping()
            cached_model = redis_client.get(f"whisper_model:{size}")
            if cached_model:
                model = pickle.loads(cached_model)
            else:
                model = whisper.load_model(size)
                # Redis model cache expires after 1 day (86400 seconds)
                redis_client.set(f"whisper_model:{size}", pickle.dumps(model), ex=86400)
            return model
        except redis.exceptions.ConnectionError as e:
            print(f"Redis connection error: {e}")

    if size not in model_cache:
        model_cache[size] = whisper.load_model(size)

    return model_cache[size]


@app.route("/transcribe", methods=["POST"])
def transcription_api_endpoint():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file part"}), 400

    audio_file = request.files["audio"]

    if audio_file.filename == "":
        return jsonify({"error": "No selected audio file"}), 400

    try:
        model = load_model()
        with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp:
            audio_file.save(temp.name)
            result = model.transcribe(temp.name, language=None)
        return jsonify({"text": result["text"], "language": result["language"]}), 200
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

    if args.use_redis:
        redis_client = redis.Redis(host=args.host, port=args.port, db=0)

    app.run(debug=args.debug, port=args.port)
