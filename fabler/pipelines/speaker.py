from pathlib import Path
from typing import List

from TTS.api import TTS
import soundfile
import torch

from fabler import FablerConfig


def make_timeline_string(start, end):
    """Create timeline string to write onto .srt subtitle files."""
    start = format_time(start)
    end = format_time(end)
    return f"{start} --> {end}"


def format_time(time):
    """Transform time (seconds) to .srt format."""
    mm, ss = divmod(time, 60)
    hh, mm = divmod(mm, 60)
    return f"{hh:02d}:{mm:02d}:{ss:02d},000"


class StorySpeaker:
    def __init__(self, config: FablerConfig):
        self.config = config
        self.model = TTS(config.speaker, progress_bar=True, gpu=True)
        self.sample_rate = self.model.synthesizer.output_sample_rate

    @torch.inference_mode()
    def _generate(self, prompt) -> List[int]:
        return self.model.tts(prompt)

    def generate(self, id_: int, sentence: str, skip: bool = False) -> str:
        audio_path = Path(f"{self.config.output_dir}/{id_}.wav")
        subtitle_path = Path(f"{self.config.output_dir}/{id_}.srt")
        audio = self._generate(sentence)
        duration, remainder = divmod(len(audio), self.sample_rate)
        if remainder:
            duration += 1
            audio.extend([0] * (self.sample_rate - remainder))
        soundfile.write(audio_path, audio, self.sample_rate)

        subtitle = f"0\n{make_timeline_string(0, duration)}\n{sentence}"
        Path(subtitle_path).write_text(subtitle)

        return str(audio_path)


def init(config: FablerConfig) -> StorySpeaker:
    return StorySpeaker(config)


# TODO: Check out Vall-E from Microsoft
#       https://github.com/microsoft/unilm/tree/master/valle
