"""
Queue 和記憶體監控配置
"""
import psutil
import os

class QueueConfig:
    MAX_QUEUE_SIZE = 10000  # 最大隊列大小
    WARNING_QUEUE_SIZE = 8000  # 警告閾值
    
    # 記憶體監控配置
    MAX_MEMORY_USAGE_PERCENT = 80  # 最大記憶體使用百分比
    WARNING_MEMORY_USAGE_PERCENT = 70  # 記憶體警告閾值
    
    # 監控間隔（秒）
    MONITOR_INTERVAL = 5
    
    # 背壓處理策略
    BACKPRESSURE_STRATEGY = "drop_oldest"  # drop_oldest, drop_newest, block
    
    @classmethod
    def get_max_memory_bytes(cls):
        """獲取最大記憶體限制（字節）"""
        total_memory = psutil.virtual_memory().total
        return int(total_memory * cls.MAX_MEMORY_USAGE_PERCENT / 100)
    
    @classmethod
    def get_warning_memory_bytes(cls):
        """獲取記憶體警告閾值（字節）"""
        total_memory = psutil.virtual_memory().total
        return int(total_memory * cls.WARNING_MEMORY_USAGE_PERCENT / 100)
