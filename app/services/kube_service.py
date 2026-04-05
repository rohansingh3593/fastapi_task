"""Kubernetes retrieval service for namespaces, pods, and metrics."""
from kubernetes import client, config
from kubernetes.client import ApiException
from kubernetes.config.config_exception import ConfigException
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class KubeServiceError(RuntimeError):
    """Raised when the Kubernetes cluster cannot be reached."""


def _load_kube_config() -> None:
    try:
        config.load_incluster_config()
        logger.info("Loaded in-cluster Kubernetes configuration.")
    except ConfigException:
        logger.info("In-cluster config unavailable, attempting local kubeconfig.")
        try:
            config.load_kube_config()
            logger.info("Loaded local kubeconfig.")
        except Exception as exc:
            logger.error("Failed to load Kubernetes configuration", exc_info=True)
            raise KubeServiceError("Failed to load Kubernetes configuration") from exc


def _get_core_api() -> client.CoreV1Api:
    _load_kube_config()
    return client.CoreV1Api()


def _get_custom_objects_api() -> client.CustomObjectsApi:
    _load_kube_config()
    return client.CustomObjectsApi()


def _extract_governance_labels(metadata: Any) -> Dict[str, str]:
    labels = getattr(metadata, "labels", {}) or {}
    return {
        "dx-id": labels.get("dx-id", ""),
        "dx-environment": labels.get("dx-environment", ""),
        "dx-is-production": labels.get("dx-is-production", ""),
    }


def list_namespaces() -> List[Dict[str, Any]]:
    """Return namespace names, labels, and governance label values."""
    try:
        api = _get_core_api()
        response = api.list_namespace()

        namespaces = []
        for item in response.items:
            metadata = item.metadata
            namespace = {
                "name": metadata.name,
                "labels": metadata.labels or {},
                "governance_labels": _extract_governance_labels(metadata),
            }
            namespaces.append(namespace)

        return namespaces
    except ApiException as exc:
        logger.error("Kubernetes API error listing namespaces", exc_info=True)
        raise KubeServiceError("Unable to list namespaces from Kubernetes cluster") from exc
    except Exception as exc:
        logger.error("Unexpected error listing namespaces", exc_info=True)
        raise KubeServiceError("Unable to connect to Kubernetes cluster") from exc


def get_namespace_pods(name: str) -> List[Dict[str, Any]]:
    """Return pods for a namespace with status and labels."""
    try:
        api = _get_core_api()
        response = api.list_namespaced_pod(name)

        pods = []
        for pod in response.items:
            pods.append(
                {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "labels": pod.metadata.labels or {},
                    "node_name": pod.spec.node_name,
                    "pod_ip": pod.status.pod_ip,
                    "host_ip": pod.status.host_ip,
                    "container_statuses": [
                        {
                            "name": cs.name,
                            "state": cs.state.to_dict() if cs.state else None,
                            "ready": cs.ready,
                            "restart_count": cs.restart_count,
                        }
                        for cs in (pod.status.container_statuses or [])
                    ],
                }
            )

        return pods
    except ApiException as exc:
        logger.error("Kubernetes API error listing pods for namespace %s", name, exc_info=True)
        raise KubeServiceError(f"Unable to list pods for namespace '{name}'") from exc
    except Exception as exc:
        logger.error("Unexpected error listing pods", exc_info=True)
        raise KubeServiceError("Unable to connect to Kubernetes cluster") from exc


def get_pod_metrics(namespace: str) -> List[Dict[str, Any]]:
    """Return CPU and memory usage for pods in a namespace via metrics API."""
    try:
        api = _get_custom_objects_api()
        response = api.list_namespaced_custom_object(
            group="metrics.k8s.io",
            version="v1beta1",
            namespace=namespace,
            plural="pods",
        )

        metrics = []
        for item in response.get("items", []):
            pod_name = item.get("metadata", {}).get("name")
            containers = []
            for container in item.get("containers", []):
                usage = container.get("usage", {})
                containers.append(
                    {
                        "name": container.get("name"),
                        "cpu": usage.get("cpu"),
                        "memory": usage.get("memory"),
                    }
                )

            metrics.append(
                {
                    "pod_name": pod_name,
                    "namespace": namespace,
                    "containers": containers,
                }
            )

        return metrics
    except ApiException as exc:
        logger.error("Kubernetes metrics API error for namespace %s", namespace, exc_info=True)
        raise KubeServiceError(f"Unable to fetch pod metrics for namespace '{namespace}'") from exc
    except Exception as exc:
        logger.error("Unexpected error fetching pod metrics", exc_info=True)
        raise KubeServiceError("Unable to connect to Kubernetes metrics API") from exc
