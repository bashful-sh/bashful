import argparse
import requests

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)


def generate_chat_response(chat_history, model="dexter-0.5b") -> str:
    """
    Generates a chat response from the Ollama server.

    Args:
      model: The name of the chat model on the Ollama server.
      chat_history: A list of dictionaries representing the chat history.
                     Each dictionary should have "role" and "content" keys.

    Returns:
      The generated text response from the model, or None if there was an error.
    """
    try:
        print("\n\n", chat_history, "\n\n")
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
        print("\n\n", response_message, "\n\n")
        return str(response_message_content)
    except requests.exceptions.RequestException as e:
        print(f"Error generating chat response: {e}")
        return str(e)


@app.route("/llm", methods=["POST"])
@cross_origin()
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
        app.run(debug=args.debug, host="127.0.0.1", port=args.port)
    else:
        r = generate_chat_response([{"role": "user", "content": args.prompt}])
        print(r)
