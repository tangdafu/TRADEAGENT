"""
定时任务调度器
支持定时分析和监控
"""
import schedule
import time
from datetime import datetime
from typing import List, Callable
from loguru import logger
from threading import Thread


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        """初始化调度器"""
        self.running = False
        self.thread = None
        logger.info("任务调度器初始化完成")
    
    def add_job(self, func: Callable, interval: int, unit: str = 'minutes', job_name: str = None):
        """
        添加定时任务
        
        Args:
            func: 要执行的函数
            interval: 时间间隔
            unit: 时间单位 ('seconds', 'minutes', 'hours', 'days')
            job_name: 任务名称
        """
        job_name = job_name or func.__name__
        
        if unit == 'seconds':
            schedule.every(interval).seconds.do(func)
        elif unit == 'minutes':
            schedule.every(interval).minutes.do(func)
        elif unit == 'hours':
            schedule.every(interval).hours.do(func)
        elif unit == 'days':
            schedule.every(interval).days.do(func)
        else:
            raise ValueError(f"不支持的时间单位: {unit}")
        
        logger.info(f"添加定时任务: {job_name} - 每 {interval} {unit}")
    
    def add_daily_job(self, func: Callable, time_str: str, job_name: str = None):
        """
        添加每日定时任务
        
        Args:
            func: 要执行的函数
            time_str: 时间字符串，格式 "HH:MM"
            job_name: 任务名称
        """
        job_name = job_name or func.__name__
        schedule.every().day.at(time_str).do(func)
        logger.info(f"添加每日任务: {job_name} - 每天 {time_str}")
    
    def start(self):
        """启动调度器（在后台线程运行）"""
        if self.running:
            logger.warning("调度器已在运行")
            return
        
        self.running = True
        self.thread = Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("任务调度器已启动")
    
    def _run_scheduler(self):
        """运行调度器循环"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"调度器执行出错: {e}", exc_info=True)
    
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("任务调度器已停止")
    
    def clear_all(self):
        """清除所有任务"""
        schedule.clear()
        logger.info("已清除所有定时任务")
    
    def get_jobs(self):
        """获取所有任务"""
        return schedule.get_jobs()


class MonitorScheduler:
    """监控调度器 - 专门用于市场监控"""
    
    def __init__(self, symbols: List[str], analysis_func: Callable, alert_func: Callable = None):
        """
        初始化监控调度器
        
        Args:
            symbols: 要监控的交易对列表
            analysis_func: 分析函数，接收symbol参数
            alert_func: 告警函数，接收symbol和analysis_result参数
        """
        self.symbols = symbols
        self.analysis_func = analysis_func
        self.alert_func = alert_func
        self.scheduler = TaskScheduler()
        logger.info(f"监控调度器初始化完成，监控币种: {', '.join(symbols)}")
    
    def monitor_all_symbols(self):
        """监控所有交易对"""
        logger.info("=" * 70)
        logger.info(f"开始定时监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 70)
        
        for symbol in self.symbols:
            try:
                logger.info(f"\n正在分析: {symbol}")
                result = self.analysis_func(symbol)
                
                # 如果有告警函数且检测到交易机会，发送告警
                if self.alert_func and result.get('has_trading_opportunity'):
                    self.alert_func(symbol, result)
                
            except Exception as e:
                logger.error(f"分析 {symbol} 时出错: {e}", exc_info=True)
        
        logger.info("=" * 70)
        logger.info("本轮监控完成")
        logger.info("=" * 70)
    
    def start_monitoring(self, interval: int = 15, unit: str = 'minutes'):
        """
        启动监控
        
        Args:
            interval: 监控间隔
            unit: 时间单位
        """
        # 添加监控任务
        self.scheduler.add_job(
            self.monitor_all_symbols,
            interval=interval,
            unit=unit,
            job_name=f"monitor_{','.join(self.symbols)}"
        )
        
        # 立即执行一次
        logger.info("执行首次监控...")
        self.monitor_all_symbols()
        
        # 启动调度器
        self.scheduler.start()
        logger.info(f"监控已启动，间隔: {interval} {unit}")
    
    def stop_monitoring(self):
        """停止监控"""
        self.scheduler.stop()
        logger.info("监控已停止")
