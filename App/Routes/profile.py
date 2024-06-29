from fastapi import FastAPI,Response,status,HTTPException,Depends,APIRouter
from App import schemas
from sqlalchemy.orm import Session
from App import database
from App import models
from App import oauth2
from database_weaviate import insert_user_data, update_user_data


router=APIRouter(
    prefix="/profiles",
    tags=["profiles"]
)


@router.post("/complete_profile", status_code=status.HTTP_201_CREATED)
async def profile_completion(
    profile: schemas.complete_profile,
    db: Session = Depends(database.get_db),
    user_id: int = Depends(oauth2.get_current_user)
):
    print(user_id)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    existing_profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
    if existing_profile:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Profiles already exists use updating route")
    else:
        profile_data = profile.dict(by_alias=True)
        profile_data['github'] = str(profile_data.get('github', ''))
        profile_data['linkedin'] = str(profile_data.get('linkedin', ''))
        profile_data['user_id'] = user_id
        profile_create = models.Profile(**profile_data)
        db.add(profile_create)
        db.commit()
        db.refresh(profile_create)
        weaviate_user_data = {
        "user_id": str(user_id),
        "name": user.username,
        "skills": profile_data.get("skills", ""),
        "past_experiences": profile_data.get("past_projects", ""),
        "projects": profile_data.get("past_projects", "")
         }
        insert_user_data(weaviate_user_data)
    return profile_create



@router.put("/update_profile", status_code=status.HTTP_200_OK)
async def update_profile(
    profile: schemas.complete_profile,
    db: Session = Depends(database.get_db),
    user_id: int = Depends(oauth2.get_current_user)
):
    print(f"Updating profile for user_id: {user_id}")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile_data = profile.dict(by_alias=True)
    profile_data['github'] = str(profile_data.get('github', ''))
    profile_data['linkedin'] = str(profile_data.get('linkedin', ''))

    for key, value in profile_data.items():
        setattr(existing_profile, key, value)

    db.commit()
    db.refresh(existing_profile)
    weaviate_user_data = {
        "user_id": str(user_id), 
        "name": user.username,
        "skills": profile_data.get("skills", ""),
        "past_experiences": profile_data.get("past_projects", ""),
        "projects": profile_data.get("past_projects", "")
    }

    print(f"Weaviate user data: {weaviate_user_data}")

    try:
        update_user_data(weaviate_user_data)
    except Exception as e:
        print(f"Error updating Weaviate data: {e}")
        raise HTTPException(status_code=500, detail="Failed to update Weaviate data")

    return existing_profile


@router.get("/my_profile",status_code=status.HTTP_200_OK)
async def get_profile(db:Session=Depends(database.get_db),user_id: int = Depends(oauth2.get_current_user)):
    user_details = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
    if user_details is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_details


