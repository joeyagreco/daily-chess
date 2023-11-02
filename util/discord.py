import requests


def send_webhook(*, webhook_url: str, embeds: list[dict]):
    """
    https://birdie0.github.io/discord-webhooks-guide/structure/embed/fields.html
    """
    data = {"embeds": embeds}
    print(data)
    response = requests.post(webhook_url, json=data)
    response.raise_for_status()
    print(response)
