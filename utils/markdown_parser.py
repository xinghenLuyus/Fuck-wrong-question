"""
Markdown 分题解析工具

解析规则：
1. 以题号加.切分，例如"1."、"11."、"1.题目"（后面可以没有空格）
2. 题号前必须是行首、空格、制表符或换行
3. 题号可以重复，按顺序自动编号
4. 题号会保留在题目文字中
5. 忽略所有#后面的内容（标题）
6. 提取图片链接
"""

import re
from typing import List, Dict, Any


def split_markdown_to_questions(markdown_content: str, base_url: str = "") -> List[Dict[str, Any]]:
    """
    将 Markdown 内容分割为题目列表
    
    Args:
        markdown_content: Markdown 文本内容
        base_url: 图片基础URL（用于拼接相对路径）
    
    Returns:
        List[Dict]: 题目列表，每个题目包含：
            - question_no: 题号（自动从1开始编号）
            - question_text: 题目文字（包含题号标记，不含图片）
            - image_urls: 图片URL列表
    """
    # 按行分割
    lines = markdown_content.split('\n')
    
    questions = []
    current_question_no = 0  # 自动编号，从0开始，第一题时会变成1
    current_text = []
    current_images = []
    in_question = False
    
    # 题号匹配模式：行首或前面有空白字符的数字后跟一个点（点后可以有空格也可以没有）
    # 支持: "1." "11." "1. " "11. " " 1." "  11." "\t1." "1.题目" 等
    question_pattern = re.compile(r'^[\s\t]*(\d+)\.')
    
    # 图片匹配模式：![](url)
    image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')
    
    for line in lines:
        # 跳过标题行
        if line.strip().startswith('#'):
            continue
        
        # 检查是否是新题目的开始
        match = question_pattern.match(line)
        
        if match:
            # 保存上一题
            if in_question:
                questions.append({
                    'question_no': current_question_no,
                    'question_text': '\n'.join(current_text).strip(),
                    'image_urls': current_images
                })
            
            # 开始新题，自动编号
            current_question_no += 1
            current_text = []
            current_images = []
            in_question = True
            
            # 保留完整的题号和内容，只去除前导空白
            remaining_text = line.lstrip()
            
            # 提取图片
            for img_match in image_pattern.finditer(remaining_text):
                img_url = img_match.group(1)
                # 拼接完整URL
                if img_url and not img_url.startswith('http'):
                    img_url = f"{base_url}/{img_url}" if base_url else img_url
                current_images.append(img_url)
            
            # 移除图片标记，保留纯文字（包括题号）
            remaining_text = image_pattern.sub('', remaining_text).strip()
            if remaining_text:
                current_text.append(remaining_text)
        
        elif in_question:
            # 当前行属于当前题目
            # 提取图片
            for img_match in image_pattern.finditer(line):
                img_url = img_match.group(1)
                # 拼接完整URL
                if img_url and not img_url.startswith('http'):
                    img_url = f"{base_url}/{img_url}" if base_url else img_url
                current_images.append(img_url)
            
            # 移除图片标记，保留纯文字
            text_only = image_pattern.sub('', line).strip()
            if text_only:
                current_text.append(text_only)
    
    # 保存最后一题
    if in_question:
        questions.append({
            'question_no': current_question_no,
            'question_text': '\n'.join(current_text).strip(),
            'image_urls': current_images
        })
    
    return questions


def validate_questions(questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    验证题目列表
    
    Returns:
        Dict: 验证结果
            - valid: bool
            - message: str
            - issues: List[str]
    """
    issues = []
    
    if not questions:
        return {
            'valid': False,
            'message': '未找到任何题目',
            'issues': ['Markdown中没有符合格式的题目（题号格式：1. 2. 3. ...）']
        }
    
    # 检查空题目
    for q in questions:
        if not q['question_text'] and not q['image_urls']:
            issues.append(f"第{q['question_no']}题为空（无文字也无图片）")
    
    return {
        'valid': len(issues) == 0,
        'message': '验证通过' if len(issues) == 0 else '存在问题',
        'issues': issues
    }


if __name__ == "__main__":
    # 测试代码 - 使用实际的题目格式
    test_markdown = """
# 三上数学测试

5.在实践课上，小佳折了7只千纸鹤，小宁比小佳少折了 2只，小思折的是小宁的3倍。下面的线段图中，正确的是( )。
6.小文和小轩看同一本故事书，小文 3天看完，第一天看了12 页，后两天一共看了18页。小轩平均每天看6页，几天能看完? 列式正确的是( ) 。
A.(12+18+18)÷6 B.(12+18)÷3
C.(12+18+18)÷3 D.(12+18)÷6
7.算式"(60-40)÷5"能解决下面哪个问题?( )
A.一箱苹果有60个，5人平分40个，平均每人分多少个?
B. 一箱苹果有60个，5 人分得40个，还剩多少个?
C. 一 箱苹果有60个，已经吃了40个，剩下的平均分给5个人，每人分得多少个?
1.口算（每题12分）
6×7= 35÷5= 86—52= 72÷8+3=
9×5= 24÷6= 80-73= 56÷8-3=
9+9÷9= 18-8÷2= 6×(24÷3)= 16÷(8÷8)=
2.递等式计算（每题3分）
41+9×5 (275-248)÷3 21÷3+9×4 221-43-57
"""
    
    questions = split_markdown_to_questions(test_markdown, "http://localhost:8001/files/task123/test/auto")
    
    print(f"解析出 {len(questions)} 道题目：\n")
    for q in questions:
        print(f"【第 {q['question_no']} 题】")
        # 显示前100个字符
        text_preview = q['question_text'][:100] if q['question_text'] else '(无文字)'
        if len(q['question_text']) > 100:
            text_preview += '...'
        print(f"内容: {text_preview}")
        print(f"图片数: {len(q['image_urls'])}")
        if q['image_urls']:
            for img in q['image_urls']:
                print(f"  - {img}")
        print("-" * 70)
    
    result = validate_questions(questions)
    print(f"\n验证结果: {result['message']}")
    if result['issues']:
        print("问题列表:")
        for issue in result['issues']:
            print(f"  - {issue}")
