import requests
import certifi
from . import log, config
import sys
import os
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import re


class BT47:
    def __init__(self):
        self.logger = log.GlobalLogger()
        self.rss_leixing = os.environ.get("rss_leixin", config.NONE)
        self.rss_nianfen = os.environ.get("rss_nianfen", config.NONE)
        self.rss_diqu = os.environ.get("rss_diqu", config.NONE)
        self.rss_huazhi = os.environ.get("rss_huazhi", config.NONE)
        self.rss_sort = os.environ.get("rss_sort", config.NONE)

    def set_cookie(self):
        bt_username = os.environ.get("bt_username", config.NONE)
        bt_password = os.environ.get("bt_password", config.NONE)
        if bt_username == config.NONE or bt_password == config.NONE:
            self.logger.info("网站账号或者密码缺失")
            return

        # 发送HTTP请求获取页面内容
        page_url = (
            config.URL
            + "/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1"
        )
        headers = {
            "User-Agent": config.USER_AGENT,
        }
        data = {
            "fastloginfield": "username",
            "username": bt_username,
            "password": bt_password,
            "quickforward": "yes",
            "handlekey": "ls",
        }
        response = requests.post(
            page_url,
            data=data,
            headers=headers,
            timeout=config.TIME_OUT,
            verify=certifi.where(),
        )
        response.encoding = config.UTF8
        if response.status_code == 200:
            # 提取为字符串格式
            cookie_str = "; ".join([f"{c.name}={c.value}" for c in response.cookies])
            os.environ["bt_cookie"] = cookie_str
            self.logger.info("网站账号：" + bt_username + "，网站cookie：" + cookie_str)
        else:
            self.logger.error("登录失败，状态码：" + response.status_code)
            sys.exit()

    # 获取请求头
    def headers(self):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": os.environ.get("bt_cookie", config.NONE),
            "Dnt": "1",
            "Host": "47bt.com",
            "Priority": "u=0, i",
            "Sec-Ch-Ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Sec-Gpc": "1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": config.USER_AGENT,
        }

    # 47bt网站签到
    def sign_in(self):
        # 签到开关
        bt_sign_switch = os.environ.get("bt_sign_switch", config.OFF)
        if bt_sign_switch == config.OFF:
            self.logger.info("签到开关为关，请打开后再签到")
            return

        # 打卡页面
        response = requests.get(
            config.URL + "/plugin.php?id=zqlj_sign",
            headers=self.headers(),
            timeout=config.TIME_OUT,
            verify=certifi.where(),
        )

        response.encoding = config.UTF8
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            # 获取打卡链接
            a = soup.find("div", class_="bm signbtn cl").find("a", class_="btna")
            if a:
                if a.text == "点击打卡":
                    # 请求打卡
                    response = requests.get(
                        config.URL + "/" + a["href"],
                        headers=self.headers(),
                        timeout=config.TIME_OUT,
                        verify=certifi.where(),
                    )
                    if response.status_code == 200:
                        self.logger.info("✅ 打卡成功", True)
                elif a.text == "今日已打卡":
                    self.logger.info("⚠️ 您今天已经打过卡了，请勿重复操作", True)
            else:
                self.logger.error("获取打卡链接失败")
        else:
            self.logger.error("进入打卡页面失败，状态码：" + response.status_code)

    # 获取视频详情
    def get_thread_detail(self, threads):
        detils_dict = []

        if len(threads) != 0:
            for thread in threads:
                tepDict = {}
                tepDict["thread_url"] = config.URL + "/" + thread.get("thread")
                self.logger.info("请求详情页链接: " + tepDict.get("thread_url"))
                response = requests.get(
                    tepDict.get("thread_url"),
                    headers=self.headers(),
                    timeout=config.TIME_OUT,
                    verify=certifi.where(),
                )
                # 确保响应内容的编码为 UTF-8
                response.encoding = config.UTF8
                if response.status_code != 200:
                    continue
                else:
                    soup = BeautifulSoup(response.text, "lxml")
                    # 重试机制
                    if not soup.find("span", id="thread_subject"):
                        for i in range(1, config.RETRY_TIMES + 1):
                            time.sleep(
                                random.randint(
                                    config.TIME_SLEEP_BEG, config.TIME_SLEEP_END
                                )
                            )
                            self.logger.info(
                                "第"
                                + str(i)
                                + "次重试，请求详情页链接: "
                                + tepDict.get("thread_url")
                            )
                            response = requests.get(
                                tepDict.get("thread_url"),
                                headers=self.headers(),
                                timeout=config.TIME_OUT,
                                verify=certifi.where(),
                            )
                            response.encoding = config.UTF8
                            if response.status_code != 200:
                                if i < 3:
                                    continue
                                else:
                                    return
                            else:
                                soup = BeautifulSoup(response.text, "lxml")
                                if not soup.find("span", id="thread_subject"):
                                    continue
                                else:
                                    break
                    tepDict["thread_title"] = soup.find(
                        "span", id="thread_subject"
                    ).text
                    tepDict["type"] = thread.get("type")
                    index = 0
                    try:
                        index1 = soup.find("td", class_="t_f").text.index("上映日期")
                    except Exception:
                        index1 = -1
                    try:
                        index2 = soup.find("td", class_="t_f").text.index("首　　播")
                    except Exception:
                        index2 = -1
                    try:
                        index3 = soup.find("td", class_="t_f").text.index("首播")
                    except Exception:
                        index3 = -1
                    try:
                        index4 = soup.find("td", class_="t_f").text.index("年　　代")
                    except Exception:
                        index4 = -1
                    if index1 > 0:
                        index = index1
                    elif index2 > 0:
                        index = index2
                    elif index3 > 0:
                        index = index3
                    elif index4 > 0:
                        index = index4
                    if index > 0:
                        tepDict["year"] = soup.find("td", class_="t_f").text[
                            index + 6 : index + 10
                        ]
                    tepDict["img_url"] = soup.find("div", class_="wzadr").find("img")[
                        "src"
                    ]
                    tepDict["video_format"] = self.rss_huazhi
                    inputs = soup.findAll(
                        "input", type="checkbox", class_="magnetinput"
                    )
                    if inputs:
                        ed2k_bluray_hdr = []
                        ed2k_webdl_hdr = []
                        ed2k_hdr = []
                        ed2k_bluray_sdr = []
                        ed2k_webdl_sdr = []
                        ed2k_sdr = []
                        ed2k_oth = []
                        # 遍历所有ed2k链接
                        for input in inputs:
                            ed2k = input["value"]
                            if (
                                ed2k.startswith("|file|")
                                and ed2k.endswith("|/")
                                and config.REMUX not in ed2k
                                and (
                                    (
                                        self.rss_huazhi == config.ONE
                                        and config.P1080 in ed2k
                                    )
                                    or (
                                        self.rss_huazhi == config.TWO
                                        and config.P2160 in ed2k
                                    )
                                )
                            ):
                                if config.BLURAY in ed2k and config.HDR in ed2k:
                                    ed2k_bluray_hdr.append("ed2k://" + ed2k)
                                elif config.WEBDL in ed2k and config.HDR in ed2k:
                                    ed2k_webdl_hdr.append("ed2k://" + ed2k)
                                elif config.HDR in ed2k:
                                    ed2k_hdr.append("ed2k://" + ed2k)
                                elif config.BLURAY in ed2k and config.SDR in ed2k:
                                    ed2k_bluray_sdr.append("ed2k://" + ed2k)
                                elif config.WEBDL in ed2k and config.SDR in ed2k:
                                    ed2k_webdl_sdr.append("ed2k://" + ed2k)
                                elif config.SDR in ed2k:
                                    ed2k_sdr.append("ed2k://" + ed2k)
                                else:
                                    ed2k_oth.append("ed2k://" + ed2k)
                        if ed2k_bluray_hdr:
                            tepDict["ed2k"] = ed2k_bluray_hdr
                        elif ed2k_webdl_hdr:
                            tepDict["ed2k"] = ed2k_webdl_hdr
                        elif ed2k_hdr:
                            tepDict["ed2k"] = ed2k_hdr
                        elif ed2k_bluray_sdr:
                            tepDict["ed2k"] = ed2k_bluray_sdr
                        elif ed2k_webdl_sdr:
                            tepDict["ed2k"] = ed2k_webdl_sdr
                        elif ed2k_sdr:
                            tepDict["ed2k"] = ed2k_sdr
                        elif ed2k_oth:
                            tepDict["ed2k"] = ed2k_oth
                        else:
                            tepDict["ed2k"] = []
                        # 电影只保留最后一项
                        if tepDict["ed2k"] and tepDict["type"] == config.DY:
                            tepDict["ed2k"][:] = [tepDict["ed2k"][-1]]
                    dls = soup.findAll("dl", class_="tattl", style=True)
                    if dls:
                        torrent_hdr = ""
                        torrent_sdr = ""
                        torrent_oth = ""
                        for dl in dls:
                            torrent_name = dl.find("p", class_="attnm").find("a").text
                            cl = dl.find("div", class_="dzlab_torrent cl")
                            if not cl:
                                continue
                            href = cl.find(
                                "a",
                                class_="torrent-btn",
                                href=re.compile(r"^javascript:setCopy"),
                            )["href"]
                            href_link = re.search(r"`(https?://[^\`]+)`", href).group(1)
                            if (
                                self.rss_huazhi == config.ONE
                                and config.P1080 in torrent_name
                                or self.rss_huazhi == config.TWO
                                and config.P2160 in torrent_name
                            ):
                                if config.HDR in torrent_name:
                                    torrent_hdr = href_link
                                elif config.SDR in torrent_name:
                                    torrent_sdr = href_link
                                else:
                                    torrent_oth = href_link
                            elif (
                                config.P1080 not in torrent_name
                                and config.P2160 not in torrent_name
                            ):
                                torrent_oth = href_link
                        if torrent_hdr:
                            tepDict["torrent"] = torrent_hdr.strip()
                        elif torrent_sdr:
                            tepDict["torrent"] = torrent_sdr.strip()
                        elif torrent_oth:
                            tepDict["torrent"] = torrent_oth.strip()
                        else:
                            tepDict["torrent"] = ""
                    detils_dict.append(tepDict)
                time.sleep(random.randint(config.TIME_SLEEP_BEG, config.TIME_SLEEP_END))
        return detils_dict

    # 获取视频列表
    def get_thread_list(self, type, order_date):
        # 获取搜索条件
        search_dict = self.search_dict(type)
        # 获取请求地址
        page_url = self.get_page_url(search_dict)
        # 获取总页数
        totlePage = self.get_totle_page(search_dict)
        # 命名视频列表
        tbodys = []
        threads = []

        if totlePage > 0:
            # 遍历每一页获取视频列表
            for page in range(1, totlePage + 1):
                temp_tbodys = []
                self.logger.info("请求列表链接: " + page_url + f"&page={page}")
                response = requests.get(
                    page_url + f"&page={page}",
                    headers=self.headers(),
                    timeout=config.TIME_OUT,
                    verify=certifi.where(),
                )
                # 确保响应内容的编码为 UTF-8
                response.encoding = config.UTF8
                if response.status_code != 200:
                    continue
                else:
                    soup = BeautifulSoup(response.text, "lxml")
                    # 重试机制
                    if not soup.find("div", id="threadlist"):
                        for i in range(1, config.RETRY_TIMES + 1):
                            time.sleep(
                                random.randint(
                                    config.TIME_SLEEP_BEG, config.TIME_SLEEP_END
                                )
                            )
                            self.logger.info(
                                "第"
                                + str(i)
                                + "次重试，请求链接: "
                                + page_url
                                + f"&page={page}"
                            )
                            response = requests.get(
                                page_url + f"&page={page}",
                                headers=self.headers(),
                                timeout=config.TIME_OUT,
                                verify=certifi.where(),
                            )
                            # 确保响应内容的编码为 UTF-8
                            response.encoding = config.UTF8
                            if response.status_code != 200:
                                if i < 3:
                                    continue
                                else:
                                    return
                            else:
                                soup = BeautifulSoup(response.text, "lxml")
                                if not soup.find("div", id="threadlist"):
                                    continue
                                else:
                                    break
                    temp_tbodys.extend(
                        soup.find("div", id="threadlist")
                        .find("table", id="threadlisttableid")
                        .find_all("tbody", id=re.compile(r"^normalthread_"))
                    )
                    if order_date == config.ALL:
                        tbodys.extend(temp_tbodys)
                        time.sleep(
                            random.randint(config.TIME_SLEEP_BEG, config.TIME_SLEEP_END)
                        )
                    else:
                        if temp_tbodys:
                            is_befor_data = False
                            for tbody in temp_tbodys:
                                tbody_date = (
                                    tbody.find_all("td", class_="by")[0]
                                    .find("em")
                                    .find("span")
                                    .text.split()[0]
                                )
                                if tbody_date == order_date:
                                    tbodys.append(tbody)
                                if datetime.strptime(
                                    tbody_date, config.FMT
                                ) < datetime.strptime(order_date, config.FMT):
                                    is_befor_data = True
                            if is_befor_data:
                                break
                            else:
                                time.sleep(
                                    random.randint(
                                        config.TIME_SLEEP_BEG, config.TIME_SLEEP_END
                                    )
                                )
            # 进一步过滤
            if tbodys:
                for tbody in tbodys:
                    thread = {}
                    xugeng = tbody.find("img", alt="续更")
                    wuzi = tbody.find("img", alt="无字")
                    check = 0
                    if any(s in tbody.text for s in config.BLACKLIST):
                        check = 1
                    if not xugeng and not wuzi and check == 0:
                        thread["type"] = type
                        thread["thread"] = tbody.find("td", class_="icn").find("a")[
                            "href"
                        ]
                        threads.append(thread)
        self.logger.info(f"获取到{len(threads)}个" + config.TYPE.get(type))
        return threads

    # 获取总页数
    def get_totle_page(self, dict):
        totlePage = 0
        try:
            # 获取总页数url
            page_url = self.get_page_url(dict)

            self.logger.info("请求总页数链接: " + page_url)

            # 发送HTTP请求获取页面内容
            response = requests.get(
                page_url,
                headers=self.headers(),
                timeout=config.TIME_OUT,
                verify=certifi.where(),
            )

            # 重试机制
            if response.status_code != 200:
                for i in range(1, config.RETRY_TIMES + 1):
                    time.sleep(
                        random.randint(config.TIME_SLEEP_BEG, config.TIME_SLEEP_END)
                    )
                    self.logger.info(
                        "第" + str(i) + "次重试，请求总页数链接: " + page_url
                    )
                    response = requests.get(
                        page_url,
                        headers=self.headers(),
                        timeout=config.TIME_OUT,
                        verify=certifi.where(),
                    )
                    if response.status_code != 200:
                        if i < 3:
                            continue
                        else:
                            return
                    else:
                        break
            if response.status_code != 200:
                self.set_cookie()
                self.logger.info("✅ 47BT网站重新登录成功")
                for i in range(4, config.RETRY_TIMES + 4):
                    time.sleep(
                        random.randint(config.TIME_SLEEP_BEG, config.TIME_SLEEP_END)
                    )
                    self.logger.info(
                        "第" + str(i) + "次重试，请求总页数链接: " + page_url
                    )
                    response = requests.get(
                        page_url,
                        headers=self.headers(),
                        timeout=config.TIME_OUT,
                        verify=certifi.where(),
                    )
                    if response.status_code != 200:
                        if i < 3:
                            continue
                        else:
                            return
                    else:
                        break
            if response.status_code != 200:
                self.logger.error("⚠️ 47BT网站异常，请稍后再试", True)
                return totlePage

            # 确保响应内容的编码为 UTF-8
            response.encoding = config.UTF8
            # 使用BeautifulSoup解析页面内容
            soup = BeautifulSoup(response.text, "lxml")
            # 找不到页数显示则直接返回1
            page_span = soup.find("span", id="fd_page_bottom").find("span", title=True)
            if page_span:
                totlePage = int(
                    re.search(
                        r"共\s*(\d+)\s*页",
                        page_span["title"],
                    ).group(1)
                )
            else:
                totlePage = 1
            self.logger.info("总页数：" + str(totlePage))
        except Exception as e:
            self.logger.error(f"获取总页数失败：{e}")
        return totlePage

    # 获取请求url
    def get_page_url(self, dict):
        page_url = config.URL + "/forum.php?mod=forumdisplay&fid=2&filter=sortid"
        if dict["sortid"]:
            page_url += f'&sortid={dict["sortid"]}'
        else:
            self.logger.error("请填写视频类型sortid")
        if dict["leixing"] or dict["nianfen"] or dict["diqu"] or dict["huazhi"]:
            page_url += "&searchsort=1"
            if dict["name"] == config.DY:
                if dict["leixing"]:
                    page_url += f'&dyleixing={dict["leixing"]}'
                if dict["nianfen"]:
                    page_url += f'&dynianfen={dict["nianfen"]}'
                if dict["diqu"]:
                    page_url += f'&dydiqu={dict["diqu"]}'
                if dict["huazhi"]:
                    page_url += f'&dyhuazhi={dict["huazhi"]}'
            elif dict["name"] == config.JJ:
                if dict["leixing"]:
                    page_url += f'&jjleixing={dict["leixing"]}'
                if dict["nianfen"]:
                    page_url += f'&jjnianfen={dict["nianfen"]}'
                if dict["diqu"]:
                    page_url += f'&jjdiqu={dict["diqu"]}'
                if dict["huazhi"]:
                    page_url += f'&jjhuazhi={dict["huazhi"]}'
            elif dict["name"] == config.DM:
                if dict["leixing"]:
                    page_url += f'&dmleixing={dict["leixing"]}'
                if dict["nianfen"]:
                    page_url += f'&dmnianfen={dict["nianfen"]}'
                if dict["diqu"]:
                    page_url += f'&dmdiqu={dict["diqu"]}'
                if dict["huazhi"]:
                    page_url += f'&dmhuazhi={dict["huazhi"]}'
            else:
                self.logger.error("请填写正确的视频名称name")
        return page_url

    # 获取检索条件
    def search_dict(self, name):
        dict = {}
        dict["name"] = name
        if name == config.DY:
            dict["sortid"] = "1"
        elif name == config.JJ:
            dict["sortid"] = "2"
        elif name == config.DM:
            dict["sortid"] = "3"
        dict["leixing"] = self.rss_leixing
        dict["nianfen"] = self.rss_nianfen
        dict["diqu"] = self.rss_diqu
        dict["huazhi"] = self.rss_huazhi
        return dict
