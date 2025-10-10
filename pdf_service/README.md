# PDF解析微服务

基于 [MinerU](https://github.com/opendatalab/MinerU) 的独立PDF解析服务，支持文本提取、OCR、公式和表格识别。

## 部署模式

### 1. 本地子进程模式（默认）

主服务自动启动PDF解析服务作为子进程，无需手动管理：

```bash
# 在项目根目录的 .env 文件中配置
PDF_PARSER_MODE=local
PDF_PARSER_AUTO_START=true
PDF_PARSER_PORT=8001

# 启动主服务即可，PDF解析服务会自动启动
python start.py
```


### 2. 独立服务模式

PDF解析服务独立运行，可部署在其他机器或容器：

```bash
# 步骤1: 安装微服务依赖
cd pdf_service
python setup.py

# 步骤2: 启动服务
# 方式1：直接运行（推荐，已支持）
python main.py

# 方式2：模块方式运行（从项目根目录）
cd ..
python -m pdf_service.main

# 方式3：使用uvicorn（从项目根目录）
uvicorn pdf_service.main:app --host 0.0.0.0 --port 8001
```

**说明**：
- 独立部署需要在 `pdf_service/.env` 配置服务参数
- `setup.py` 会自动安装 `mineru[core]` 及其依赖
- 会自动下载 MinerU 模型（pipeline 模式）
- 模型会下载到用户目录（`~/.mineru/`）
- **详细配置说明**：查看 [CONFIG.md](./CONFIG.md)

在主服务的 `.env` 中配置远程地址：

```bash
PDF_PARSER_MODE=remote
PDF_PARSER_URL=http://other-server:8001
```

### 3. 容器化部署

创建 `Dockerfile`（在 `pdf_service/` 目录）：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制微服务代码
COPY . .

# 安装微服务依赖
RUN python setup.py

# 暴露端口
EXPOSE 8001

# 启动服务
CMD ["uvicorn", "pdf_service.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

构建和运行：

```bash
# 构建镜像
docker build -t pdf-parser:latest .

# 运行容器
docker run -d -p 8001:8001 \
  -e MINERU_MODEL_SOURCE=local \
  -e MINERU_BACKEND=pipeline \
  --name pdf-parser \
  pdf-parser:latest
```

## API 接口

### POST /api/pdf/parse

解析PDF文件，返回访问路径。

**请求：**
```bash
curl -X POST "http://localhost:8001/api/pdf/parse" \
  -F "file=@document.pdf" \
  -F "lang=ch" \
  -F "parse_method=auto"
```

**响应（简化）：**
```json
{
  "success": true,
  "message": "解析成功",
  "data": {
    "task_id": "5e6142bc-49d7-4536-bdd3-f196630ca228",
    "file_name": "document",
    "auto_dir_url": "/files/5e6142bc-49d7-4536-bdd3-f196630ca228/document/auto"
  }
}
```

**使用 auto_dir_url 访问文件：**
- Markdown: `{auto_dir_url}/{file_name}.md`
- 图片: `{auto_dir_url}/images/{image_name}.jpg`
- Content List: `{auto_dir_url}/{file_name}_content_list.json`

**参数：**
- `file`: PDF文件（必填）
- `lang`: 语言代码，默认 `ch`（可选：en, korean, japan）
- `backend`: 解析后端，默认 `pipeline`
- `parse_method`: 解析方法，默认 `auto`（可选：txt, ocr）
- `formula_enable`: 是否启用公式解析，默认 `false`
- `table_enable`: 是否启用表格解析，默认 `false`
- `start_page`: 起始页码，默认 `0`
- `end_page`: 结束页码，默认 `null`（全部）

### GET /api/pdf/result/{task_id}

获取 Markdown 内容（兼容旧版）。

**响应：**
```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "task_id": "xxx",
    "markdown_content": "...",
    "markdown_file": "document.md"
  }
}
```

### DELETE /api/pdf/result/{task_id}

删除解析结果。

**响应：**
```json
{
  "success": true,
  "message": "删除成功"
}
```

### POST /api/pdf/cleanup

手动清理过期文件（超过24小时）。

**响应：**
```json
{
  "success": true,
  "message": "清理完成",
  "data": {
    "deleted_count": 3,
    "freed_space_mb": 125.6
  }
}
```

## 环境配置

在 `.env` 文件中配置：

```bash
# PDF解析服务配置
PDF_PARSER_MODE=local              # 部署模式: local(子进程) / remote(远程服务)
PDF_PARSER_AUTO_START=true         # 本地模式是否自动启动
PDF_PARSER_HOST=0.0.0.0           # 监听地址
PDF_PARSER_PORT=8001              # 监听端口
PDF_PARSER_URL=http://localhost:8001  # 服务地址（remote模式使用）

# MinerU配置
MINERU_MODEL_SOURCE=local         # 模型来源: local / huggingface
MINERU_BACKEND=pipeline           # 解析后端: pipeline / vlm-transformers
MINERU_PARSE_METHOD=auto          # 解析方法: auto / txt / ocr
MINERU_DEFAULT_LANG=ch            # 默认语言: ch / en / korean / japan
```

