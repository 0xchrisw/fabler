from pathlib import Path
from typing import List

import nltk
from nltk.tokenize import sent_tokenize
import torch
from transformers import pipeline

from fabler import FablerConfig


class StoryWriter:
    def __init__(self, config: FablerConfig):
        # global model, tokenizer
        nltk.download("punkt")
        self.config = config

        self.model = pipeline(
            "text-generation",
            device=torch.device(config.writer_device),
            model=config.writer,
            # tokenizer="gpt2",
        )
        # self.tokenizer = AutoTokenizer.from_pretrained("gpt2")

    @torch.inference_mode()
    def _generate(self, prompt: str) -> str:
        return self.model(prompt, max_new_tokens=self.config.max_new_tokens, prefix=self.config.writer_prompt_prefix,)[
            0
        ]["generated_text"]

    def generate(self, prompt: str, num_sentences: int) -> List[str]:
        sentences = sent_tokenize(prompt)
        while len(sentences) < num_sentences + 1:
            prompt = self._generate(prompt)
            sentences = sent_tokenize(prompt)
        while len(sentences) > num_sentences + 1:
            sentences.pop()
        Path(f"{self.config.output_dir}/sentences.txt").write_text("\n".join(sentences))
        return sentences


def init(config: FablerConfig) -> StoryWriter:
    return StoryWriter(config)
