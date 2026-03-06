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
import time

from dotenv import load_dotenv

from utils import get_connection, ping

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
