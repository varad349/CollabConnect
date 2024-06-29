from fastapi import APIRouter, Depends, HTTPException, status,WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from App import schemas, models, database
from datetime import datetime
from typing import List, Dict
from App.schemas import ChatMessage
from App.utils import manager
from App.utils import check_project_user_exists
from App import oauth2
import json
from database_weaviate import insert_user_data, update_user_data,insert_project_data,update_project_data
router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)

@router.post("/create_projects", response_model=schemas.ProjectCreate, status_code=status.HTTP_201_CREATED)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(database.get_db), user_id: int = Depends(oauth2.get_current_user)):
    co_lead_id = int(project.co_leader_id) if project.co_leader_id else None
    co_leader = None
    if co_lead_id:
        co_leader = db.query(models.User).filter(models.User.id == co_lead_id).first()
        if not co_leader:
            raise HTTPException(status_code=404, detail="Co-leader not found")
    member_ids = [int(id) for id in project.member_ids]
    members = db.query(models.User).filter(models.User.id.in_(member_ids)).all()
    if len(members) != len(member_ids):
        raise HTTPException(status_code=400, detail="One or more member IDs are invalid")
    
    new_project = models.Project(**project.dict(), owner_id=user_id)
    db.add(new_project)
    db.commit() 
    db.refresh(new_project)
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    projects_list = json.loads(user.projects_list) if user.projects_list else []
    projects_list.append(new_project.project_id)
    user.projects_list = json.dumps(projects_list)
    db.commit()
    db.refresh(user)
    if project.co_leader_id:
        co_lead_id=int(project.co_leader_id)
        co_leader = db.query(models.User).filter(models.User.id == co_lead_id).first()
        if not co_leader:
            raise HTTPException(status_code=404, detail="Co-leader not found")
        co_leader_projects_list = json.loads(co_leader.projects_list) if co_leader.projects_list else []
        co_leader_projects_list.append(new_project.project_id)
        co_leader.projects_list = json.dumps(co_leader_projects_list)
        db.commit()
        db.refresh(co_leader)
    for member_id in project.member_ids:
        member = db.query(models.User).filter(models.User.id == int(member_id)).first()
        if member:
            member_projects_list = json.loads(member.projects_list) if member.projects_list else []
            member_projects_list.append(new_project.project_id)
            member.projects_list = json.dumps(member_projects_list)
            db.commit()
            db.refresh(member)

    project_data = {
        "project_id": new_project.project_id,
        "title": new_project.title,
        "description": new_project.description
    }
    insert_project_data(project_data)

    return new_project


