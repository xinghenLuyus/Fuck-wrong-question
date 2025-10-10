"""
PDF解析微服务主程序

FastAPI应用，提供RESTful API接口
"""

import sys
from pathlib import Path

# 支持直接运行：将父目录添加到模块搜索路径
if __name__ == "__main__":
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pdf_service.api import parse_router
from pdf_service.config import (
    HOST, PORT, TEMP_DIR, 
    TEMP_FILE_MAX_AGE_HOURS, CLEANUP_INTERVAL_HOURS, AUTO_CLEANUP_ENABLED
)
from pdf_service.utils import TempFileCleaner
import uvicorn
import asyncio
from contextlib import asynccontextmanager


# 临时文件清理器
cleaner = TempFileCleaner(TEMP_DIR, max_age_hours=TEMP_FILE_MAX_AGE_HOURS)


async def cleanup_task():
    """后台清理任务"""
    interval_seconds = CLEANUP_INTERVAL_HOURS * 3600
    
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            cleaner.clean_expired_files()
        except Exception as e:
            print(f"⚠️  清理任务异常: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    task = None
    if AUTO_CLEANUP_ENABLED:
        print(f"🧹 启动临时文件清理任务")
        print(f"   清理间隔: 每 {CLEANUP_INTERVAL_HOURS} 小时")
        print(f"   文件保留: {TEMP_FILE_MAX_AGE_HOURS} 小时")
        task = asyncio.create_task(cleanup_task())
    else:
        print("⚠️  自动清理已禁用，请手动调用 /api/pdf/cleanup 接口清理文件")
    
    yield
    
    # 关闭时
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        print("🧹 清理任务已停止")


# 创建FastAPI应用
app = FastAPI(
    title="PDF解析微服务",
    description="基于MinerU的PDF解析服务，支持文本提取、OCR、公式和表格识别",
    version="2.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(parse_router, prefix="/api/pdf", tags=["PDF解析"])

# 挂载静态文件目录（提供图片访问）
app.mount("/files", StaticFiles(directory=str(TEMP_DIR)), name="files")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "pdf-parser"}


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "PDF解析微服务",
        "version": "2.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    # 直接运行时使用uvicorn启动
    uvicorn.run(
        "pdf_service.main:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info"
    )
