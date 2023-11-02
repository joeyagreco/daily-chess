import requests


def send_webhook(*, webhook_url: str, content: str):
    data = {"content": content}
    response = requests.post(webhook_url, json=data)
    print(response)
