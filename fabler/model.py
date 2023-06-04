import logging
import os
from pathlib import Path
from typing import List

from fabler import FablerConfig
from fabler.pipelines import painter, speaker, writer, animator
from fabler.utils import check_ffmpeg, set_seed, subprocess_run

os.environ["TOKENIZERS_PARALLELISM"] = "false"
logging.getLogger("diffusers").setLevel(logging.CRITICAL)
logging.getLogger("transformers").setLevel(logging.CRITICAL)


class Fabler:
    def __init__(self, config: FablerConfig):
        check_ffmpeg()
        set_seed(config.seed)
        self.config = config
        self.writer = writer.init(self.config)
        os.makedirs(config.output_dir, exist_ok=True)

    @classmethod
    def init(cls, config: FablerConfig = FablerConfig()):
        return cls(config)

    def generate(
        self,
        prompt: str,
        num_images: int,
    ) -> None:
        if self.config.animated:
            self.animator = animator.init(self.config)
            if num_images % 2 == 0:
                num_images += 1
            sentences = self.writer.generate(prompt, num_images - 1)
            sentences.append("The End")
            video_paths = self.animator.generate(sentences)
        else:
            video_paths = []
            self.speaker = speaker.init(self.config)
            self.painter = painter.init(self.config)
            sentences = self.writer.generate(prompt, num_images)
            for i, sentence in enumerate(sentences):
                video_paths.append(self._generate(i, sentence))
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
            # TODO: Add multi-processing here
            subprocess_run(
                f"ffmpeg -loop 1 -i {video['image']} -i {video['audio']} -vf subtitles={video['subtitle']} -tune stillimage -shortest {video['video']}"
            )
        files_path.write_text("\n".join(files_data))
        subprocess_run(f"ffmpeg -f concat -i {files_path} -c copy {output_path}")
