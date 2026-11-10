"""Retrieval of dependency information from the NuGet registration API."""

import json
import gzip
from typing import Any
from urllib.parse import quote
from urllib.request import urlopen


def registration_url(repository: str, package: str) -> str:
    """Build the URL of a NuGet registration index."""
    return f"{repository.rstrip('/')}/{quote(package.lower())}/index.json"


def request_json(url: str) -> dict[str, Any]:
    """Download and decode a JSON document using the standard library."""
    with urlopen(url, timeout=15) as response:
        data = response.read()
        if response.headers.get("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
    return json.loads(data.decode("utf-8"))


def get_direct_dependencies(repository: str, package: str) -> list[str]:
    """Return direct dependency names of the latest package registration."""
    data = request_json(registration_url(repository, package))
    entry = latest_catalog_entry(data)
    groups = entry.get("dependencyGroups", [])
    return dependencies_from_groups(groups)


def latest_catalog_entry(data: dict[str, Any]) -> dict[str, Any]:
    """Extract the catalog entry from the newest registration leaf."""
    items = data.get("items", [])
    if not items:
        raise ValueError("Package registration does not contain versions.")
    leaf = items[-1].get("items", [])[-1]
    entry = leaf.get("catalogEntry")
    if not isinstance(entry, dict):
        raise ValueError("Package registration has an invalid catalog entry.")
    return entry


def dependencies_from_groups(groups: list[dict[str, Any]]) -> list[str]:
    """Collect unique dependency names from all target-framework groups."""
    names: list[str] = []
    for group in groups:
        for dependency in group.get("dependencies", []):
            name = dependency.get("id")
            if isinstance(name, str) and name not in names:
                names.append(name)
    return names
