"""
错题管理系统配置模块
所有配置从环境变量读取，支持.env文件
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent


class Config:
    """主服务配置"""
    
    # 应用信息
    APP_NAME = "错题管理系统"
    APP_VERSION = "2.0.0"
    APP_DESCRIPTION = "一个用于录入试卷、标记学生错题、导出Word的H5应用"
    
    # 服务器配置
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # 数据库配置
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./wrong_question.db")
    
    # 文件上传配置
    UPLOAD_DIR = os.getenv("UPLOAD_FOLDER", "static/uploads")
    MAX_FILE_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "52428800"))  # 50MB
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    
    # 导出配置
    EXPORT_DIR = os.getenv("EXPORT_SETTINGS_FOLDER", "static/export_settings")
    MAX_EXPORT_FILES = int(os.getenv("MAX_EXPORT_FILES", "20"))
    EXPORT_FILE_LIFETIME = int(os.getenv("EXPORT_FILE_LIFETIME", "3600"))
    WORD_IMAGE_WIDTH = 5  # Word文档中图片宽度（英寸）


class PDFParserConfig:
    """PDF解析服务配置"""
    
    # 部署模式
    MODE = os.getenv("PDF_PARSER_MODE", "local")  # local 或 remote
    
    # 服务地址
    URL = os.getenv("PDF_PARSER_URL", "http://localhost:8001")
    
    # 服务端口（本地模式）
    PORT = int(os.getenv("PDF_PARSER_PORT", "8001"))
    
    # 是否自动启动（本地模式）
    AUTO_START = os.getenv("PDF_PARSER_AUTO_START", "true").lower() == "true"
    
    # 微服务路径
    SERVICE_PATH = BASE_DIR / "pdf_service"
    
    # 超时设置（秒）
    TIMEOUT = int(os.getenv("PDF_PARSER_TIMEOUT", "300"))


# 向后兼容旧代码
APP_NAME = Config.APP_NAME
APP_VERSION = Config.APP_VERSION
APP_DESCRIPTION = Config.APP_DESCRIPTION
DATABASE_URL = Config.DATABASE_URL
UPLOAD_DIR = Config.UPLOAD_DIR
MAX_FILE_SIZE = Config.MAX_FILE_SIZE
ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS
EXPORT_DIR = Config.EXPORT_DIR
WORD_IMAGE_WIDTH = Config.WORD_IMAGE_WIDTH
HOST = Config.HOST
PORT = Config.PORT
DEBUG = Config.DEBUG