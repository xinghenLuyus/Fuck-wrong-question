# 应用配置
APP_NAME = "错题管理系统"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "一个用于录入试卷、标记学生错题、导出Word的H5应用"

# 数据库配置
DATABASE_URL = "sqlite:///wrong_question.db"

# 文件上传配置
UPLOAD_DIR = "static/uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

# 导出配置
EXPORT_DIR = "static/uploads"
WORD_IMAGE_WIDTH = 5  # Word文档中图片宽度（英寸）

# 服务器配置
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True