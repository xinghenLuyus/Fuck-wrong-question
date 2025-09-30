from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import sqlite3
import os

# 数据库文件路径
DATABASE_PATH = "wrong_question.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Category(Base):
    """试卷分类表"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)  # 父分类 ID，实现层级结构
    
    # 关联关系
    parent = relationship("Category", remote_side=[id], backref="children")
    papers = relationship("Paper", back_populates="category")

class Paper(Base):
    """试卷表"""
    __tablename__ = "papers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)  # 所属分类
    
    # 关联关系
    category = relationship("Category", back_populates="papers")
    questions = relationship("Question", back_populates="paper")

class Question(Base):
    """题目表"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    question_no = Column(Integer, nullable=False)
    question_text = Column(Text)  # 题目文字内容
    image_urls = Column(Text)  # 多个图片URL，逗号分隔
    wrong_students = Column(Text)  # 错题学生ID，逗号分隔
    
    # 关联试卷
    paper = relationship("Paper", back_populates="questions")

class Student(Base):
    """学生表"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String, nullable=False)  # 班级
    student_no = Column(String, nullable=False, unique=True)  # 学号
    name = Column(String, nullable=False)  # 姓名

def create_tables():
    """创建所有数据表"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """获取数据库连接"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """初始化数据库"""
    create_tables()
    print(f"数据库已初始化: {DATABASE_PATH}")