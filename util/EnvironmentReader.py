import os
from typing import Optional

from dotenv import load_dotenv


class EnvironmentReader:
    @staticmethod
    def get(name: str, default: Optional[any] = None) -> str:
        load_dotenv()
        env_var = os.getenv(name)
        if env_var is None:
            env_var = default
        return env_var
