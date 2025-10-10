"""
题目序号管理工具

处理题目的插入、删除、移动等操作时的序号重排
"""

from sqlalchemy.orm import Session
from database.models import Question
from typing import List


def reorder_questions(db: Session, paper_id: int, start_from: int = 1):
    """
    重新排列题目序号（从指定序号开始）
    
    Args:
        db: 数据库会话
        paper_id: 试卷ID
        start_from: 起始序号
    """
    questions = db.query(Question).filter(
        Question.paper_id == paper_id
    ).order_by(Question.question_no).all()
    
    for idx, question in enumerate(questions, start=start_from):
        question.question_no = idx
    
    db.commit()


def insert_question_at(
    db: Session, 
    paper_id: int, 
    insert_position: int,
    question_text: str,
    image_urls: List[str] = None
) -> Question:
    """
    在指定位置插入题目
    
    Args:
        db: 数据库会话
        paper_id: 试卷ID
        insert_position: 插入位置（题号）
        question_text: 题目文字
        image_urls: 图片URL列表
    
    Returns:
        Question: 新创建的题目
    """
    # 将插入位置及之后的题目序号全部+1
    questions_to_shift = db.query(Question).filter(
        Question.paper_id == paper_id,
        Question.question_no >= insert_position
    ).all()
    
    for question in questions_to_shift:
        question.question_no += 1
    
    # 创建新题目
    new_question = Question(
        paper_id=paper_id,
        question_no=insert_position,
        question_text=question_text,
        image_urls=','.join(image_urls) if image_urls else ''
    )
    
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    
    return new_question


def delete_question_at(db: Session, paper_id: int, question_id: int):
    """
    删除题目并重新排序
    
    Args:
        db: 数据库会话
        paper_id: 试卷ID
        question_id: 题目ID
    """
    # 获取要删除的题目
    question = db.query(Question).filter(
        Question.id == question_id,
        Question.paper_id == paper_id
    ).first()
    
    if not question:
        raise ValueError(f"题目不存在: {question_id}")
    
    deleted_no = question.question_no
    
    # 删除题目
    db.delete(question)
    
    # 将之后的题目序号全部-1
    questions_to_shift = db.query(Question).filter(
        Question.paper_id == paper_id,
        Question.question_no > deleted_no
    ).all()
    
    for q in questions_to_shift:
        q.question_no -= 1
    
    db.commit()


def move_question(
    db: Session, 
    paper_id: int, 
    question_id: int, 
    new_position: int
):
    """
    移动题目到新位置
    
    Args:
        db: 数据库会话
        paper_id: 试卷ID
        question_id: 题目ID
        new_position: 新位置（题号）
    """
    # 获取要移动的题目
    question = db.query(Question).filter(
        Question.id == question_id,
        Question.paper_id == paper_id
    ).first()
    
    if not question:
        raise ValueError(f"题目不存在: {question_id}")
    
    old_position = question.question_no
    
    if old_position == new_position:
        return  # 位置没变
    
    if new_position < old_position:
        # 向前移动：[new_position, old_position) 范围内的题目序号+1
        questions_to_shift = db.query(Question).filter(
            Question.paper_id == paper_id,
            Question.question_no >= new_position,
            Question.question_no < old_position
        ).all()
        
        for q in questions_to_shift:
            q.question_no += 1
    else:
        # 向后移动：(old_position, new_position] 范围内的题目序号-1
        questions_to_shift = db.query(Question).filter(
            Question.paper_id == paper_id,
            Question.question_no > old_position,
            Question.question_no <= new_position
        ).all()
        
        for q in questions_to_shift:
            q.question_no -= 1
    
    # 更新目标题目位置
    question.question_no = new_position
    
    db.commit()


def get_max_question_no(db: Session, paper_id: int) -> int:
    """
    获取试卷的最大题号
    
    Args:
        db: 数据库会话
        paper_id: 试卷ID
    
    Returns:
        int: 最大题号，如果没有题目则返回0
    """
    result = db.query(Question).filter(
        Question.paper_id == paper_id
    ).order_by(Question.question_no.desc()).first()
    
    return result.question_no if result else 0
