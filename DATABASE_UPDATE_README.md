# 数据库结构更新说明

## ⚠️ 重要提示

**这个更新脚本仅用于已有旧数据库的项目！**

### 适用场景
- ✅ **旧项目**：如果你已经有一个运行中的数据库（`wrong_question.db`存在），需要运行此脚本
- ❌ **新项目**：如果是首次运行或全新项目，**不需要运行此脚本**，系统会自动创建正确的表结构

### 如何判断
- 如果项目根目录存在 `wrong_question.db` 文件，且之前添加过学生数据 → **需要运行脚本**
- 如果是刚克隆的项目或首次运行 → **不需要运行脚本**

---

## 问题
之前的学生表中，学号在全局范围内唯一，导致不同班级无法使用相同学号。

## 解决方案
已更新数据模型和API，使学号在班级内唯一，不同班级可以使用相同学号。

## 更新步骤

### 1. 运行数据库更新脚本
```bash
python update_student_table.py
```

这个脚本会：
- ✅ 备份现有学生数据
- ✅ 重建students表，添加 `UNIQUE(class_name, student_no)` 约束
- ✅ 迁移所有数据（自动去重）
- ✅ 创建必要的索引

### 2. 验证更新
运行后，你应该看到类似这样的输出：
```
🎉 数据库更新成功！
📊 最终统计: X 条学生记录
✅ 现在学号在班级内唯一，不同班级可以使用相同学号
```

### 3. 测试功能
- 尝试在同一班级添加相同学号 → 应该失败并提示错误
- 尝试在不同班级添加相同学号 → 应该成功

### 4. 清理
更新成功后，可以删除 `update_student_table.py`（保留此README作为记录）

## 新项目说明

**如果你是新项目或首次运行，请忽略上述步骤！**

新项目会自动使用正确的表结构：
1. 直接运行 `python start.py`
2. 系统会自动创建包含正确约束的数据库表
3. 学号已经是班级内唯一，无需任何额外操作

## 技术细节

### 数据模型变化
```python
# 之前
student_no = Column(String, nullable=False, unique=True)  # 全局唯一

# 现在  
student_no = Column(String, nullable=False, index=True)  # 班级内唯一
__table_args__ = (
    UniqueConstraint('class_name', 'student_no', name='uq_class_student_no'),
)
```

### API验证逻辑
```python
# 创建学生时检查班级内是否重复
existing_student = db.query(Student).filter(
    Student.class_name == student.class_name,
    Student.student_no == student.student_no
).first()
```

## 注意事项
- ⚠️ 更新前会自动备份数据
- ⚠️ 如果存在重复的班级+学号组合，脚本会保留第一条记录并跳过后续重复
- ⚠️ 更新过程中请勿中断程序
- ⚠️ 建议在更新前手动备份 `wrong_question.db` 文件