@router.get("/get_projects")
def get_all_projects(user_id: int = Depends(oauth2.get_current_user), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or not user.projects_list:
        return []
    if isinstance(user.projects_list, str):
        projects_list = json.loads(user.projects_list)
    else:
        projects_list = user.projects_list

    projects = db.query(models.Project).filter(models.Project.project_id.in_(projects_list)).all()
    return projects


@router.get("/get_projects/{project_id}")
def get_project(project_id: int, db: Session = Depends(database.get_db), user_id: int = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if isinstance(user.projects_list, str):
        projects_list = json.loads(user.projects_list)
    else:
        projects_list = user.projects_list
    if project_id not in projects_list:
        raise HTTPException(status_code=403, detail="You do not have permission to view this project")
    project = db.query(models.Project).filter_by(project_id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")
    return project



@router.put("/update_project/{id}", response_model=schemas.ProjectCreate, status_code=status.HTTP_202_ACCEPTED)
async def update_project(id: int, updated_info: schemas.ProjectCreate, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter_by(project_id=id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id {id} not found")
    for key, value in updated_info.dict().items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    project_data = {
        "project_id": project.project_id,
        "title": project.title,
        "description": project.description
    }
    update_project_data(project_data)
    return project

@router.delete("/api/v1/projects/{project_id}", status_code=204)
def delete_project(id: int, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter_by(project_id=id).first()

    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id {id} not found")
    db.delete(project)
    db.commit()

    return {"message": f"Project {id} deleted successfully"}

@router.delete("/projects/{project_id}/delete_members/{member_id}")
def delete_member(
    project_id: int,
    member_id: int,
    db: Session = Depends(database.get_db),
    user_id: int = Depends(oauth2.get_current_user)
):
    project = db.query(models.Project).filter(models.Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != user_id and project.co_leader_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete members")
    member = db.query(models.User).filter(models.User.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    if member_id not in project.member_ids:
        raise HTTPException(status_code=404, detail="Member not part of the project")
    project.member_ids = [m_id for m_id in project.member_ids if m_id != member_id]
    db.commit()  
    if member.projects_list:
        projects_list = json.loads(member.projects_list)
        if project_id in projects_list:
            projects_list.remove(project_id)
            member.projects_list = json.dumps(projects_list)
            print("Deleted from member's projects_list")  
            db.commit()  
        else:
            print(f"Project ID {project_id} not found in member's projects_list")  
    else:
        print("Member has no projects_list")

    db.refresh(project)
    db.refresh(member)
    return {"message":"ok"}



@router.post("/projects/{project_id}/add_members", status_code=status.HTTP_200_OK)
def add_members(
    project_id: int,
    members: Dict[str, list], 
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(oauth2.get_current_user)
):
    member_ids = members.get("member_ids", [])
    
    if not member_ids:
        raise HTTPException(status_code=400, detail="Member IDs not provided")
    project = db.query(models.Project).filter(models.Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user_id and project.co_leader_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to add members")
    users = db.query(models.User).filter(models.User.id.in_(member_ids)).all()
    if len(users) != len(member_ids):
        raise HTTPException(status_code=404, detail="One or more members not found")
    current_member_ids = project.member_ids or []
    new_member_ids = list(set(current_member_ids + member_ids))

    project.member_ids = new_member_ids

    try:
        db.commit()
        db.refresh(project)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update project member_ids: {e}")
    print(f"Project member IDs in database after update: {project.member_ids}")
    for user in users:
        projects_list = json.loads(user.projects_list) if user.projects_list else []
        if project_id not in projects_list:
            projects_list.append(project_id)
            user.projects_list = json.dumps(projects_list)
            try:
                db.commit()
                db.refresh(user)
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=f"Failed to update user projects_list: {e}")
            print(f"User {user.id} projects_list after update: {projects_list}")

    return {"message": "Members added successfully"}





@router.put("/projects/{project_id}/change_co_leader/{co_leader_id}")
def change_co_leader(project_id: int, co_leader_id: int, db: Session = Depends(database.get_db), user_id: int = Depends(oauth2.get_current_user)):
    project = db.query(models.Project).filter_by(project_id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to change co-leader")
    new_co_leader = db.query(models.User).filter_by(id=co_leader_id).first()
    if not new_co_leader:
        raise HTTPException(status_code=404, detail="New co-leader not found")
    project.co_leader_id = co_leader_id
    db.commit()
    return project
#####################################################################################################
#######################################################################################################
##########################################################################################################
##############################################################################################################

@router.post("/projects/{project_id}/request_join", response_model=schemas.JoinRequest, status_code=status.HTTP_201_CREATED)
def request_join(project_id: int, db: Session = Depends(database.get_db), user_id: int = Depends(oauth2.get_current_user)):
    join_request = models.JoinRequest(project_id=project_id, user_id=user_id)
    db.add(join_request)
    db.commit()
    db.refresh(join_request)
    return join_request

@router.post("/projects/{project_id}/invite_user/{invite_id}", response_model=schemas.Invitation, status_code=status.HTTP_201_CREATED)
def invite_user(project_id: int, invite_id: int, db: Session = Depends(database.get_db), current_user_id: int = Depends(oauth2.get_current_user)):
    project = db.query(models.Project).filter(models.Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to invite users")

    invitation = models.Invitation(project_id=project_id, user_id=invite_id)
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return invitation

@router.post("/invitations/{invitation_id}/respond", response_model=schemas.Invitation, status_code=status.HTTP_200_OK)
def respond_invitation(invitation_id: int, response: str, db: Session = Depends(database.get_db), user_id: int = Depends(oauth2.get_current_user)):
    invitation = db.query(models.Invitation).filter(models.Invitation.id == invitation_id).first()
    if not invitation or invitation.user_id != user_id:
        raise HTTPException(status_code=404, detail="Invitation not found or not authorized")
    if response not in ["accepted", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid response")

    invitation.status = response
    db.commit()
    db.refresh(invitation)

    if response == "accepted":
        project = db.query(models.Project).filter(models.Project.project_id == invitation.project_id).first()
        project.member_ids.append(invitation.user_id)
        db.commit()
        user = db.query(models.User).filter(models.User.id == invitation.user_id).first()
        if user:
            projects_list = json.loads(user.projects_list) if user.projects_list else []
            if project.project_id not in projects_list:
                projects_list.append(project.project_id)
                user.projects_list = json.dumps(projects_list)
                db.commit()
                db.refresh(user)
    return invitation

@router.post("/join_requests/{request_id}/respond", response_model=schemas.JoinRequest, status_code=status.HTTP_200_OK)
def respond_join_request(request_id: int, response: str, db: Session = Depends(database.get_db), user_id: int = Depends(oauth2.get_current_user)):
    join_request = db.query(models.JoinRequest).filter(models.JoinRequest.id == request_id).first()
    project = db.query(models.Project).filter(models.Project.project_id == join_request.project_id).first()
    if not join_request or (project.owner_id != user_id and project.co_leader_id != user_id):
        raise HTTPException(status_code=404, detail="Join request not found or not authorized")
    if response not in ["accepted", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid response")
    join_request.status = response
    db.commit()
    db.refresh(join_request)
    if response == "accepted":
        project.member_ids.append(join_request.user_id)
        db.commit()
        user = db.query(models.User).filter(models.User.id == join_request.user_id).first()
        if user:
            projects_list = json.loads(user.projects_list) if user.projects_list else []
            if project.project_id not in projects_list:
                projects_list.append(project.project_id)
                user.projects_list = json.dumps(projects_list)
                db.commit()
                db.refresh(user)
    return join_request
































# @router.websocket("/ws/{project_id}")
# async def websocket_endpoint(websocket: WebSocket, project_id: str):
#     await manager.connect(websocket, project_id)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             chat_message = schemas.ChatMessage(
#                 project_id=project_id,
#                 user_id=1,  # Retrieve actual user ID from session or token
#                 username="User",  # Retrieve actual username from session or token
#                 message=data,
#                 timestamp=datetime.utcnow()
#             )
#             chat_collection.insert_one(chat_message.dict())
#             await manager.broadcast(data, project_id)
#     except WebSocketDisconnect:
#         manager.disconnect(websocket, project_id)



# @router.get("/{project_id}/chats", response_model=List[schemas.ChatMessage])
# async def get_chat_history(project_id: str):
#     messages = chat_collection.find({"project_id": project_id})
#     chat_history = [schemas.ChatMessage(**msg) for msg in messages]
#     return chat_history