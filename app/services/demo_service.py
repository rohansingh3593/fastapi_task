"""Demo/mock data service for development without a live Kubernetes cluster."""
from typing import Any, Dict, List


def get_demo_namespaces() -> List[Dict[str, Any]]:
    """Return mock namespace data for demo mode."""
    return [
        {
            "name": "demo-app-prod",
            "labels": {"app": "demo-app", "env": "production"},
            "governance_labels": {
                "dx-id": "APP-001",
                "dx-environment": "production",
                "dx-is-production": "true",
            },
        },
        {
            "name": "demo-app-dev",
            "labels": {"app": "demo-app", "env": "development"},
            "governance_labels": {
                "dx-id": "APP-001-DEV",
                "dx-environment": "development",
                "dx-is-production": "",
            },
        },
        {
            "name": "demo-microservice-qa",
            "labels": {"app": "demo-microservice", "env": "qa"},
            "governance_labels": {
                "dx-id": "SVC-002-QA",
                "dx-environment": "qa",
                "dx-is-production": "",
            },
        },
    ]


def get_demo_namespace_detail(name: str) -> Dict[str, Any]:
    """Return mock aggregated namespace data for demo mode."""
    return {
        "namespace_name": name,
        "namespace": {
            "name": name,
            "labels": {"app": "demo-app", "env": "demo"},
            "governance_labels": {
                "dx-id": "DEMO-001",
                "dx-environment": "demo",
                "dx-is-production": "false",
            },
        },
        "pods": [
            {
                "name": f"{name}-pod-1",
                "namespace": name,
                "status": "Running",
                "labels": {"tier": "frontend"},
                "node_name": "worker-node-1",
                "pod_ip": "10.0.1.100",
                "host_ip": "192.168.1.10",
                "container_statuses": [
                    {
                        "name": "app-container",
                        "state": {"running": {"startedAt": "2026-04-05T10:00:00Z"}},
                        "ready": True,
                        "restart_count": 0,
                    }
                ],
            },
            {
                "name": f"{name}-pod-2",
                "namespace": name,
                "status": "Running",
                "labels": {"tier": "backend"},
                "node_name": "worker-node-2",
                "pod_ip": "10.0.1.101",
                "host_ip": "192.168.1.11",
                "container_statuses": [
                    {
                        "name": "app-container",
                        "state": {"running": {"startedAt": "2026-04-05T10:00:00Z"}},
                        "ready": True,
                        "restart_count": 0,
                    }
                ],
            },
        ],
        "resource_usage": [
            {
                "pod_name": f"{name}-pod-1",
                "namespace": name,
                "containers": [
                    {"name": "app-container", "cpu": "125m", "memory": "256Mi"}
                ],
            },
            {
                "pod_name": f"{name}-pod-2",
                "namespace": name,
                "containers": [
                    {"name": "app-container", "cpu": "250m", "memory": "512Mi"}
                ],
            },
        ],
        "app_info": {
            "app_name": "Demo Application",
            "namespaces": {
                "dev": "demo-app-dev",
                "prod": "demo-app-prod",
                "qa": "demo-app-qa",
                "uat": "demo-app-uat",
            },
            "microservices": ["auth-service", "payment-service", "notification-service"],
            "repo_url": "https://github.com/demo/demo-app",
            "tech_stack": "Node.js, React, MongoDB, Docker, Kubernetes",
            "matched_namespace_type": "prod",
        },
        "migration_info": {
            "app_name": "Demo Application",
            "roadmap_status": "In Progress",
            "migration_progress": "60%",
            "owner": "Platform Team",
            "hosting_location": "AWS EKS",
        },
        "governance_compliance": {
            "dx-id": True,
            "dx-environment": True,
            "dx-is-production": False,
        },
        "last_refreshed": "2026-04-05T12:00:00Z",
    }
