"""Excel metadata service for application and migration metadata."""
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging
import pandas as pd

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
APP_METADATA_FILE = DATA_DIR / "app_metadata.xlsx"
MIGRATION_ROADMAP_FILE = DATA_DIR / "migration_roadmap.xlsx"


class MetadataError(RuntimeError):
    """Raised when metadata cannot be loaded or parsed."""


def _normalize_namespace(namespace: Any) -> str:
    if namespace is None:
        return ""
    return str(namespace).strip().lower()


def _normalize_column_name(column_name: str) -> str:
    return str(column_name).strip().lower().replace(" ", "_")


def _read_excel(path: Path) -> pd.DataFrame:
    if not path.exists():
        logger.error("Excel metadata file not found: %s", path)
        raise MetadataError(f"Metadata file not found: {path}")

    try:
        return pd.read_excel(path, engine="openpyxl")
    except Exception as exc:
        logger.error("Error reading Excel file %s", path, exc_info=True)
        raise MetadataError(f"Unable to read Excel file: {path}") from exc


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [_normalize_column_name(c) for c in df.columns]
    return df


def _extract_string(row: pd.Series, field_names: List[str]) -> str:
    for name in field_names:
        value = row.get(name)
        if pd.notna(value) and value is not None:
            return str(value).strip()
    return ""


def _split_list(value: Any) -> List[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    raw = str(value)
    return [part.strip() for part in raw.split(",") if part.strip()]


def load_app_metadata() -> List[Dict[str, Any]]:
    """Read application metadata from app_metadata.xlsx."""
    df = _read_excel(APP_METADATA_FILE)
    df = _normalize_columns(df)

    apps: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        app_name = _extract_string(row, ["app_name", "application", "application_name"])
        if not app_name:
            continue

        namespaces = {
            "dev": _normalize_namespace(_extract_string(row, ["dev_namespace", "dev"])),
            "prod": _normalize_namespace(_extract_string(row, ["prod_namespace", "prod"])),
            "qa": _normalize_namespace(_extract_string(row, ["qa_namespace", "qa"])),
            "uat": _normalize_namespace(_extract_string(row, ["uat_namespace", "uat"])),
        }

        apps.append(
            {
                "app_name": app_name,
                "namespaces": namespaces,
                "microservices": _split_list(row.get("microservices") or row.get("services")),
                "repo_url": _extract_string(row, ["repo_url", "repository", "git_url", "repo"]),
                "tech_stack": _extract_string(row, ["tech_stack", "technology_stack", "technology"]),
            }
        )

    return apps


def load_migration_data() -> List[Dict[str, Any]]:
    """Read migration roadmap data from migration_roadmap.xlsx."""
    df = _read_excel(MIGRATION_ROADMAP_FILE)
    df = _normalize_columns(df)

    roadmap: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        app_name = _extract_string(row, ["app_name", "application", "application_name"])
        if not app_name:
            continue

        roadmap.append(
            {
                "app_name": app_name,
                "roadmap_status": _extract_string(row, ["roadmap_status", "status"]),
                "migration_progress": _extract_string(row, ["migration_progress", "progress"]),
                "owner": _extract_string(row, ["ownership", "owner", "team"]),
                "hosting_location": _extract_string(row, ["hosting_location", "hosting", "host_location"]),
            }
        )

    return roadmap


def get_app_for_namespace(namespace: str) -> Optional[Dict[str, Any]]:
    """Lookup application metadata by normalized namespace name."""
    normalized_namespace = _normalize_namespace(namespace)
    apps = load_app_metadata()

    for app in apps:
        for ns_type, ns_name in app["namespaces"].items():
            if ns_name and ns_name == normalized_namespace:
                return {
                    **app,
                    "matched_namespace_type": ns_type,
                }

    return None


def get_migration_for_app(app_name: str) -> Optional[Dict[str, Any]]:
    """Lookup migration roadmap data by application name."""
    if not app_name:
        return None

    normalized_name = str(app_name).strip().lower()
    roadmap = load_migration_data()

    for item in roadmap:
        if item["app_name"].strip().lower() == normalized_name:
            return item

    return None
