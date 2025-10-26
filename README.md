## 简介
`47bt.com订阅工具，订阅网站视频，自动下载`

## 主要功能：
**网站签到**：默认每天0点1分签到，重开开关立即签到一次<br/>
**TG指令**：所有操作均可指令完成，实现远程操控<br/>
**视频订阅**：可订阅分类、画质、延迟、定时等<br/>
**115离线**：订阅视频自动发送115离线下载，不支持历史订阅<br/>
**QB下载**：订阅视频自动发送QB下载，不支持历史订阅<br/>
**追更订阅**：按订阅配置，追更订阅，可手动开始或停止订阅任务<br/>
**历史订阅**：按订阅配置，订阅所有时间的视频<br/>
**磁力导出**：磁力链接导出到TXT，并发送至TG<br/>

## 部署命令：
```
docker run -d \
    --name 47bt-rss \
    --network bridge \
    -e bot_token=<your_bot_token> \
    -e chat_id=<your_chat_id> \
    -e http_proxy=<http代理可选> \
    -v <your_path>:/app/data \
    --restart always \
    47bt-rss:latest
```

## 免责声明
- 本项目完全免费，仅限个人学习、研究和非商业用途
- 本项目开发者不对因使用本项目而可能导致的任何直接或间接后果负责

## 赞赏
- 如果您欣赏本项目，欢迎为它点亮一颗⭐️
- 如果本项目对您有帮助，不妨请我喝杯咖啡
<br/><br/>
<span><img src="assets/zhifubao.png" alt="支付宝" width="20%" align="left">
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src="assets/weixin.png" alt="微信 " width="20%" align="left"></span>