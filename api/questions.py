from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.models import get_db, Question, Paper
from pydantic import BaseModel
from typing import List, Optional
from utils.question_order import (
    insert_question_at,
    delete_question_at,
    move_question,
    get_max_question_no
)

router = APIRouter(prefix="/api/questions", tags=["题目管理"])

class QuestionCreate(BaseModel):
    paper_id: int
    question_text: Optional[str] = ""  # 题目文字内容
    image_urls: Optional[str] = ""  # 多个URL用逗号分隔
    wrong_students: Optional[str] = ""  # 错题学生ID，用逗号分隔

class QuestionBatchItem(BaseModel):
    """批量创建题目的单项"""
    question_text: str
    image_urls: List[str] = []

class QuestionBatchCreate(BaseModel):
    """批量创建题目请求"""
    questions: List[QuestionBatchItem]

class QuestionInsert(BaseModel):
    """插入题目请求"""
    insert_position: int
    question_text: str
    image_urls: List[str] = []

class QuestionMove(BaseModel):
    """移动题目请求"""
    new_position: int

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


@router.post("/paper/{paper_id}/batch")
async def create_questions_batch(
    paper_id: int,
    data: QuestionBatchCreate,
    db: Session = Depends(get_db)
):
    """
    批量创建题目（用于PDF导入）
    
    自动分配题号（从1开始）
    """
    # 检查试卷是否存在
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    
    # 获取当前最大题号
    max_no = get_max_question_no(db, paper_id)
    
    # 批量创建
    created_questions = []
    for idx, q_data in enumerate(data.questions, start=max_no + 1):
        question = Question(
            paper_id=paper_id,
            question_no=idx,
            question_text=q_data.question_text,
            image_urls=','.join(q_data.image_urls) if q_data.image_urls else ''
        )
        db.add(question)
        created_questions.append(question)
    
    db.commit()
    
    return {
        "success": True,
        "message": f"成功创建 {len(created_questions)} 道题目",
        "count": len(created_questions)
    }


@router.post("/paper/{paper_id}/insert")
async def insert_question_at_position(
    paper_id: int,
    data: QuestionInsert,
    db: Session = Depends(get_db)
):
    """
    在指定位置插入题目
    
    会自动调整后续题目的序号
    """
    # 检查试卷是否存在
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    
    # 插入题目
    try:
        new_question = insert_question_at(
            db, paper_id, data.insert_position,
            data.question_text, data.image_urls
        )
        
        return {
            "success": True,
            "message": "题目已插入",
            "question": {
                "id": new_question.id,
                "question_no": new_question.question_no,
                "question_text": new_question.question_text,
                "image_urls": new_question.image_urls.split(',') if new_question.image_urls else []
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"插入失败: {str(e)}")


@router.put("/{question_id}/move")
async def move_question_position(
    question_id: int,
    data: QuestionMove,
    db: Session = Depends(get_db)
):
    """移动题目到新位置"""
    # 获取题目
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    try:
        move_question(db, question.paper_id, question_id, data.new_position)
        
        return {
            "success": True,
            "message": f"题目已移动到第 {data.new_position} 题"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"移动失败: {str(e)}")


@router.delete("/{question_id}/reorder")
async def delete_question_with_reorder(
    question_id: int,
    db: Session = Depends(get_db)
):
    """删除题目并重新排序"""
    # 获取题目
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    paper_id = question.paper_id
    
    try:
        delete_question_at(db, paper_id, question_id)
        
        return {
            "success": True,
            "message": "题目已删除"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")