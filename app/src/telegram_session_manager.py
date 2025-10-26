from telegram.ext import CallbackContext


class TelegramSessionManager:
    """TG会话管理器"""

    def __init__(self):
        self.active_sessions = {}  # {chat_id: {"job": job, "step": step}}

    def add_session(self, chat_id: int, job: object, step: int):
        self.active_sessions[chat_id] = {"job": job, "step": step, "active": True}

    def terminate_session(self, chat_id: int, context: CallbackContext):
        """彻底终止会话"""
        if chat_id in self.active_sessions:
            # 检查任务是否存在
            job = self.active_sessions[chat_id].get("job")
            if job and job in context.job_queue.jobs():
                job.schedule_removal()

            # 标记会话终止
            self.active_sessions[chat_id]["active"] = False
            del self.active_sessions[chat_id]

    def is_active(self, chat_id: int) -> bool:
        """检查会话是否活跃"""
        return chat_id in self.active_sessions
