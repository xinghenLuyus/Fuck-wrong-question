#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错题管理系统启动脚本
"""

import sys
import os
import uvicorn
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    # 定义包的安装名和导入名的映射
    package_mapping = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn', 
        'sqlalchemy': 'sqlalchemy',
        'python-multipart': 'multipart',  # 安装名 -> 导入名
        'python-docx': 'docx',            # 安装名 -> 导入名
        'Pillow': 'PIL',                  # 安装名 -> 导入名
        'aiofiles': 'aiofiles',
        'jinja2': 'jinja2'
    }
    
    missing_packages = []
    
    for install_name, import_name in package_mapping.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(install_name)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 错题管理系统启动器")
    print("=" * 50)
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python版本过低: {python_version.major}.{python_version.minor}")
        print("建议使用Python 3.9-3.11")
        sys.exit(1)
    
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    print("✅ 所有依赖已安装")
    
    # 确保必要目录存在
    os.makedirs("static/uploads", exist_ok=True)
    print("✅ 目录结构检查完成")
    
    # 启动应用
    print("\n🌐 启动Web服务器...")
    print("📱 访问地址: http://localhost:8000")
    print("⏹️  按 Ctrl+C 停止服务\n")
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")

if __name__ == "__main__":
    main()