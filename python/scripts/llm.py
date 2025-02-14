import os
import sys
import json
import torch

from transformers import AutoTokenizer, AutoModelForCausalLM

# System
home_directory = os.path.expanduser("~")
bashful_directory = os.path.join(home_directory, ".bashful")
bashful_tmp_directory = os.path.join(bashful_directory, ".tmp")
log_file_name = "llm.messages"
log_file_path = os.path.join(bashful_tmp_directory, log_file_name)

# LLM
dsc_1b_id = "deepseek-ai/deepseek-coder-1.3b-instruct"
dsc_6b_id = "deepseek-ai/deepseek-coder-6.7b-instruct"
dsc_7b_id = "deepseek-ai/deepseek-coder-7b-instruct"
dsc_33b_id = "deepseek-ai/deepseek-coder-33b-instruct"
dscv2_id = "deepseek-ai/DeepSeek-Coder-V2-Instruct"
dscv2_lite_id = "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"

# Application
debug = False
model = None
tokenizer = None
messages = []
system_message = {
    "role": "system",
    "content": (
        "You are an AI code generation tool. "
        "The user will describe something and you will begin by thinking about what the user has described, "
        "and if it is possible to code it. "
        "You must at all cost remember to start every message you send with <think> and end your thoughts with </think> and the actual code that will be sent to the user to answer their question, always wrap that code in code blocks like this <code> </code> or markdown compatible syntax."
        "If you decide it is possible to code up, "
        "you will then respond only with the exact code snippet you would apply to the their description. "
        "Do not explain anything. "
        "Do not waste your time speaking to the user. "
        "Just simply only ever reply to them with your code snippet block."
    ),
}


def init_model(model_id: str) -> None:
    """
    Loads the model of a given id into memory
    """
    global model, tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

    def init_with_gpu():
        global model
        model = AutoModelForCausalLM.from_pretrained(
            model_id, trust_remote_code=True, torch_dtype=torch.bfloat16
        ).cuda()

    def init_with_cpu():
        global model
        model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)

    init_with_cpu()


def error_and_exit(error_message: str):
    """
    Log and error and exit
    """
    print(error_message)
    exit()


def log(*args, **kwargs) -> None:
    """
    Log and continue if debugging
    """
    if not debug:
        return
    print(*args, **kwargs)


def sanitize_prompt(user_input: str) -> str:
    """
    Applies some post processing to the users input
    """
    return f"{user_input.strip()}\n"


def single_inference(input_text: str) -> str:
    """
    Runs a single instance inference on the model.
    """
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_length=1024)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def sanitize_response(prompt: str, response: str) -> str:
    """
    Applies some post processing to the models repsonse
    """
    prompt = f"{prompt}"
    response = response.strip()
    if response.startswith(prompt):
        response = response.split(prompt)
        response = f"{prompt}".join(response[1:])
    response = response.strip()
    response = response if not response.startswith("\n") else response + "\n"
    return response.strip()


def append_prompt_to_context(prompt: str, role: str = "user") -> None:
    """
    Adds the users input to the users message log
    """
    messages.append(
        {
            "role": role,
            "content": prompt,
        }
    )


def append_response_to_context(response: str, role: str = "assistant") -> None:
    """
    Adds the models response to the users message log
    """
    messages.append(
        {
            "role": role,
            "content": response,
        }
    )


def run_inference(model_id: str, user_prompt: str) -> None:
    """
    Executes inference of the model associated with the provided model_id
    """
    # Prepare prompt
    init_model(model_id)
    sanitized_prompt = sanitize_prompt(user_prompt)
    append_prompt_to_context(sanitized_prompt)

    # Inference
    inputs = tokenizer.apply_chat_template(
        [system_message] + messages, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)
    outputs = model.generate(
        inputs,
        max_new_tokens=1024,
        do_sample=False,
        top_k=50,
        top_p=0.95,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
    )

    # Process response
    decoded_response = tokenizer.decode(
        outputs[0][len(inputs[0]) :], skip_special_tokens=True
    ).strip()
    sanitized_response = sanitize_response(sanitized_prompt, decoded_response)
    append_response_to_context(sanitized_response)
    return decoded_response


def save_messages() -> None:
    """
    Save the users messages to local storage
    """
    with open(log_file_path, "w") as file:
        to_save = messages[:5]
        json.dump(to_save, file, indent=2)
        log(f"SAVED LAST ({len(to_save)}) MESSAGES:", to_save)


def load_messages() -> list:
    """
    Load the users locally stored message history into context
    """
    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as file:
            return json.load(file)
    return []


def clear_messages() -> None:
    with open(log_file_path, "w") as file:
        json.dump([], file, indent=2)


def extract_code_snippet(input_string):
    """
    Extracts and preserves the content within the first "<code>" and the last "</code>"
    including the tags themselves. Handles missing closing tags.

    Args:
        input_string: The string to process.

    Returns:
        The extracted code snippet (including tags) or the original string if no <code> is found.
        Returns an empty string if closing tag is before opening tag
    """
    start_tag = "<code>"
    end_tag = "</code>"

    start_index = input_string.find(start_tag)

    if start_index == -1:  # No opening tag found
        return input_string

    end_index = input_string.rfind(end_tag)

    if end_index == -1:  # No closing tag found
        return input_string[start_index:]  # Return from opening tag to the end

    if end_index < start_index:  # Closing tag before opening tag
        return ""

    return input_string[
        start_index : end_index + len(end_tag)
    ]  # Return from opening tag to closing tag (inclusive)


def main():
    """
    The main entry point function for executing llm.py from the
    bashful command line.
    """
    global messages
    log("Starting llm instance...")

    # System
    model_id = sys.argv[1]
    user_prompt = sys.argv[2]
    log("Read command line (", model_id, ",", user_prompt, ")\n")

    # Model Aliases
    if model_id == "clear":
        clear_messages()
        exit()
    elif model_id == "code":
        model_id = dscv2_lite_id
    elif len(model_id) == "":
        error_and_exit("Provide a `model_id` as the first argument.")
    log("MODEL ID:", model_id)

    # Input Handler
    if user_prompt == "init":
        exit(init_model(model_id))
    if len(user_prompt) == 0:
        error_and_exit("Provide a `prompt` as the second argument.")
    log("USER PROMPT:", user_prompt)

    # Preprocess Context
    messages = load_messages()
    log("MESSAGE LOG:", messages, "\n")

    # Inference Handler
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, "w")
    try:
        out = run_inference(model_id, user_prompt)
        out = extract_code_snippet(out)
    except Exception as exception:
        out = str(exception)
    sys.stdout = original_stdout

    # Output Handler
    if out.startswith("<code>"):
        out = out[6:]
    if out.endswith("</code>"):
        out = out[:-7]
    print(out.strip())

    # Postprocess Context
    save_messages()
    log("\nMESSAGE LOG:", messages)


if __name__ == "__main__":
    main()
