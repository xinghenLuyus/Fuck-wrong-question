"""
PDF解析微服务配置

从环境变量加载配置，支持.env文件
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 多位置查找 .env 文件（按优先级）
env_locations = [
    Path(__file__).parent.parent / ".env",       # 1. 项目根目录/.env（子进程模式）
    Path(__file__).parent / ".env",              # 2. pdf_service/.env（独立部署）
    Path.cwd() / ".env",                         # 3. 当前工作目录/.env
]

# 加载第一个找到的 .env 文件
for env_file in env_locations:
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ 已加载配置文件: {env_file}")
        break
else:
    # 没有找到 .env 文件，使用默认值
    print("⚠️  未找到 .env 文件，使用默认配置")

# 服务配置
HOST = os.getenv("PDF_PARSER_HOST", "0.0.0.0")
PORT = int(os.getenv("PDF_PARSER_PORT", "8001"))

# 临时文件配置
TEMP_DIR = Path(__file__).parent / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# 自动清理配置
TEMP_FILE_MAX_AGE_HOURS = int(os.getenv("TEMP_FILE_MAX_AGE_HOURS", "24"))  # 文件保留时间（小时）
CLEANUP_INTERVAL_HOURS = int(os.getenv("CLEANUP_INTERVAL_HOURS", "1"))     # 清理间隔（小时）
AUTO_CLEANUP_ENABLED = os.getenv("AUTO_CLEANUP_ENABLED", "true").lower() == "true"  # 是否自动清理

# MinerU配置
MINERU_MODEL_SOURCE = os.getenv("MINERU_MODEL_SOURCE", "local")
MINERU_BACKEND = os.getenv("MINERU_BACKEND", "pipeline")  # pipeline, vlm-transformers
MINERU_PARSE_METHOD = os.getenv("MINERU_PARSE_METHOD", "auto")  # auto, txt, ocr
MINERU_DEFAULT_LANG = os.getenv("MINERU_DEFAULT_LANG", "ch")  # ch, en, korean, japan

# 设置MinerU环境变量
os.environ['MINERU_MODEL_SOURCE'] = MINERU_MODEL_SOURCE
