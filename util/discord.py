from typing import Optional

from api.DiscordApiClient import DiscordApiClient


def send_discord_message(*, webhook_url: str, embeds: list[dict], file_path: Optional[str] = None):
    """
    https://birdie0.github.io/discord-webhooks-guide/structure/embeds.html
    """
    DiscordApiClient().send_webhook(url=webhook_url, embeds=embeds, file_path=file_path)
