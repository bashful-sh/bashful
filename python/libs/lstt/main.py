import whisper
import tempfile

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file part"}), 400

    audio_file = request.files["audio"]

    if audio_file.filename == "":
        return jsonify({"error": "No selected audio file"}), 400

    try:
        # Load the Whisper model (use a smaller model for faster results)
        model = whisper.load_model("base")  # or "small", "medium", "large"

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp:
            audio_file.save(temp.name)

            # Use Whisper to transcribe and detect language
            result = model.transcribe(temp.name, language=None)  # Auto-detect language

        # Return the transcription and detected language
        return jsonify({"text": result["text"], "language": result["language"]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
