"""Aggregates Kubernetes, metadata, and cache data into a single namespace view."""
from datetime import datetime, timedelta, timezone
import logging
from typing import Any, Dict, Optional

from app.database import get_database
from app.services import kube_service, metadata_service

logger = logging.getLogger(__name__)
CACHE_TTL_SECONDS = 600


def _normalize_namespace(namespace: str) -> str:
    return str(namespace or "").strip().lower()


def _build_aggregated_namespace_data(namespace_name: str) -> Dict[str, Any]:
    normalized_name = _normalize_namespace(namespace_name)

    namespace_list = kube_service.list_namespaces()
    namespace_data = None
    for ns in namespace_list:
        if _normalize_namespace(ns["name"]) == normalized_name:
            namespace_data = ns
            break

    if namespace_data is None:
        raise ValueError(f"Namespace '{namespace_name}' not found in Kubernetes cluster")

    pods = kube_service.get_namespace_pods(namespace_name)
    resource_usage = kube_service.get_pod_metrics(namespace_name)
    app_info = metadata_service.get_app_for_namespace(namespace_name)
    migration_info = None
    if app_info:
        migration_info = metadata_service.get_migration_for_app(app_info.get("app_name"))

    governance_labels = namespace_data.get("governance_labels", {})
    compliance = {
        "dx-id": bool(governance_labels.get("dx-id")),
        "dx-environment": bool(governance_labels.get("dx-environment")),
        "dx-is-production": bool(governance_labels.get("dx-is-production")),
    }

    return {
        "namespace_name": namespace_name,
        "namespace": namespace_data,
        "pods": pods,
        "resource_usage": resource_usage,
        "app_info": app_info,
        "migration_info": migration_info,
        "governance_compliance": compliance,
        "last_refreshed": datetime.now(timezone.utc),
    }


async def refresh_cache(namespace: str) -> Dict[str, Any]:
    """Force-update cached aggregated namespace results in MongoDB."""
    db = get_database()
    cache_collection = db["aggregated_namespace_cache"]
    payload = _build_aggregated_namespace_data(namespace)
    payload["namespace_name"] = _normalize_namespace(namespace)
    payload["cache_ts"] = datetime.now(timezone.utc)

    await cache_collection.update_one(
        {"namespace_name": payload["namespace_name"]},
        {"$set": payload},
        upsert=True,
    )

    payload.pop("_id", None)
    return payload


async def get_aggregated_namespace_data(namespace_name: str) -> Dict[str, Any]:
    """Return cached aggregated namespace data or refresh the cache if stale."""
    db = get_database()
    cache_collection = db["aggregated_namespace_cache"]
    normalized_name = _normalize_namespace(namespace_name)

    cached = await cache_collection.find_one({"namespace_name": normalized_name})
    if cached:
        cache_ts = cached.get("cache_ts")
        if isinstance(cache_ts, datetime):
            age = datetime.now(timezone.utc) - cache_ts
            if age < timedelta(seconds=CACHE_TTL_SECONDS):
                cached.pop("_id", None)
                return cached

    return await refresh_cache(namespace_name)
