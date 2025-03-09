# 47bt.com订阅工具

## 更新日志：
### 2015/3/9 更新1.0.4版本
    - 完善/help帮助文档
    - 调整指令位置
### 2025/3/7 更新1.0.3版本
    - qBittorrent整合开关
    - 订阅信息整合延迟和定时
    - 新增订阅延迟
    - 视频提取逻辑优化
### 2025/3/4 更新1.0.2版本
    - 新增qBittorrent开关，打开开关还需配置
    - 新增磁力导出txt，一键导出至tg
### 2025/2/28 更新1.0.1版本
    - 初始化tg指令
    - 初步完成基本功能，可正常使用订阅


## 主要功能：
    - 47bt.com网站订阅，需自备网站cookie
    - telegram指令，需申请单独bot进行管理
    - 自定义订阅信息，如分类、画质、格式、延迟、定时等
    - 自定义qBittorrent下载，需配置qBittorrent主机地址、端口、用户名、密码等
    - 库中磁力导出txt

## docker部署命令：
    docker run -d \
        --name 47bt-rss \
        --network host \
        -e bot_token=<your_token> \
        -e chat_id=<your_chat_id> \
        -e http_proxy=<http代理可选> \
        -v <your_path>:/47bt-rss/data \
        --restart unless-stopped \
        47bt-rss:latest
    
## 免责声明
    - 本项目完全免费，仅限个人学习、研究和非商业用途。
    - 本项目开发者不对因使用本项目而可能导致的任何直接或间接后果负责。

## 赞赏
如果这个项目对你有帮助，不妨请我喝杯咖啡
如果你欣赏这个项目，欢迎为它点亮一颗⭐️
![donate](donate.png "donate")