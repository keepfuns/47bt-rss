VERSION = "V1.1.2"
PATH = ""  # 全局路径
URL = "https://47bt.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
JJ_TEXT = "剧集"
JJ = "jj"
DY_TEXT = "电影"
DY = "dy"
DM_TEXT = "动漫"
DM = "dm"
TWO = "2"
YES_TEXT = "是"
ONE = "1"
NO_TEXT = "否"
ZERO = "0"
ON_TEXT = "开"
ON = "on"
OFF_TEXT = "关"
OFF = "off"
RUNNING_TEXT = "进行中"
RUNNING = "running"
STOP_TEXT = "已停止"
STOP = "stop"
ALL_TEXT = "不限"
ALL = "all"
NONE_TEXT = "未配置"
NONE = ""
ED2K = "ed2k"
TORRENT = "torrent"
P1080 = "1080p"
P2160 = "2160p"
HDR = "HDR"
SDR = "SDR"
WEBDL = "WEB-DL"
BLURAY = "BluRay"
REMUX = "REMUX"
RETRY_TIMES = 3  # 重试次数
TIME_OUT = 60  # 超时时间（秒）
UTF8 = "utf-8"
TIME_SLEEP_BEG = 5  # 休眠时间（秒）
TIME_SLEEP_END = 8  # 休眠时间（秒）
FMT = "%Y-%m-%d"  # 时间格式
IF = {ONE: YES_TEXT, ZERO: NO_TEXT, NONE: NONE_TEXT}  # 是否
IQ = {ONE: P1080, TWO: P2160, NONE: NONE_TEXT}  # 视频画质
SWITCH = {ON: ON_TEXT, OFF: OFF_TEXT, NONE: OFF_TEXT}  # 开关
STATUS = {RUNNING: RUNNING_TEXT, STOP: STOP_TEXT, NONE: STOP_TEXT}  # 状态
TYPE = {JJ: JJ_TEXT, DY: DY_TEXT, DM: DM_TEXT}  # 视频分类
BLACKLIST = [
    "更早",
    "情涩",
    "青涩",
    "同性",
]  # 视频类型黑名单
SIGE_TIME = {"HOUR": "0", "MINUTE": "1", "SECOND": "0"}  # 每天签到时间
