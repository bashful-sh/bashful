import sys
import os
from transformers import AutoTokenizer, AutoModelForCausalLM

model = None
tokenizer = None


def error_and_exit(error_message: str):
    print(error_message)
    exit()


def respond_and_exit(response_message: str):
    print(response_message)
    exit()


def model_init():
    global model, tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct", trust_remote_code=True
    )
    model = AutoModelForCausalLM.from_pretrained(
        "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
        trust_remote_code=True,
    )


def sanitize_prompt(user_input: str) -> str:
    return f"{user_input.strip()}\n"


def inference(input_text: str) -> str:
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_length=1024)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def sanitize_response(prompt: str, response: str) -> str:
    prompt = f"{prompt}"
    response = response.strip()
    if response.startswith(prompt):
        response = response.split(prompt)
        response = f"{prompt}".join(response[1:])
    response = response.strip()
    response = response if not response.startswith("\n") else response + "\n"
    return response.strip()


if __name__ == "__main__":
    # Initialise model and log the status
    if len(sys.argv) == 2 and sys.argv[1] == "init":
        model_init()
        exit()
    # Inference model and log response only
    if len(sys.argv) > 1:
        # User Input
        raw_prompt = " ".join(sys.argv[1:])
        if len(raw_prompt) == 0:
            error_and_exit("No prompt provided.")
        # Model output
        output_response = ""
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        # Download, initialise and inference model
        try:
            model_init()
            sanitized_prompt = sanitize_prompt(raw_prompt)
            raw_response = inference(sanitized_prompt)
            sanitized_response = sanitize_response(sanitized_prompt, raw_response)
        finally:
            sys.stdout = original_stdout
        # Logs the generated code
        respond_and_exit(sanitized_response)
    # Triggers when an invalid argument set is provided.
    error_and_exit("Unexpected number of arguments provided.")
