import os
from datetime import datetime, timedelta
from . import (
    config,
    bt47,
    database,
    pan115_client,
    qbittorrent_bot,
    log,
)
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import json


class Rss:

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.database = database.Database()
        self.bt47 = bt47.BT47()
        self.job = None
        self.pan115 = pan115_client.Pan115Client()
        self.qb = qbittorrent_bot.QbittorrenBot()
        self.logger = log.GlobalLogger()

        # 加载环境变量
        self.rss_jj = os.environ.get("rss_jj", config.ZERO)
        self.rss_dy = os.environ.get("rss_dy", config.ZERO)
        self.rss_dm = os.environ.get("rss_dm", config.ZERO)
        self.rss_cron = os.environ.get("rss_cron", config.NONE)
        self.rss_delay = os.environ.get("rss_delay", config.NONE)
        self.pan115_switch = os.environ.get("pan115_switch", config.OFF)
        self.qb_switch = os.environ.get("qb_switch", config.OFF)

    def start(self):
        self.job = self.scheduler.add_job(
            self.spider, CronTrigger.from_crontab(self.rss_cron)
        )
        self.scheduler.start()

    def stop(self):
        if self.scheduler.running:
            self.scheduler.remove_job(self.job.id)  # 移除任务
            self.scheduler.shutdown(wait=False)  # 停止调度器

    # check_renew：Ture追更，False历史
    def spider(self, check_renew: bool = True):
        # 定义变量
        messages = []
        start_time = datetime.now()
        threads = []
        details = []
        order_data = config.ALL

        # 历史订阅清空数据库
        if not check_renew:
            self.database.clear()

        # 计算延迟后日期
        if check_renew:
            order_data = (
                (
                    (datetime.now() - timedelta(days=float(self.rss_delay))).strftime(
                        "%Y-%m-%d"
                    )
                )
                .replace("-0", "-")
                .replace("-", "-", 1)
            )
            self.logger.info(
                "订阅延时：" + self.rss_delay + "，订阅时间：" + order_data
            )
        if self.rss_jj == config.ONE:
            self.logger.info("开始提取剧集")
            threads.extend(self.bt47.get_thread_list(config.JJ, order_data))
            self.logger.info("提取剧集完成")
        if self.rss_dy == config.ONE:
            self.logger.info("开始提取电影")
            threads.extend(self.bt47.get_thread_list(config.DY, order_data))
            self.logger.info("提取电影完成")
        if self.rss_dm == config.ONE:
            self.logger.info("开始提取动漫")
            threads.extend(self.bt47.get_thread_list(config.DM, order_data))
            self.logger.info("提取动漫完成")
        if threads:
            details.extend(self.bt47.get_thread_detail(threads))
            self.logger.info(f"总共提取到视频数量：{len(details)}")

        end_time = datetime.now()
        totle_time = int((end_time - start_time).total_seconds())
        self.logger.info(f"提取结束，耗时为：{totle_time}秒")
        messages.append(f"提取耗时{totle_time}秒，")

        if details:
            messages.append(f"提取视频{len(details)}条，具体如下所示：\n")
            threads = []
            ed2ks = []
            torrents = []
            all_torrents = []
            type = ""

            for detail in details:
                # 整理入库数据
                threads.append(
                    [
                        detail.get("thread_url"),
                        detail.get("thread_title"),
                        detail.get("type"),
                        detail.get("year"),
                        detail.get("video_format"),
                        detail.get("img_url"),
                        json.dumps(detail.get("ed2k")),
                        detail.get("torrent"),
                        datetime.now().strftime("%Y-%m-%d"),
                        datetime.now().strftime("%Y-%m-%d"),
                    ]
                )
                # 提取需要的ed2k和torrent
                if detail.get("ed2k"):
                    ed2ks.extend(detail.get("ed2k"))
                elif detail.get("torrent"):
                    torrents.append(detail.get("torrent"))
                all_torrents.append(detail.get("torrent"))
                # 整理TG消息
                if detail.get("type") != type:
                    type = detail.get("type")
                    messages.append(f"\n{config.TYPE.get(detail.get('type'))}：\n")
                messages.append(f"  {detail.get('thread_title')}\n")

            # 统一发送TG消息
            if check_renew:
                self.logger.info("".join(messages), True)
            else:
                self.logger.info(f"历史订阅共提取视频{len(details)}条", True)
            # 统一写入数据库
            if threads:
                self.database.update_batch(threads)
            # 统一发送115下载
            if ed2ks and check_renew and self.pan115_switch == config.ON:
                self.pan115.send_ed2ks(ed2ks)
            # 统一发送qb下载
            if torrents and check_renew and self.qb_switch == config.ON:
                # 115离线优先于qb下载
                if self.pan115_switch == config.ON:
                    self.qb.send_torrents(torrents)
                else:
                    self.qb.send_torrents(all_torrents)
        else:
            messages.append("共提取视频0条")
            # 统一发送TG消息
            if check_renew:
                self.logger.info("".join(messages), True)
            else:
                self.logger.info("历史订阅共提取视频0条", True)
