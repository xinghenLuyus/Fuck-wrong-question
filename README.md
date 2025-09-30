# 🎓 智能错题管理系统

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/yourusername/wrong-question-system.svg)](https://github.com/yourusername/wrong-question-system)

**一个功能强大的现代化错题管理系统，专为教师量身定制**

*支持试卷录入、学生错题标记、高度自定义的Word文档导出和实时预览*

[🚀 快速开始](#-快速开始) • [📱 功能展示](#-功能展示) • [🔧 API文档](#-api接口) • [🤝 贡献指南](#-贡献指南)

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

### 🛠 技术特色
- **现代化架构** - FastAPI + SQLAlchemy + 原生前端，高性能异步处理
- **响应式设计** - 完美适配手机、平板、桌面设备，随时随地使用
- **数据安全** - SQLite本地数据库，数据完全可控，支持备份导出
- **智能配置** - 支持全局设置+单题个性化覆盖的层级配置系统
- **实时预览** - 导出前可实时预览Word文档效果，确保完美呈现
- **零依赖部署** - 一键启动脚本，自动检查环境和依赖

## 🔧 技术栈

<table>
<tr>
<td><strong>后端框架</strong></td>
<td>FastAPI 0.104.1 - 现代化Python Web框架</td>
</tr>
<tr>
<td><strong>数据库</strong></td>
<td>SQLite + SQLAlchemy 2.0.23 - 轻量级关系数据库</td>
</tr>
<tr>
<td><strong>前端技术</strong></td>
<td>HTML5 + CSS3 + 原生JavaScript - 轻量无依赖</td>
</tr>
<tr>
<td><strong>文档处理</strong></td>
<td>python-docx 1.1.0 - Word文档生成和格式化</td>
</tr>
<tr>
<td><strong>图片处理</strong></td>
<td>Pillow 10.1.0 - 图片上传、压缩、格式转换</td>
</tr>
<tr>
<td><strong>文件上传</strong></td>
<td>python-multipart 0.0.6 - 多文件异步上传</td>
</tr>
<tr>
<td><strong>模板引擎</strong></td>
<td>Jinja2 3.1.2 - 动态HTML渲染</td>
</tr>
</table>

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

# 2. 安装依赖
pip install -r requirements.txt

# 3. 一键启动（自动检查环境）
python start.py
```

### 🐍 手动安装
```bash
# 创建虚拟环境
python -m venv venv

# 激活环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖并启动
pip install -r requirements.txt
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

## 📱 功能展示

### 🏠 试卷管理首页
- **📊 试卷概览**: 显示所有试卷，按创建时间倒序排列
- **➕ 快速创建**: 一键创建新试卷，自动跳转题目录入
- **🗂️ 试卷操作**: 预览试卷、删除试卷、快速导航
- **📈 统计信息**: 显示题目数量、学生错题统计

### 📝 智能题目录入
- **🖼️ 多图上传**: 支持拖拽上传、批量选择、实时预览
- **📝 文字录入**: 支持题目文字内容录入，可配合图片使用
- **👥 学生选择**: 智能搜索学生，支持多选、批量操作
- **🔢 自动编号**: 系统自动为题目分配连续序号
- **💾 灵活保存**: 保存继续添加 or 保存返回预览

### 👥 学生信息管理
- **📚 班级管理**: 按班级分组显示，支持班级筛选
- **🔍 智能搜索**: 支持按姓名、学号、班级实时搜索
- **✏️ 信息维护**: 添加、编辑、删除学生信息
- **📊 统计功能**: 显示各班级学生数量统计

### 🔍 试卷预览与编辑
- **👁️ 直观预览**: 题目图片、文字内容、错题学生一目了然
- **✏️ 在线编辑**: 点击题目可修改图片、文字和错题学生
- **⚙️ 导出设置**: 强大的全局+单题个性化配置系统
- **🔧 设置继承**: 单题设置可继承或覆盖全局设置

### 📤 高级导出系统

#### 🌐 全局导出设置
- **📝 字体配置**: 标题、题号、正文字体大小独立设置
- **🖼️ 图片控制**: 图片缩放比例、显示宽度精确控制
- **📏 间距调整**: 题目间距、留白行数自定义设置
- **📄 内容控制**: 学生信息头部、题目文字显示开关

#### 🎯 单题个性化设置
- **🔧 独立配置**: 每道题可单独设置字体、图片、间距
- **📋 设置继承**: 继承全局设置，仅覆盖需要调整的项目
- **🔄 快速重置**: 一键重置为全局设置
- **👁️ 实时预览**: 配置修改后立即预览效果

#### � Word导出功能
- **👤 单学生导出**: 生成个人专属错题文档
- **📦 批量导出**: 一键生成所有学生错题，自动打包ZIP
- **🎨 格式美观**: Word文档排版整齐，支持自定义样式
- **💾 下载管理**: 支持在线预览和直接下载

### 📋 实时Word预览
- **👀 所见即所得**: 完美还原最终Word文档效果
- **⚙️ 配置同步**: 实时应用导出配置，预览即最终效果
- **📐 尺寸精确**: 按照Word标准显示字体大小和图片尺寸
- **🖼️ 图片处理**: 自动转换图片尺寸，模拟Word显示效果

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

## 📊 数据库设计

### 🗂️ 数据表结构

#### 试卷表 (papers)
| 字段名 | 数据类型 | 说明 | 约束 |
|--------|----------|------|------|
| id | INTEGER | 主键ID | PRIMARY KEY, AUTOINCREMENT |
| name | TEXT | 试卷名称 | NOT NULL |
| created_at | DATETIME | 创建时间 | DEFAULT CURRENT_TIMESTAMP |

#### 题目表 (questions)
| 字段名 | 数据类型 | 说明 | 约束 |
|--------|----------|------|------|
| id | INTEGER | 主键ID | PRIMARY KEY, AUTOINCREMENT |
| paper_id | INTEGER | 试卷ID | FOREIGN KEY -> papers.id |
| question_no | INTEGER | 题目序号 | NOT NULL |
| question_text | TEXT | 题目文字内容 | NULLABLE |
| image_urls | TEXT | 图片URL列表 | 逗号分隔存储 |
| wrong_students | TEXT | 错题学生ID列表 | 逗号分隔存储 |
| created_at | DATETIME | 创建时间 | DEFAULT CURRENT_TIMESTAMP |

#### 学生表 (students)
| 字段名 | 数据类型 | 说明 | 约束 |
|--------|----------|------|------|
| id | INTEGER | 主键ID | PRIMARY KEY, AUTOINCREMENT |
| class_name | TEXT | 班级名称 | NOT NULL |
| student_no | TEXT | 学号 | UNIQUE, NOT NULL |
| name | TEXT | 学生姓名 | NOT NULL |
| created_at | DATETIME | 创建时间 | DEFAULT CURRENT_TIMESTAMP |

### 🔧 导出配置文件结构
```json
{
  "title_size": 16,           // 标题字体大小
  "question_number_size": 14, // 题号字体大小
  "text_size": 12,           // 正文字体大小
  "line_spacing": 1.5,       // 行间距
  "image_scale": 1.0,        // 图片缩放比例
  "image_width": 5.0,        // 图片宽度(英寸)
  "question_spacing": 0,     // 题目后留白行数
  "show_student_info": true, // 显示学生信息
  "show_question_text": true,// 显示题目文字
  "question_overrides": {    // 单题覆盖设置
    "1": {                   // 题目ID
      "question_number_size": 18,
      "text_size": 14
    }
  }
}
```

## 🔧 API接口

### 📋 试卷管理
```http
GET    /api/papers/              # 获取试卷列表
POST   /api/papers/              # 创建新试卷
DELETE /api/papers/{paper_id}    # 删除试卷
```

### 📝 题目管理
```http
GET    /api/questions/paper/{paper_id}    # 获取试卷下的所有题目
POST   /api/questions/                    # 创建新题目
PUT    /api/questions/{question_id}       # 更新题目信息
DELETE /api/questions/{question_id}       # 删除题目
```

### 👥 学生管理
```http
GET    /api/students/           # 获取学生列表
POST   /api/students/           # 创建新学生
PUT    /api/students/{id}       # 更新学生信息
DELETE /api/students/{id}       # 删除学生
```

### 📤 导出功能
```http
GET    /api/export/settings/{paper_id}           # 获取导出设置
POST   /api/export/settings/{paper_id}           # 保存导出设置
POST   /api/export/student/{paper_id}            # 导出单个学生错题
POST   /api/export/all/{paper_id}                # 导出所有学生错题
GET    /api/export/preview/{paper_id}            # 获取预览数据
GET    /download/{filename}                      # 下载文件
```

### 📁 文件上传
```http
POST   /api/upload             # 上传图片文件
```

## 🚀 部署指南

### 🏠 本地开发环境
```bash
# 克隆项目
git clone https://github.com/yourusername/wrong-question-system.git
cd wrong-question-system

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器（支持热重载）
python start.py
```

### 🌐 生产环境部署

#### 使用 Gunicorn（Linux/macOS）
```bash
# 安装Gunicorn
pip install gunicorn

# 启动生产服务器
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 使用 Docker
```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# 构建和运行
docker build -t wrong-question-system .
docker run -p 8000:8000 -v ./data:/app/data wrong-question-system
```

#### Nginx 反向代理配置
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /static/ {
        alias /path/to/your/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

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

## 🔒 安全建议

### 🛡️ 生产环境安全配置
1. **关闭调试模式**: 设置 `DEBUG = False`
2. **配置防火墙**: 仅开放必要端口
3. **定期备份**: 备份数据库和上传文件
4. **SSL证书**: 使用HTTPS加密传输
5. **访问控制**: 配置IP白名单或用户认证

### 💾 数据备份策略
```bash
# 数据库备份
cp wrong_question.db backup/wrong_question_$(date +%Y%m%d).db

# 上传文件备份
tar -czf backup/uploads_$(date +%Y%m%d).tar.gz static/uploads/

# 配置文件备份
tar -czf backup/settings_$(date +%Y%m%d).tar.gz static/export_settings/
```

## 🚧 故障排除

### ❗ 常见问题及解决方案

#### 1. 依赖安装失败
```bash
# 问题：pip安装依赖时出错
# 解决：升级pip并清理缓存
python -m pip install --upgrade pip
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

#### 2. 端口被占用
```bash
# 问题：端口8000已被占用
# 解决：修改config.py中的PORT设置或终止占用进程
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # macOS/Linux
```

#### 3. 文件上传失败
```bash
# 问题：图片上传失败
# 解决：检查目录权限和磁盘空间
ls -la static/uploads/        # 检查权限
df -h                         # 检查磁盘空间
```

#### 4. Word导出异常
```bash
# 问题：Word文档生成失败
# 解决：检查python-docx版本和图片文件
pip show python-docx
# 确保图片文件存在且格式正确
```

#### 5. 数据库错误
```bash
# 问题：数据库连接失败
# 解决：检查数据库文件权限和SQLite版本
sqlite3 wrong_question.db ".schema"  # 检查数据库结构
```

### 🔍 日志查看
```bash
# 启动应用时查看详细日志
python start.py --log-level debug

# 或使用uvicorn直接启动
uvicorn main:app --reload --log-level debug
```

## 🎯 性能优化

### ⚡ 前端优化
- **图片压缩**: 上传时自动压缩大图片
- **缓存策略**: 静态资源设置适当缓存时间
- **懒加载**: 大量题目时使用分页加载

### 🚀 后端优化
- **数据库索引**: 为常用查询字段添加索引
- **异步处理**: 使用FastAPI的异步特性
- **文件清理**: 定期清理过期的导出文件

### 📊 监控建议
- **资源监控**: 监控CPU、内存、磁盘使用率
- **日志分析**: 分析错误日志和访问日志
- **性能指标**: 监控API响应时间和数据库查询性能

## 🔮 未来规划

### 🎯 即将推出的功能
- [ ] 🤖 **OCR自动识别** - 自动识别题目图片中的文字内容
- [ ] 📊 **数据统计分析** - 错题率统计、学生表现分析
- [ ] 👥 **多用户权限管理** - 支持教师、管理员等不同角色
- [ ] 📱 **移动端APP** - 原生iOS/Android应用
- [ ] 🎨 **Word模板自定义** - 更多导出样式和模板选择

### 🛠 技术改进计划
- [ ] ⚡ **性能优化** - 数据库查询优化、前端加载优化
- [ ] 🔐 **安全增强** - 用户认证、数据加密、访问控制
- [ ] 🌐 **国际化支持** - 多语言界面支持
- [ ] ☁️ **云存储支持** - 支持阿里云OSS、腾讯云COS等
- [ ] 🔄 **数据同步** - 支持多设备数据同步

## 🤝 贡献指南

### � 参与贡献

我们欢迎所有形式的贡献！无论是bug报告、功能建议、代码贡献还是文档改进。

#### 🐛 报告Bug
1. 在 [Issues](https://github.com/yourusername/wrong-question-system/issues) 中搜索是否已有相同问题
2. 如果没有，请创建新的Issue，并提供：
   - 详细的问题描述
   - 复现步骤
   - 环境信息（操作系统、Python版本等）
   - 错误日志或截图

#### ✨ 建议新功能
1. 在 [Issues](https://github.com/yourusername/wrong-question-system/issues) 中创建Feature Request
2. 详细描述功能需求和使用场景
3. 说明该功能的重要性和预期效果

#### 🔧 代码贡献
1. **Fork项目** 到你的GitHub账号
2. **创建分支** `git checkout -b feature/AmazingFeature`
3. **编写代码** 并确保遵循项目代码规范
4. **运行测试** `python test_system.py`
5. **提交更改** `git commit -m 'Add some AmazingFeature'`
6. **推送分支** `git push origin feature/AmazingFeature`
7. **创建Pull Request**

#### 📝 代码规范
- **Python代码**: 遵循PEP 8规范
- **JavaScript代码**: 使用2空格缩进，分号结尾
- **注释**: 重要功能必须有中文注释
- **命名**: 使用有意义的变量和函数名

### 🏆 贡献者

感谢所有为项目做出贡献的开发者！

<!-- 这里可以添加贡献者头像 -->

## 📄 许可证

本项目基于 **MIT许可证** 开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

### 🎯 MIT许可证说明
- ✅ **商业使用** - 可用于商业项目
- ✅ **修改** - 可以修改源代码
- ✅ **分发** - 可以分发原始或修改后的代码
- ✅ **私人使用** - 可以私人使用
- ❗ **责任** - 作者不承担任何责任
- ❗ **保修** - 不提供任何形式的保修

## � 致谢

### 🎉 特别感谢
- **FastAPI团队** - 提供优秀的Web框架
- **SQLAlchemy团队** - 强大的ORM工具
- **python-docx团队** - Word文档处理库
- **所有贡献者** - 让项目变得更好

### 💖 支持项目

如果这个项目对你有帮助，请考虑：

- ⭐ **给项目点Star** - 这是对我们最大的鼓励
- 🐛 **报告Bug** - 帮助我们发现和修复问题
- 💡 **提出建议** - 让项目功能更完善
- 🔧 **参与开发** - 一起让项目变得更好
- 📢 **分享推荐** - 让更多人受益

---

<div align="center">

### 📞 联系我们

🌐 **项目主页**: [GitHub Repository](https://github.com/yourusername/wrong-question-system)

📧 **邮箱联系**: your-email@example.com

💬 **问题反馈**: [GitHub Issues](https://github.com/yourusername/wrong-question-system/issues)

📱 **QQ群**: 123456789（错题管理系统交流群）

---

**如果这个项目对您有帮助，请不要忘记给它一个 ⭐ Star！**

*让每一道错题都成为进步的阶梯* 🚀

</div>

