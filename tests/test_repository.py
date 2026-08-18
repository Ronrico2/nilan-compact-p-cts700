"""Repository-level consistency tests."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
COMPONENT = ROOT / "custom_components" / "nilan_cts700"


def test_manifests_are_valid_json() -> None:
    manifest = json.loads((COMPONENT / "manifest.json").read_text())
    hacs = json.loads((ROOT / "hacs.json").read_text())

    assert manifest["domain"] == "nilan_cts700"
    assert manifest["version"] == "1.0.3"
    assert hacs["name"] == manifest["name"]


def test_dashboard_is_valid_and_has_no_duplicate_heating_button() -> None:
    dashboard = yaml.safe_load((ROOT / "dashboard" / "nilan_panel.yaml").read_text())

    assert dashboard["type"] == "picture-elements"
    heating = [
        element
        for element in dashboard["elements"]
        if element.get("entity") == "switch.nilan_air9_nilan_centralvarme_drift"
    ]
    assert len(heating) == 1
    assert dashboard["image"].startswith("/nilan_cts700_static/")


def test_every_dashboard_image_exists() -> None:
    dashboard_text = (ROOT / "dashboard" / "nilan_panel.yaml").read_text()
    image_names = {
        token.split("/nilan_cts700_static/", 1)[1].split()[0]
        for token in dashboard_text.splitlines()
        if "/nilan_cts700_static/" in token
    }
    assert image_names
    assert all((COMPONENT / "frontend" / name).is_file() for name in image_names)


def test_hacs_installed_dashboard_matches_repository_example() -> None:
    """The dashboard shipped inside the component must stay in sync."""
    repository_dashboard = ROOT / "dashboard" / "nilan_panel.yaml"
    installed_dashboard = COMPONENT / "dashboard" / "nilan_panel.yaml"

    assert installed_dashboard.read_text() == repository_dashboard.read_text()
