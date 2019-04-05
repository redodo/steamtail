import os
from pathlib import Path


def secret_from_env(key, default=None):
    secret = os.environ.get(key)
    if secret is not None:
        return secret

    secret_filename = os.environ.get('%s_FILE' % key)
    if secret_filename:
        secret_file = Path(secret_filename)
        if secret_file.exists():
            return secret_file.read_text()

    return default
