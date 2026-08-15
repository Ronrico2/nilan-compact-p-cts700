"""Test bootstrap without importing Home Assistant's package initializer."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "custom_components" / "nilan_cts700"


def _load(name: str, path: Path) -> None:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)


custom_components = types.ModuleType("custom_components")
custom_components.__path__ = [str(ROOT / "custom_components")]
sys.modules.setdefault("custom_components", custom_components)

nilan_package = types.ModuleType("custom_components.nilan_cts700")
nilan_package.__path__ = [str(PACKAGE)]
sys.modules.setdefault("custom_components.nilan_cts700", nilan_package)

_load("custom_components.nilan_cts700.const", PACKAGE / "const.py")
_load("custom_components.nilan_cts700.api", PACKAGE / "api.py")
