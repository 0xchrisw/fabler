import logging
import os
from pathlib import Path
from typing import List

from PIL.Image import Image
from TTS.api import TTS
from diffusers import StableDiffusionPipeline
# import nltk
# from nltk.tokenize import sent_tokenize
import soundfile
import torch
from transformers import pipeline

from storyteller import StoryTellerConfig
from storyteller.pipelines import speaker
from storyteller.pipelines import writer
from storyteller.utils import (
    check_ffmpeg,
    # make_timeline_string,
    set_seed,
    subprocess_run,
)

os.environ["TOKENIZERS_PARALLELISM"] = "false"
logging.getLogger("diffusers").setLevel(logging.CRITICAL)
logging.getLogger("transformers").setLevel(logging.CRITICAL)


class StoryTeller:
    def __init__(self, config: StoryTellerConfig):
        check_ffmpeg()
        set_seed(config.seed)
        self.config = config
        os.makedirs(config.output_dir, exist_ok=True)
        painter_device = torch.device(config.writer_device)
        self.writer = writer.init(self.config)
        # self.speaker = TTS(config.speaker, progress_bar=True, gpu=True)
        # self.sample_rate = self.speaker.synthesizer.output_sample_rate
        self.speaker = speaker.init(self.config)
        # self.painter = StableDiffusionPipeline.from_pretrained(
        #     self.config.painter,
        #     torch_dtype=torch.float16,
        #     # revision="fp16",
        #     use_auth_token=False,
        # ).to(painter_device)
        # if not self.config.nsfw_check:
        #     self.painter.safety_checker = self.safety_checker

    @classmethod
    def init(cls, config: StoryTellerConfig = StoryTellerConfig()):
        return cls(config)

    @classmethod
    def safety_checker(cls, images, **kwargs):
        return images, False

    @torch.inference_mode()
    def paint(self, prompt) -> Image:
        return self.painter(
            f"{self.config.painter_prompt_prefix} {prompt}, {self.config.painter_prompt_postfix}"
        ).images[0]

    # @torch.inference_mode()
    # def speak(self, prompt) -> List[int]:
    #     return self.speaker.tts(prompt)

    def generate(
        self,
        prompt: str,
        num_images: int,
    ) -> None:
        video_paths = []

        # If there is an even number of sentences, use self.generate_text()
        # to generate a final sentence; useful for animations
        if num_images % 2 == 0:
            num_images += 1
        # sentences = self.writer.generate(prompt, num_images)
        sentences = [
            "Good evening, and welcome to the nightly news. It is March 9th 8163.",
            "In a shocking turn of events, a toaster has been appointed as the CEO of the largest technology company in the world.",
            "The announcement has caused widespread concern and debate about the role of artificial intelligence in the workplace.",
            "According to sources, the toaster was chosen for its efficiency and attention to detail."
            "... as well as its ability to handle multiple tasks at once.",
            "Critics argue that the appointment sets a dangerous precedent and could lead to the replacement of human workers with machines.",
            "The toaster, who declined to be interviewed, has already implemented several changes at the company.",
            "The changes include the installation of additional outlets in the office for toasting bread and the introduction of a toaster-themed dress code.",
            "Employees at the company have mixed reactions to the appointment.",
        ]
        for i, sentence in enumerate(sentences):
            video_path = self._generate(i, sentence)
            video_paths.append(video_path)
        # self.concat_videos(video_paths)

    def _generate(self, id_: int, sentence: str) -> dict:
        return {
            "audio": self.speaker.generate(id_, sentence),
            "image": self.generate_image(id_, sentence),
            "subtitle": Path(f"{self.config.output_dir}/{id_}.srt"),
            "video": Path(f"{self.config.output_dir}/{id_}.mp4"),
        }

    def concat_videos(self, video_paths: List[dict]) -> None:
        files_data = []
        files_path = Path(f"{self.config.output_dir}/files.txt")
        output_path = Path(f"{self.config.output_dir}/out.mp4")
        for video in video_paths:
            print(f"Generating {video['video']}...")
            files_data.append(f"file {Path(video['video']).name}")
            subprocess_run(
                f"ffmpeg -loop 1 -i {video['image']} -i {video['audio']} -vf subtitles={video['subtitle']} -tune stillimage -shortest {video['video']}"
            )
        files_path.write_text("\n".join(files_data))
        subprocess_run(f"ffmpeg -f concat -i {files_path} -c copy {output_path}")

    # def generate_audio(self, id_: int, sentence: str) -> str:
    #     audio_path = os.path.join(self.config.output_dir, f"{id_}.wav")
    #     subtitle_path = os.path.join(self.config.output_dir, f"{id_}.srt")
    #     audio = self.speak(sentence)
    #     duration, remainder = divmod(len(audio), self.sample_rate)
    #     if remainder:
    #         duration += 1
    #         audio.extend([0] * (self.sample_rate - remainder))
    #     soundfile.write(audio_path, audio, self.sample_rate)
    #     subtitle = f"0\n{make_timeline_string(0, duration)}\n{sentence}"
    #     with open(subtitle_path, "w+") as f:
    #         f.write(subtitle)
    #     return audio_path

    def generate_image(self, id_: int, sentence: str) -> str:
        image_path = os.path.join(self.config.output_dir, f"{id_}.png")
        # image = self.paint(sentence)
        # image.save(image_path)
        return image_path

    def generate_animation(self, sentences: str) -> str:
        # https://colab.research.google.com/github/nateraw/stable-diffusion-videos/blob/main/stable_diffusion_videos.ipynb
        # https://towardsdatascience.com/make-your-art-move-with-stable-diffusion-animations-80de62eec633
        num_frames = self.num_images
        animations = [sentences[x : x + 2] for x in range(0, len(sentences), 2)]
        print(animations)
        # image_path = os.path.join(self.config.output_dir, f"{id_}.png")
        # image = self.paint(sentence)
        # image.save(image_path)
        # return image_path
