"""Constants for the Nilan CTS700 integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "nilan_cts700"
NAME = "Nilan CTS700 Compact P + AIR9"

CONF_COMPACT_SLAVE = "compact_slave"
CONF_AIR9_SLAVE = "air9_slave"
CONF_USE_AIR9 = "use_air9"
CONF_MESSAGE_WAIT = "message_wait_milliseconds"

DEFAULT_PORT = 502
DEFAULT_COMPACT_SLAVE = 1
DEFAULT_AIR9_SLAVE = 4
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_MESSAGE_WAIT = 50
DEFAULT_TIMEOUT = 5

MIN_SCAN_INTERVAL = 10
MAX_SCAN_INTERVAL = 300

ROLE_COMPACT = "compact"
ROLE_AIR9 = "air9"

PLATFORMS = (
    "binary_sensor",
    "button",
    "climate",
    "number",
    "select",
    "sensor",
    "switch",
)

# Only documented, actually used registers are grouped together. Some CTS700
# firmware rejects a whole Modbus request when the requested range crosses an
# unsupported register, even when the requested start and end are valid.
REGISTER_BLOCKS: dict[str, tuple[tuple[int, int], ...]] = {
    ROLE_COMPACT: (
        (20100, 1),
        (20102, 2),
        (20106, 2),
        (20120, 1),
        (20140, 8),
        (20164, 1),
        (20180, 1),
        (20260, 2),
        (20282, 1),
        (20284, 1),
        (20286, 1),
        (20288, 1),
        (20290, 1),
        (20292, 1),
        (20294, 1),
        (20296, 1),
        (20298, 1),
        (20340, 1),
        (20460, 1),
        (20462, 1),
        (20464, 1),
        (20520, 1),
        (20522, 1),
        (21770, 7),
        (21778, 1),
        (21780, 2),
        (21788, 1),
        (21791, 1),
        (22490, 1),
    ),
    ROLE_AIR9: (
        (20602, 1),
        (20680, 1),
        (20684, 1),
        (20686, 1),
        (20688, 1),
        (20690, 1),
        (20700, 1),
        (21900, 6),
        (21913, 1),
    ),
}

FAN_OPTIONS = ("Slukket", "Trin 1", "Trin 2", "Trin 3", "Trin 4")
FAN_COMMANDS = {"Trin 1": 101, "Trin 2": 102, "Trin 3": 103, "Trin 4": 104}

UPDATE_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)
