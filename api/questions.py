from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.models import get_db, Question, Paper
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/questions", tags=["题目管理"])

class QuestionCreate(BaseModel):
    paper_id: int
    question_text: Optional[str] = ""  # 题目文字内容
    image_urls: Optional[str] = ""  # 多个URL用逗号分隔
    wrong_students: Optional[str] = ""  # 错题学生ID，用逗号分隔

class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    image_urls: Optional[str] = None
    wrong_students: Optional[str] = None

class QuestionResponse(BaseModel):
    id: int
    paper_id: int
    question_no: int
    question_text: Optional[str] = ""
    image_urls: Optional[str] = ""
    wrong_students: Optional[str] = ""
    
    class Config:
        from_attributes = True

@router.post("/", response_model=QuestionResponse)
async def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    """创建新题目"""
    # 检查试卷是否存在
    paper = db.query(Paper).filter(Paper.id == question.paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    
    # 获取下一个题号
    last_question = db.query(Question).filter(Question.paper_id == question.paper_id).order_by(Question.question_no.desc()).first()
    next_no = 1 if not last_question else last_question.question_no + 1
    
    db_question = Question(
        paper_id=question.paper_id,
        question_no=next_no,
        question_text=question.question_text or "",
        image_urls=question.image_urls or "",
        wrong_students=question.wrong_students or ""
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

@router.get("/paper/{paper_id}", response_model=List[QuestionResponse])
async def get_questions_by_paper(paper_id: int, db: Session = Depends(get_db)):
    """获取指定试卷的所有题目"""
    questions = db.query(Question).filter(Question.paper_id == paper_id).order_by(Question.question_no).all()
    return questions

@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: int, db: Session = Depends(get_db)):
    """获取指定题目"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    return question

@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(question_id: int, question_update: QuestionUpdate, db: Session = Depends(get_db)):
    """更新题目"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    if question_update.question_text is not None:
        question.question_text = question_update.question_text
    if question_update.image_urls is not None:
        question.image_urls = question_update.image_urls
    if question_update.wrong_students is not None:
        question.wrong_students = question_update.wrong_students
    
    db.commit()
    db.refresh(question)
    return question

@router.delete("/{question_id}")
async def delete_question(question_id: int, db: Session = Depends(get_db)):
    """删除题目"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    db.delete(question)
    db.commit()
    
    return {"message": "题目删除成功"}