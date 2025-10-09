from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from database.models import init_database
from api import papers, questions, students, categories, export, document_parser
import os

# 创建FastAPI应用
app = FastAPI(title="错题管理系统", description="一个用于录入试卷、标记学生错题、导出Word的H5应用")

# 注册API路由
app.include_router(categories.router)
app.include_router(papers.router)
app.include_router(questions.router)
app.include_router(students.router)
app.include_router(export.router)
app.include_router(document_parser.router)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 模板引擎
templates = Jinja2Templates(directory="templates")

# 初始化数据库
@app.on_event("startup")
async def startup_event():
    init_database()
    print("应用启动完成")

# 首页路由
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 学生管理页面
@app.get("/students", response_class=HTMLResponse)
async def students_page(request: Request):
    return templates.TemplateResponse("students.html", {"request": request})

# 添加试卷页面
@app.get("/add_paper", response_class=HTMLResponse)
async def add_paper_page(request: Request):
    return templates.TemplateResponse("add_paper.html", {"request": request})

# 添加题目页面
@app.get("/add_question/{paper_id}", response_class=HTMLResponse)
async def add_question_page(request: Request, paper_id: int):
    return templates.TemplateResponse("add_question.html", {"request": request, "paper_id": paper_id})

# 自动解析试卷页面
@app.get("/auto_parse/{paper_id}", response_class=HTMLResponse)
async def auto_parse_page(request: Request, paper_id: int):
    return templates.TemplateResponse("auto_parse.html", {"request": request, "paper_id": paper_id})

# 试卷预览页面
@app.get("/preview/{paper_id}", response_class=HTMLResponse)
async def preview_page(request: Request, paper_id: int):
    return templates.TemplateResponse("preview.html", {"request": request, "paper_id": paper_id})

# 导出预览页面（支持单个或多个学生ID，用逗号分隔）
@app.get("/export_preview/{paper_id}/{student_id}", response_class=HTMLResponse)
async def export_preview_page(request: Request, paper_id: int, student_id: str):
    return templates.TemplateResponse("export_preview.html", {
        "request": request, 
        "paper_id": paper_id, 
        "student_id": student_id
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)