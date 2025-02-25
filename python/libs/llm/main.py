import argparse
import requests

from flask import Flask, request, jsonify
from flask_cors import CORS

ollama_host = "http://127.0.0.1"
ollama_port = 11434
app = Flask(__name__)
CORS(app)


def prompt(text: str):
    response = requests.post(
        f"{ollama_host}:{ollama_port}/api/generate",
        json={
            "model": "dexter:0.5b",
            "prompt": text,
            "stream": False,
        },
    )
    response.raise_for_status()
    ollama_response = response.json()
    return ollama_response["response"]


@app.route("/prompt", methods=["POST"])
def prompt_api_endpoint():
    request_data = request.get_json()
    user_prompt = request_data.get("prompt", "")
    try:
        llm_response = prompt(user_prompt)
        return jsonify({"response": llm_response}), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error communicating with Ollama server: {e}"}), 500
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid request data: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=9501,
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
        "--prompt", "-t", type=str, default="", help="Inference the llm directly."
    )
    args = parser.parse_args()
    if len(args.prompt) == 0:
        app.run(debug=args.debug, port=args.port)
    else:
        r = prompt(args.prompt)
        print(r)
