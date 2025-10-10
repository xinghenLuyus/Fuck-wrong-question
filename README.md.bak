# 🎓 智能错题管理系统

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/yourusername/wrong-question-system.svg)](https://github.com/yourusername/wrong-question-system)

**一个功能强大的现代化错题管理系统，专为教师量身定制**

*支持试卷录入、学生错题标记、高度自定义的Word文档导出和实时预览*

[🚀 快速开始](#-快速开始) • [📱 功能展示](#-功能展示) • [🤝 贡献指南](#-贡献指南)

</div>

---

## ✨ 核心亮点

### 🎯 主要功能
- **📝 试卷管理** - 创建、编辑、删除试卷，支持试卷列表查看和快速检索
- **📷 题目录入** - 多图片拖拽上传，自动题目编号，支持题目文字内容录入
- **👥 学生管理** - 完整的班级和学生信息管理，支持按班级筛选和智能搜索
- **🔍 试卷预览** - 直观展示所有题目截图、题目文字和错题学生信息
- **⚙️ 高级导出配置** - 全局+单题个性化设置，支持字体、图片、间距等精细化配置
- **� 实时Word预览** - 所见即所得的Word文档预览，完美还原最终导出效果
- **�📤 智能导出** - 单个学生Word文档、所有学生批量ZIP导出，支持自定义格式

## 🚀 快速开始

### 📋 环境要求
- **Python 3.9-3.11** (推荐 Python 3.10)
- **操作系统**: Windows / macOS / Linux
- **内存**: 最少 512MB RAM
- **存储**: 最少 100MB 可用空间

### ⚡ 一键启动（推荐）
```bash
# 1. 克隆项目
git clone https://github.com/yourusername/wrong-question-system.git
cd wrong-question-system

# 2. 安装依赖(确保在合适的环境)
python setup.py

# 3. 一键启动（自动检查环境）
python start.py
```

### 🌐 访问应用
启动成功后，在浏览器中访问：
- **本地访问**: http://localhost:8000
- **局域网访问**: http://你的IP地址:8000

## 📁 项目结构

```
wrong-question-system/
├── � start.py               # 一键启动脚本（推荐使用）
├── � main.py                # FastAPI主程序入口
├── ⚙️  config.py             # 应用配置文件
├── 📋 requirements.txt       # Python依赖包列表
├── � wrong_question.db      # SQLite数据库文件
├── �📖 README.md             # 项目说明文档
├── 🧪 test_system.py        # 系统测试文件
├── 
├── �️ database/             # 数据库层
│   ├── __init__.py
│   └── models.py           # SQLAlchemy ORM模型定义
├── 
├── 🔌 api/                  # REST API接口层
│   ├── __init__.py
│   ├── papers.py           # 试卷管理API
│   ├── questions.py        # 题目管理API
│   ├── students.py         # 学生管理API
│   ├── categories.py       # 分类管理API
│   └── export.py           # 导出功能API（核心）
├── 
├── 🎨 static/               # 静态资源目录
│   ├── css/
│   │   └── style.css       # 全局样式文件
│   ├── js/
│   │   └── utils.js        # 前端工具函数库
│   ├── export_settings/    # 导出配置存储
│   │   └── paper_*.json    # 各试卷的导出设置
│   └── uploads/            # 图片上传目录
│       ├── .gitkeep
│       └── *.png/jpg/...   # 用户上传的题目图片
└── 
└── 🌐 templates/            # Jinja2 HTML模板
    ├── index.html          # 首页（试卷列表管理）
    ├── students.html       # 学生信息管理页面
    ├── add_question.html   # 题目录入页面
    ├── preview.html        # 试卷预览和导出设置
    └── export_preview.html # 单学生导出预览页面
```

## 🎯 使用流程

### 第一步：学生信息准备 👥
1. 点击右上角「👥 学生管理」
2. 按班级添加学生基本信息（班级、学号、姓名）
3. 利用搜索和筛选功能管理学生信息

### 第二步：创建试卷 📝
1. 在首页点击「➕ 添加新试卷」
2. 输入试卷名称（如：期中考试、单元测试等）
3. 系统自动跳转到题目录入页面

### 第三步：录入题目 📷
1. **上传题目图片**：拖拽或点击上传，支持多张图片
2. **录入题目文字**：补充题目的文字内容（可选）
3. **标记错题学生**：搜索并选择做错的学生
4. **保存题目**：选择"保存并继续"或"保存并返回"

### 第四步：预览和配置 🔍
1. **查看题目**：在试卷预览页面查看所有录入的题目
2. **编辑调整**：点击题目可修改图片、文字和错题学生
3. **导出设置**：配置全局导出样式和单题个性化设置
4. **实时预览**：查看最终Word文档效果

### 第五步：导出错题 📤
1. **选择导出方式**：
   - 👤 单个学生：选择学生，预览并下载个人错题文档
   - 📦 批量导出：一键生成所有学生错题，下载ZIP压缩包
2. **下载文件**：支持浏览器直接下载

## ⚙️ 配置说明

### 🔧 基础配置 (config.py)
```python
# 应用信息
APP_NAME = "错题管理系统"
APP_VERSION = "2.0.0"

# 数据库配置
DATABASE_URL = "sqlite:///wrong_question.db"

# 文件上传限制
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

# 服务器配置
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True  # 生产环境请设置为 False
```

### 📁 目录权限设置
```bash
# 确保上传目录有写权限
chmod 755 static/uploads
chmod 755 static/export_settings

# 确保数据库文件有写权限
chmod 644 wrong_question.db
```

### 💾 数据备份策略
```bash
# 数据库备份
cp wrong_question.db backup/wrong_question_$(date +%Y%m%d).db

# 上传文件备份
tar -czf backup/uploads_$(date +%Y%m%d).tar.gz static/uploads/

# 配置文件备份
tar -czf backup/settings_$(date +%Y%m%d).tar.gz static/export_settings/
```

## 🤝 贡献指南

### � 参与贡献

我们欢迎所有形式的贡献！无论是bug报告、功能建议、代码贡献还是文档改进。

### 🏆 贡献者

感谢所有为项目做出贡献的开发者！

<!-- 这里可以添加贡献者头像 -->

## 📄 许可证

本项目基于 **Apache License 2.0** 开源 - 查看 [LICENSE](LICENSE) 文件了解详情。


### 💖 支持项目

如果这个项目对你有帮助，请考虑：

- ⭐ **给项目点Star** - 这是对我们最大的鼓励
- 🐛 **报告Bug** - 帮助我们发现和修复问题
- 🔧 **参与开发** - 一起让项目变得更好

---

<div align="center">

**如果这个项目对您有帮助，请不要忘记给它一个 ⭐ Star！**

*让每一道错题都成为进步的阶梯* 🚀

</div>

