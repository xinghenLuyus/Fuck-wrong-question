from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.models import get_db, Paper, Question, Category
from pydantic import BaseModel
from typing import List, Optional
import datetime

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
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    
    # 删除相关题目
    db.query(Question).filter(Question.paper_id == paper_id).delete()
    
    # 删除试卷
    db.delete(paper)
    db.commit()
    
    return {"message": "试卷删除成功"}