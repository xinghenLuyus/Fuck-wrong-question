from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from database.models import get_db, Paper, Question, Category
from pydantic import BaseModel
from typing import List, Optional
import datetime
from api.pdf_parser_client import get_pdf_parser_client
from utils.markdown_parser import split_markdown_to_questions, validate_questions
from pathlib import Path
import tempfile
import os

router = APIRouter(prefix="/api/papers", tags=["试卷管理"])

class PaperCreate(BaseModel):
    name: str
    category_id: Optional[int] = None

class PaperUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None

class CategoryInfo(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class PaperResponse(BaseModel):
    id: int
    name: str
    category_id: Optional[int] = None
    category: Optional[CategoryInfo] = None
    
    class Config:
        from_attributes = True

@router.post("/", response_model=PaperResponse)
async def create_paper(paper: PaperCreate, db: Session = Depends(get_db)):
    """创建新试卷"""
    # 检查分类是否存在
    if paper.category_id:
        category = db.query(Category).filter(Category.id == paper.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="分类不存在")
    
    db_paper = Paper(
        name=paper.name,
        category_id=paper.category_id
    )
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)
    return db_paper

@router.get("/", response_model=List[PaperResponse])
async def get_papers(
    category_id: Optional[int] = Query(None, description="按分类筛选"),
    db: Session = Depends(get_db)
):
    """获取所有试卷列表"""
    query = db.query(Paper)
    
    if category_id is not None:
        query = query.filter(Paper.category_id == category_id)
    
    papers = query.order_by(Paper.id.desc()).all()
    return papers

@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(paper_id: int, db: Session = Depends(get_db)):
    """获取指定试卷"""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    return paper

@router.put("/{paper_id}", response_model=PaperResponse)
async def update_paper(paper_id: int, paper_update: PaperUpdate, db: Session = Depends(get_db)):
    """更新试卷"""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    
    # 检查分类是否存在（如果要更新分类）
    if paper_update.category_id is not None and paper_update.category_id != paper.category_id:
        if paper_update.category_id:
            category = db.query(Category).filter(Category.id == paper_update.category_id).first()
            if not category:
                raise HTTPException(status_code=404, detail="分类不存在")
    
    if paper_update.name is not None:
        paper.name = paper_update.name
    if paper_update.category_id is not None:
        paper.category_id = paper_update.category_id
    
    db.commit()
    db.refresh(paper)
    return paper

@router.delete("/{paper_id}")
async def delete_paper(paper_id: int, db: Session = Depends(get_db)):
    """删除试卷"""
    import os
    import shutil
    from config import UPLOAD_DIR
    
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    
    # 获取试卷关联的所有题目
    questions = db.query(Question).filter(Question.paper_id == paper_id).all()
    
    # 删除旧版本的图片文件（兼容旧版本）
    deleted_images = []
    for question in questions:
        if question.image_urls:
            urls = question.image_urls.split(',')
            for url in urls:
                url = url.strip()
                if url.startswith('/static/uploads/'):
                    # 提取文件名
                    filename = url.split('/')[-1]
                    old_file_path = os.path.join(UPLOAD_DIR, filename)
                    if os.path.exists(old_file_path):
                        try:
                            os.remove(old_file_path)
                            deleted_images.append(filename)
                        except Exception as e:
                            print(f"删除旧版文件失败 {old_file_path}: {e}")
    
    # 删除新版本的试卷文件夹（如果存在）
    paper_folder = os.path.join(UPLOAD_DIR, f"paper_{paper_id}")
    if os.path.exists(paper_folder):
        try:
            shutil.rmtree(paper_folder)
            print(f"已删除试卷文件夹: {paper_folder}")
        except Exception as e:
            print(f"删除文件夹失败 {paper_folder}: {e}")
    
    # 删除相关题目
    db.query(Question).filter(Question.paper_id == paper_id).delete()
    
    # 删除试卷
    db.delete(paper)
    db.commit()
    
    return {
        "message": "试卷删除成功",
        "deleted_images": deleted_images,
        "deleted_folder": paper_folder if os.path.exists(paper_folder) else None
    }


@router.post("/{paper_id}/parse-pdf")
async def parse_pdf_for_paper(
    paper_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传PDF并解析为题目
    
    步骤：
    1. 上传PDF到解析服务
    2. 获取Markdown内容
    3. 分题处理
    4. 返回题目列表供前端确认
    """
    # 检查试卷是否存在
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    
    # 检查文件类型
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只支持PDF文件")
    
    try:
        # 保存临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # 调用PDF解析客户端
        client = get_pdf_parser_client()
        parse_result = client.parse_pdf(tmp_path)
        
        # 获取Markdown内容
        markdown_content = client.get_markdown(parse_result)
        if not markdown_content:
            raise HTTPException(status_code=500, detail="获取Markdown失败")
        
        # 构建图片基础URL
        from config import PDFParserConfig
        base_url = f"{PDFParserConfig.URL}{parse_result['auto_dir_url']}"
        
        # 分题处理
        questions = split_markdown_to_questions(markdown_content, base_url)
        
        # 验证题目
        validation = validate_questions(questions)
        
        # 删除临时文件
        try:
            os.unlink(tmp_path)
        except:
            pass
        
        return {
            "success": True,
            "message": "PDF解析成功",
            "task_id": parse_result['task_id'],
            "file_name": parse_result['file_name'],
            "auto_dir_url": parse_result['auto_dir_url'],
            "questions": questions,
            "validation": validation,
            "total_questions": len(questions)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


@router.post("/{paper_id}/split-markdown")
async def split_markdown(
    paper_id: int,
    markdown_content: str,
    auto_dir_url: str,
    db: Session = Depends(get_db)
):
    """
    将Markdown内容分割为题目（备用接口）
    
    如果前端已经有Markdown内容，可以直接调用此接口分题
    """
    # 检查试卷是否存在
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    
    try:
        # 构建图片基础URL
        from config import PDFParserConfig
        base_url = f"{PDFParserConfig.URL}{auto_dir_url}"
        
        # 分题处理
        questions = split_markdown_to_questions(markdown_content, base_url)
        
        # 验证题目
        validation = validate_questions(questions)
        
        return {
            "success": True,
            "questions": questions,
            "validation": validation,
            "total_questions": len(questions)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分题失败: {str(e)}")