from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud import item as item_crud
from app.models.item import PriorityLevel, TaskStatus
from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate, ItemStats

router = APIRouter()


@router.get("", response_model=List[ItemResponse])
def read_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[TaskStatus] = None,
    priority: Optional[PriorityLevel] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Retrieve list of tasks with pagination and optional status/priority filtering."""
    return item_crud.get_items(
        db=db, skip=skip, limit=limit, status=status, priority=priority, search=search
    )


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item_in: ItemCreate,
    db: Session = Depends(get_db),
):
    """Create a new task item."""
    return item_crud.create_item(db=db, item=item_in)


@router.get("/stats", response_model=ItemStats)
def read_item_stats(db: Session = Depends(get_db)):
    """Retrieve item statistics and status counts."""
    return item_crud.get_stats(db=db)


@router.get("/{item_id}", response_model=ItemResponse)
def read_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve a specific task item by ID."""
    db_item = item_crud.get_item(db=db, item_id=item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task item with ID {item_id} not found",
        )
    return db_item


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    item_in: ItemUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing task item."""
    db_item = item_crud.get_item(db=db, item_id=item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task item with ID {item_id} not found",
        )
    return item_crud.update_item(db=db, db_item=db_item, item_update=item_in)


@router.delete("/{item_id}", response_model=ItemResponse)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    """Delete a task item."""
    db_item = item_crud.get_item(db=db, item_id=item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task item with ID {item_id} not found",
        )
    return item_crud.delete_item(db=db, db_item=db_item)
