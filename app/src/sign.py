from . import log, bt47, config
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


class SIGN:

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.job = None
        self.logger = log.GlobalLogger()

    def start(self):
        self.job = self.scheduler.add_job(
            bt47.BT47().sign_in,
            CronTrigger(
                hour=config.SIGE_TIME.get("HOUR"),
                minute=config.SIGE_TIME.get("MINUTE"),
                second=config.SIGE_TIME.get("SECOND"),
            ),
        )
        self.scheduler.start()
        self.logger.info("签到任务已启动")

    def stop(self):
        if self.scheduler.running:
            self.scheduler.remove_job(self.job.id)  # 移除任务
            self.scheduler.shutdown(wait=False)  # 停止调度器
            self.logger.info("签到任务已停止")
