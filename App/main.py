from fastapi import FastAPI
from App.database import engine
from App import models
from App.Routes import profile, user, projects, notifications, chatroom, tasks,auth,recommend

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    print("Hello world")

def include_routers():
    from Routes import profile, user, projects, notifications
    app.include_router(profile.router)
    app.include_router(user.router)
    app.include_router(projects.router)
    app.include_router(notifications.router)
    app.include_router(tasks.router)
    app.include_router(auth.router)
    app.include_router(recommend.router)
include_routers()
app.include_router(chatroom.router)


