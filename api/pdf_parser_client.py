"""
PDF解析客户端

统一的PDF解析接口，自动判断使用本地或远程服务

使用方法如下：
from api.pdf_parser_client import get_pdf_parser_client

# 1. 获取客户端
client = get_pdf_parser_client()

# 2. 解析 PDF（返回简化结果）
result = client.parse_pdf("test.pdf")
# 返回: {"task_id": "xxx", "file_name": "test", "auto_dir_url": "/files/xxx/test/auto"}

# 3. 按需获取数据
# 3.1 获取 Markdown
markdown = client.get_markdown(result)

# 3.2 获取内容列表
content_list = client.get_content_list(result)

# 3.3 下载特定文件
client.download_file(f"{result['auto_dir_url']}/images/xxx.jpg", "output.jpg")
"""

import requests
from typing import Optional, Dict, Any
from pathlib import Path
from config import PDFParserConfig


class PDFParserClient:
    """PDF解析客户端 - 统一调用接口"""
    
    def __init__(self):
        self.base_url = PDFParserConfig.URL
        self.timeout = 300  # 5分钟超时
    
    def parse_pdf(
        self,
        pdf_path: str,
        lang: str = "ch",
        backend: str = "pipeline",
        parse_method: str = "auto",
        formula_enable: bool = False,
        table_enable: bool = False,
        start_page: int = 0,
        end_page: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        解析PDF文件
        
        Args:
            pdf_path: PDF文件路径
            lang: 语言代码，默认'ch'
            backend: 解析后端，默认'pipeline'
            parse_method: 解析方法，默认'auto'
            formula_enable: 是否启用公式解析
            table_enable: 是否启用表格解析
            start_page: 起始页码
            end_page: 结束页码
        
        Returns:
            Dict[str, Any]: 解析结果，包含：
                - task_id: 任务ID
                - file_name: 文件名（不含扩展名）
                - auto_dir_url: auto目录的URL路径
                
            使用示例：
                result = client.parse_pdf("test.pdf")
                
                # 访问 Markdown
                md_url = f"{base_url}{result['auto_dir_url']}/{result['file_name']}.md"
                
                # 访问图片
                img_url = f"{base_url}{result['auto_dir_url']}/images/xxx.jpg"
                
                # 访问 content_list.json
                json_url = f"{base_url}{result['auto_dir_url']}/{result['file_name']}_content_list.json"
        
        Raises:
            FileNotFoundError: PDF文件不存在
            requests.exceptions.RequestException: 服务请求失败
        """
        # 检查文件是否存在
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        # 调用API
        try:
            with open(pdf_file, 'rb') as f:
                files = {'file': (pdf_file.name, f, 'application/pdf')}
                data = {
                    'lang': lang,
                    'backend': backend,
                    'parse_method': parse_method,
                    'formula_enable': formula_enable,
                    'table_enable': table_enable,
                    'start_page': start_page
                }
                
                # end_page为None时不传递
                if end_page is not None:
                    data['end_page'] = end_page
                
                response = requests.post(
                    f"{self.base_url}/api/pdf/parse",
                    files=files,
                    data=data,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                result = response.json()
                
                if not result.get('success'):
                    raise RuntimeError(f"解析失败: {result.get('message', '未知错误')}")
                
                return result['data']
        
        except requests.exceptions.Timeout:
            raise TimeoutError(f"PDF解析超时（{self.timeout}秒）")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"无法连接到PDF解析服务: {self.base_url}\n"
                f"请检查:\n"
                f"1. 服务是否启动\n"
                f"2. 地址是否正确\n"
                f"3. 网络是否正常"
            )
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"PDF解析服务返回错误: {e.response.status_code} - {e.response.text}")
    
    def download_file(self, file_url: str, save_path: str) -> bool:
        """
        从微服务下载文件（通用方法）
        
        Args:
            file_url: 文件URL（相对或绝对路径）
            save_path: 保存路径
        
        Returns:
            bool: 是否下载成功
            
        使用示例：
            result = client.parse_pdf("test.pdf")
            
            # 下载 Markdown
            md_url = f"{result['auto_dir_url']}/{result['file_name']}.md"
            client.download_file(md_url, "output/test.md")
            
            # 下载图片
            img_url = f"{result['auto_dir_url']}/images/xxx.jpg"
            client.download_file(img_url, "output/images/xxx.jpg")
        """
        try:
            # 如果是相对路径，拼接base_url
            if not file_url.startswith('http'):
                file_url = f"{self.base_url}{file_url}"
            
            response = requests.get(file_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # 确保目录存在
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 保存文件
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        
        except Exception as e:
            print(f"⚠️  下载文件失败 ({file_url}): {str(e)}")
            return False
    
    def get_content_list(self, parse_result: dict) -> list:
        """
        获取解析结果的内容列表（从 content_list.json）
        
        Args:
            parse_result: parse_pdf 返回的结果
        
        Returns:
            list: 内容列表，包含文本和图片信息
            
        使用示例：
            result = client.parse_pdf("test.pdf")
            content_list = client.get_content_list(result)
            
            for item in content_list:
                if item['type'] == 'image':
                    print(f"图片: {item['img_path']}")
        """
        try:
            json_url = f"{parse_result['auto_dir_url']}/{parse_result['file_name']}_content_list.json"
            
            # 如果是相对路径，拼接base_url
            if not json_url.startswith('http'):
                json_url = f"{self.base_url}{json_url}"
            
            response = requests.get(json_url, timeout=30)
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            print(f"⚠️  获取内容列表失败: {str(e)}")
            return []
    
    def get_markdown(self, parse_result: dict) -> Optional[str]:
        """
        获取解析结果的 Markdown 内容
        
        Args:
            parse_result: parse_pdf 返回的结果
        
        Returns:
            str: Markdown 内容，失败返回 None
            
        使用示例：
            result = client.parse_pdf("test.pdf")
            markdown = client.get_markdown(result)
            if markdown:
                print(markdown)
        """
        try:
            md_url = f"{parse_result['auto_dir_url']}/{parse_result['file_name']}.md"
            
            # 如果是相对路径，拼接base_url
            if not md_url.startswith('http'):
                md_url = f"{self.base_url}{md_url}"
            
            response = requests.get(md_url, timeout=30)
            response.raise_for_status()
            
            return response.text
        
        except Exception as e:
            print(f"⚠️  获取Markdown失败: {str(e)}")
            return None
    
    def health_check(self) -> bool:
        """
        检查服务健康状态
        
        Returns:
            bool: 服务是否正常
        """
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False


# 单例客户端
_client = None


def get_pdf_parser_client() -> PDFParserClient:
    """
    获取PDF解析客户端单例
    
    Returns:
        PDFParserClient: 客户端实例
    """
    global _client
    if _client is None:
        _client = PDFParserClient()
    return _client
