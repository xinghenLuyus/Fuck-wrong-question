"""
上传文件迁移脚本
功能：将旧版本的 uploads 文件夹结构迁移到新版本
- 旧版本：所有图片都在 static/uploads/ 根目录
- 新版本：每个试卷的图片在 static/uploads/paper_{paper_id}/ 目录

使用方法：
python migrate_uploads.py
"""

import os
import shutil
from sqlalchemy.orm import Session
from database.models import SessionLocal, Paper, Question
from config import UPLOAD_DIR


def migrate_uploads():
    """迁移上传文件到新的目录结构"""
    print("="*60)
    print("开始迁移上传文件...")
    print("="*60)
    
    db: Session = SessionLocal()
    
    try:
        # 获取所有试卷
        papers = db.query(Paper).all()
        total_papers = len(papers)
        
        print(f"\n找到 {total_papers} 张试卷")
        
        migrated_count = 0
        failed_count = 0
        skipped_count = 0
        
        for idx, paper in enumerate(papers, 1):
            print(f"\n[{idx}/{total_papers}] 处理试卷: {paper.name} (ID: {paper.id})")
            
            # 获取该试卷的所有题目
            questions = db.query(Question).filter(Question.paper_id == paper.id).all()
            
            if not questions:
                print(f"  └─ 该试卷没有题目，跳过")
                skipped_count += 1
                continue
            
            # 创建试卷专属文件夹
            paper_folder = os.path.join(UPLOAD_DIR, f"paper_{paper.id}")
            os.makedirs(paper_folder, exist_ok=True)
            print(f"  ├─ 创建文件夹: {paper_folder}")
            
            # 遍历题目，迁移图片
            moved_files = []
            for question in questions:
                if not question.image_urls:
                    continue
                
                urls = question.image_urls.split(',')
                new_urls = []
                
                for url in urls:
                    url = url.strip()
                    if not url:
                        continue
                    
                    # 只处理旧版本的URL格式（/static/uploads/filename）
                    if url.startswith('/static/uploads/') and 'paper_' not in url:
                        # 提取文件名
                        filename = url.split('/')[-1]
                        old_path = os.path.join(UPLOAD_DIR, filename)
                        new_path = os.path.join(paper_folder, filename)
                        new_url = f"/static/uploads/paper_{paper.id}/{filename}"
                        
                        # 检查源文件是否存在
                        if os.path.exists(old_path):
                            try:
                                # 如果目标文件已存在，跳过
                                if os.path.exists(new_path):
                                    print(f"  │  ├─ 文件已存在，跳过: {filename}")
                                    new_urls.append(new_url)
                                else:
                                    # 移动文件
                                    shutil.move(old_path, new_path)
                                    moved_files.append(filename)
                                    new_urls.append(new_url)
                                    print(f"  │  ├─ 移动文件: {filename}")
                            except Exception as e:
                                print(f"  │  ├─ ❌ 移动文件失败 {filename}: {e}")
                                new_urls.append(url)  # 保留原URL
                                failed_count += 1
                        else:
                            print(f"  │  ├─ ⚠️ 源文件不存在: {old_path}")
                            new_urls.append(url)  # 保留原URL
                    else:
                        # 已经是新版本格式或其他URL，保持不变
                        new_urls.append(url)
                
                # 更新数据库中的URL
                if new_urls != urls:
                    question.image_urls = ','.join(new_urls)
            
            if moved_files:
                print(f"  └─ ✅ 成功迁移 {len(moved_files)} 个文件")
                migrated_count += 1
            else:
                print(f"  └─ 无需迁移或文件已迁移")
                skipped_count += 1
        
        # 提交数据库更改
        db.commit()
        
        print("\n" + "="*60)
        print("迁移完成！")
        print("="*60)
        print(f"总试卷数: {total_papers}")
        print(f"已迁移: {migrated_count}")
        print(f"跳过: {skipped_count}")
        print(f"失败: {failed_count}")
        print("="*60)
        
        # 检查是否有遗留文件
        print("\n检查遗留文件...")
        remaining_files = []
        if os.path.exists(UPLOAD_DIR):
            for item in os.listdir(UPLOAD_DIR):
                item_path = os.path.join(UPLOAD_DIR, item)
                # 跳过文件夹
                if os.path.isdir(item_path):
                    continue
                # 跳过非图片文件
                if not any(item.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']):
                    continue
                remaining_files.append(item)
        
        if remaining_files:
            print(f"\n⚠️ 发现 {len(remaining_files)} 个未迁移的文件:")
            for f in remaining_files[:10]:  # 只显示前10个
                print(f"  - {f}")
            if len(remaining_files) > 10:
                print(f"  ... 还有 {len(remaining_files) - 10} 个文件")
            print("\n这些文件可能是:")
            print("  1. 数据库中未引用的孤立文件")
            print("  2. 导出的临时文件")
            print("  3. 其他系统文件")
            print("\n建议手动检查后决定是否删除")
        else:
            print("✅ 没有遗留文件")
        
    except Exception as e:
        print(f"\n❌ 迁移过程出错: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


def create_backup():
    """创建备份"""
    print("\n是否需要备份当前 uploads 文件夹？(y/n) [y]: ", end='')
    choice = input().strip().lower()
    
    if choice != 'n':
        backup_dir = f"{UPLOAD_DIR}_backup"
        if os.path.exists(UPLOAD_DIR):
            try:
                if os.path.exists(backup_dir):
                    print(f"备份目录已存在: {backup_dir}")
                    print("是否覆盖？(y/n) [n]: ", end='')
                    if input().strip().lower() != 'y':
                        print("跳过备份")
                        return
                    shutil.rmtree(backup_dir)
                
                shutil.copytree(UPLOAD_DIR, backup_dir)
                print(f"✅ 已创建备份: {backup_dir}")
                return True
            except Exception as e:
                print(f"❌ 备份失败: {e}")
                print("是否继续迁移？(y/n) [n]: ", end='')
                if input().strip().lower() != 'y':
                    return False
    
    return True


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║        上传文件迁移脚本 v1.0                          ║
    ╠════════════════════════════════════════════════════════╣
    ║  本脚本将旧版本的上传文件迁移到新的目录结构           ║
    ║                                                        ║
    ║  旧版本: static/uploads/xxx.jpg                       ║
    ║  新版本: static/uploads/paper_{id}/xxx.jpg            ║
    ║                                                        ║
    ║  注意事项:                                            ║
    ║  1. 会自动更新数据库中的图片URL                       ║
    ║  2. 建议先备份数据库和uploads文件夹                   ║
    ║  3. 迁移过程中不会删除原文件，只是移动               ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    print("按回车键开始迁移...")
    input()
    
    # 创建备份
    if not create_backup():
        print("迁移已取消")
        exit(0)
    
    # 执行迁移
    migrate_uploads()
    
    print("\n迁移脚本执行完毕！")
