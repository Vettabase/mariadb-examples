#!/usr/bin/env python3
"""
iot-lkv.py – Periodically ping a list of URLs and store the latest
round-trip time in MariaDB using INSERT … ON DUPLICATE KEY UPDATE so
that only one row per domain is ever kept in the table.

Requirements
------------
    pip install mariadb python-dotenv

Credentials are read from a .env file in the same directory:
    DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
"""

import os
import platform
import re
import subprocess
import time

import mariadb
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

URLS = ["nextcloud.com", "mozilla.org"]
PING_INTERVAL = 5  # seconds between rounds

# ---------------------------------------------------------------------------
# Load credentials from .env
# ---------------------------------------------------------------------------

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def main() -> None:
    conn = get_connection()
    cur = conn.cursor()

    print("Starting ping loop. Press Ctrl-C to stop.")
    try:
        while True:
            for url in URLS:
                duration = ping(url)
                if duration is None:
                    print(f"  {url}: ping failed – skipping insert")
                    continue

                # Keep only the latest duration per URL.
                # The UNIQUE constraint on `url` triggers the UPDATE branch
                # whenever a row for this domain already exists.
                cur.execute(
                    "INSERT INTO ping (url, duration) VALUES (?, ?) "
                    "ON DUPLICATE KEY UPDATE duration = ?",
                    (url, duration, duration),
                )
                print(f"  {url}: {duration:.3f} ms")

            conn.commit()
            time.sleep(PING_INTERVAL)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
