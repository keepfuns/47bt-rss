import os
from . import config, database, log


class Export:
    def __init__(self):
        self.database = database.Database()
        self.logger = log.GlobalLogger()
        self.path = config.PATH + "/app/data"
        # 确保目录存在，如果不存在则创建目录
        os.makedirs(self.path, exist_ok=True)

    async def export_txt(self, type: str):
        file_path = self.path + "/" + type + ".txt"
        links = self.database.export()
        # 检查并删除文件
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except PermissionError:
                self.logger.error(f"权限不足，无法删除 {file_path}")
            except Exception as e:
                self.logger.error(f"未知错误：{e}")

        # 数据写到txt文件
        with open(file_path, "w", encoding="utf-8") as f:
            if links:
                count = 0
                for link in links:
                    if link.get(type):
                        if type == config.ED2K:
                            for i in link.get(type):
                                count += 1
                                f.write(i + "\n")
                        elif type == config.TORRENT:
                            count += 1
                            f.write(link.get(type) + "\n")
                self.logger.info(f"已成功导出 {count} 条 {type} 链接到 {file_path}")
