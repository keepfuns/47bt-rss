from src import config, telegram_bot, log
import os

logger = log.GlobalLogger()
# 环境变量文件位置
path = config.PATH + "/app/data/.env"
# 获取必须环境变量
bot_token = os.environ.get("bot_token", config.NONE)
chat_id = os.environ.get("chat_id", config.NONE)
if bot_token and chat_id:
    # 确保目录存在，如果不存在则创建目录
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # 初始化环境变量文件
    open(path, "a", encoding="utf-8")
    # 启动机器人
    bot = telegram_bot.TelegramBot()
    bot.run()
else:
    logger.error("请配置bot_token和chat_id环境变量")
