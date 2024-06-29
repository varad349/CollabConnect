from fastapi import FastAPI,Response,status,HTTPException,Depends,APIRouter
from App import schemas
from sqlalchemy.orm import Session
from App import database
from App import models
from App import utils,oauth2

router=APIRouter(tags=["Authentication"])
@router.post("/login",status_code=status.HTTP_202_ACCEPTED)
async def login(user_cred:schemas.user_login,db:Session=Depends(database.get_db)):
    user=db.query(models.User).filter(models.User.email ==user_cred.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid Credentials")
    if not utils.verify(user_cred.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid Credentials")
    access_token=oauth2.create_access_token(data={"user_id":user.id})
    return{"access_token":access_token,"token_type":"bearer"}