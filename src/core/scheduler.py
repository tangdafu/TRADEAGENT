"""
调度器模块 - 使用APScheduler实现专业的任务调度
"""
from datetime import datetime
from typing import Callable
from loguru import logger
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR


class TradingScheduler:
    """交易分析调度器"""

    def __init__(self):
        """初始化调度器"""
        self.scheduler = BlockingScheduler()
        self._setup_event_listeners()

    def _setup_event_listeners(self):
        """设置事件监听器"""
        def job_executed_listener(event):
            """任务执行成功监听"""
            logger.debug(f"任务执行完成: {event.job_id}")

        def job_error_listener(event):
            """任务执行失败监听"""
            logger.error(f"任务执行失败: {event.job_id}, 异常: {event.exception}")

        self.scheduler.add_listener(job_executed_listener, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(job_error_listener, EVENT_JOB_ERROR)

    def add_interval_job(
        self,
        func: Callable,
        minutes: int,
        job_id: str,
        **kwargs
    ):
        """
        添加间隔执行的任务

        Args:
            func: 要执行的函数
            minutes: 执行间隔（分钟）
            job_id: 任务ID
            **kwargs: 传递给函数的参数
        """
        trigger = IntervalTrigger(minutes=minutes)

        self.scheduler.add_job(
            func=func,
            trigger=trigger,
            id=job_id,
            kwargs=kwargs,
            replace_existing=True,
            max_instances=1,  # 同一时间只运行一个实例
            coalesce=True,    # 如果错过了执行时间，只执行一次
        )

        logger.info(f"已添加定时任务: {job_id}, 间隔: {minutes} 分钟")

    def add_cron_job(
        self,
        func: Callable,
        hour: int,
        minute: int,
        job_id: str,
        **kwargs
    ):
        """
        添加定时执行的任务（每天固定时间）

        Args:
            func: 要执行的函数
            hour: 小时 (0-23)
            minute: 分钟 (0-59)
            job_id: 任务ID
            **kwargs: 传递给函数的参数
        """
        self.scheduler.add_job(
            func=func,
            trigger='cron',
            hour=hour,
            minute=minute,
            id=job_id,
            kwargs=kwargs,
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )

        logger.info(f"已添加定时任务: {job_id}, 执行时间: {hour:02d}:{minute:02d}")

    def start(self):
        """启动调度器"""
        logger.info("=" * 70)
        logger.info("调度器启动")
        logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 显示所有任务
        jobs = self.scheduler.get_jobs()
        if jobs:
            logger.info(f"已注册任务数: {len(jobs)}")
            for job in jobs:
                next_run = getattr(job, 'next_run_time', None)
                if next_run:
                    logger.info(f"  - {job.id}: 下次执行时间 {next_run}")
                else:
                    logger.info(f"  - {job.id}")

        logger.info("按 Ctrl+C 停止调度器")
        logger.info("=" * 70)

        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("收到停止信号")
            self.shutdown()
            # 重新抛出异常，让上层处理
            raise

    def shutdown(self):
        """关闭调度器"""
        logger.info("正在关闭调度器...")
        self.scheduler.shutdown(wait=True)
        logger.info("调度器已关闭")

    def get_jobs(self):
        """获取所有任务"""
        return self.scheduler.get_jobs()

    def remove_job(self, job_id: str):
        """移除任务"""
        self.scheduler.remove_job(job_id)
        logger.info(f"已移除任务: {job_id}")
