import os
import logging
import argparse

from backend.types import BackendType

logging.basicConfig(level=logging.INFO)


class Server:
    """
    The Server object defines core server functionality and wraps
    the objects with instance specific functionality.
    """

    instance = None
    backend: BackendType | None = None

    def __init__(self, *args, **kwargs) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument("server_type")
        parser.add_argument(
            "--port",
            "-p",
            type=int,
            default=9000,
            help="Websocket port to run the server on.",
        )
        parser.add_argument(
            "--backend",
            "-b",
            type=str,
            default="faster_whisper",
            help='Backends from ["tensorrt", "faster_whisper"]',
        )
        parser.add_argument(
            "--faster_whisper_custom_model_path",
            "-fw",
            type=str,
            default=None,
            help="Custom Faster Whisper Model",
        )
        parser.add_argument(
            "--trt_model_path",
            "-trt",
            type=str,
            default=None,
            help="Whisper TensorRT model path",
        )
        parser.add_argument(
            "--trt_multilingual",
            "-m",
            action="store_true",
            help="Boolean only for TensorRT model. True if multilingual.",
        )
        parser.add_argument(
            "--omp_num_threads",
            "-omp",
            type=int,
            default=1,
            help="Number of threads to use for OpenMP",
        )
        parser.add_argument(
            "--no_single_model",
            "-nsm",
            action="store_true",
            help="Set this if every connection should instantiate its own model. Only relevant for custom model, passed using -trt or -fw.",
        )
        args = parser.parse_args()

        if args.backend == "tensorrt":
            if args.trt_model_path is None:
                raise ValueError("Please Provide a valid tensorrt model path")

        if "OMP_NUM_THREADS" not in os.environ:
            os.environ["OMP_NUM_THREADS"] = str(args.omp_num_threads)

        if BackendType.is_valid(backend=args.server_type):
            self.backend = BackendType(args.server_type)
        else:
            exit("No backend for " + args.server_type + " type was supplied")

        if self.backend.is_faster_whisper() or self.backend.is_tensorrt():
            from backend.transcription.server import TranscriptionServer

            self.instance = TranscriptionServer()
            self.instance_args = ("127.0.0.1",)
            self.instance_kwargs = {
                "port": args.port,
                "backend": args.backend,
                "faster_whisper_custom_model_path": args.faster_whisper_custom_model_path,
                "whisper_tensorrt_path": args.trt_model_path,
                "trt_multilingual": args.trt_multilingual,
                "single_model": not args.no_single_model,
            }
        elif self.backend == "LLM":
            from backend.llm.server import LLMServer

            self.instance = LLMServer()
            self.instance_args = ("127.0.0.1",)
            self.instance_kwargs = {
                "port": args.port,
                "backend": args.backend,
            }


if __name__ == "__main__":
    server = Server()

    if server.instance is not None:
        server.instance.run(*server.instance_args, **server.instance_kwargs)
