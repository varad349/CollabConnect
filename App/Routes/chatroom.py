from fastapi import APIRouter, Depends, HTTPException, status,WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from App import schemas, models, database
from datetime import datetime
from typing import List, Dict
from App.schemas import ChatMessage
from App.utils import manager
from App.utils import check_project_user_exists
from pymongo.cursor import Cursor
from bson import json_util
router = APIRouter(
    prefix="/chatroom",
    tags=["chatroom"]
)



@router.websocket("/ws/send_message/{project_id}/{user_id}")
async def send_message_ws(websocket: WebSocket, project_id: str, user_id: int, db: Session = Depends(database.get_db)):
    await manager.connect(websocket, project_id)
    try:
        while True:
            data = await websocket.receive_text()
            timestamp = datetime.utcnow()
            chat_message = schemas.ChatMessage(project_id=project_id, user_id=user_id, username="Username", message=data, timestamp=timestamp)
            database.chat_collection.insert_one(chat_message.dict())
            await manager.broadcast(f"User {user_id}: {data}", project_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)

@router.websocket("/ws/get_messages/{project_id}")
async def get_messages_ws(websocket: WebSocket, project_id: str):
    await manager.connect(websocket, project_id)
    try:
        messages_cursor = database.chat_collection.find({"project_id": project_id})
        for message in messages_cursor:
            message_str = json_util.dumps(message)
            await manager.send_personal_message(message_str, websocket)
    except Exception as e:
        print(f"Error in get_messages_ws: {e}")

    finally:
        await manager.disconnect(websocket, project_id)
