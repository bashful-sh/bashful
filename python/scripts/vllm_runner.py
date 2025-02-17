from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

max_model_len, tp_size = 2048, 1
model_name = "facebook/opt-125m"

# max_model_len, tp_size = 8192, 1
# model_name = "deepseek-ai/deepseek-coder-1.3b-instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name)
llm = LLM(
    model=model_name,
    tensor_parallel_size=tp_size,
    max_model_len=max_model_len,
    trust_remote_code=True,
    enforce_eager=True,
)
sampling_params = SamplingParams(
    temperature=0.3, max_tokens=256, stop_token_ids=[tokenizer.eos_token_id]
)

messages_list = [
    [{"role": "user", "content": "write a quick sort algorithm in python."}],
]

prompt_token_ids = [
    tokenizer.apply_chat_template(messages, add_generation_prompt=True)
    for messages in messages_list
]

outputs = llm.generate(
    prompt_token_ids=prompt_token_ids, sampling_params=sampling_params
)

generated_text = [output.outputs[0].text for output in outputs]
print(generated_text)
