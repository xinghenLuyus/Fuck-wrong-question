# Copyright (c) Opendatalab. All rights reserved.
# 此为官方文档，仅供参考mineru用法，项目已经二次封装。
import copy
import json
import os
from pathlib import Path

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
from mineru.utils.guess_suffix_or_lang import guess_suffix_by_path


def do_parse(
    output_dir,  # 解析结果输出目录
    pdf_file_names: list[str],  # 待解析的PDF文件名列表
    pdf_bytes_list: list[bytes],  # 待解析的PDF字节流列表
    p_lang_list: list[str],  # 每个PDF的语言列表，默认'zh'（中文）
    backend="pipeline",  # 解析PDF所用后端，默认pipeline
    parse_method="auto",  # 解析PDF的方法，默认自动
    formula_enable=False,  # 是否启用公式解析
    table_enable=False,  # 是否启用表格解析
    server_url=None,  # vlm-http-client后端的服务器地址
    f_draw_layout_bbox=True,  # 是否绘制版面框
    f_draw_span_bbox=True,  # 是否绘制文本框
    f_dump_md=True,  # 是否导出markdown文件
    f_dump_middle_json=True,  # 是否导出中间json文件
    f_dump_model_output=True,  # 是否导出模型输出文件
    f_dump_orig_pdf=False,  # 是否导出原始PDF
    f_dump_content_list=True,  # 是否导出内容列表文件
    f_make_md_mode=MakeMode.MM_MD,  # 生成markdown内容的模式，默认MM_MD
    start_page_id=0,  # 解析起始页码，默认0
    end_page_id=None,  # 解析结束页码，默认None（解析到文档结尾）
):

    if backend == "pipeline":
        for idx, pdf_bytes in enumerate(pdf_bytes_list):
            new_pdf_bytes = convert_pdf_bytes_to_bytes_by_pypdfium2(pdf_bytes, start_page_id, end_page_id)
            pdf_bytes_list[idx] = new_pdf_bytes

        infer_results, all_image_lists, all_pdf_docs, lang_list, ocr_enabled_list = pipeline_doc_analyze(pdf_bytes_list, p_lang_list, parse_method=parse_method, formula_enable=formula_enable,table_enable=table_enable)

        for idx, model_list in enumerate(infer_results):
            model_json = copy.deepcopy(model_list)
            pdf_file_name = pdf_file_names[idx]
            local_image_dir, local_md_dir = prepare_env(output_dir, pdf_file_name, parse_method)
            image_writer, md_writer = FileBasedDataWriter(local_image_dir), FileBasedDataWriter(local_md_dir)

            images_list = all_image_lists[idx]
            pdf_doc = all_pdf_docs[idx]
            _lang = lang_list[idx]
            _ocr_enable = ocr_enabled_list[idx]
            middle_json = pipeline_result_to_middle_json(model_list, images_list, pdf_doc, image_writer, _lang, _ocr_enable, formula_enable)

            pdf_info = middle_json["pdf_info"]

            pdf_bytes = pdf_bytes_list[idx]
            _process_output(
                pdf_info, pdf_bytes, pdf_file_name, local_md_dir, local_image_dir,
                md_writer, f_draw_layout_bbox, f_draw_span_bbox, f_dump_orig_pdf,
                f_dump_md, f_dump_content_list, f_dump_middle_json, f_dump_model_output,
                f_make_md_mode, middle_json, model_json, is_pipeline=True
            )
    else:
        if backend.startswith("vlm-"):
            backend = backend[4:]

        f_draw_span_bbox = False
        parse_method = "vlm"
        for idx, pdf_bytes in enumerate(pdf_bytes_list):
            pdf_file_name = pdf_file_names[idx]
            pdf_bytes = convert_pdf_bytes_to_bytes_by_pypdfium2(pdf_bytes, start_page_id, end_page_id)
            local_image_dir, local_md_dir = prepare_env(output_dir, pdf_file_name, parse_method)
            image_writer, md_writer = FileBasedDataWriter(local_image_dir), FileBasedDataWriter(local_md_dir)
            middle_json, infer_result = vlm_doc_analyze(pdf_bytes, image_writer=image_writer, backend=backend, server_url=server_url)

            pdf_info = middle_json["pdf_info"]

            _process_output(
                pdf_info, pdf_bytes, pdf_file_name, local_md_dir, local_image_dir,
                md_writer, f_draw_layout_bbox, f_draw_span_bbox, f_dump_orig_pdf,
                f_dump_md, f_dump_content_list, f_dump_middle_json, f_dump_model_output,
                f_make_md_mode, middle_json, infer_result, is_pipeline=False
            )


