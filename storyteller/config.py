from dataclasses import dataclass
from pathlib import Path


@dataclass()
class StoryTellerConfig:
    output_dir: str = Path(__file__).parent.parent / "out"
    disable_nsfw_check: bool = False
    seed: int = 42

    writer: str = "gpt2"
    writer_device: str = "cuda:0"
    max_new_tokens: int = 50
    writer_prompt: str = "Once upon a time, unicorns roamed the Earth."

    painter: str = "stabilityai/stable-diffusion-2"
    painter_device: str = "cuda:0"
    image_size: int = 512
    num_images: int = 10
    diffusion_prompt_prefix: str = "Beautiful painting"

    speaker: str = "tts_models/en/ljspeech/glow-tts"
