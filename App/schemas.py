from pydantic import BaseModel,EmailStr,AnyUrl,Field
from typing import Optional, Dict
from datetime import datetime,date
from pydantic import BaseModel
from typing import List
from datetime import datetime


class user_reg(BaseModel):  
    username: str
    email: EmailStr
    dob:date
    password: str

class user_login(BaseModel):
    email: EmailStr
    password: str
class complete_profile(BaseModel):
    domain: Optional[str] = Field(None, example="software development")
    github: Optional[str] = Field(None, example="https://github.com/johndoe")
    linkedin: Optional[str] = Field(None, example="https://linkedin.com/in/johndoe")
    skills: Optional[str] = Field(None, example="Python, Django, FastAPI")
    past_projects: Optional[Dict] = Field(None, example={"project1": "details"})
    is_private:Optional[bool]=Field(None, examples=[False])


class ProjectCreate(BaseModel):
    title: str
    description: str
    co_leader_id: Optional[int]=None
    member_ids:Optional[list] = None

class ProjectUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]


class TeamMemberCreate(BaseModel):
    user_id: int
    project_id: int


class TeamMemberUpdate(BaseModel):
    user_id: Optional[int]
    project_id: Optional[int]


class ProjectDetails(BaseModel):
    title: str
    description: Optional[str]  
    owner_id: int
    leader_id: int
    co_leader_id: int


class TeamMemberDetails(BaseModel):
    id: int
    user: dict



class NotificationBase(BaseModel):
    message: str
    is_read: Optional[bool] = False

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationUpdate(NotificationBase):
    pass

class NotificationInDB(NotificationBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class ChatMessage(BaseModel):
    project_id: str
    user_id: int
    username: str
    message: str
    timestamp: datetime

class ChatRoom(BaseModel):
    project_id: str
    messages: Dict[int, List[ChatMessage]] = {}

    def add_message(self, user_id: int, message: str, timestamp: datetime):
        if user_id not in self.messages:
            self.messages[user_id] = []
        self.messages[user_id].append(ChatMessage(user_id=user_id, message=message, timestamp=timestamp))
class TaskResponse(BaseModel):
    title:str
    description:str
    status:str
    priority:int
    due_date:date
    assignee_id:int

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    id:Optional[int]=None


class Invitation(BaseModel):
    id: int
    project_id: int
    user_id: int
    status: str = "pending"
    created_at: datetime

    class Config:
        orm_mode = True

class JoinRequest(BaseModel):
    id: int
    project_id: int
    user_id: int
    status: str = "pending"
    created_at: datetime

    class Config:
        orm_mode = True
class ProjectRecommendation(BaseModel):
    project_id: str
    title: str
    description: str

class UserRecommendation(BaseModel):
    user_id: str
    name: str
    skills: str
    past_experiences: str
    projects: str