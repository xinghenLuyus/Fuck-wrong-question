#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
更新学生表结构 - 添加班级+学号的复合唯一约束
使用说明：运行此脚本后，学号在班级内将保持唯一，不同班级可以有相同学号
"""

import sqlite3
import os

DATABASE_PATH = "wrong_question.db"

def update_student_table():
    """更新学生表，添加复合唯一约束"""
    
    if not os.path.exists(DATABASE_PATH):
        print(f"❌ 数据库文件不存在: {DATABASE_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        print("🔍 检查当前students表结构...")
        
        # 获取当前表结构
        cursor.execute("PRAGMA table_info(students)")
        columns = cursor.fetchall()
        print(f"当前列: {[col[1] for col in columns]}")
        
        # 获取当前索引
        cursor.execute("PRAGMA index_list(students)")
        indexes = cursor.fetchall()
        print(f"当前索引: {indexes}")
        
        # 检查是否已经有复合唯一约束
        has_composite_unique = False
        for idx in indexes:
            cursor.execute(f"PRAGMA index_info({idx[1]})")
            idx_info = cursor.fetchall()
            if len(idx_info) >= 2:  # 如果索引包含多个列
                cols = [info[2] for info in idx_info]
                if 'class_name' in cols and 'student_no' in cols:
                    has_composite_unique = True
                    print(f"✅ 已存在复合唯一约束: {idx[1]}")
                    break
        
        if has_composite_unique:
            print("✅ 数据库结构已是最新，无需更新")
            conn.close()
            return True
        
        print("\n🔄 开始更新数据库结构...")
        
        # 备份当前数据
        cursor.execute("SELECT id, class_name, student_no, name FROM students")
        students_data = cursor.fetchall()
        print(f"📦 备份了 {len(students_data)} 条学生记录")
        
        # SQLite不支持直接修改约束，需要重建表
        # 1. 创建新表
        cursor.execute("""
            CREATE TABLE students_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name VARCHAR NOT NULL,
                student_no VARCHAR NOT NULL,
                name VARCHAR NOT NULL,
                UNIQUE(class_name, student_no)
            )
        """)
        print("✅ 创建新表结构")
        
        # 2. 复制数据到新表（去重：班级+学号组合唯一）
        inserted_count = 0
        skipped_count = 0
        seen_combinations = set()
        
        for student in students_data:
            student_id, class_name, student_no, name = student
            combination = (class_name, student_no)
            
            if combination not in seen_combinations:
                cursor.execute("""
                    INSERT INTO students_new (id, class_name, student_no, name)
                    VALUES (?, ?, ?, ?)
                """, student)
                seen_combinations.add(combination)
                inserted_count += 1
            else:
                print(f"⚠️  跳过重复记录: {name} ({class_name}-{student_no})")
                skipped_count += 1
        
        print(f"✅ 迁移了 {inserted_count} 条记录")
        if skipped_count > 0:
            print(f"⚠️  跳过了 {skipped_count} 条重复记录")
        
        # 3. 删除旧表
        cursor.execute("DROP TABLE students")
        print("✅ 删除旧表")
        
        # 4. 重命名新表
        cursor.execute("ALTER TABLE students_new RENAME TO students")
        print("✅ 重命名新表")
        
        # 5. 创建索引
        cursor.execute("CREATE INDEX idx_students_class_name ON students(class_name)")
        cursor.execute("CREATE INDEX idx_students_student_no ON students(student_no)")
        print("✅ 创建索引")
        
        # 提交更改
        conn.commit()
        print("\n🎉 数据库更新成功！")
        print(f"📊 最终统计: {inserted_count} 条学生记录")
        print("✅ 现在学号在班级内唯一，不同班级可以使用相同学号")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("学生表结构更新工具")
    print("=" * 60)
    print()
    
    success = update_student_table()
    
    if success:
        print("\n✅ 所有操作完成！可以安全删除此脚本。")
    else:
        print("\n❌ 操作失败，请检查错误信息。")
