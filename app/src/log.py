import logging
import os
from logging.handlers import RotatingFileHandler
from . import config, telegram_msg


class ReverseFileHandler(RotatingFileHandler):
    """自定义文件处理器，将日志写入文件开头而不是末尾"""

    def __init__(
        self, filename, mode="a", maxBytes=0, backupCount=0, encoding=None, delay=False
    ):
        # 强制使用写入模式，这样每次都会从文件开头写入
        super().__init__(filename, "w", maxBytes, backupCount, encoding, delay)

    def emit(self, record):
        # 获取当前文件内容
        if os.path.exists(self.baseFilename):
            with open(self.baseFilename, "r", encoding=self.encoding) as f:
                existing_content = f.read()
        else:
            existing_content = ""

        # 格式化新日志行
        msg = self.format(record)

        # 将新内容写入文件开头，后面跟着原有内容
        with open(self.baseFilename, "w", encoding=self.encoding) as f:
            f.write(msg + self.terminator + existing_content)

        # 处理文件轮转
        if self.shouldRollover(record):
            self.doRollover()


class GlobalLogger:
    _instance = None  # 单例实例

    def __new__(cls, *args, **kwargs):
        # 确保全局只有一个实例
        if not cls._instance:
            cls._instance = super(GlobalLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        log_path=config.PATH + "/app/data/console.log",
        log_level=logging.INFO,
        encoding="UTF-8",
        max_bytes=10485760,
        backup_count=5,
    ):
        # 初始化TG消息
        self.msg = telegram_msg.TelegamMsg()

        # 防止重复初始化
        if self._initialized:
            return
        self._initialized = True

        # 创建日志记录器
        self.logger = logging.getLogger("GlobalLogger")
        self.logger.setLevel(log_level)  # 设置日志级别

        # 如果日志目录不存在，则创建
        log_dir = os.path.dirname(log_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 创建反向文件处理器
        handler = ReverseFileHandler(
            log_path, maxBytes=max_bytes, backupCount=backup_count, encoding=encoding
        )
        # 控制台输出日志（保持正常顺序）
        console_handler = logging.StreamHandler()

        # 根据日志等级输出不同格式日志
        formatter_str = ""
        if log_level == logging.DEBUG:
            formatter_str = "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] [%(funcName)s] %(message)s"
        else:
            formatter_str = "[%(asctime)s] [%(levelname)s] %(message)s"

        # 日志格式
        formatter = logging.Formatter(
            formatter_str,
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        # 设置日志格式
        handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 将处理器添加到日志记录器
        self.logger.addHandler(handler)
        self.logger.addHandler(console_handler)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str, send_tg: bool = False):
        self.logger.info(message)
        if send_tg:
            self.msg.send_message(message)

    def error(self, message: str, send_tg: bool = False):
        self.logger.error(message)
        if send_tg:
            self.msg.send_message(message)


# 调用示例
if __name__ == "__main__":
    # 初始化日志
    logger = GlobalLogger()

    # 使用日志
    logger.debug("这是一条调试信息")
    logger.info("这是一条普通信息")
    logger.warning("这是一条警告信息")
    logger.error("这是一条错误信息")
    logger.critical("这是一条严重错误信息")
