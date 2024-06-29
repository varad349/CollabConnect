from fastapi import FastAPI,APIRouter,HTTPException, status,Depends
from sqlalchemy.orm import Session
from App import schemas, models, database
from datetime import datetime
from typing import List, Dict

router=APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)
@router.post("/api/v1/projects/{project_id}/tasks/", response_model=schemas.TaskResponse)
def create_task(project_id: int, task:schemas.TaskResponse , db: Session = Depends(database.get_db)):
    db_task = models.Task(**task.dict(), project_id=project_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.put("/api/v1/tasks/{task_id}/", response_model=schemas.TaskResponse)
def update_task(task_id: int, task: schemas.TaskResponse, db: Session = Depends(database.get_db)):
    db_task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task.dict().items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/api/v1/projects/{project_id}/tasks/", response_model=List[schemas.TaskResponse])
def get_tasks(project_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.Task).filter(models.Task.project_id == project_id).all()

