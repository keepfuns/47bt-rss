# 47bt.com订阅工具
通过订阅网站视频，解放双手，全自动下载，实现自动更新媒体库
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

&nbsp;&nbsp;&nbsp;&nbsp;**TG指令**：所有操作均可指令完成，实现远程操控<br/>
&nbsp;&nbsp;&nbsp;&nbsp;**视频订阅**：可订阅分类、画质、格式、延迟、定时等<br/>
&nbsp;&nbsp;&nbsp;&nbsp;**QB下载**：订阅视频自动发送QB下载，不支持历史订阅<br/>
&nbsp;&nbsp;&nbsp;&nbsp;**追更订阅**：按订阅配置，追更订阅，可手动开始或停止订阅任务<br/>
&nbsp;&nbsp;&nbsp;&nbsp;**历史订阅**：按订阅配置，订阅所有时间的视频<br/>
&nbsp;&nbsp;&nbsp;&nbsp;**磁力导出**：磁力链接导出到TXT，并发送至TG<br/>
## 部署命令：
```
docker run -d \
    --name 47bt-rss \
    --network host \
    -e bot_token=<your_bot_token> \
    -e chat_id=<your_chat_id> \
    -e http_proxy=<http代理可选> \
    -v <your_path>:/47bt-rss/data \
    --restart unless-stopped \
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