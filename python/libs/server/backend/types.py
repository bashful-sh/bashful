from enum import Enum
from typing import List


class BackendType(Enum):
    """
    Represents the type of function this server performs.

    Model servers usually load a specific model into memory,
    await for an input, perform inference, and then return
    their given output type to the user as a complete response over
    http(s) rest api or a stream of data via websocket connection.

    LANGUAGE SERVER BACKENDS:
        LLM:
            hosts a simple basic CPU/GPU compatible llm runner,
            takes text input and returns text output.

        VLLM:
            hosts a production ready GPU only llm manager,
            used for more complex LLM operations at scale.

    TRANSCRIPTION SERVER BACKENDS:
        FASTER_WHISPER:
            hosts a simple basic CPU/GPU compatible speech recognition engine,
            takes audio input and returns a text output.

        TENSORRT:
            hosts a production ready GPU only speech recognition engine,
            used for more complex speech recognition operations at scale.
    """

    LLM = "llm"
    VLLM = "vllm"
    FASTER_WHISPER = "faster_whisper"
    TENSORRT = "tensorrt"

    @staticmethod
    def valid_types() -> List[str]:
        return [backend_type.value for backend_type in BackendType]

    @staticmethod
    def is_valid(backend: str) -> bool:
        return backend in BackendType.valid_types()

    def is_llm(self) -> bool:
        return self == BackendType.LLM

    def is_vllm(self) -> bool:
        return self == BackendType.VLLM

    def is_faster_whisper(self) -> bool:
        return self == BackendType.FASTER_WHISPER

    def is_tensorrt(self) -> bool:
        return self == BackendType.TENSORRT
