import os
import random
import shutil
import subprocess

import numpy as np
import torch


def check_ffmpeg():
    """Check ffmpeg installation."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("`ffmpeg` not found. Please install `ffmpeg` and try again.")


def subprocess_run(command):
    """Wrapper around `subprocess.run()` with /dev/null redirection in stdout and stderr."""
    subprocess.run(command.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def set_seed(seed):
    """Set seed."""
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = True
