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

# The blocks are deliberately kept below the Modbus limit of 125 registers.
# Reading blocks instead of individual registers reduces load on the CTS700.
REGISTER_BLOCKS: dict[str, tuple[tuple[int, int], ...]] = {
    ROLE_COMPACT: (
        (20100, 81),
        (20260, 39),
        (20340, 1),
        (20460, 63),
        (21770, 22),
        (22490, 2),
    ),
    ROLE_AIR9: (
        (20602, 1),
        (20680, 21),
        (21900, 14),
    ),
}

FAN_OPTIONS = ("Slukket", "Trin 1", "Trin 2", "Trin 3", "Trin 4")
FAN_COMMANDS = {"Trin 1": 101, "Trin 2": 102, "Trin 3": 103, "Trin 4": 104}

UPDATE_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)
