import sys

from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

dsc_1b_id = "deepseek-ai/deepseek-coder-1.3b-instruct"
dsc_6b_id = "deepseek-ai/deepseek-coder-6.7b-instruct"
dsc_7b_id = "deepseek-ai/deepseek-coder-7b-instruct"
dsc_33b_id = "deepseek-ai/deepseek-coder-33b-instruct"
dscv2_id = "deepseek-ai/DeepSeek-Coder-V2-Instruct"
dscv2_lite_id = "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"


def error(error_message: str):
    exit(error_message)


def respond(response_message: str):
    print(response_message)


def sanitize_prompt(user_input: str) -> str:
    return f"{user_input.strip()}\n"


def sanitize_response(prompt: str, response: str) -> str:
    prompt = f"{prompt}"
    response = response.strip()
    if response.startswith(prompt):
        response = response.split(prompt)
        response = f"{prompt}".join(response[1:])
    response = response.strip()
    response = response if not response.startswith("\n") else response + "\n"
    return response.strip()


def generate_response(model_name: str, last_user_input: str):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    llm = LLM(
        model=model_name,
        tensor_parallel_size=1,
        max_model_len=8192,
        trust_remote_code=True,
        enforce_eager=True,
    )
    sampling_params = SamplingParams(
        temperature=0.3, max_tokens=256, stop_token_ids=[tokenizer.eos_token_id]
    )
    messages_list = [
        [{"role": "user", "content": "Who are you?"}],
        [{"role": "user", "content": "write a quick sort algorithm in python."}],
        [{"role": "user", "content": "Write a piece of quicksort code in C++."}],
    ]
    prompt_token_ids = [
        tokenizer.apply_chat_template(messages, add_generation_prompt=True)
        for messages in messages_list
    ]
    outputs = llm.generate(
        prompt_token_ids=prompt_token_ids, sampling_params=sampling_params
    )
    generated_text = [output.outputs[0].text for output in outputs]
    return generated_text


if __name__ == "__main__":
    args = sys.argv[1:]
    model_id = args[0]
    last_user_input = sanitize_prompt(" ".join(args[1:]))

    # Sample prompts.
    prompts = [
        "Hello, my name is",
        "The president of the United States is",
        "The capital of France is",
        "The future of AI is",
    ]

    # Create a sampling params object.
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

    # Create an LLM.
    llm = LLM(model="facebook/opt-125m")

    # Generate texts from the prompts. The output is a list of RequestOutput objects
    # that contain the prompt, generated text, and other information.
    outputs = llm.generate(prompts, sampling_params)

    # Print the outputs.
    for output in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
    exit()

    # Input Handler
    if len(model_id) == 0:
        exit("Please provide a model as the first argument.")
    elif len(last_user_input) == 0:
        exit("Please provide a prompt as the second argument.")

    # Model Selector
    if model_id == "code":
        response = generate_response(dscv2_lite_id, last_user_input)
    else:
        response = generate_response(model_id, last_user_input)

    # Output Response
    sanitized_response = sanitize_response(last_user_input, response)
    print(sanitize_response)
