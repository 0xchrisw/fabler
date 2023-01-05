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
        "--scene", type=str, default=None, help="StoryTeller config file path."
    )
    parser.add_argument("--num_images", type=int, default=10)
    parser.add_argument("--story-only", type=bool, default=False)
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    if args.scene is not None and Path(args.scene).exists():
        _config = yaml.safe_load(open(args.scene))
        story_teller = StoryTeller.init(StoryTellerConfig(**_config))
    else:
        _config = args.__dict__
        story_teller = StoryTeller.init()
    story_teller.generate(_config["writer_prompt"], _config["num_images"])


if __name__ == "__main__":
    main()
