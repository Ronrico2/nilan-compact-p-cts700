"""Repository-level consistency tests."""

from __future__ import annotations

import json
import zlib
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
COMPONENT = ROOT / "custom_components" / "nilan_cts700"


def test_manifests_are_valid_json() -> None:
    manifest = json.loads((COMPONENT / "manifest.json").read_text())
    hacs = json.loads((ROOT / "hacs.json").read_text())

    assert manifest["domain"] == "nilan_cts700"
    assert manifest["version"] == "1.0.5"
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


def _assert_valid_png(path: Path) -> None:
    """Validate the complete PNG chunk stream without external dependencies."""
    data = path.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n"), f"Invalid PNG signature: {path.name}"

    offset = 8
    saw_iend = False
    while offset < len(data):
        assert offset + 12 <= len(data), f"Truncated PNG chunk header: {path.name}"
        length = int.from_bytes(data[offset : offset + 4], "big")
        chunk_type = data[offset + 4 : offset + 8]
        chunk_end = offset + 12 + length
        assert chunk_end <= len(data), f"Truncated PNG chunk data: {path.name}"

        chunk_data = data[offset + 8 : offset + 8 + length]
        expected_crc = int.from_bytes(data[offset + 8 + length : chunk_end], "big")
        actual_crc = zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF
        assert actual_crc == expected_crc, f"Invalid PNG CRC: {path.name}"

        offset = chunk_end
        if chunk_type == b"IEND":
            assert length == 0, f"Invalid PNG IEND chunk: {path.name}"
            saw_iend = True
            break

    assert saw_iend, f"Missing PNG IEND chunk: {path.name}"
    assert offset == len(data), f"Unexpected data after PNG IEND: {path.name}"


def test_all_frontend_png_files_are_complete() -> None:
    """A truncated background must never be included in a HACS release."""
    images = sorted((COMPONENT / "frontend").glob("*.png"))
    assert images
    for image in images:
        _assert_valid_png(image)


def test_hacs_installed_dashboard_matches_repository_example() -> None:
    """The dashboard shipped inside the component must stay in sync."""
    repository_dashboard = ROOT / "dashboard" / "nilan_panel.yaml"
    installed_dashboard = COMPONENT / "dashboard" / "nilan_panel.yaml"

    assert installed_dashboard.read_text() == repository_dashboard.read_text()
