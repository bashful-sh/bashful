import argparse
import requests

from ollama import chat, ChatResponse
from flask import Flask, request, jsonify
from flask_cors import CORS

debug = False
local_api = "http://127.0.0.1:11434/api/generate"
production_api = "https://api.easter.company/llm"

app = Flask(__name__)
CORS(app)


def prompt(text: str, model: str = "dexter-0.5b"):
    response: ChatResponse = chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": text,
            },
        ],
    )
    return response.message.content


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
        debug = args.debug
        app.run(debug=args.debug, host="127.0.0.1", port=args.port)
    else:
        r = prompt(args.prompt)
        print(r)
