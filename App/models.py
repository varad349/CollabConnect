from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, TIMESTAMP, DATE, Table, Date,ARRAY
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.expression import text
from .database import Base



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    dob = Column(DATE, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    projects_list = Column(JSON) 
    profile = relationship("Profile", back_populates="owner", uselist=False)
    notifications = relationship("Notification", back_populates="user")
    projects_owned = relationship("Project", back_populates="owner", foreign_keys="[Project.owner_id]")
    projects_as_co_leader = relationship("Project", back_populates="co_leader", foreign_keys="[Project.co_leader_id]")

class Profile(Base):
    __tablename__ = "profiles"
    profile_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    domain = Column(String, index=True)
    github = Column(String, index=True)
    linkedin = Column(String, index=True)
    skills = Column(String, index=True)
    past_projects = Column(JSON)
    is_private = Column(Boolean, nullable=False, default=False)

    owner = relationship("User", back_populates="profile")

class Project(Base):
    __tablename__ = "projects"
    project_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String,nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    co_leader_id = Column(Integer, ForeignKey("users.id"),nullable=True)
    member_ids = Column(JSON, nullable=False, default=list)
    owner = relationship("User", back_populates="projects_owned", foreign_keys=[owner_id])
    co_leader = relationship("User", back_populates="projects_as_co_leader", foreign_keys=[co_leader_id])
    tasks = relationship("Task", back_populates="project")
    

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    user = relationship("User", back_populates="notifications")
class Task(Base):
    __tablename__ = "tasks"
    
    task_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, nullable=False, default="to-do")
    priority = Column(String, default="medium")
    due_date = Column(Date)
    assignee_id = Column(Integer, ForeignKey("users.id"))

    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User")

class Invitation(Base):
    __tablename__ = "invitations"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")  
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    project = relationship("Project")
    user = relationship("User")

class JoinRequest(Base):
    __tablename__ = "join_requests"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")  # pending, accepted, rejected
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    project = relationship("Project")
    user = relationship("User")
