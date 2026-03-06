#!/usr/bin/env python3
"""
utils.py – Shared utilities for iot-lkv.py.

Provides:
    ping(url)        – ICMP-ping a host and return the RTT in ms, or None.
    get_connection() – Return an authenticated MariaDB connection.
"""

import os
import platform
import re
import subprocess

import mariadb


def ping(url: str) -> float | None:
    """Return the round-trip time in milliseconds, or None on failure."""
    is_windows = platform.system().lower() == "windows"
    count_flag = "-n" if is_windows else "-c"

    try:
        result = subprocess.run(
            ["ping", count_flag, "1", url],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None

    if result.returncode != 0:
        return None

    # Linux / macOS:  "time=12.3 ms"  or  "time=12.3ms"
    # Windows:        "time=12ms"      or  "time<1ms"
    match = re.search(r"time[<=](\d+(?:\.\d+)?)\s*ms", result.stdout)
    if match:
        return float(match.group(1))

    return None


def get_connection() -> mariadb.Connection:
    missing = [v for v in ("DB_USER", "DB_PASSWORD", "DB_NAME") if not os.getenv(v)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variable(s): {', '.join(missing)}. "
            "Copy .env.template to .env and fill in the values."
        )
    try:
        return mariadb.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
    except mariadb.Error as e:
        raise RuntimeError(f"Could not connect to MariaDB: {e}") from e
