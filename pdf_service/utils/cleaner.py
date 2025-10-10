"""
临时文件清理工具

定时清理过期的临时文件
"""

import time
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger


class TempFileCleaner:
    """临时文件清理器"""
    
    def __init__(self, temp_dir: Path, max_age_hours: int = 24):
        """
        初始化清理器
        
        Args:
            temp_dir: 临时文件目录
            max_age_hours: 文件最大保留时间（小时）
        """
        self.temp_dir = temp_dir
        self.max_age_seconds = max_age_hours * 3600
        self.running = False
    
    def clean_expired_files(self) -> dict:
        """
        清理过期文件
        
        Returns:
            dict: 清理统计信息
        """
        if not self.temp_dir.exists():
            return {"deleted": 0, "kept": 0, "errors": 0}
        
        now = time.time()
        deleted = 0
        kept = 0
        errors = 0
        
        # 遍历所有任务目录
        for task_dir in self.temp_dir.iterdir():
            if not task_dir.is_dir():
                continue
            
            try:
                # 获取目录创建时间
                dir_mtime = task_dir.stat().st_mtime
                age_seconds = now - dir_mtime
                
                # 检查是否过期
                if age_seconds > self.max_age_seconds:
                    logger.info(f"清理过期文件: {task_dir.name} (已存在 {age_seconds/3600:.1f} 小时)")
                    shutil.rmtree(task_dir, ignore_errors=True)
                    deleted += 1
                else:
                    kept += 1
            
            except Exception as e:
                logger.error(f"清理文件失败: {task_dir.name}, 错误: {e}")
                errors += 1
        
        result = {
            "deleted": deleted,
            "kept": kept,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }
        
        if deleted > 0:
            logger.info(f"清理完成: 删除 {deleted} 个, 保留 {kept} 个, 错误 {errors} 个")
        
        return result
