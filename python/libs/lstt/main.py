import whisper
import tempfile

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/transcribe", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file part"}), 400

    audio_file = request.files["audio"]

    if audio_file.filename == "":
        return jsonify({"error": "No selected audio file"}), 400

    try:
        model = whisper.load_model("base")  # or "small", "medium", "large"

        with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp:
            audio_file.save(temp.name)
            result = model.transcribe(temp.name, language=None)  # Auto-detect language

        return jsonify({"text": result["text"], "language": result["language"]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=9500)
