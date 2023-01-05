import logging
import os
from pathlib import Path
from typing import List

from storyteller import StoryTellerConfig
from storyteller.pipelines import painter, speaker, writer
from storyteller.utils import check_ffmpeg, set_seed, subprocess_run

os.environ["TOKENIZERS_PARALLELISM"] = "false"
logging.getLogger("diffusers").setLevel(logging.CRITICAL)
logging.getLogger("transformers").setLevel(logging.CRITICAL)


class StoryTeller:
    def __init__(self, config: StoryTellerConfig):
        # check_ffmpeg()
        # set_seed(config.seed)
        # self.config = config
        # self.writer = writer.init(self.config)
        # self.speaker = speaker.init(self.config)
        # self.painter = painter.init(self.config)
        # os.makedirs(config.output_dir, exist_ok=True)
        print(config)
        __import__("sys").exit(0)


    @classmethod
    def init(cls, config: StoryTellerConfig = StoryTellerConfig()):
        return cls(config)

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
        sentences = self.writer.generate(prompt, num_images)
        for i, sentence in enumerate(sentences):
            video_path = self._generate(i, sentence)
            video_paths.append(video_path)
        self.concat_videos(video_paths)

    def _generate(self, id_: int, sentence: str) -> dict:
        return {
            "audio": self.speaker.generate(id_, sentence),
            "image": self.painter.generate(id_, sentence),
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
                f"ffmpeg -loop 1 -i {video['image']} -i {video['audio']} -vf subtitles={video['subtitle']} -hwaccel -tune stillimage -shortest {video['video']}"
            )
        files_path.write_text("\n".join(files_data))
        subprocess_run(f"ffmpeg -f concat -i {files_path} -c copy {output_path}")
