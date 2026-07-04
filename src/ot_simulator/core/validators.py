"""Field validators for OT data."""

import ipaddress
import re

_PROTO_RE = re.compile(r"^[A-Za-z0-9_\-]+(:\d{1,5})?$")


def validate_ip(value: str) -> str:
    """Validate and normalize an IPv4/IPv6 address.

    Raises ValueError if invalid.
    """
    value = str(value).strip()
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        raise ValueError(f"invalid IP address: {value!r}")
    return str(ip)


def validate_port(value) -> int:
    """Validate a TCP/UDP port (1-65535)."""
    try:
        port = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"port must be an integer: {value!r}")
    if not 1 <= port <= 65535:
        raise ValueError(f"port out of range (1-65535): {port}")
    return port


def validate_protocol(value: str) -> str:
    """Validate a protocol token like 'S7:102' or 'Modbus:502'."""
    value = str(value).strip()
    if not _PROTO_RE.match(value):
        raise ValueError(f"invalid protocol format: {value!r}")
    return value
