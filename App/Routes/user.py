from fastapi import FastAPI,Response,status,HTTPException,Depends,APIRouter
from App import schemas
from sqlalchemy.orm import Session
from App import database
from App import models
from App import utils



router=APIRouter(
    prefix="/users",
    tags=["users"]
)




#User registration
@router.post("/register",status_code=status.HTTP_201_CREATED)
async def create_user(user:schemas.user_reg,db: Session = Depends(database.get_db)):
    print("something")
    try:
        hashed_password=utils.hash(user.password)
        user.password=hashed_password
        new_user = models.User(**user.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message":"User creation successful"}
    except Exception as e:
        return {"error": "User creation failed"}




