from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path
from app.core.config import get_settings
from app.database import get_database
from app.schemas.namespace import NamespaceDetail, NamespaceListItem, PodContainerInfo, PodInfo
from app.services import kube_service, aggregator_service, demo_service
from app.services.kube_service import KubeServiceError

router = APIRouter()


def get_kube_service():
    return kube_service


def get_aggregator_service():
    return aggregator_service


@router.get("/namespaces", response_model=List[NamespaceListItem], tags=["Namespaces"])
def list_namespaces(db=Depends(get_database), kube=Depends(get_kube_service)):
    settings = get_settings()
    try:
        namespaces = kube.list_namespaces()
        result = []
        for item in namespaces:
            labels = item.get("labels", {}) or {}
            governance = item.get("governance_labels", {})
            compliance = all(
                bool(governance.get(key))
                for key in ["dx-id", "dx-environment", "dx-is-production"]
            )
            result.append(
                NamespaceListItem(
                    name=item.get("name"),
                    labels=labels,
                    governance_compliant=compliance,
                )
            )
        return result
    except KubeServiceError as exc:
        if settings.demo_mode:
            namespaces = demo_service.get_demo_namespaces()
            result = []
            for item in namespaces:
                labels = item.get("labels", {}) or {}
                governance = item.get("governance_labels", {})
                compliance = all(
                    bool(governance.get(key))
                    for key in ["dx-id", "dx-environment", "dx-is-production"]
                )
                result.append(
                    NamespaceListItem(
                        name=item.get("name"),
                        labels=labels,
                        governance_compliant=compliance,
                    )
                )
            return result
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get(
    "/namespace/{name}",
    response_model=NamespaceDetail,
    tags=["Namespaces"],
)
async def get_namespace_detail(
    name: str = Path(..., regex=r"^[a-zA-Z0-9-]+$", description="Kubernetes namespace name"),
    db=Depends(get_database),
    aggregator=Depends(get_aggregator_service),
):
    settings = get_settings()
    try:
        aggregated = await aggregator.get_aggregated_namespace_data(name)
        resource_usage = aggregated.get("resource_usage", [])
        pods = aggregated.get("pods", [])

        pod_metrics = {item["pod_name"]: item for item in resource_usage}

        pod_list = []
        for pod in pods:
            pod_metric = pod_metrics.get(pod["name"], {})
            cpu_usage = None
            memory_usage = None
            containers = []
            for container in pod_metric.get("containers", []):
                containers.append(
                    PodContainerInfo(
                        name=container.get("name"),
                        cpu=container.get("cpu"),
                        memory=container.get("memory"),
                    )
                )
                if container.get("cpu"):
                    cpu_usage = container.get("cpu")
                if container.get("memory"):
                    memory_usage = container.get("memory")

            if not containers:
                containers = [
                    PodContainerInfo(name=item.get("name"), cpu=None, memory=None)
                    for item in (pod.get("container_statuses") or [])
                ]

            pod_list.append(
                PodInfo(
                    name=pod["name"],
                    status=pod.get("status", "unknown"),
                    containers=containers,
                    cpu_usage=cpu_usage,
                    memory_usage=memory_usage,
                )
            )

        app_info = aggregated.get("app_info") or {}
        migration_info = aggregated.get("migration_info")
        governance_labels = aggregated.get("governance_compliance", {})

        namespace_cpu = None
        namespace_memory = None
        if resource_usage:
            cpu_values = []
            memory_values = []
            for usage in resource_usage:
                for container in usage.get("containers", []):
                    if container.get("cpu"):
                        cpu_values.append(container.get("cpu"))
                    if container.get("memory"):
                        memory_values.append(container.get("memory"))
            namespace_cpu = ", ".join(cpu_values) if cpu_values else None
            namespace_memory = ", ".join(memory_values) if memory_values else None

        return NamespaceDetail(
            namespace_name=aggregated.get("namespace_name"),
            cpu=namespace_cpu,
            memory=namespace_memory,
            pods=pod_list,
            application_name=app_info.get("app_name") if app_info else None,
            microservices=app_info.get("microservices") if app_info else [],
            repo_url=app_info.get("repo_url") if app_info else None,
            tech_stack=app_info.get("tech_stack") if app_info else None,
            migration_status=migration_info,
            governance_labels=governance_labels,
        )
    except KubeServiceError as exc:
        if settings.demo_mode:
            aggregated = demo_service.get_demo_namespace_detail(name)
            resource_usage = aggregated.get("resource_usage", [])
            pods = aggregated.get("pods", [])

            pod_metrics = {item["pod_name"]: item for item in resource_usage}

            pod_list = []
            for pod in pods:
                pod_metric = pod_metrics.get(pod["name"], {})
                cpu_usage = None
                memory_usage = None
                containers = []
                for container in pod_metric.get("containers", []):
                    containers.append(
                        PodContainerInfo(
                            name=container.get("name"),
                            cpu=container.get("cpu"),
                            memory=container.get("memory"),
                        )
                    )
                    if container.get("cpu"):
                        cpu_usage = container.get("cpu")
                    if container.get("memory"):
                        memory_usage = container.get("memory")

                if not containers:
                    containers = [
                        PodContainerInfo(name=item.get("name"), cpu=None, memory=None)
                        for item in (pod.get("container_statuses") or [])
                    ]

                pod_list.append(
                    PodInfo(
                        name=pod["name"],
                        status=pod.get("status", "unknown"),
                        containers=containers,
                        cpu_usage=cpu_usage,
                        memory_usage=memory_usage,
                    )
                )

            app_info = aggregated.get("app_info") or {}
            migration_info = aggregated.get("migration_info")
            governance_labels = aggregated.get("governance_compliance", {})

            namespace_cpu = None
            namespace_memory = None
            if resource_usage:
                cpu_values = []
                memory_values = []
                for usage in resource_usage:
                    for container in usage.get("containers", []):
                        if container.get("cpu"):
                            cpu_values.append(container.get("cpu"))
                        if container.get("memory"):
                            memory_values.append(container.get("memory"))
                namespace_cpu = ", ".join(cpu_values) if cpu_values else None
                namespace_memory = ", ".join(memory_values) if memory_values else None

            return NamespaceDetail(
                namespace_name=aggregated.get("namespace_name"),
                cpu=namespace_cpu,
                memory=namespace_memory,
                pods=pod_list,
                application_name=app_info.get("app_name") if app_info else None,
                microservices=app_info.get("microservices") if app_info else [],
                repo_url=app_info.get("repo_url") if app_info else None,
                tech_stack=app_info.get("tech_stack") if app_info else None,
                migration_status=migration_info,
                governance_labels=governance_labels,
            )
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
