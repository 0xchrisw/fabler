import argparse
from pathlib import Path

import yaml

from storyteller import StoryTeller, StoryTellerConfig


def run_demo():
    story_teller = StoryTeller.from_default()
    story_teller.generate(args.prompt, args.num_images)


def run_from_config(config_file: str):
    config_data = yaml.safe_load(open(config_file))
    storyteller_config = StoryTellerConfig(**config_data)
    story_teller = StoryTeller.from_config(storyteller_config)
    story_teller.generate(config_data["writer_prompt"], config_data["num_images"])


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prompt", type=str, default="Once upon a time, unicorns roamed the Earth."
    )
    parser.add_argument(
        "--config", type=str, default=None, help="StoryTeller config file path."
    )
    parser.add_argument("--num_images", type=int, default=10)
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    if args.config is not None and Path(args.config).exists():
        run_from_config(args.config)
    else:
        run_demo()


if __name__ == "__main__":
    main()
