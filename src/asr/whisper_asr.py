import os
import time
import torch
from transformers import pipeline

from src.audio_utils import save_audio_to_file

from .asr_interface import ASRInterface


class WhisperASR(ASRInterface):
    def __init__(self, **kwargs):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model_name = kwargs.get("model_name", "openai/whisper-large-v3")
        self.asr_pipeline = pipeline(
            "automatic-speech-recognition",
            model=model_name,
            device=device,
        )

    async def transcribe(self, client):
        file_path = await save_audio_to_file(
            client.scratch_buffer, client.get_file_name()
        )

        if client.config["language"] is not None:
            to_return = self.asr_pipeline(
                file_path,
                generate_kwargs={"language": client.config["language"],"task": "translate"})["text"]
        else:
            pip_time = time.time()
            to_return = self.asr_pipeline(file_path,generate_kwargs={"task": "translate"})["text"]
            print(str(time.time() - pip_time ) + " seconds for pipeline")
        os.remove(file_path)

        to_return = {
            
            "text": to_return.strip(),
            
        }
        return to_return
