import requests

from api.BaseApiClient import BaseApiClient


class DiscordApiClient(BaseApiClient):
    def __init__(self):
        super().__init__()

    @classmethod
    def send_webhook(cls, *, url: str, embeds: list[dict]) -> None:
        """
        https://birdie0.github.io/discord-webhooks-guide/structure/embeds.html
        """
        data = {"embeds": embeds}
        cls._rest_call(requests.post, url, json=data)
