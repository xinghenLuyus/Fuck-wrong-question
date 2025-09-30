#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 验证错题管理系统功能
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    """测试API功能"""
    print("🧪 开始测试错题管理系统...")
    
    # 1. 测试分类API
    print("\n📁 测试分类功能...")
    try:
        # 创建分类
        category_data = {"name": "测试分类"}
        response = requests.post(f"{BASE_URL}/api/categories/", json=category_data)
        if response.status_code == 200:
            print("✅ 分类创建成功")
            category = response.json()
            category_id = category["id"]
        else:
            print("❌ 分类创建失败")
            return False
            
        # 获取分类列表
        response = requests.get(f"{BASE_URL}/api/categories/")
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ 获取分类列表成功，共 {len(categories)} 个分类")
        else:
            print("❌ 获取分类列表失败")
            
    except Exception as e:
        print(f"❌ 分类测试失败: {e}")
        return False
    
    # 2. 测试试卷API
    print("\n📄 测试试卷功能...")
    try:
        # 创建试卷
        paper_data = {"name": "测试试卷", "category_id": category_id}
        response = requests.post(f"{BASE_URL}/api/papers/", json=paper_data)
        if response.status_code == 200:
            print("✅ 试卷创建成功")
            paper = response.json()
            paper_id = paper["id"]
        else:
            print("❌ 试卷创建失败")
            return False
            
        # 获取试卷列表
        response = requests.get(f"{BASE_URL}/api/papers/")
        if response.status_code == 200:
            papers = response.json()
            print(f"✅ 获取试卷列表成功，共 {len(papers)} 个试卷")
        else:
            print("❌ 获取试卷列表失败")
            
    except Exception as e:
        print(f"❌ 试卷测试失败: {e}")
        return False
    
    # 3. 测试学生API
    print("\n👥 测试学生功能...")
    try:
        # 创建学生
        student_data = {"class_name": "测试班级", "student_no": "001", "name": "测试学生"}
        response = requests.post(f"{BASE_URL}/api/students/", json=student_data)
        if response.status_code == 200:
            print("✅ 学生创建成功")
            student = response.json()
            student_id = student["id"]
        else:
            print("❌ 学生创建失败")
            return False
            
        # 获取学生列表
        response = requests.get(f"{BASE_URL}/api/students/")
        if response.status_code == 200:
            students = response.json()
            print(f"✅ 获取学生列表成功，共 {len(students)} 个学生")
        else:
            print("❌ 获取学生列表失败")
            
    except Exception as e:
        print(f"❌ 学生测试失败: {e}")
        return False
    
    # 4. 测试题目API
    print("\n📝 测试题目功能...")
    try:
        # 创建题目
        question_data = {
            "paper_id": paper_id,
            "question_text": "这是一道测试题目",
            "image_urls": "",
            "wrong_students": str(student_id)
        }
        response = requests.post(f"{BASE_URL}/api/questions/", json=question_data)
        if response.status_code == 200:
            print("✅ 题目创建成功")
            question = response.json()
            question_id = question["id"]
        else:
            print("❌ 题目创建失败")
            return False
            
        # 获取题目列表
        response = requests.get(f"{BASE_URL}/api/questions/paper/{paper_id}")
        if response.status_code == 200:
            questions = response.json()
            print(f"✅ 获取题目列表成功，共 {len(questions)} 道题目")
        else:
            print("❌ 获取题目列表失败")
            
    except Exception as e:
        print(f"❌ 题目测试失败: {e}")
        return False
    
    print("\n🎉 所有测试通过！系统功能正常。")
    return True

def test_pages():
    """测试页面访问"""
    print("\n🌐 测试页面访问...")
    
    pages = [
        ("/", "首页"),
        ("/students", "学生管理"),
        (f"/add_question/1", "添加题目"),
        (f"/preview/1", "试卷预览"),
    ]
    
    for path, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{path}")
            if response.status_code == 200:
                print(f"✅ {name} 页面访问成功")
            else:
                print(f"❌ {name} 页面访问失败 (状态码: {response.status_code})")
        except Exception as e:
            print(f"❌ {name} 页面访问失败: {e}")

if __name__ == "__main__":
    print("请确保服务器正在运行 (python main.py)")
    print("如果服务器未启动，请先运行: python main.py")
    
    try:
        # 测试服务器是否运行
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ 服务器正在运行")
            test_api()
            test_pages()
        else:
            print("❌ 服务器未正常响应")
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("请先启动服务器: python main.py")