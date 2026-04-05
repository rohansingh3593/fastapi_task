from typing import Dict, List, Optional
from pydantic import BaseModel


class ApplicationInfo(BaseModel):
    app_name: str
    namespaces: Dict[str, str]
    microservices: List[str]
    repo_url: Optional[str] = None
    tech_stack: Optional[str] = None


class MigrationStatus(BaseModel):
    roadmap_status: Optional[str] = None
    migration_progress: Optional[str] = None
    ownership: Optional[str] = None
    hosting_location: Optional[str] = None
