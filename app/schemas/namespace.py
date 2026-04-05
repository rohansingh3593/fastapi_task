from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NamespaceListItem(BaseModel):
    name: str
    labels: Dict[str, Any]
    governance_compliant: bool


class PodContainerInfo(BaseModel):
    name: str
    cpu: Optional[str] = None
    memory: Optional[str] = None


class PodInfo(BaseModel):
    name: str
    status: str
    containers: List[PodContainerInfo]
    cpu_usage: Optional[str] = None
    memory_usage: Optional[str] = None


class NamespaceDetail(BaseModel):
    namespace_name: str
    cpu: Optional[str] = None
    memory: Optional[str] = None
    pods: List[PodInfo]
    application_name: Optional[str] = None
    microservices: List[str] = Field(default_factory=list)
    repo_url: Optional[str] = None
    tech_stack: Optional[str] = None
    migration_status: Optional[Dict[str, Any]] = None
    governance_labels: Dict[str, bool]
