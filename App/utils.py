from sqlalchemy.orm import Session
from . import models
from passlib.context import CryptContext

async def check_project_user_exists(db: Session, project_id: int, user_id: int) -> bool:
    project_exists = db.query(models.Project).filter(models.Project.project_id == project_id).first()
    if not project_exists:
        return False
    user_exists = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_exists:
        return False
    
    return True

from typing import List, Dict
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, project_id: str):
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = []
        self.active_connections[project_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, project_id: str):
        if project_id in self.active_connections:
            self.active_connections[project_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, project_id: str):
        if project_id in self.active_connections:
            for connection in self.active_connections[project_id]:
                await connection.send_text(message)

manager = ConnectionManager()



pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")
def hash(password:str):
    return pwd_context.hash(password)

def verify(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)