def _process_output(
        pdf_info,
        pdf_bytes,
        pdf_file_name,
        local_md_dir,
        local_image_dir,
        md_writer,
        f_draw_layout_bbox,
        f_draw_span_bbox,
        f_dump_orig_pdf,
        f_dump_md,
        f_dump_content_list,
        f_dump_middle_json,
        f_dump_model_output,
        f_make_md_mode,
        middle_json,
        model_output=None,
        is_pipeline=True
):
    """处理输出文件，包括保存PDF、markdown、内容列表等"""
    if f_draw_layout_bbox:
        draw_layout_bbox(pdf_info, pdf_bytes, local_md_dir, f"{pdf_file_name}_layout.pdf")

    if f_draw_span_bbox:
        draw_span_bbox(pdf_info, pdf_bytes, local_md_dir, f"{pdf_file_name}_span.pdf")

    if f_dump_orig_pdf:
        md_writer.write(
            f"{pdf_file_name}_origin.pdf",
            pdf_bytes,
        )

    image_dir = str(os.path.basename(local_image_dir))

    if f_dump_md:
        make_func = pipeline_union_make if is_pipeline else vlm_union_make
        md_content_str = make_func(pdf_info, f_make_md_mode, image_dir)
        md_writer.write_string(
            f"{pdf_file_name}.md",
            md_content_str,
        )

    if f_dump_content_list:
        make_func = pipeline_union_make if is_pipeline else vlm_union_make
        content_list = make_func(pdf_info, MakeMode.CONTENT_LIST, image_dir)
        md_writer.write_string(
            f"{pdf_file_name}_content_list.json",
            json.dumps(content_list, ensure_ascii=False, indent=4),
        )

    if f_dump_middle_json:
        md_writer.write_string(
            f"{pdf_file_name}_middle.json",
            json.dumps(middle_json, ensure_ascii=False, indent=4),
        )

    if f_dump_model_output:
        md_writer.write_string(
            f"{pdf_file_name}_model.json",
            json.dumps(model_output, ensure_ascii=False, indent=4),
        )

    logger.info(f"local output dir is {local_md_dir}")


def parse_doc(
        path_list: list[Path],
        output_dir,
        lang="ch",
        backend="pipeline",
        method="auto",
        server_url=None,
        start_page_id=0,
        end_page_id=None
):
    """
        参数说明：
        path_list: 待解析文档路径列表，可以是PDF或图片文件。
        output_dir: 解析结果输出目录。
        lang: 语言选项，默认'zh'，可选['ch', 'ch_server', 'ch_lite', 'en', 'korean', 'japan', 'chinese_cht', 'ta', 'te', 'ka']。
            若已知PDF内语言可填写，提高OCR准确率，仅pipeline后端有效。
        backend: 解析后端：
            pipeline：通用。
            vlm-transformers：通用。
            vlm-vllm-engine：更快（engine）。
            vlm-http-client：更快（client）。
            不指定method时默认pipeline。
        method: 解析方法：
            auto：自动根据文件类型选择。
            txt：文本提取。
            ocr：图片PDF用OCR。
            不指定时默认'auto'，仅pipeline后端有效。
        server_url: backend为http-client时需指定服务器地址，如：http://127.0.0.1:30000
        start_page_id: 解析起始页码，默认0。
        end_page_id: 解析结束页码，默认None（解析到文档结尾）。
    """
    try:
        file_name_list = []
        pdf_bytes_list = []
        lang_list = []
        for path in path_list:
            file_name = str(Path(path).stem)
            pdf_bytes = read_fn(path)
            file_name_list.append(file_name)
            pdf_bytes_list.append(pdf_bytes)
            lang_list.append(lang)
        do_parse(
            output_dir=output_dir,
            pdf_file_names=file_name_list,
            pdf_bytes_list=pdf_bytes_list,
            p_lang_list=lang_list,
            backend=backend,
            parse_method=method,
            server_url=server_url,
            start_page_id=start_page_id,
            end_page_id=end_page_id
        )
    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    # 主程序入口，批量解析pdfs目录下所有PDF和图片文件
    __dir__ = os.path.dirname(os.path.abspath(__file__))  # 当前文件所在目录
    pdf_files_dir = os.path.join(__dir__, "pdfs")  # PDF文件目录
    output_dir = os.path.join(__dir__, "output")  # 输出目录
    pdf_suffixes = ["pdf"]  # 支持的PDF后缀
    image_suffixes = ["png", "jpeg", "jp2", "webp", "gif", "bmp", "jpg"]  # 支持的图片后缀

    doc_path_list = []  # 待处理文档路径列表
    for doc_path in Path(pdf_files_dir).glob('*'):
        # 判断文件后缀是否为支持的PDF或图片
        if guess_suffix_by_path(doc_path) in pdf_suffixes + image_suffixes:
            doc_path_list.append(doc_path)

    """配置模型下载源和缓存目录"""
    os.environ['MINERU_MODEL_SOURCE'] = "local"

    """如环境不支持VLM，建议使用pipeline模式"""
    parse_doc(doc_path_list, output_dir, backend="pipeline")

    """如需启用VLM模式，将backend改为'vlm-xxx'"""
    # parse_doc(doc_path_list, output_dir, backend="vlm-transformers")  # 通用
    # parse_doc(doc_path_list, output_dir, backend="vlm-vllm-engine")  # 更快(engine)
    # parse_doc(doc_path_list, output_dir, backend="vlm-http-client", server_url="http://127.0.0.1:30000")  # 更快(client)