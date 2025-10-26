from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
)
import asyncio
import os
from dotenv import load_dotenv, set_key
from . import rss, config, export, log, bt47, sign
import warnings
from telegram.warnings import PTBUserWarning
import sys

# 屏蔽 PTBUserWarning 警告
warnings.filterwarnings("ignore", category=PTBUserWarning)


class TelegramBot:
    # 环境变量文件位置
    DOTENV_PATH = f"{config.PATH}/app/data/.env"
    # 定义对话处理器的状态
    (
        BT_USERNAME,
        BT_PASSWORD,
        BT_SIGN_SWITCH,
        PAN115_SWITCH,
        PAN115_COOKIE,
        PAN115_CID,
        QB_SWITCH,
        QB_HOST,
        QB_PORT,
        QB_USERNAME,
        QB_PASSWORD,
        RSS_JJ,
        RSS_DY,
        RSS_DM,
        RSS_HUAZHI,
        RSS_DELAY,
        RSS_CRON,
        RSS_HIS,
        EXPORT,
    ) = range(19)

    QB_DATA = {}
    RSS_DATA = {}

    def __init__(self):
        # 订阅机器人初始化
        self.rssbot = None
        self.signbot = None
        load_dotenv(
            dotenv_path=self.DOTENV_PATH,
            override=True,
            encoding="utf-8",
        )
        # 初始化日志
        self.logger = log.GlobalLogger()
        # 从环境变量中获取 Telegram Bot 的 Token
        self.bot_token = os.environ.get("bot_token", config.NONE)
        self.chat_id = os.environ.get("chat_id", config.NONE)
        self.http_proxy = os.environ.get("http_proxy", config.NONE)
        self.rss_status = os.environ.get("rss_status", config.STOP)
        self.sign_switch = os.environ.get("bt_sign_switch", config.OFF)
        try:
            # 初始化 Telegram Bot 应用
            self.application = (
                Application.builder()
                .token(self.bot_token)
                .proxy(self.http_proxy)
                .get_updates_proxy(self.http_proxy)
                .get_updates_read_timeout(30.0)  # 设置 get_updates 读取超时
                .get_updates_connect_timeout(30.0)  # 设置 get_updates 连接超时
                .get_updates_pool_timeout(30.0)  # 设置 get_updates 池超时
                .build()
            )
            # 设置命令处理器
            self.setup_handlers()
            # 初始化后设置命令菜单
            self.post_init()
        except Exception as e:
            self.logger.error(f"TelegramBot启动失败，失败原因：{e}")
            sys.exit()

    def setup_handlers(self):
        # 添加 start 命令处理器
        self.application.add_handler(CommandHandler("start", self.start))

        # 添加 help 命令处理器
        self.application.add_handler(CommandHandler("help", self.help))

        # 添加 bt 命令的对话处理器
        bt_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("set_bt", self.bt)],
            states={
                self.BT_USERNAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.bt_username_input
                    )
                ],
                self.BT_PASSWORD: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.bt_password_input
                    )
                ],
            },
            fallbacks=[],
        )
        self.application.add_handler(bt_conv_handler)

        # 添加 47bt 签到开关
        bt_sign_switch_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("set_bt_sign_switch", self.bt_sign_switch)],
            states={
                self.BT_SIGN_SWITCH: [CallbackQueryHandler(self.bt_sign_switch_input)],
            },
            fallbacks=[],
        )
        self.application.add_handler(bt_sign_switch_conv_handler)

        # 添加 pan115_switch 命令的对话处理器
        pan115_switch_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("set_pan115_switch", self.pan115_switch)],
            states={
                self.PAN115_SWITCH: [CallbackQueryHandler(self.pan115_switch_input)],
            },
            fallbacks=[],
        )
        self.application.add_handler(pan115_switch_conv_handler)

        # 添加 pan115 命令的对话处理器
        pan115_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("set_pan115", self.pan115)],
            states={
                self.PAN115_COOKIE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.pan115_cookie_input
                    )
                ],
                self.PAN115_CID: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.pan115_cid_input
                    )
                ],
            },
            fallbacks=[],
        )
        self.application.add_handler(pan115_conv_handler)

        # 添加 qb_switch 命令的对话处理器
        qb_switch_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("set_qb_switch", self.qb_switch)],
            states={
                self.QB_SWITCH: [CallbackQueryHandler(self.qb_switch_input)],
            },
            fallbacks=[],
        )
        self.application.add_handler(qb_switch_conv_handler)

        # 添加 qbittorrent 命令的对话处理器
        qbittorrent_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("set_qb", self.qb)],
            states={
                self.QB_HOST: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.qb_host_input)
                ],
                self.QB_PORT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.qb_port_input)
                ],
                self.QB_USERNAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.qb_username_input
                    )
                ],
                self.QB_PASSWORD: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.qb_password_input
                    )
                ],
            },
            fallbacks=[],
        )
        self.application.add_handler(qbittorrent_conv_handler)

        # 添加 rss 命令的对话处理器
        rss_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("set_rss", self.rss)],
            states={
                self.RSS_JJ: [CallbackQueryHandler(self.rss_jj_input)],
                self.RSS_DY: [CallbackQueryHandler(self.rss_dy_input)],
                self.RSS_DM: [CallbackQueryHandler(self.rss_dm_input)],
                self.RSS_HUAZHI: [CallbackQueryHandler(self.rss_huazhi_input)],
                self.RSS_DELAY: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.rss_delay_input
                    )
                ],
                self.RSS_CRON: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.rss_cron_input)
                ],
            },
            fallbacks=[],
        )
        self.application.add_handler(rss_conv_handler)
        # 添加 rss_start 命令处理器
        self.application.add_handler(CommandHandler("rss_start", self.rss_start))
        # 添加 rss_stop 命令处理器
        self.application.add_handler(CommandHandler("rss_stop", self.rss_stop))
        # 添加 get_conf 命令处理器
        self.application.add_handler(CommandHandler("get_conf", self.get_conf))

        # 添加 rss_his 命令处理器
        rss_his_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("rss_his", self.rss_his)],
            states={
                self.RSS_HIS: [CallbackQueryHandler(self.rss_his_input)],
            },
            fallbacks=[],
        )
        self.application.add_handler(rss_his_conv_handler)

        # 添加 export 命令处理器
        export_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("export", self.export)],
            states={
                self.EXPORT: [CallbackQueryHandler(self.export_input)],
            },
            fallbacks=[],
        )
        self.application.add_handler(export_conv_handler)

    def post_init(self):
        # 初始化后设置命令菜单
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.set_commands())

    async def set_commands(self):
        # 清空命令菜单
        await self.application.bot.delete_my_commands()
        # 设置 Telegram Bot 的命令菜单
        await self.application.bot.set_my_commands(
            [
                ("start", "初始化"),
                ("help", "配置帮助"),
                ("set_bt", "设置网站"),
                ("set_bt_sign_switch", "签到开关"),
                ("set_pan115_switch", "115开关"),
                ("set_pan115", "设置115"),
                ("set_qb_switch", "QB开关"),
                ("set_qb", "设置QB"),
                ("set_rss", "设置订阅"),
                ("rss_start", "开始订阅"),
                ("rss_stop", "停止订阅"),
                ("get_conf", "获取配置"),
                ("rss_his", "历史订阅"),
                ("export", "导出磁力"),
            ]
        )

    async def start(self, update: Update, context):
        # 处理 start 命令，显示欢迎信息和可用命令
        await update.message.reply_text(
            "欢迎使用47BT订阅机器人，首次使用请 /help 查看帮助文档"
        )

    async def help(self, update: Update, context):
        # 处理 help 命令，显示帮助文档
        msg = "📢 指令菜单 📢\n"
        msg += "\n"
        msg += "⚠️ 首次使用需配置前7步\n"
        msg += "⚠️ 配置生效需重启订阅\n"
        msg += "⚠️ 订阅年份仅限2000年及以后\n"
        msg += "⚠️ 订阅已屏蔽以下类型：\n"
        msg += "    情涩、青涩、同性\n"
        msg += "\n"
        msg += "一 /set_bt\n"
        msg += "    配置47bt.com网站账号密码\n"
        msg += "二 /set_bt_sign_switch\n"
        msg += "    网站签到开关，可选，默认关\n"
        msg += "三 /set_pan115_switch\n"
        msg += "    115离线开关，优先于qb，可选\n"
        msg += "四 /set_pan115\n"
        msg += "    配置115离线下载\n"
        msg += "    信息不完整则取消发送\n"
        msg += "五 /set_qb_switch\n"
        msg += "    qbittorrent开关，可选，默认关\n"
        msg += "六 /set_qb\n"
        msg += "    配置qbittorrent发送下载\n"
        msg += "    信息不完整则取消发送\n"
        msg += "七 /set_rss\n"
        msg += "    配置订阅信息\n"
        msg += "    cron格式：0 2 * * *\n"
        msg += "    延迟天数：大于等于1\n"
        msg += "八 /rss_start\n"
        msg += "    开始订阅\n"
        msg += "九 /rss_stop\n"
        msg += "    停止订阅\n"
        msg += "十 /get_conf\n"
        msg += "    查看配置是否完整\n"
        msg += "十一 /rss_his\n"
        msg += "    历史订阅，获取全部日期视频\n"
        msg += "    仅需运行一次，且会清空库\n"
        msg += "十二 /export\n"
        msg += "    导出当前库中所有链接\n"
        msg += "    可选：ed2k、torrent\n"
        msg += "\n"
        msg += "🙏 欢迎星标或赞赏，感谢使用！\n"
        await update.message.reply_text(msg)

    async def bt(self, update: Update, context):
        # 处理 bt 命令，请求用户输入 bt_username
        await update.message.reply_text("🔔 请输入网站账号：")
        return self.BT_USERNAME

    async def bt_username_input(self, update: Update, context):
        # 处理用户输入的 bt_username
        context.user_data["bt_username"] = update.message.text
        # 请求用户输入 bt_password
        await update.message.reply_text("🔔 请输入网站密码：")
        return self.BT_PASSWORD

    async def bt_password_input(self, update: Update, context):
        # 处理用户输入的 bt_password
        context.user_data["bt_password"] = update.message.text
        # 数据存入.env中
        set_key(self.DOTENV_PATH, "bt_username", context.user_data["bt_username"])
        set_key(self.DOTENV_PATH, "bt_password", context.user_data["bt_password"])
        load_dotenv(
            dotenv_path=self.DOTENV_PATH,
            override=True,
            encoding="utf-8",
        )
        await update.message.reply_text("✅ 配置网站完成")
        # 缓存47bt网站cookie
        bt47.BT47().set_cookie()
        return ConversationHandler.END

    async def bt_sign_switch(self, update: Update, context):
        # 处理 47bt 签到命令
        keyboard = [
            [
                InlineKeyboardButton(config.ON_TEXT, callback_data=config.ON),
                InlineKeyboardButton(config.OFF_TEXT, callback_data=config.OFF),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🔔 网站签到开关？", reply_markup=reply_markup)
        return self.BT_SIGN_SWITCH

    async def bt_sign_switch_input(self, update: Update, context):
        # 处理用户输入的 bt_sign_switch 选项
        query = update.callback_query
        await query.answer()
        msg = ""
        if query.data == config.ON:
            msg = "✅ 网站签到已开启"
            if not self.signbot:
                if self.check_sign_data():
                    self.signbot = sign.SIGN()
                    self.signbot.start()
                    set_key(self.DOTENV_PATH, "bt_sign_switch", config.ON)
                    load_dotenv(
                        dotenv_path=self.DOTENV_PATH,
                        override=True,
                        encoding="utf-8",
                    )
                    bt47.BT47().sign_in()
                else:
                    await update.message.reply_text("⚠️ 请先完成网站基本配置")
        else:
            msg = "✅ 网站签到已关闭"
            if self.signbot:
                self.signbot.stop()
                self.signbot = None
                set_key(self.DOTENV_PATH, "bt_sign_switch", config.OFF)
        await query.edit_message_text(msg)
        return ConversationHandler.END

    async def pan115_switch(self, update: Update, context):
        # 处理 pan115_switch 命令
        keyboard = [
            [
                InlineKeyboardButton(config.ON_TEXT, callback_data=config.ON),
                InlineKeyboardButton(config.OFF_TEXT, callback_data=config.OFF),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🔔 115离线开关？", reply_markup=reply_markup)
        return self.PAN115_SWITCH

    async def pan115_switch_input(self, update: Update, context):
        # 处理用户输入的 pan115_switch 选项
        query = update.callback_query
        await query.answer()
        set_key(self.DOTENV_PATH, "pan115_switch", query.data)
        msg = ""
        if query.data == config.ON:
            msg = "✅ 115离线已开启"
        else:
            msg = "✅ 115离线已关闭"
        await query.edit_message_text(msg)
        return ConversationHandler.END

    async def pan115(self, update: Update, context):
        # 处理 pan115 命令，请求用户输入 pan115_cookie
        await update.message.reply_text("🔔 请输入115云盘cookie：")
        return self.PAN115_COOKIE

    async def pan115_cookie_input(self, update: Update, context):
        # 处理用户输入的 pan115_cookie
        context.user_data["pan115_cookie"] = update.message.text
        await update.message.reply_text("🔔 请输入115云盘离线文件夹cid：")
        return self.PAN115_CID

    async def pan115_cid_input(self, update: Update, context):
        # 处理用户输入的 pan115_cid
        context.user_data["pan115_cid"] = update.message.text
        # 数据存入.env中
        set_key(self.DOTENV_PATH, "pan115_cookie", context.user_data["pan115_cookie"])
        set_key(self.DOTENV_PATH, "pan115_cid", context.user_data["pan115_cid"])
        await update.message.reply_text("✅ 配置115云下载完成")
        return ConversationHandler.END

    async def qb_switch(self, update: Update, context):
        # 处理 qb_switch 命令
        keyboard = [
            [
                InlineKeyboardButton(config.ON_TEXT, callback_data=config.ON),
                InlineKeyboardButton(config.OFF_TEXT, callback_data=config.OFF),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🔔 qBittorrent下载器开关？", reply_markup=reply_markup
        )
        return self.QB_SWITCH

    async def qb_switch_input(self, update: Update, context):
        # 处理用户输入的 qb_switch 选项
        query = update.callback_query
        await query.answer()
        set_key(self.DOTENV_PATH, "qb_switch", query.data)
        msg = ""
        if query.data == config.ON:
            msg = "✅ qBittorrent 已开启"
        else:
            msg = "✅ qBittorrent 已关闭"
        await query.edit_message_text(msg)
        return ConversationHandler.END

    async def qb(self, update: Update, context):
        # 处理 qbittorrent 命令，请求用户输入 qBittorrent 主机地址
        await update.message.reply_text("🔔 请输入 qBittorrent 主机地址：")
        return self.QB_HOST

    async def qb_host_input(self, update: Update, context):
        # 处理用户输入的 qBittorrent 主机地址
        context.user_data["qb_host"] = update.message.text
        await update.message.reply_text("🔔 请输入 qBittorrent 端口：")
        return self.QB_PORT

    async def qb_port_input(self, update: Update, context):
        # 处理用户输入的 qBittorrent 端口
        context.user_data["qb_port"] = update.message.text
        await update.message.reply_text("🔔 请输入 qBittorrent 用户名：")
        return self.QB_USERNAME

    async def qb_username_input(self, update: Update, context):
        # 处理用户输入的 qBittorrent 用户名
        context.user_data["qb_username"] = update.message.text
        await update.message.reply_text("🔔 请输入 qBittorrent 密码：")
        return self.QB_PASSWORD

    async def qb_password_input(self, update: Update, context):
        # 处理用户输入的 qBittorrent 密码
        context.user_data["qb_password"] = update.message.text
        # 数据存入.env中
        set_key(self.DOTENV_PATH, "qb_host", context.user_data["qb_host"])
        set_key(self.DOTENV_PATH, "qb_port", context.user_data["qb_port"])
        set_key(self.DOTENV_PATH, "qb_username", context.user_data["qb_username"])
        set_key(self.DOTENV_PATH, "qb_password", context.user_data["qb_password"])
        # 在这里处理 qBittorrent 输入
        await update.message.reply_text("✅ 配置 qBittorrent 下载器完成")
        return ConversationHandler.END

    async def rss(self, update: Update, context):
        # 处理 rss 命令，请求用户选择 rss_jj 的选项
        keyboard = [
            [
                InlineKeyboardButton(config.YES_TEXT, callback_data=config.ONE),
                InlineKeyboardButton(config.NO_TEXT, callback_data=config.ZERO),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🔔 启用剧集订阅？", reply_markup=reply_markup)
        return self.RSS_JJ

    async def rss_jj_input(self, update: Update, context):
        # 处理用户输入的 rss_jj 选项
        query = update.callback_query
        await query.answer()
        context.user_data["rss_jj"] = query.data
        keyboard = [
            [
                InlineKeyboardButton(config.YES_TEXT, callback_data=config.ONE),
                InlineKeyboardButton(config.NO_TEXT, callback_data=config.ZERO),
            ]
        ]
        await query.edit_message_text(
            text="🔔 启用电影订阅？", reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return self.RSS_DY

    async def rss_dy_input(self, update: Update, context):
        # 处理用户输入的 rss_dy 选项
        query = update.callback_query
        await query.answer()
        context.user_data["rss_dy"] = query.data
        keyboard = [
            [
                InlineKeyboardButton(config.YES_TEXT, callback_data=config.ONE),
                InlineKeyboardButton(config.NO_TEXT, callback_data=config.ZERO),
            ]
        ]
        await query.edit_message_text(
            text="🔔 启用动漫订阅？", reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return self.RSS_DM

    async def rss_dm_input(self, update: Update, context):
        # 处理用户输入的 rss_dm 选项
        query = update.callback_query
        await query.answer()
        context.user_data["rss_dm"] = query.data
        keyboard = [
            [
                InlineKeyboardButton(config.P1080, callback_data=config.ONE),
                InlineKeyboardButton(config.P2160, callback_data=config.TWO),
            ]
        ]
        await query.edit_message_text(
            text="🔔 订阅画质选择？", reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return self.RSS_HUAZHI

    async def rss_huazhi_input(self, update: Update, context):
        # 处理用户输入的 rss_huazhi 选项
        query = update.callback_query
        await query.answer()
        context.user_data["rss_huazhi"] = query.data
        await query.edit_message_text("🔔 订阅延迟天数：")
        return self.RSS_DELAY

    async def rss_delay_input(self, update: Update, context):
        # 处理用户输入的 rss_delay 选项
        rss_delay = update.message.text
        context.user_data["rss_delay"] = rss_delay

        await update.message.reply_text("🔔 订阅 cron 定时：")
        return self.RSS_CRON

    async def rss_cron_input(self, update: Update, context):
        # 处理用户输入的 rss_cron 选项
        rss_delay = update.message.text
        context.user_data["rss_cron"] = rss_delay
        # 数据存入.env中
        set_key(self.DOTENV_PATH, "rss_jj", context.user_data["rss_jj"])
        set_key(self.DOTENV_PATH, "rss_dy", context.user_data["rss_dy"])
        set_key(self.DOTENV_PATH, "rss_dm", context.user_data["rss_dm"])
        set_key(self.DOTENV_PATH, "rss_huazhi", context.user_data["rss_huazhi"])
        set_key(self.DOTENV_PATH, "rss_delay", context.user_data["rss_delay"])
        set_key(self.DOTENV_PATH, "rss_cron", context.user_data["rss_cron"])
        await update.message.reply_text("✅ 配置订阅完成")
        return ConversationHandler.END

    async def get_conf(self, update: Update, context):
        load_dotenv(
            dotenv_path=self.DOTENV_PATH,
            override=True,
            encoding="utf-8",
        )
        # 处理 start 命令，显示欢迎信息和可用命令
        msg = "⭐️详细配置如下⭐️\n\n"
        msg += "网站账号：" + os.environ.get("bt_username", config.NONE_TEXT) + "\n"
        msg += "网站密码：" + os.environ.get("bt_password", config.NONE_TEXT) + "\n"
        msg += (
            "签到开关："
            + config.SWITCH.get(os.environ.get("bt_sign_switch", config.OFF))
            + "\n"
        )
        msg += "\n"
        msg += (
            "云盘开关："
            + config.SWITCH.get(os.environ.get("pan115_switch", config.OFF))
            + "\n"
        )
        if not os.environ.get("pan115_cookie", config.NONE):
            msg += "云盘CK：" + config.NONE_TEXT + "\n"
        else:
            msg += "云盘CK：# # # # # #\n"
        msg += "云盘路径：" + os.environ.get("pan115_cid", config.NONE_TEXT) + "\n"
        msg += "\n"
        msg += (
            "QB开关："
            + config.SWITCH.get(os.environ.get("qb_switch", config.OFF))
            + "\n"
        )
        msg += "QB地址：" + os.environ.get("qb_host", config.NONE_TEXT) + "\n"
        msg += "QB端口：" + os.environ.get("qb_port", config.NONE_TEXT) + "\n"
        msg += "QB用户：" + os.environ.get("qb_username", config.NONE_TEXT) + "\n"
        msg += "QB密码：" + os.environ.get("qb_password", config.NONE_TEXT) + "\n"
        msg += "\n"
        msg += (
            "订阅状态："
            + config.STATUS.get(os.environ.get("rss_status", config.NONE))
            + "\n"
        )
        msg += (
            "订阅剧集：" + config.IF.get(os.environ.get("rss_jj", config.NONE)) + "\n"
        )
        msg += (
            "订阅电影：" + config.IF.get(os.environ.get("rss_dy", config.NONE)) + "\n"
        )
        msg += (
            "订阅动漫：" + config.IF.get(os.environ.get("rss_dm", config.NONE)) + "\n"
        )
        msg += (
            "订阅画质："
            + config.IQ.get(os.environ.get("rss_huazhi", config.NONE))
            + "\n"
        )
        msg += "订阅延时：" + os.environ.get("rss_delay", config.NONE_TEXT) + "\n"
        msg += "订阅定时：" + os.environ.get("rss_cron", config.NONE_TEXT) + "\n"
        await update.message.reply_text(msg)

    async def rss_his(self, update: Update, context):
        # 处理 rss 命令，请求用户选择 rss_jj 的选项
        keyboard = [
            [
                InlineKeyboardButton(config.YES_TEXT, callback_data=config.ONE),
                InlineKeyboardButton(config.NO_TEXT, callback_data=config.ZERO),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🔔 确认历史订阅？", reply_markup=reply_markup)
        return self.RSS_HIS

    async def rss_his_input(self, update: Update, context):
        # 处理用户输入的 rss_huazhi 选项
        query = update.callback_query
        await query.answer()
        if query.data == config.ONE:
            load_dotenv(
                dotenv_path=self.DOTENV_PATH,
                override=True,
                encoding="utf-8",
            )
            if self.rssbot:
                await query.edit_message_text("⚠️ 有订阅任务正在进行中...")
            else:
                if self.check_rss_data():
                    await query.edit_message_text("✅ 开始历史订阅")
                    rss.Rss().spider(False)
                    await query.edit_message_text("✅ 历史订阅已完成")
                else:
                    await query.edit_message_text("⚠️ 请先完成订阅基本配置")
        elif query.data == config.ZERO:
            await query.edit_message_text("✅ 撤销历史订阅")

    async def rss_start(self, update: Update, context):
        load_dotenv(
            dotenv_path=self.DOTENV_PATH,
            override=True,
            encoding="utf-8",
        )
        if self.rssbot:
            await update.message.reply_text("⚠️ 有订阅任务正在进行中...")
        else:
            if self.check_rss_data():
                self.rssbot = rss.Rss()
                self.rssbot.start()
                set_key(self.DOTENV_PATH, "rss_status", config.RUNNING)
                await update.message.reply_text("✅ 开始订阅任务")
            else:
                await update.message.reply_text("⚠️ 请先完成订阅基本配置")

    async def rss_stop(self, update: Update, context):
        if self.rssbot:
            self.rssbot.stop()
            self.rssbot = None
            set_key(self.DOTENV_PATH, "rss_status", config.STOP)
            await update.message.reply_text("✅ 结束订阅任务")
        else:
            await update.message.reply_text("⚠️ 无订阅任务")

    # 订阅数据校验
    def check_rss_data(self):
        bt_username = os.environ.get("bt_username", config.NONE)
        bt_password = os.environ.get("bt_password", config.NONE)
        rss_jj = os.environ.get("rss_jj", config.NONE)
        rss_dy = os.environ.get("rss_dy", config.NONE)
        rss_dm = os.environ.get("rss_dm", config.NONE)
        rss_huazhi = os.environ.get("rss_huazhi", config.NONE)
        rss_delay = os.environ.get("rss_delay", config.NONE)
        rss_cron = os.environ.get("rss_cron", config.NONE)
        if (
            not bt_username
            or not bt_password
            or not rss_jj
            or not rss_dy
            or not rss_dm
            or not rss_huazhi
            or not rss_delay
            or not rss_cron
        ):
            return False
        else:
            return True

    # 网站数据校验
    def check_sign_data(self):
        bt_username = os.environ.get("bt_username", config.NONE)
        bt_password = os.environ.get("bt_password", config.NONE)

        if not bt_username or not bt_password:
            return False
        else:
            return True

    async def export(self, update: Update, context):
        # 处理 export 命令
        keyboard = [
            [
                InlineKeyboardButton(config.ED2K, callback_data=config.ED2K),
                InlineKeyboardButton(config.TORRENT, callback_data=config.TORRENT),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🔔 请选择导出类型：", reply_markup=reply_markup
        )
        return self.EXPORT

    async def export_input(self, update: Update, context):
        # 处理用户输入的 export 选项
        query = update.callback_query
        await query.answer()
        # 导出文件
        await export.Export().export_txt(query.data)
        path = f"{config.PATH}/app/data/{query.data}.txt"
        await query.edit_message_text("✅ 导出成功")
        # 发送文件
        with open(path, "rb") as file:
            await context.bot.send_document(chat_id=self.chat_id, document=file)
        return ConversationHandler.END

    def run(self):
        self.logger.info(
            f"欢迎使用47BT订阅机器人，当前版本{config.VERSION}，首次使用请 /help 查看帮助文档",
            True,
        )
        bt47.BT47().set_cookie()
        if self.sign_switch == config.ON:
            self.signbot = sign.SIGN()
            self.signbot.start()
            self.logger.info(
                "✅ 网站签到任务已恢复",
                True,
            )
        if self.rss_status == config.RUNNING:
            self.rssbot = rss.Rss()
            self.rssbot.start()
            self.logger.info(
                "✅ 订阅任务已恢复，状态为：" + config.STATUS.get(self.rss_status),
                True,
            )
        # 启动 Telegram Bot
        self.application.run_polling(
            poll_interval=1.0,  # 轮询间隔（秒）
            timeout=30.0,  # 轮询超时时间
            drop_pending_updates=True,  # 启动时丢弃待处理的更新
        )
