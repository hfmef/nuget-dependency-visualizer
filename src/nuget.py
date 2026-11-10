"""Retrieval of dependency information from the NuGet registration API."""

import json
import gzip
from typing import Any
from urllib.parse import quote
from urllib.request import urlopen

def registration_url(repository: str, package: str) -> str:
    """Находим адрес регистраций NuGet V3."""
    base = repository.rstrip("/")
    if base.endswith("/v3/index.json"):
        resources = request_json(repository).get("resources", [])
        candidates = [
            item for item in resources
            if "RegistrationsBaseUrl" in str(item.get("@type", ""))
        ]
        preferred = next(
            (
                item for item in candidates
                if "SemVer2" in str(item.get("@type", ""))
            ),
            None,
        )
        selected = preferred or (candidates[0] if candidates else None)
        if selected is None:
            raise ValueError("No NuGet registration endpoint in service index.")
        base = selected["@id"].rstrip("/")
    return f"{base}/{quote(package.lower())}/index.json"

def request_json(url: str) -> dict[str, Any]:
    """Получаем JSON по HTTPS, распаковываем gzip."""
    with urlopen(url, timeout=15) as response:
        data = response.read()
        if response.headers.get("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
    return json.loads(data.decode("utf-8"))

def get_direct_dependencies(repository: str, package: str) -> list[str]:
    """Получаем прямые зависимости пакета."""
    data = request_json(registration_url(repository, package))
    entry = latest_catalog_entry(data)
    groups = entry.get("dependencyGroups", [])
    return dependencies_from_groups(groups)

def latest_catalog_entry(data: dict[str, Any]) -> dict[str, Any]:
    """Читаем запись последней версии пакета."""
    items = data.get("items", [])
    if not items:
        raise ValueError("Package registration does not contain versions.")
    page = items[-1]
    leaves = page.get("items")
    if not leaves:
        leaves = request_json(page["@id"]).get("items", [])
    if not leaves:
        raise ValueError("Registration page has no versions.")
    leaf = leaves[-1]
    entry = leaf.get("catalogEntry")
    if isinstance(entry, str):
        entry = request_json(entry)
    if not isinstance(entry, dict):
        raise ValueError("Package registration has an invalid catalog entry.")
    return entry

def dependencies_from_groups(groups: list[dict[str, Any]]) -> list[str]:
    """Собираем уникальные зависимости разных платформ."""
    names: list[str] = []
    for group in groups:
        for dependency in group.get("dependencies", []):
            name = dependency.get("id")
            if isinstance(name, str) and name not in names:
                names.append(name)
    return names

def get_latest_version(repository: str, package: str) -> str:
    """Получаем версию для подписи графа."""
    url = registration_url(repository, package)
    entry = latest_catalog_entry(request_json(url))
    return str(entry.get("version", ""))
