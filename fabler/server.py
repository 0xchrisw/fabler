# import logging
# import os
from pathlib import Path

# from typing import List
import urllib

from flask import Flask, jsonify, request

from fabler import FablerConfig
from fabler.pipelines import writer
from fabler.utils import set_seed

app = Flask(
    __name__,
    template_folder=Path(__file__).parent / "static/www",
    static_folder=Path(__file__).parent / "static/assets",
)


config = FablerConfig()
set_seed(config.seed)
sentence_writer = writer.init(config)


def Write(prompt_text: str, num_sentences: int) -> list:
    # config = FablerConfig(**{
    #     "writer_prompt": prompt_text,
    #     "num_images": num_sentences,
    # })
    # set_seed(config.seed)
    # sentence_writer = writer.init(config)
    return sentence_writer.generate(prompt_text, num_sentences)


@app.route("/", methods=["GET"])
def arguments():
    prompt_text = request.args.get("prompt_text", "")
    num_sentences = int(request.args.get("num_sentences", 0))
    if not prompt_text or not num_sentences:
        # TODO: Move to config
        return Path(app.template_folder / "index.html").read_text(encoding="utf-8")

    prompt_text = urllib.parse.unquote(prompt_text)
    generation = Write(prompt_text, num_sentences)
    out = {"generation": generation}
    return jsonify(out)


def serve(port: int = 9000):
    app.run(
        host="0.0.0.0",
        port=port,
        debug=True,
    )
