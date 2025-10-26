from typing import List
import requests
import os
from . import config, log, telegram_msg
from datetime import datetime


class Pan115Client:
    def __init__(self):
        self.session = requests.Session()
        self.logger = log.GlobalLogger()
        self.msg = telegram_msg.TelegamMsg()
        self.cookie_115 = os.environ.get("pan115_cookie", config.NONE)
        self.cid_115 = os.environ.get("pan115_cid", config.NONE)
        self.session.headers.update(self.get_header())
        self.is_ready = False

    def get_header(self):
        return {
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "https://115.com",
            "User-Agent": config.USER_AGENT,
            "Referer": f"https://115.com/?cid={self.cid_115}&offset=0&mode=wangpan",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
            "Cookie": self.cookie_115,
        }

    def login(self):
        try:
            self.session.headers.update({"Host": "my.115.com"})
            res = self.session.get("https://my.115.com/?ct=guide&ac=status")
            res.json()
        except Exception as e:
            self.logger.error(f"login错误：{e}")

    def set_sign_and_time(self):
        try:
            self.session.headers.update({"Host": "115.com"})
            res = self.session.get("https://115.com/?ct=offline&ac=space")
            result = res.json()
            self.sign = result["sign"]
            self.time = result["time"]
        except Exception as e:
            self.logger.error(f"获取sign_and_time错误：{e}")

    def set_uid(self):
        try:
            self.session.headers.update({"Host": "my.115.com"})
            res = self.session.get("https://my.115.com/?ct=ajax&ac=get_user_aq")
            result = res.json()
            self.uid = result["data"]["uid"]
        except Exception as e:
            self.logger.error(f"获取uid错误：{e}")

    def ready(self):
        self.login()
        self.set_sign_and_time()
        self.set_uid()
        self.is_ready = True

    def check(self) -> bool:
        if not self.cookie_115 or not self.cid_115:
            self.logger.error("115信息配置不全，发送取消", True)
            return False
        else:
            return True

    def send_ed2ks(self, links: List):
        try:
            if not self.check():
                return
            if not self.is_ready:
                self.ready()
            data = {
                "savepath": "",
                "wp_path_id": self.cid_115,
                "uid": self.uid,
                "sign": self.sign,
                "time": self.time,
            }
            data.update({f"url[{i}]": url for i, url in enumerate(links)})
            self.session.headers.update({"Host": "115.com"})
            res = self.session.post(
                "https://115.com/web/lixian/?ct=lixian&ac=add_task_urls", data=data
            )
            resjson = res.json()
            self.logger.debug(resjson)
            fai_msg = ""
            info_msg = ""
            if resjson["state"]:
                suc_count = 0
                fai_count = 0
                if resjson["result"]:
                    for result in resjson["result"]:
                        if result["state"]:
                            suc_count += 1
                        else:
                            fai_count += 1
                            fai_msg += (
                                "失败原因："
                                + result["error_msg"]
                                + "，链接："
                                + result["url"]
                                + "\n"
                            )
                info_msg = "发送115离线下载共 " + str(len(links)) + " ，"
                if suc_count:
                    info_msg += "成功 " + str(suc_count) + " "
                if fai_count:
                    info_msg += "失败 " + str(fai_count) + " "
                self.logger.info(info_msg, True)
                if fai_count:
                    fai_title = "115离线失败链接如下所示：\n"
                    self.logger.info(fai_title + fai_msg)
                    self.msg.send_message("```\n" + fai_title + fai_msg + "```", True)
            else:
                if resjson["errcode"] == 911:
                    url = (
                        "https://captchaapi.115.com/?ac=security_code&type=web&cb=Close911_"
                        + str(int(datetime.now().timestamp() * 1000))
                    )
                    self.logger.error("请登录115云盘验证账号，验证链接：" + url, True)
                else:
                    self.logger.error("115云盘cookie已失效，请重新配置", True)
                if links:
                    fai_msg = "115离线失败链接如下所示：\n"
                    for link in links:
                        fai_msg += link + "\n"
                    self.logger.info(fai_msg)
                    self.msg.send_message("```\n" + fai_msg + "```", True)
        except Exception as e:
            self.logger.error(f"send_links错误：{e}")
