from fastapi import APIRouter, Depends, HTTPException
from app.schemas.common import HealthResponse
from app.database import get_database
from app.services import kube_service
from app.services.kube_service import KubeServiceError

router = APIRouter()


def get_kube_service():
    return kube_service


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db=Depends(get_database), kube=Depends(get_kube_service)):
    try:
        await db.client.admin.command("ping")
    except Exception as exc:
        raise HTTPException(status_code=503, detail="MongoDB is unavailable") from exc

    try:
        kube.list_namespaces()
    except KubeServiceError as exc:
        raise HTTPException(status_code=503, detail="Kubernetes cluster connectivity failure") from exc

    return HealthResponse(status="healthy", version="0.1.0")
