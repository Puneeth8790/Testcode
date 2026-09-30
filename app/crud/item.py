from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.item import Item, TaskStatus, PriorityLevel
from app.schemas.item import ItemCreate, ItemUpdate, ItemStats


def get_item(db: Session, item_id: int) -> Optional[Item]:
    """Retrieve a single item by ID."""
    return db.query(Item).filter(Item.id == item_id).first()


def get_items(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[TaskStatus] = None,
    priority: Optional[PriorityLevel] = None,
    search: Optional[str] = None,
) -> List[Item]:
    """Retrieve multiple items with optional filtering and search."""
    query = db.query(Item)
    
    if status:
        query = query.filter(Item.status == status)
    if priority:
        query = query.filter(Item.priority == priority)
    if search:
        query = query.filter(
            (Item.title.ilike(f"%{search}%")) | (Item.description.ilike(f"%{search}%"))
        )
        
    return query.order_by(Item.created_at.desc()).offset(skip).limit(limit).all()


def create_item(db: Session, item: ItemCreate) -> Item:
    """Create a new item in the database."""
    db_item = Item(
        title=item.title,
        description=item.description,
        priority=item.priority,
        status=item.status,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(db: Session, db_item: Item, item_update: ItemUpdate) -> Item:
    """Update existing item attributes."""
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, db_item: Item) -> Item:
    """Delete an item from the database."""
    db.delete(db_item)
    db.commit()
    return db_item


def get_stats(db: Session) -> ItemStats:
    """Calculate summary statistics for items."""
    total = db.query(func.count(Item.id)).scalar() or 0
    pending = db.query(func.count(Item.id)).filter(Item.status == TaskStatus.PENDING).scalar() or 0
    in_progress = db.query(func.count(Item.id)).filter(Item.status == TaskStatus.IN_PROGRESS).scalar() or 0
    completed = db.query(func.count(Item.id)).filter(Item.status == TaskStatus.COMPLETED).scalar() or 0
    high_priority = db.query(func.count(Item.id)).filter(Item.priority == PriorityLevel.HIGH).scalar() or 0

    return ItemStats(
        total=total,
        pending=pending,
        in_progress=in_progress,
        completed=completed,
        high_priority=high_priority,
    )
