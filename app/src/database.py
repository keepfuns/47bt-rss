import sqlite3
import os
from typing import List
from . import config
import json


class Database:
    def __init__(self):
        # 指定数据库文件的路径
        self.path = config.PATH + "/app/data/data.db"
        # 确保目录存在，如果不存在则创建目录
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        # 初始化threads表
        self.create_table()
        self.rss_jj = os.environ.get("rss_jj", config.ZERO)
        self.rss_dy = os.environ.get("rss_dy", config.ZERO)
        self.rss_dm = os.environ.get("rss_dm", config.ZERO)

    def get_conn(self):
        # 每次调用时创建一个新的连接
        conn = sqlite3.connect(self.path)
        conn.execute('PRAGMA encoding="UTF-8"')
        return conn

    def create_table(self):
        # 获取新连接
        conn = self.get_conn()
        # 创建一个游标对象
        cursor = conn.cursor()
        # 创建一个名为threads的表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS threads (
            thread_url TEXT NOT NULL,
            thread_title TEXT NULL,
            type TEXT NULL,
            year TEXT NULL,
            video_format TEXT NULL,
            img_url TEXT  NULL,
            ed2k TEXT NULL,
            torrent TEXT NULL,
            creat_time TEXT NOT NULL,
            update_time TEXT NOT NULL,
            UNIQUE(thread_url)
            )
        """
        )
        # 提交事务
        conn.commit()
        # 关闭游标
        cursor.close()
        # 关闭连接
        conn.close()

    # 批量插入数据
    def insert_batch(self, threads: List):
        # 获取新连接
        conn = self.get_conn()
        # 创建一个游标对象
        cursor = conn.cursor()
        # 批量插入数据
        cursor.executemany(
            """
        INSERT INTO threads (thread_url, thread_title, type, year, video_format, img_url, ed2k, torrent, creat_time, update_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            threads,
        )
        # 提交事务
        conn.commit()
        # 关闭游标
        cursor.close()
        # 关闭连接
        conn.close()

    # 查询单个记录
    def selectone(self, thread_url: str):
        # 获取新连接
        conn = self.get_conn()
        # 创建一个游标对象
        cursor = conn.cursor()
        # 查询单个记录
        cursor.execute("SELECT * FROM threads WHERE thread_url = ?", (thread_url,))
        row = cursor.fetchone()
        # 关闭游标
        cursor.close()
        # 关闭连接
        conn.close()
        # 返回结果
        if row:
            return {
                "thread_url": {row[0]},
                "thread_title": {row[1]},
                "type": {row[2]},
                "year": {row[3]},
                "video_format": {row[4]},
                "img_url": {row[5]},
                "ed2k": {row[6]},
                "torrent": {row[7]},
                "creat_time": {row[8]},
                "update_time": {row[9]},
            }
        else:
            return None

    # 批量更新数据
    def update_batch(self, threads: List):
        # 获取新连接
        conn = self.get_conn()
        # 创建一个游标对象
        cursor = conn.cursor()
        if threads:
            for thread in threads:
                # 查询单个记录
                cursor.execute(
                    "SELECT * FROM threads WHERE thread_url = ?", (thread[0],)
                )
                if cursor.fetchone():
                    # 更新记录
                    cursor.execute(
                        """
                        UPDATE threads SET thread_title = ?, type = ?, year = ?, video_format = ?, img_url = ?, ed2k = ?, torrent = ?, update_time = ? WHERE thread_url = ?
                        """,
                        (
                            thread[1],
                            thread[2],
                            thread[3],
                            thread[4],
                            thread[5],
                            thread[6],
                            thread[7],
                            thread[9],
                            thread[0],
                        ),
                    )
                else:
                    # 插入记录
                    cursor.execute(
                        """
                        INSERT INTO threads (thread_url, thread_title, type, year, video_format, img_url, ed2k, torrent, creat_time, update_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            thread[0],
                            thread[1],
                            thread[2],
                            thread[3],
                            thread[4],
                            thread[5],
                            thread[6],
                            thread[7],
                            thread[8],
                            thread[9],
                        ),
                    )
        # 提交事务
        conn.commit()
        # 关闭游标
        cursor.close()
        # 关闭连接
        conn.close()

    # 清空数据库
    def clear(self):
        if (
            self.rss_jj == config.ZERO
            and self.rss_dy == config.ZERO
            and self.rss_dm == config.ZERO
        ):
            return

        sql = ""
        if self.rss_jj == config.ONE:
            sql += "'" + config.JJ + "',"
        if self.rss_dy == config.ONE:
            sql += "'" + config.DY + "',"
        if self.rss_dm == config.ONE:
            sql += "'" + config.DM + "',"
        # 获取新连接
        conn = self.get_conn()
        # 创建一个游标对象
        cursor = conn.cursor()
        # 执行语句
        cursor.execute("delete from threads where type in(" + sql[:-1] + ")")
        # 提交事务
        conn.commit()
        # 关闭游标
        cursor.close()
        # 关闭连接
        conn.close()

    # 查询所有链接
    def export(self) -> List:
        links = []
        # 获取新连接
        conn = self.get_conn()
        # 创建一个游标对象
        cursor = conn.cursor()
        # 执行语句
        cursor.execute("SELECT ed2k,torrent FROM threads order by type,update_time asc")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                links.append({config.ED2K: json.loads(row[0]), config.TORRENT: row[1]})
        # 关闭游标
        cursor.close()
        # 关闭连接
        conn.close()
        return links
