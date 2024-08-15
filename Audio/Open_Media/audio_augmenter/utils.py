import numpy as np
import torch
import soundfile as sf

def read_audio(file_path: str) -> np.ndarray:
    """
    Reading audio signal
    """

    waveform, sample_rate = sf.read(file_path)
    return waveform, sample_rate


def save_audio(file_path: str, audio: np.ndarray, sr: int):
    """
    Saving the augmented audio.

    """
    waveform_np = audio.numpy() if isinstance(audio, torch.Tensor) else audio
    waveform_np = waveform_np.astype(np.float32)
    sf.write(file_path, waveform_np, sr) 
