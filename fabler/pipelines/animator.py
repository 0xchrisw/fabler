import logging
import os
import random

from pathlib import Path
from PIL.Image import Image
from stable_diffusion_videos import StableDiffusionWalkPipeline
import torch

from fabler import FablerConfig

os.environ["TOKENIZERS_PARALLELISM"] = "false"
logging.getLogger("diffusers").setLevel(logging.CRITICAL)
logging.getLogger("transformers").setLevel(logging.CRITICAL)


class StoryAnimator:
  def __init__(self, config: FablerConfig):
    self.config = config
    self.model = StableDiffusionWalkPipeline.from_pretrained(
        self.config.painter,
        torch_dtype=torch.float16,
        use_auth_token=False,
    ).to(torch.device(config.painter_device))


  # @torch.inference_mode()
  def _generate(self, prompts: list, frame_number: int, fps: int = 30) -> str:
      prompts = [f"{self.config.painter_prompt_prefix} {prompt}, {self.config.painter_prompt_postfix}" for prompt in prompts]
      video_path = self.model.walk(
          prompts=prompts,
          seeds=random.sample(range(42, 1337), 2),
          num_interpolation_steps=3,
          height=self.config.image_size,      # use multiples of 64 if > 512. Multiples of 8 if < 512.
          width=self.config.image_size,       # use multiples of 64 if > 512. Multiples of 8 if < 512.
          output_dir=self.config.output_dir,  # Where images/videos will be saved
          name=f"{frame_number}",             # Subdirectory of output_dir where images/videos will be saved
          guidance_scale=8.5,                 # Higher adheres to prompt more, lower lets model take the wheel
          num_inference_steps=50,             # Number of diffusion steps per image generated. 50 is good default
      )
      return video_path

  def generate(self, sentences: list) -> list:
      animations = [sentences[x : x + 2] for x in range(0, len(sentences), 2)]
      video_paths = []
      fps = 30  # Use lower values for testing (5 or 10), higher values for better quality (30 or 60)
      for i, animation in enumerate(animations):
        video_paths.append(self._generate(animation, i, fps=fps))
      print(video_paths)
      return video_paths


def init(config: FablerConfig) -> StoryAnimator:
    return StoryAnimator(config)
