import os
import requests
from . import config


class TelegamMsg:
    def __init__(self):
        self.http_proxy = os.environ.get("http_proxy", config.NONE)
        self.bot_token = os.environ.get("bot_token", config.NONE)
        self.chat_id = os.environ.get("chat_id", config.NONE)

    # 给TG机器人发送消息
    def send_message(self, message: str, markdown: bool = False):
        # 构造消息发送的URL
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        # 准备POST请求的数据
        params = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "MarkdownV2" if markdown else None,
        }
        proxies = {
            "http": self.http_proxy,
            "https": self.http_proxy,
        }
        # 发送POST请求
        requests.post(url, params=params, proxies=proxies, timeout=config.TIME_OUT)
