from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.models import get_db, Category
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/categories", tags=["分类管理"])

class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class CategoryTreeResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    children: List['CategoryTreeResponse'] = []
    
    class Config:
        from_attributes = True

@router.post("/", response_model=CategoryResponse)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """创建新分类"""
    # 检查父分类是否存在
    if category.parent_id:
        parent = db.query(Category).filter(Category.id == category.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="父分类不存在")
    
    db_category = Category(
        name=category.name,
        parent_id=category.parent_id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """获取所有分类列表（平铺）"""
    categories = db.query(Category).order_by(Category.id).all()
    return categories

@router.get("/tree", response_model=List[CategoryTreeResponse])
async def get_categories_tree(db: Session = Depends(get_db)):
    """获取分类树形结构"""
    def build_tree(categories, parent_id=None):
        result = []
        for category in categories:
            if category.parent_id == parent_id:
                children = build_tree(categories, category.id)
                category_dict = {
                    "id": category.id,
                    "name": category.name,
                    "parent_id": category.parent_id,
                    "children": children
                }
                result.append(category_dict)
        return result
    
    categories = db.query(Category).all()
    return build_tree(categories)

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """获取指定分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, category_update: CategoryUpdate, db: Session = Depends(get_db)):
    """更新分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 检查父分类是否存在（如果要更新父分类）
    if category_update.parent_id is not None and category_update.parent_id != category.parent_id:
        if category_update.parent_id:
            parent = db.query(Category).filter(Category.id == category_update.parent_id).first()
            if not parent:
                raise HTTPException(status_code=404, detail="父分类不存在")
        
        # 检查是否会造成循环引用
        def check_circular_reference(cat_id, parent_id):
            if cat_id == parent_id:
                return True
            parent = db.query(Category).filter(Category.id == parent_id).first()
            if parent and parent.parent_id:
                return check_circular_reference(cat_id, parent.parent_id)
            return False
        
        if category_update.parent_id and check_circular_reference(category_id, category_update.parent_id):
            raise HTTPException(status_code=400, detail="不能将分类移动到其子分类下")
    
    if category_update.name is not None:
        category.name = category_update.name
    if category_update.parent_id is not None:
        category.parent_id = category_update.parent_id
    
    db.commit()
    db.refresh(category)
    return category

@router.delete("/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    """删除分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 检查是否有子分类
    children = db.query(Category).filter(Category.parent_id == category_id).count()
    if children > 0:
        raise HTTPException(status_code=400, detail="请先删除子分类")
    
    # 检查是否有试卷
    from database.models import Paper
    papers_count = db.query(Paper).filter(Paper.category_id == category_id).count()
    if papers_count > 0:
        raise HTTPException(status_code=400, detail="该分类下还有试卷，无法删除")
    
    db.delete(category)
    db.commit()
    
    return {"message": "分类删除成功"}