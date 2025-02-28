"""
LLM: Model Container
"""


class LLMContainer:
    model: str
    device: str

    def __init__(self, *args, **kwargs) -> None:
        self.model = "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"
        self.device = "CPU"
