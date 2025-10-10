"""
PDF解析核心逻辑

提取自MinerU/test_parse.py，封装为可调用的函数
"""

import copy
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger

from mineru.cli.common import convert_pdf_bytes_to_bytes_by_pypdfium2, prepare_env, read_fn
from mineru.data.data_reader_writer import FileBasedDataWriter
from mineru.utils.draw_bbox import draw_layout_bbox, draw_span_bbox
from mineru.utils.enum_class import MakeMode
from mineru.backend.vlm.vlm_analyze import doc_analyze as vlm_doc_analyze
from mineru.backend.pipeline.pipeline_analyze import doc_analyze as pipeline_doc_analyze
from mineru.backend.pipeline.pipeline_middle_json_mkcontent import union_make as pipeline_union_make
from mineru.backend.pipeline.model_json_to_middle_json import result_to_middle_json as pipeline_result_to_middle_json
from mineru.backend.vlm.vlm_middle_json_mkcontent import union_make as vlm_union_make


def parse_pdf(
    pdf_bytes: bytes,
    output_dir: str,
    file_name: str,
    lang: str = "ch",
    backend: str = "pipeline",
    parse_method: str = "auto",
    formula_enable: bool = False,
    table_enable: bool = False,
    server_url: Optional[str] = None,
    start_page_id: int = 0,
    end_page_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    解析单个PDF文件
    
    Args:
        pdf_bytes: PDF文件字节流
        output_dir: 输出目录
        file_name: 文件名（不含扩展名）
        lang: 语言代码，默认'ch'
        backend: 解析后端，可选 'pipeline', 'vlm-transformers', 'vlm-vllm-engine', 'vlm-http-client'
        parse_method: 解析方法，可选 'auto', 'txt', 'ocr'
        formula_enable: 是否启用公式解析
        table_enable: 是否启用表格解析
        server_url: 当backend为http-client时的服务器地址
        start_page_id: 起始页码
        end_page_id: 结束页码
    
    Returns:
        Dict[str, Any]: 解析结果，包含markdown内容、图片列表等
    """
    try:
        if backend == "pipeline":
            return _parse_with_pipeline(
                pdf_bytes, output_dir, file_name, lang,
                parse_method, formula_enable, table_enable,
                start_page_id, end_page_id
            )
        else:
            # VLM后端
            if backend.startswith("vlm-"):
                backend = backend[4:]
            
            return _parse_with_vlm(
                pdf_bytes, output_dir, file_name,
                backend, server_url,
                start_page_id, end_page_id
            )
    except Exception as e:
        logger.exception(f"解析PDF失败: {e}")
        raise


def _parse_with_pipeline(
    pdf_bytes: bytes,
    output_dir: str,
    file_name: str,
    lang: str,
    parse_method: str,
    formula_enable: bool,
    table_enable: bool,
    start_page_id: int,
    end_page_id: Optional[int]
) -> Dict[str, Any]:
    """使用Pipeline后端解析PDF"""
    
    # 转换PDF页面
    new_pdf_bytes = convert_pdf_bytes_to_bytes_by_pypdfium2(
        pdf_bytes, start_page_id, end_page_id
    )
    
    # 调用解析
    infer_results, all_image_lists, all_pdf_docs, lang_list, ocr_enabled_list = \
        pipeline_doc_analyze(
            [new_pdf_bytes], [lang],
            parse_method=parse_method,
            formula_enable=formula_enable,
            table_enable=table_enable
        )
    
    # 处理结果
    model_list = infer_results[0]
    model_json = copy.deepcopy(model_list)
    
    # 准备输出环境
    local_image_dir, local_md_dir = prepare_env(output_dir, file_name, parse_method)
    image_writer = FileBasedDataWriter(local_image_dir)
    md_writer = FileBasedDataWriter(local_md_dir)
    
    images_list = all_image_lists[0]
    pdf_doc = all_pdf_docs[0]
    _lang = lang_list[0]
    _ocr_enable = ocr_enabled_list[0]
    
    # 生成中间JSON
    middle_json = pipeline_result_to_middle_json(
        model_list, images_list, pdf_doc,
        image_writer, _lang, _ocr_enable, formula_enable
    )
    
    # 生成输出
    pdf_info = middle_json["pdf_info"]
    image_dir = str(os.path.basename(local_image_dir))
    
    # 生成Markdown
    md_content_str = pipeline_union_make(pdf_info, MakeMode.MM_MD, image_dir)
    md_writer.write_string(f"{file_name}.md", md_content_str)
    
    # 生成内容列表
    content_list = pipeline_union_make(pdf_info, MakeMode.CONTENT_LIST, image_dir)
    md_writer.write_string(
        f"{file_name}_content_list.json",
        json.dumps(content_list, ensure_ascii=False, indent=4)
    )
    
    # 生成中间JSON
    md_writer.write_string(
        f"{file_name}_middle.json",
        json.dumps(middle_json, ensure_ascii=False, indent=4)
    )
    
    # 生成模型输出
    md_writer.write_string(
        f"{file_name}_model.json",
        json.dumps(model_json, ensure_ascii=False, indent=4)
    )
    
    logger.info(f"解析完成，输出目录: {local_md_dir}")
    
    return {
        "success": True,
        "output_dir": str(local_md_dir),
        "markdown_file": f"{file_name}.md",
        "markdown_content": md_content_str,
        "content_list": content_list,
        "image_dir": str(local_image_dir)
    }


def _parse_with_vlm(
    pdf_bytes: bytes,
    output_dir: str,
    file_name: str,
    backend: str,
    server_url: Optional[str],
    start_page_id: int,
    end_page_id: Optional[int]
) -> Dict[str, Any]:
    """使用VLM后端解析PDF"""
    
    # 转换PDF页面
    pdf_bytes = convert_pdf_bytes_to_bytes_by_pypdfium2(
        pdf_bytes, start_page_id, end_page_id
    )
    
    # 准备输出环境
    parse_method = "vlm"
    local_image_dir, local_md_dir = prepare_env(output_dir, file_name, parse_method)
    image_writer = FileBasedDataWriter(local_image_dir)
    md_writer = FileBasedDataWriter(local_md_dir)
    
    # 调用VLM解析
    middle_json, infer_result = vlm_doc_analyze(
        pdf_bytes,
        image_writer=image_writer,
        backend=backend,
        server_url=server_url
    )
    
    # 生成输出
    pdf_info = middle_json["pdf_info"]
    image_dir = str(os.path.basename(local_image_dir))
    
    # 生成Markdown
    md_content_str = vlm_union_make(pdf_info, MakeMode.MM_MD, image_dir)
    md_writer.write_string(f"{file_name}.md", md_content_str)
    
    # 生成内容列表
    content_list = vlm_union_make(pdf_info, MakeMode.CONTENT_LIST, image_dir)
    md_writer.write_string(
        f"{file_name}_content_list.json",
        json.dumps(content_list, ensure_ascii=False, indent=4)
    )
    
    # 生成中间JSON
    md_writer.write_string(
        f"{file_name}_middle.json",
        json.dumps(middle_json, ensure_ascii=False, indent=4)
    )
    
    # 生成模型输出
    md_writer.write_string(
        f"{file_name}_model.json",
        json.dumps(infer_result, ensure_ascii=False, indent=4)
    )
    
    logger.info(f"解析完成，输出目录: {local_md_dir}")
    
    return {
        "success": True,
        "output_dir": str(local_md_dir),
        "markdown_file": f"{file_name}.md",
        "markdown_content": md_content_str,
        "content_list": content_list,
        "image_dir": str(local_image_dir)
    }
