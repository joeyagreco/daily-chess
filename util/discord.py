import requests


def send_webhook(*, webhook_url: str, embeds: list[dict]):
    """
    https://birdie0.github.io/discord-webhooks-guide/structure/embed/fields.html
    """
    data = {"embeds": embeds}
    response = requests.post(webhook_url, json=data)
    response.raise_for_status()
