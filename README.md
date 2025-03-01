# 计划清单：
    - 对接115网盘发送离线下载，等openapi稳定后
    - tgbot指令导出数据库存量磁链txt

# 更新日志：
## 2025/3/1 docker部署命令
    docker run -d \
        --name 47bt-rss \
        --network host \
        -e bot_token=<your_token> \
        -e chat_id=<your_chat_id> \
        -e http_proxy=<http代理可选> \
        -v <your_path>:/47bt-rss/data \
        --restart unless-stopped \
        47bt-rss:latest
## 2025/2/28 初始化版本
    - 支持47bt.com网站订阅，需自备网站cookie
    - 支持telegram指令，需申请单独bot进行管理
    - 支持自定义cron定时任务，如：0 2 * * *
    - 支持自定义订阅视频分类和画质
    - 支持发送磁力到qBittorrent下载，需qBittorrent主机地址、端口、用户名、密码