import logging
import os

from PIL.Image import Image
from diffusers import StableDiffusionPipeline
import torch

from fabler import FablerConfig

os.environ["TOKENIZERS_PARALLELISM"] = "false"
logging.getLogger("diffusers").setLevel(logging.CRITICAL)
logging.getLogger("transformers").setLevel(logging.CRITICAL)


class StoryPainter:
    def __init__(self, config: FablerConfig):
        self.config = config
        self.model = StableDiffusionPipeline.from_pretrained(
            self.config.painter,
            torch_dtype=torch.float16,
            use_auth_token=False,
        ).to(torch.device(config.painter_device))

        if not self.config.nsfw_check:
            self.model.safety_checker = self.safety_checker

    @classmethod
    def safety_checker(cls, images, **kwargs):
        return images, False

    @torch.inference_mode()
    def _generate(self, prompt) -> Image:
        prompt_text = f"{self.config.painter_prompt_prefix} {prompt}, {self.config.painter_prompt_postfix}"
        return self.model(prompt_text).images[0]

    def generate(self, id_: int, sentence: str) -> str:
        image_path = os.path.join(self.config.output_dir, f"{id_}.png")
        image = self._generate(sentence)
        image.save(image_path)
        return image_path


def init(config: FablerConfig) -> StoryPainter:
    return StoryPainter(config)
