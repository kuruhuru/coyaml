from typing import Any

import yaml

from coyaml.sources.base import YSource


class YamlFileSource(YSource):
    """
    Source for loading YAML file.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> dict[str, Any]:
        """
        Add configuration data from a YAML file with environment variable support.

        :param file_path: Path to YAML file.
        """
        with open(self.file_path, 'rb') as file:  # Changed to binary mode for better encoding support
            binary_content = file.read()
            try:
                text_content = binary_content.decode('utf-8')
            except UnicodeDecodeError as e:
                raise UnicodeDecodeError(
                    'utf-8',  # encoding
                    binary_content,  # object
                    e.start,  # start
                    e.end,  # end
                    f'Error decoding file {self.file_path}: {e}',
                ) from e
            config = yaml.safe_load(text_content)
            return config
