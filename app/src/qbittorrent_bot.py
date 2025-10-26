from typing import List
from qbittorrentapi import Client
import os
from . import log, telegram_msg


class QbittorrenBot:
    def __init__(self):
        self.logger = log.GlobalLogger()
        self.msg = telegram_msg.TelegamMsg()
        # 加载环境变量
        self.qb_host = os.environ.get("qb_host", "")
        self.qb_port = os.environ.get("qb_port", "")
        self.qb_username = os.environ.get("qb_username", "")
        self.qb_password = os.environ.get("qb_password", "")

    def send_torrents(self, links: List):
        # 信息不完整不发送qbittorrent
        if (
            not self.qb_host
            or not self.qb_port
            or not self.qb_username
            or not self.qb_password
        ):
            self.logger.error("qbittorrent信息配置不全，发送取消", True)
            return

        try:
            # 创建 qbittorrent 客户端实例
            qb = Client(
                host=self.qb_host,
                port=self.qb_port,
                username=self.qb_username,
                password=self.qb_password,
            )

            # 登录验证
            qb.auth_log_in()
            for link in links:
                qb.torrents_add(link)
            self.logger.info("发送qb下载共 " + str(len(links)), True)
            # 关闭 qbittorrent 客户端连接
            qb.auth_log_out()
        except Exception as e:
            self.logger.info(f"发送qbittorrent下载失败，原因：{e}")
            fai_msg = "qbittorrent下载失败链接如下所示：\n"
            if links:
                for link in links:
                    fai_msg += link + "\n"
                self.logger.info(fai_msg)
                self.msg.send_message("```\n" + fai_msg + "```", True)
