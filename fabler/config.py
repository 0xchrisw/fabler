from dataclasses import dataclass, field
from pathlib import Path


@dataclass()
class FablerConfig:
    story: str = "Unicorn Earth"
    output_dir: str = str(Path(__file__).parent.parent / "out")
    animated: bool = False
    nsfw_check: bool = False
    seed: int = 42
    num_images: int = 10

    writer: str = "gpt2"
    writer_device: str = "cuda:0"
    max_new_tokens: int = 50
    writer_prompt_prefix: str = f"Acting as a story teller. Tell a fascinating, {num_images} sentence story from begining to end about the following:\n"
    writer_prompt: str = "Once upon a time, unicorns roamed the Earth."

    painter: str = "prompthero/openjourney"
    painter_device: str = "cuda:0"
    image_size: int = 512
    painter_prompt_prefix: str = "beautiful painting"
    painter_prompt_postfix: str = "\n\n"

    speaker: str = "tts_models/en/ljspeech/glow-tts"

    # TODO: Remove mutable `default_factory` and replace with default values
    puppeteer: dict = field(default_factory=dict)

    def __post_init__(self):
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
