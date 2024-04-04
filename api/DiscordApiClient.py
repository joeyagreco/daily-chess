import json
from typing import Optional

import requests

from api.BaseApiClient import BaseApiClient


class DiscordApiClient(BaseApiClient):
    def __init__(self):
        super().__init__()

    def send_webhook(cls, *, url: str, embeds: list[dict], file_path: Optional[str] = None) -> None:
        """
        Send a webhook to Discord with optional file attachment.

        Args:
        - url (str): The webhook URL.
        - embeds (list[dict]): The embeds to send.
        - file_path (Optional[str]): The path to the file to attach (default is None).
        """
        if file_path:
            with open(file_path, "rb") as file:
                # Set the image in the last embed's image url field
                embeds[-1]["image"] = {"url": f"attachment://{file_path.split('/')[-1]}"}

                payload = {
                    "payload_json": (None, json.dumps({"embeds": embeds})),
                    "file": (file_path.split("/")[-1], file),
                }
                cls._rest_call(requests.post, url, files=payload)
        else:
            data = {"embeds": embeds}
            cls._rest_call(requests.post, url, json=data)
