from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.models import get_db, Student
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/students", tags=["学生管理"])

class StudentCreate(BaseModel):
    class_name: str
    student_no: str
    name: str

class StudentUpdate(BaseModel):
    class_name: Optional[str] = None
    student_no: Optional[str] = None
    name: Optional[str] = None

class StudentResponse(BaseModel):
    id: int
    class_name: str
    student_no: str
    name: str
    
    class Config:
        from_attributes = True

@router.post("/", response_model=StudentResponse)
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """创建新学生"""
    # 检查学号在该班级是否已存在
    existing_student = db.query(Student).filter(
        Student.class_name == student.class_name,
        Student.student_no == student.student_no
    ).first()
    if existing_student:
        raise HTTPException(status_code=400, detail=f"学号 {student.student_no} 在班级 {student.class_name} 中已存在")
    
    db_student = Student(
        class_name=student.class_name,
        student_no=student.student_no,
        name=student.name
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@router.get("/", response_model=List[StudentResponse])
async def get_students(
    class_name: Optional[str] = Query(None, description="班级筛选"),
    search: Optional[str] = Query(None, description="搜索学号或姓名"),
    db: Session = Depends(get_db)
):
    """获取学生列表"""
    query = db.query(Student)
    
    if class_name:
        query = query.filter(Student.class_name == class_name)
    
    if search:
        query = query.filter(
            (Student.student_no.contains(search)) | 
            (Student.name.contains(search))
        )
    
    students = query.order_by(Student.student_no).all()
    return students

@router.get("/classes")
async def get_classes(db: Session = Depends(get_db)):
    """获取所有班级列表"""
    classes = db.query(Student.class_name).distinct().all()
    return [{"class_name": c[0]} for c in classes]

@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int, db: Session = Depends(get_db)):
    """获取指定学生"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return student

@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(student_id: int, student_update: StudentUpdate, db: Session = Depends(get_db)):
    """更新学生信息"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    # 确定要检查的班级和学号
    check_class = student_update.class_name if student_update.class_name is not None else student.class_name
    check_no = student_update.student_no if student_update.student_no is not None else student.student_no
    
    # 检查学号在班级内是否重复（排除当前学生）
    if (student_update.student_no and student_update.student_no != student.student_no) or \
       (student_update.class_name and student_update.class_name != student.class_name):
        existing = db.query(Student).filter(
            Student.class_name == check_class,
            Student.student_no == check_no,
            Student.id != student_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"学号 {check_no} 在班级 {check_class} 中已存在")
    
    if student_update.class_name is not None:
        student.class_name = student_update.class_name
    if student_update.student_no is not None:
        student.student_no = student_update.student_no
    if student_update.name is not None:
        student.name = student_update.name
    
    db.commit()
    db.refresh(student)
    return student

@router.delete("/{student_id}")
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    """删除学生"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    db.delete(student)
    db.commit()
    
    return {"message": "学生删除成功"}