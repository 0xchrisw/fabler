import argparse
from pathlib import Path

import yaml

from storyteller import StoryTeller, StoryTellerConfig


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
    config_obj = args
    if args.config is not None and Path(args.config).exists():
        config_data = yaml.safe_load(open(args.config))
        story_teller = StoryTeller.from_config(StoryTellerConfig(**config_data))
        config_obj = config_data
    else:
        story_teller = StoryTeller.from_default()
    story_teller.generate(config_obj["writer_prompt"], config_obj["num_images"])


if __name__ == "__main__":
    main()
