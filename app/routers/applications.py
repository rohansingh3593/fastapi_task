from typing import List
from fastapi import APIRouter, Depends
from app.schemas.application import ApplicationInfo
from app.services import metadata_service
from app.database import get_database

router = APIRouter()


def get_metadata_service():
    return metadata_service


@router.get("/applications", response_model=List[ApplicationInfo], tags=["Applications"])
def list_applications(db=Depends(get_database), metadata=Depends(get_metadata_service)):
    applications = metadata.load_app_metadata()
    return [ApplicationInfo(**app) for app in applications]
