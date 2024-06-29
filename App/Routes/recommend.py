from fastapi import APIRouter, Depends, HTTPException,status
from App import schemas, models, database
from sqlalchemy.orm import Session
from App import oauth2
from typing import List
from database_weaviate import insert_user_data, update_user_data,insert_project_data,update_project_data,get_client
import logging

router=APIRouter(prefix="/recommend",tags=["recommendation"])


@router.get("/get_recommendations", status_code=status.HTTP_202_ACCEPTED, response_model=List[schemas.ProjectRecommendation])
async def get_recommendations(
    db: Session = Depends(database.get_db), 
    user_id: int = Depends(oauth2.get_current_user)
):
    user_details = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()

    if not user_details:
        raise HTTPException(status_code=404, detail="User not found")

    user_domain = user_details.domain
    user_skills = user_details.skills
    user_past_projects = user_details.past_projects
    query_text = f"{user_domain} {user_skills} {user_past_projects}"

    client = get_client()
    try:
        response = client.query.get("Project", ["project_id", "title", "description"]).with_near_text({
            "concepts": [query_text],
            "distance": 0.7
        }).with_limit(5).do()

        projects = response['data']['Get']['Project']
        recommendations = [
            schemas.ProjectRecommendation(
                project_id=project['project_id'],
                title=project['title'],
                description=project['description']
            ) for project in projects
        ]

        return recommendations

    except Exception as e:
        logging.error(f"Error querying Weaviate: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.get("/get_recommendations_projects/{project_id}", status_code=status.HTTP_202_ACCEPTED, response_model=List[schemas.UserRecommendation])
async def get_users(project_id: int, user_id: int = Depends(oauth2.get_current_user), db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != user_id:
        raise HTTPException(status_code=403, detail="User does not own this project")

    project_title = project.title
    project_description = project.description
    query_text = f"{project_title} {project_description}"
    client = get_client()
    try:
        response = client.query.get("User", ["user_id", "name", "skills", "past_experiences", "projects"]).with_near_text({
            "concepts": [query_text],
            "distance": 0.7
        }).with_limit(5).do()

        users = response['data']['Get']['User']
        recommendations = [
            schemas.UserRecommendation(
                user_id=user['user_id'],
                name=user['name'],
                skills=user['skills'],
                past_experiences=user['past_experiences'],
                projects=user['projects']
            ) for user in users
        ]
        return recommendations
    except Exception as e:
        logging.error(f"Error querying Weaviate: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")