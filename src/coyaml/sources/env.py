import os
from typing import Any

from dotenv import load_dotenv

from coyaml.sources.base import YSource


class EnvFileSource(YSource):
    """
    Source for loading environment variables.
    """

    def __init__(self, file_path: str | None = None):
        self.file_path = file_path

    def load(self) -> dict[str, Any]:
        if self.file_path:
            load_dotenv(self.file_path)
        return dict(os.environ.items())
