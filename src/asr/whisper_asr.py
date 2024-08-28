import os
import time
import torch
from transformers import pipeline,AutoModelForSeq2SeqLM

from src.audio_utils import save_audio_to_file

from .asr_interface import ASRInterface


class WhisperASR(ASRInterface):
    def __init__(self, **kwargs):
    # Determine if CUDA is available and how many GPUs are available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        n_gpus = torch.cuda.device_count() if device == "cuda" else 0
    
        model_name = kwargs.get("model_name", "openai/whisper-large-v3")
    
        if n_gpus > 1:
            # Load the model and wrap it with DataParallel for multi-GPU usage
            model = torch.nn.DataParallel(AutoModelForSeq2SeqLM.from_pretrained(model_name))
            self.asr_pipeline = pipeline(
            "automatic-speech-recognition",
            model=model,
            device=0,  # Specify the first GPU as the device for the pipeline
            )
        else:
        # Single GPU or CPU usage
            self.asr_pipeline = pipeline(
                "automatic-speech-recognition",
                model=model_name,
                device=0 if device == "cuda" else -1,  # device 0 for GPU, -1 for CPU
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
