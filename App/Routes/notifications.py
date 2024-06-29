from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from App import schemas, models, database  
from datetime import datetime

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)


@router.get("/", response_model=List[schemas.NotificationInDB])
def get_notifications(db: Session = Depends(database.get_db)):
    notifications = db.query(models.Notification).all()
    return notifications

@router.put("/{notification_id}", response_model=schemas.NotificationInDB)
def update_notification(notification_id: int, notification: schemas.NotificationUpdate, db: Session = Depends(database.get_db)):
    db_notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not db_notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    for field, value in notification.dict(exclude_unset=True).items():
        setattr(db_notification, field, value)
    
    db.commit()
    db.refresh(db_notification)
    return db_notification
