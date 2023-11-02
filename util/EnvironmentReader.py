import os

from dotenv import load_dotenv


class EnvironmentReader:
    @staticmethod
    def get(name: str) -> str:
        load_dotenv()
        return os.getenv(name)
