import weaviate
import logging
from weaviate.exceptions import UnexpectedStatusCodeException
import requests

USER_INDEX_NAME = "User"
PROJECT_INDEX_NAME = "Project"
USER_SCHEMA = {
    "class": USER_INDEX_NAME,
    "description": "A collection of users",
    "vectorizer": "text2vec-ollama",
    "moduleConfig": {
        "text2vec-ollama": {
            "model": "snowflake-arctic-embed:latest",
            "apiEndpoint": "http://host.docker.internal:11434"
        }
    },
    "properties": [
        {
            "name": "user_id",
            "dataType": ["string"],
            "moduleConfig": {
                "text2vec-ollama": {
                    "skip": True
                }
            }
        },
        {
            "name": "name",
            "dataType": ["string"],
            "moduleConfig": {
                "text2vec-ollama": {
                    "skip": True
                }
            }
        },
        {
            "name": "skills",
            "dataType": ["text"]
        },
        {
            "name": "past_experiences",
            "dataType": ["text"]
        },
        {
            "name": "projects",
            "dataType": ["text"]
        }
    ]
}

PROJECT_SCHEMA = {
    "class": PROJECT_INDEX_NAME,
    "description": "A collection of projects",
    "vectorizer": "text2vec-ollama",
    "moduleConfig": {
        "text2vec-ollama": {
            "model": "snowflake-arctic-embed:latest",
            "apiEndpoint": "http://host.docker.internal:11434"
        }
    },
    "properties": [
        {
            "name": "project_id",
            "dataType": ["string"],
            "moduleConfig": {
                "text2vec-ollama": {
                    "skip": True
                }
            }
        },
        {
            "name": "title",
            "dataType": ["string"]
        },
        {
            "name": "description",
            "dataType": ["text"]
        }
    ]
}

def get_client():
    WEAVIATE_LOCAL_URL = 'http://localhost:8080'
    OPENAI_API_KEY = 'your_api_key'
    client = weaviate.Client(
        url=WEAVIATE_LOCAL_URL,
        additional_headers={"X-OpenAI-Api-Key": OPENAI_API_KEY}
    )
    return client

def init_db():
    client = get_client()

    try:
        client.schema.delete_class(USER_INDEX_NAME)
        logging.info(f"Deleted existing '{USER_INDEX_NAME}' class.")
    except UnexpectedStatusCodeException as e:
        logging.warning(f"Could not delete class '{USER_INDEX_NAME}': {e}")
    except requests.ConnectionError as e:
        logging.warning(f"Connection error: {e}")

    try:
        client.schema.delete_class(PROJECT_INDEX_NAME)
        logging.info(f"Deleted existing '{PROJECT_INDEX_NAME}' class.")
    except UnexpectedStatusCodeException as e:
        logging.warning(f"Could not delete class '{PROJECT_INDEX_NAME}': {e}")
    except requests.ConnectionError as e:
        logging.warning(f"Connection error: {e}")

    if not client.schema.contains(USER_SCHEMA):
        logging.debug("Creating user schema")
        client.schema.create_class(USER_SCHEMA)
    else:
        logging.debug(f"Schema for {USER_INDEX_NAME} already exists")
        logging.debug("Skipping schema creation")

    if not client.schema.contains(PROJECT_SCHEMA):
        logging.debug("Creating project schema")
        client.schema.create_class(PROJECT_SCHEMA)
    else:
        logging.debug(f"Schema for {PROJECT_INDEX_NAME} already exists")
        logging.debug("Skipping schema creation")

def insert_user_data(user):
    client = get_client()

    try:
        skills = ' '.join(user['skills']) if isinstance(user['skills'], list) else user['skills']
        past_experiences = ' '.join(user['past_experiences']) if isinstance(user['past_experiences'], list) else str(user['past_experiences'])
        projects = ' '.join(user['projects']) if isinstance(user['projects'], list) else str(user['projects'])

        properties = {
            "user_id": user['user_id'],
            "name": user['name'],
            "skills": skills,
            "past_experiences": past_experiences,
            "projects": projects
        }

        client.data_object.create(properties, USER_INDEX_NAME)
        logging.info(f"User data inserted: {user['user_id']}")
    except Exception as e:
        logging.error(f"Error inserting user data: {e}")
        raise e

def update_user_data(user):
    client = get_client()

    try:
        user_object = client.data_object.get(user['user_id'], USER_INDEX_NAME)
        properties = {
            "user_id": user['user_id'],
            "name": user['name'],
            "skills": user['skills'],
            "past_experiences": str(user['past_experiences']),
            "projects": str(user['projects'])
        }
        client.data_object.update(properties, user['user_id'], USER_INDEX_NAME)
        logging.info(f"User data updated: {user['user_id']}")
    except Exception as e:
        logging.error(f"Error updating user data: {e}")
        raise e

def insert_project_data(project):

    client = get_client() 

    try:
        properties = {
            "project_id": str(project['project_id']),  
            "title": project['title'],
            "description": project['description']
        }

        client.data_object.create(properties, PROJECT_INDEX_NAME)
        logging.info(f"Project data inserted: {project['project_id']}")
    except Exception as e:
        logging.error(f"Error inserting project data: {e}")
        raise e
def update_project_data(project):
    client = get_client()

    try:
        project_object = client.data_object.get(project['project_id'], PROJECT_INDEX_NAME)
        properties = {
            "project_id": project['project_id'],
            "title": project['title'],
            "description": project['description']
        }
        client.data_object.update(properties, project['project_id'], PROJECT_INDEX_NAME)
        logging.info(f"Project data updated: {project['project_id']}")
    except Exception as e:
        logging.error(f"Error updating project data: {e}")
        raise e
