import os
from pathlib import Path


def secret_from_env(key, default=None):
    secret = os.environ.get(key)
    if secret is not None:
        return secret

    secret_file = Path('%s_FILE' % key)
    if secret_file.exists():
        return secret_file.read_text()

    return default
