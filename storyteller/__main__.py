import argparse
from pathlib import Path
import sys

import yaml
from typing import List
from storyteller import StoryTeller, StoryTellerConfig


def cli_parser(argv: List[str] = sys.argv[1:]) -> argparse.Namespace:
    parser = argparse.ArgumentParser("storyteller")
    arguments = (
        (
            "--prompt",
            dict(
                type=str,
                default="Once upon a time, unicorns roamed the Earth.",
                help="Initial prompt used to generate the story.",
            ),
        ),
        (
            "--scene",
            dict(type=str, default=None, help="StoryTeller config file path."),
        ),
        (
            "--num_images",
            dict(type=int, default=10),
        ),
        (
            "--story-only",
            dict(type=bool, default=False),
        ),
    )
    for args, kwargs in arguments:
        args = args if isinstance(args, tuple) else (args,)
        parser.add_argument(*args, **kwargs)

    if len(argv) == 0 or argv[0] in ("usage", "help"):
        parser.print_help()
        sys.exit(1)

    parser.set_defaults(func=main)

    return parser.parse_args(argv)


def main():
    arguments = cli_parser()
    config = arguments.__dict__

    if arguments.scene is not None and (scene_path := Path(arguments.scene)).exists():
        config = yaml.safe_load(scene_path.read_text())

    story_teller = StoryTeller.init(StoryTellerConfig(**config))
    story_teller.generate(config["writer_prompt"], config["num_images"])


if __name__ == "__main__":
    main()
