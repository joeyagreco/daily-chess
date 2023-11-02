from api.DiscordApiClient import DiscordApiClient


def send_discord_message(*, webhook_url: str, embeds: list[dict]):
    """
    https://birdie0.github.io/discord-webhooks-guide/structure/embeds.html
    """
    DiscordApiClient().send_webhook(url=webhook_url, embeds=embeds)
