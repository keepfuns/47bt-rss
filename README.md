# 更新日志：
## 2025/3/4 上线1.0.2版本
    - 新增qBittorrent开关，打开开关还需配置
    - 新增磁力导出txt，一键导出至tg
## 2025/2/28 上线1.0.1版本
    - 初始化tg指令
    - 初步完成基本功能，可正常使用订阅


# 主要功能：
    - 47bt.com网站订阅，需自备网站cookie
    - telegram指令，需申请单独bot进行管理
    - 自定义cron定时任务订阅视频，如：0 2 * * *
    - 自定义订阅视频分类和画质，如2K、4K
    - qBittorrent开关，可发送磁力到qBittorrent下载，需配置qBittorrent主机地址、端口、用户名、密码
    - 库中磁力导出txt，可选画质优先度，如：HDR、SDR、OTHER

# docker部署命令：
    docker run -d \
        --name 47bt-rss \
        --network host \
        -e bot_token=<your_token> \
        -e chat_id=<your_chat_id> \
        -e http_proxy=<http代理可选> \
        -v <your_path>:/47bt-rss/data \
        --restart unless-stopped \
        47bt-rss:latest