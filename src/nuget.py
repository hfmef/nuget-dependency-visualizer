"""Retrieval of dependency information from the NuGet registration API."""

import json
import gzip
from typing import Any
from urllib.parse import quote
from urllib.request import urlopen


# Находим адрес NuGet API для сведений о пакете.
def registration_url(repository: str, package: str) -> str:
    """Resolve the registration endpoint from a NuGet V3 service index."""
    base = repository.rstrip("/")
    if base.endswith("/v3/index.json"):
        resources = request_json(repository).get("resources", [])
        candidates = [
            item for item in resources
            if "RegistrationsBaseUrl" in str(item.get("@type", ""))
        ]
        preferred = next(
            (item for item in candidates if "SemVer2" in str(item.get("@type", ""))),
            None,
        )
        selected = preferred or (candidates[0] if candidates else None)
        if selected is None:
            raise ValueError("No NuGet registration endpoint in service index.")
        base = selected["@id"].rstrip("/")
    return f"{base}/{quote(package.lower())}/index.json"


# Загружаем JSON по HTTPS и при необходимости распаковываем gzip.
def request_json(url: str) -> dict[str, Any]:
    """Download and decode a JSON document using the standard library."""
    with urlopen(url, timeout=15) as response:
        data = response.read()
        if response.headers.get("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
    return json.loads(data.decode("utf-8"))


# Получаем прямые зависимости выбранного пакета.
def get_direct_dependencies(repository: str, package: str) -> list[str]:
    """Return direct dependency names of the latest package registration."""
    data = request_json(registration_url(repository, package))
    entry = latest_catalog_entry(data)
    groups = entry.get("dependencyGroups", [])
    return dependencies_from_groups(groups)


# Выбираем запись версии из каталога NuGet.
def latest_catalog_entry(data: dict[str, Any]) -> dict[str, Any]:
    """Extract the catalog entry from the newest registration leaf."""
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


# Собираем имена зависимостей из групп платформ без повторов.
def dependencies_from_groups(groups: list[dict[str, Any]]) -> list[str]:
    """Collect unique dependency names from all target-framework groups."""
    names: list[str] = []
    for group in groups:
        for dependency in group.get("dependencies", []):
            name = dependency.get("id")
            if isinstance(name, str) and name not in names:
                names.append(name)
    return names


# Получаем номер версии для подписи блока на графе.
def get_latest_version(repository: str, package: str) -> str:
    """Return the latest registration version for a package."""
    entry = latest_catalog_entry(request_json(registration_url(repository, package)))
    return str(entry.get("version", ""))
