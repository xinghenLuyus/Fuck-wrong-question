"""
PDF解析服务子进程管理器

功能：
1. 启动PDF解析微服务作为子进程
2. 监控服务健康状态
3. 优雅关闭子进程
"""

import subprocess
import time
import requests
import signal
import sys
import os
from pathlib import Path
from config import PDFParserConfig


class PDFServiceManager:
    """PDF解析服务管理器 - 管理子进程生命周期"""
    
    def __init__(self):
        self.process = None
        self.port = PDFParserConfig.PORT
        self.base_url = PDFParserConfig.URL
        self.service_path = PDFParserConfig.SERVICE_PATH
    
    def start(self, timeout=30):
        """
        启动PDF解析子进程
        
        Args:
            timeout: 等待服务启动的超时时间（秒）
        
        Raises:
            FileNotFoundError: 如果微服务目录不存在
            TimeoutError: 如果服务启动超时
        """
        if self.is_running():
            print(f"   PDF解析服务已在运行: {self.base_url}")
            return
        
        # 检查微服务目录是否存在
        if not self.service_path.exists():
            raise FileNotFoundError(
                f"PDF解析微服务目录不存在: {self.service_path}\n"
                f"请确保 pdf_service/ 目录存在"
            )
        
        # 检查main.py是否存在
        main_file = self.service_path / "main.py"
        if not main_file.exists():
            raise FileNotFoundError(
                f"微服务主程序不存在: {main_file}\n"
                f"请确保 pdf_service/main.py 文件存在"
            )
        
        # 启动命令
        cmd = [
            sys.executable,  # 使用当前Python解释器
            "-m", "uvicorn",
            "pdf_service.main:app",
            "--host", "0.0.0.0",
            "--port", str(self.port),
            "--log-level", "warning"
        ]
        
        print(f"   启动命令: {' '.join(cmd)}")
        
        # 启动子进程
        try:
            # Windows特殊处理
            if sys.platform == 'win32':
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setpgrp
                )
        except Exception as e:
            raise RuntimeError(f"启动子进程失败: {e}")
        
        # 等待服务就绪
        try:
            self._wait_for_ready(timeout)
        except TimeoutError as e:
            # 启动失败，清理子进程
            self.stop()
            raise e
    
    def stop(self):
        """停止PDF解析子进程"""
        if self.process is None:
            return
        
        try:
            # 尝试优雅关闭
            if sys.platform == 'win32':
                # Windows: 发送CTRL_BREAK_EVENT
                try:
                    self.process.send_signal(signal.CTRL_BREAK_EVENT)
                except:
                    pass
            else:
                # Unix: 发送SIGTERM
                self.process.terminate()
            
            # 等待进程结束
            try:
                self.process.wait(timeout=5)
                print("   ✅ PDF解析服务已停止")
            except subprocess.TimeoutExpired:
                # 强制杀死
                self.process.kill()
                self.process.wait()
                print("   ⚠️  PDF解析服务已强制停止")
        except Exception as e:
            print(f"   ⚠️  停止服务时出错: {e}")
        finally:
            self.process = None
    
    def is_running(self) -> bool:
        """
        检查服务是否运行
        
        Returns:
            bool: 服务是否正在运行
        """
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False
    
    def _wait_for_ready(self, timeout):
        """
        等待服务就绪
        
        Args:
            timeout: 超时时间（秒）
        
        Raises:
            TimeoutError: 如果服务启动超时
        """
        start = time.time()
        last_error = None
        
        while time.time() - start < timeout:
            try:
                if self.is_running():
                    return
            except Exception as e:
                last_error = e
            
            # 检查子进程是否崩溃
            if self.process and self.process.poll() is not None:
                # 读取错误信息
                _, stderr = self.process.communicate()
                error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "未知错误"
                raise RuntimeError(
                    f"PDF解析服务启动失败，进程已退出\n"
                    f"错误信息: {error_msg}"
                )
            
            time.sleep(0.5)
        
        # 超时
        error_detail = f": {last_error}" if last_error else ""
        raise TimeoutError(
            f"PDF解析服务启动超时（{timeout}秒）{error_detail}\n"
            f"请检查:\n"
            f"1. 端口 {self.port} 是否被占用\n"
            f"2. pdf_service 目录下的依赖是否已安装\n"
            f"3. 查看子进程日志输出"
        )
    
    def restart(self, timeout=30):
        """
        重启服务
        
        Args:
            timeout: 等待服务启动的超时时间（秒）
        """
        print("   重启PDF解析服务...")
        self.stop()
        time.sleep(1)
        self.start(timeout)
