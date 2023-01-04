import logging
import os
from typing import List

from PIL.Image import Image
from TTS.api import TTS
from diffusers import StableDiffusionPipeline
import nltk
from nltk.tokenize import sent_tokenize
import soundfile as sf
import torch
from transformers import pipeline

from storyteller import StoryTellerConfig
from storyteller.utils import (
    check_ffmpeg,
    make_timeline_string,
    set_seed,
    subprocess_run,
)

os.environ["TOKENIZERS_PARALLELISM"] = "false"
logging.getLogger("diffusers").setLevel(logging.CRITICAL)
logging.getLogger("transformers").setLevel(logging.CRITICAL)


class StoryTeller:
    def __init__(self, config: StoryTellerConfig):
        check_ffmpeg()
        nltk.download("punkt")
        set_seed(config.seed)
        self.config = config
        os.makedirs(config.output_dir, exist_ok=True)
        writer_device = torch.device(config.writer_device)
        painter_device = torch.device(config.writer_device)
        self.writer = pipeline(
            "text-generation", model=config.writer, device=writer_device
        )
        self.painter = StableDiffusionPipeline.from_pretrained(
            self.config.painter,
            torch_dtype=torch.float16,
            revision="fp16",
            use_auth_token=False,
        ).to(painter_device)
        if self.config.disable_nsfw_check:
            self.painter.safety_checker = self.safety_checker
        self.speaker = TTS(config.speaker)
        self.sample_rate = self.speaker.synthesizer.output_sample_rate

    @classmethod
    def from_default(cls):
        config = StoryTellerConfig()
        return cls(config)

    @classmethod
    def from_config(cls, config: StoryTellerConfig):
        return cls(config)

    @classmethod
    def safety_checker(cls, images, **kwargs):
        return images, False

    @torch.inference_mode()
    def paint(self, prompt) -> Image:
        return self.painter(f"{self.config.diffusion_prompt_prefix}: {prompt}").images[
            0
        ]

    @torch.inference_mode()
    def speak(self, prompt) -> List[int]:
        return self.speaker.tts(prompt)

    @torch.inference_mode()
    def write(self, prompt) -> str:
        return self.writer(prompt, max_new_tokens=self.config.max_new_tokens)[0][
            "generated_text"
        ]

    def generate(
        self,
        prompt: str,
        num_images: int,
    ) -> None:
        video_paths = []
        sentences = self.write_story(prompt, num_images)
        for i, sentence in enumerate(sentences):
            video_path = self._generate(i, sentence)
            video_paths.append(video_path)
        self.concat_videos(video_paths)

    def concat_videos(self, video_paths: List[str]) -> None:
        files_path = os.path.join(self.config.output_dir, "files.txt")
        output_path = os.path.join(self.config.output_dir, "out.mp4")
        with open(files_path, "w+") as f:
            for video_path in video_paths:
                f.write(f"file {os.path.split(video_path)[-1]}\n")
        subprocess_run(f"ffmpeg -f concat -i {files_path} -c copy {output_path}")

    def _generate(self, id_: int, sentence: str) -> str:
        image_path = os.path.join(self.config.output_dir, f"{id_}.png")
        audio_path = os.path.join(self.config.output_dir, f"{id_}.wav")
        subtitle_path = os.path.join(self.config.output_dir, f"{id_}.srt")
        video_path = os.path.join(self.config.output_dir, f"{id_}.mp4")
        image = self.paint(sentence)
        image.save(image_path)
        audio = self.speak(sentence)
        duration, remainder = divmod(len(audio), self.sample_rate)
        if remainder:
            duration += 1
            audio.extend([0] * (self.sample_rate - remainder))
        sf.write(audio_path, audio, self.sample_rate)
        subtitle = f"0\n{make_timeline_string(0, duration)}\n{sentence}"
        with open(subtitle_path, "w+") as f:
            f.write(subtitle)
        subprocess_run(
            f"ffmpeg -loop 1 -i {image_path} -i {audio_path} -vf subtitles={subtitle_path} -tune stillimage -shortest {video_path}"
        )
        return video_path

    def write_story(self, prompt: str, num_sentences: int) -> List[str]:
        sentences = prompt.split(".")
        while len(sentences) < num_sentences + 1:
            prompt = self.write(prompt)
            sentences = sent_tokenize(prompt)
        while len(sentences) > num_sentences:
            sentences.pop()
        return sentences
