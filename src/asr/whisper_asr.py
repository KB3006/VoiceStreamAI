import os
import time
import torch
from transformers import pipeline

from src.audio_utils import save_audio_to_file
from .asr_interface import ASRInterface

class WhisperASR(ASRInterface):
    def __init__(self, **kwargs):
        # Determine if CUDA is available and how many GPUs are available
        self.device_count = torch.cuda.device_count() if torch.cuda.is_available() else 0
    
        model_name = kwargs.get("model_name", "openai/whisper-large-v3")
        
        # Create a list of pipelines, one for each GPU or just one for CPU
        self.asr_pipelines = []
        if self.device_count > 1:
            for i in range(self.device_count):
                self.asr_pipelines.append(
                    pipeline(
                        "automatic-speech-recognition",
                        model=model_name,
                        device=i  # Use GPU i
                    )
                )
        else:
            # Single GPU or CPU usage
            self.asr_pipeline = pipeline(
                "automatic-speech-recognition",
                model=model_name,
                device=0 if self.device_count == 1 else -1  # device 0 for GPU, -1 for CPU
            )
    
    async def transcribe(self, client):
        file_path = await save_audio_to_file(
            client.scratch_buffer, client.get_file_name()
        )

        if client.config["language"] is not None:
            to_return = self._run_pipeline(file_path, {"language": client.config["language"], "task": "translate"})
        else:
            pip_time = time.time()
            to_return = self._run_pipeline(file_path, {"task": "translate"})
            print(str(time.time() - pip_time) + " seconds for pipeline")

        os.remove(file_path)

        return {
            "text": to_return.strip(),
        }

    def _run_pipeline(self, file_path, generate_kwargs):
        if self.device_count > 1:
            # If multiple GPUs are available, split the workload (this example assumes you split work outside of this method)
            # Here, just run on the first pipeline as a simple example
            return self.asr_pipelines[0](file_path, generate_kwargs=generate_kwargs)["text"]
        else:
            # Single GPU or CPU usage
            return self.asr_pipeline(file_path, generate_kwargs=generate_kwargs)["text"]
