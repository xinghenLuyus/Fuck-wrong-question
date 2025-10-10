# 🎓 智能错题管理系统

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)
[![Version](https://img.shields.io/badge/version-2.0.0-brightgreen.svg)](https://github.com/xinghenLuyus/Fuck-wrong-question)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

**一个功能强大的现代化错题管理系统，专为教师量身定制**

*支持 PDF 自动导入、试卷录入、学生错题标记、高度自定义的 Word 文档导出*

[🚀 快速开始](#-快速开始) • [✨ 核心功能](#-核心功能) • [📖 使用指南](#-使用指南)

</div>

---

## ✨ 核心功能

### 🎯 主要特性
- **📄 PDF 自动导入** - 智能识别 PDF 试卷，自动切分题目，支持多位数题号和灵活格式
- **📝 试卷管理** - 创建、编辑、删除试卷，支持手动添加和 PDF 自动导入两种方式
- **📷 题目录入** - 多图片拖拽上传，自动题目编号，支持题目文字和图片混排
- **👥 学生管理** - 完整的班级和学生信息管理，支持按班级筛选和智能搜索
- **✏️ 在线编辑** - 实时题目编辑，支持题目顺序调整、批量操作和快捷键
- **📤 智能导出** - 单个学生 Word 文档、批量 ZIP 导出，支持高度自定义格式配置
- **🎨 所见即所得** - 实时预览最终 Word 文档效果，精确控制字体、图片和间距

### 🆕 v2.0.0 更新内容
- ✨ **新增 PDF 自动导入功能**：基于 MinerU 的 PDF 解析服务，支持智能题目切分
- 🎨 **统一页面样式**：所有页面采用统一的卡片式布局，提升用户体验

---

## 🚀 快速开始

### 📋 环境要求
- **Python 3.9-3.11**（推荐 3.10）
- **操作系统**：Windows / macOS / Linux
- **内存**：最少 1GB RAM（PDF 解析需要更多内存）
- **存储**：最少 500MB 可用空间

### ⚡ 一键启动（推荐）
```bash
# 1. 克隆项目
git clone https://github.com/xinghenLuyus/Fuck-wrong-question.git
cd Fuck-wrong-question

# 2. 安装依赖
python setup.py

# 3. 一键启动（自动检查环境并启动服务）
python start.py
```

### 🌐 访问应用
启动成功后，在浏览器访问：
- **主应用**：http://localhost:8000
- **PDF 解析服务**：http://localhost:8001（自动启动）

---

## 📖 使用指南

### 第一步：准备学生信息 👥
1. 点击右上角「👥 学生管理」
2. 按班级添加学生（班级、学号、姓名）
3. 支持搜索和筛选管理

### 第二步：创建试卷 📝
1. 在首页点击「➕ 添加新试卷」
2. 选择录入方式：
   - **手动添加**：逐题上传图片和录入文字
   - **PDF 自动导入**：上传 PDF 文件，自动识别题目

### 第三步：PDF 自动导入（新功能）📄
1. **上传 PDF 文件**：点击或拖拽 PDF 文件到上传区域
2. **等待解析**：系统自动解析 PDF，提取题目和图片（约 1-3 分钟）
3. **预览题目**：查看解析结果，确认题目数量和内容
4. **保存题目**：点击「保存并进入编辑」进入编辑模式

### 第四步：编辑题目 ✏️
1. **调整顺序**：拖拽题目卡片调整题目顺序
2. **修改内容**：点击题目编辑文字、图片和错题学生
3. **标记错题**：搜索并选择做错该题的学生
4. **批量操作**：支持批量删除、批量标记等操作

### 第五步：导出错题 📤
1. **配置样式**：设置全局和单题个性化导出格式
2. **选择导出**：
   - 单个学生：预览并下载个人错题文档
   - 批量导出：一键生成所有学生错题 ZIP 包
3. **下载文件**：浏览器自动下载生成的文档

---

## 📁 项目结构

```
Fuck-wrong-question/
├── 🚀 start.py                  # 一键启动脚本（推荐）
├── 🏠 main.py                   # FastAPI 主程序
├── ⚙️  config.py                 # 配置文件
├── 📋 requirements.txt          # 依赖包列表
├── 🗄️  wrong_question.db        # SQLite 数据库
│
├── 🗂️  database/                # 数据库层
│   ├── __init__.py
│   └── models.py               # ORM 模型定义
│
├── 🔌 api/                      # REST API 接口
│   ├── papers.py               # 试卷管理
│   ├── questions.py            # 题目管理
│   ├── students.py             # 学生管理
│   ├── categories.py           # 分类管理
│   ├── export.py               # 导出功能
│   ├── document_parser.py      # PDF 解析 API
│   └── pdf_parser_client.py   # PDF 服务客户端
│
├── 🛠️  utils/                   # 工具模块
│   ├── markdown_parser.py      # Markdown 题目切分
│   └── question_order.py       # 题目排序逻辑
│
├── 🎨 static/                   # 静态资源
│   ├── css/style.css           # 全局样式
│   ├── js/utils.js             # 前端工具
│   ├── uploads/                # 图片上传目录
│   └── export_settings/        # 导出配置存储
│
├── 🌐 templates/                # HTML 模板
│   ├── index.html              # 首页（试卷列表）
│   ├── students.html           # 学生管理
│   ├── add_question.html       # 题目录入
│   ├── preview.html            # 试卷预览
│   ├── question_edit.html      # 题目编辑
│   ├── pdf_import.html         # PDF 导入（新）
│   └── export_preview.html     # 导出预览
│
└── 📦 pdf_service/              # PDF 解析微服务
    ├── main.py                 # 服务入口
    ├── config.py               # 服务配置
    ├── requirements.txt        # 服务依赖
    ├── api/parse.py            # 解析 API
    ├── core/parser.py          # 解析核心逻辑
    └── utils/cleaner.py        # 临时文件清理
```

---

## ⚙️ 配置说明

### 基础配置 (config.py)
```python
# 应用信息
APP_NAME = "错题管理系统"
APP_VERSION = "2.0.0"

# 数据库配置
DATABASE_URL = "sqlite:///./wrong_question.db"

# 文件上传
MAX_FILE_SIZE = 52428800  # 50MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

# PDF 解析服务
PDF_PARSER_MODE = "local"           # local 或 remote
PDF_PARSER_URL = "http://localhost:8001"
PDF_PARSER_AUTO_START = True        # 是否自动启动
```

### 环境变量（可选）
创建 `.env` 文件自定义配置：
```bash
# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=false

# PDF 解析服务
PDF_PARSER_MODE=local
PDF_PARSER_PORT=8001
PDF_PARSER_AUTO_START=true
```

---

## 🔧 技术栈

- **后端框架**：FastAPI + SQLAlchemy
- **数据库**：SQLite
- **前端**：原生 JavaScript + Jinja2 模板
- **文档生成**：python-docx
- **PDF 解析**：MinerU + PyMuPDF
- **依赖管理**：pip + requirements.txt

---

## 📄 许可证

本项目基于 **Apache License 2.0** 开源 - 查看 [LICENSE](LICENSE) 了解详情。

---

<div align="center">

**如果这个项目对您有帮助，请不要忘记给它一个 ⭐ Star！**

*让每一道错题都成为进步的阶梯* 🚀

Made with ❤️ by [xinghenLuyus](https://github.com/xinghenLuyus)

</div>
