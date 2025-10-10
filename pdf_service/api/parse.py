"""
PDF解析API路由

提供RESTful API接口
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
from loguru import logger

from pdf_service.core.parser import parse_pdf
from pdf_service.config import TEMP_DIR, MINERU_BACKEND, MINERU_PARSE_METHOD, MINERU_DEFAULT_LANG
from pdf_service.utils import TempFileCleaner


router = APIRouter()

# 临时文件清理器实例
_cleaner = None


def get_cleaner() -> TempFileCleaner:
    """获取清理器实例（单例）"""
    global _cleaner
    if _cleaner is None:
        _cleaner = TempFileCleaner(TEMP_DIR, max_age_hours=24)
    return _cleaner


class ParseResponse(BaseModel):
    """解析响应"""
    success: bool
    message: str
    data: Optional[dict] = None


@router.post("/parse", response_model=ParseResponse)
async def parse_pdf_file(
    file: UploadFile = File(..., description="PDF文件"),
    lang: str = Form(MINERU_DEFAULT_LANG, description="语言代码"),
    backend: str = Form(MINERU_BACKEND, description="解析后端"),
    parse_method: str = Form(MINERU_PARSE_METHOD, description="解析方法"),
    formula_enable: bool = Form(False, description="是否启用公式解析"),
    table_enable: bool = Form(False, description="是否启用表格解析"),
    start_page: int = Form(0, description="起始页码"),
    end_page: Optional[int] = Form(None, description="结束页码")
):
    """
    解析PDF文件
    
    - **file**: 上传的PDF文件
    - **lang**: 语言代码，可选 ch, en, korean, japan 等
    - **backend**: 解析后端，可选 pipeline, vlm-transformers 等
    - **parse_method**: 解析方法，可选 auto, txt, ocr
    - **formula_enable**: 是否启用公式解析
    - **table_enable**: 是否启用表格解析
    - **start_page**: 起始页码（从0开始）
    - **end_page**: 结束页码（不包含），None表示到文档末尾
    """
    # 验证文件类型
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只支持PDF文件")
    
    # 生成唯一任务ID
    task_id = str(uuid.uuid4())
    task_dir = TEMP_DIR / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 读取文件内容
        pdf_bytes = await file.read()
        
        # 提取文件名（不含扩展名）
        file_stem = Path(file.filename).stem
        
        # 调用解析
        result = parse_pdf(
            pdf_bytes=pdf_bytes,
            output_dir=str(task_dir),
            file_name=file_stem,
            lang=lang,
            backend=backend,
            parse_method=parse_method,
            formula_enable=formula_enable,
            table_enable=table_enable,
            start_page_id=start_page,
            end_page_id=end_page
        )
        
        # 构建简化的响应数据
        # 计算 auto 目录的 URL
        temp_dir = Path(TEMP_DIR)
        task_dir = temp_dir / task_id
        output_dir = Path(result["output_dir"])
        
        try:
            # 获取相对于 task_dir 的路径
            rel_path = output_dir.relative_to(task_dir)
            auto_dir_url = f"/files/{task_id}/{rel_path.as_posix()}"
        except ValueError:
            # 降级方案：使用文件名拼接
            auto_dir_url = f"/files/{task_id}/{file_stem}/auto"
        
        return ParseResponse(
            success=True,
            message="解析成功",
            data={
                "task_id": task_id,
                "file_name": file_stem,
                "auto_dir_url": auto_dir_url
            }
        )
    
    except Exception as e:
        # 清理临时文件
        if task_dir.exists():
            shutil.rmtree(task_dir, ignore_errors=True)
        
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


@router.get("/result/{task_id}")
async def get_parse_result(task_id: str):
    """
    获取解析结果
    
    - **task_id**: 任务ID
    """
    task_dir = TEMP_DIR / task_id
    
    if not task_dir.exists():
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 查找markdown文件
    md_files = list(task_dir.rglob("*.md"))
    
    if not md_files:
        raise HTTPException(status_code=404, detail="结果文件不存在")
    
    # 读取markdown内容
    md_file = md_files[0]
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return ParseResponse(
        success=True,
        message="获取成功",
        data={
            "task_id": task_id,
            "markdown_content": content,
            "markdown_file": md_file.name
        }
    )


@router.delete("/result/{task_id}")
async def delete_parse_result(task_id: str):
    """
    删除解析结果
    
    - **task_id**: 任务ID
    """
    task_dir = TEMP_DIR / task_id
    
    if not task_dir.exists():
        raise HTTPException(status_code=404, detail="任务不存在")
    
    try:
        shutil.rmtree(task_dir)
        return ParseResponse(
            success=True,
            message="删除成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.post("/cleanup")
async def manual_cleanup():
    """
    手动清理过期文件
    
    清理超过24小时的临时文件
    """
    cleaner = get_cleaner()
    result = cleaner.clean_expired_files()
    
    return ParseResponse(
        success=True,
        message="清理完成",
        data=result
    )

