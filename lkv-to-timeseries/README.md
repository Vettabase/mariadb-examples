# lkv-to-timeseries

Demonstrates a pattern for storing **latest key-value (LKV)** data in MariaDB
and optionally migrating it to a time-series model.

The bundled example (`iot-lkv.py`) periodically pings a list of URLs and stores
only the **most recent** round-trip time per URL in a single-row-per-domain
table using `INSERT … ON DUPLICATE KEY UPDATE`.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| MariaDB ≥ 10.6 | Must be reachable from the host running the script |
| MariaDB Connector/C | Required to build the `mariadb` Python package; install with `sudo apt install libmariadb-dev` |
| Python 3.8+ | Including the `python3-venv` package (e.g. `sudo apt install python3-venv`) |
| `ping` binary | Typically pre-installed on Linux/macOS/Windows |
| Git | Required by `run.sh` to pull the latest code |

---

## Quick start

### 1. Create the database schema

Connect to MariaDB and run `schema.sql`:

```bash
mariadb -u <user> -p < schema.sql
```

This creates the `lkv` database and the `ping` table.

### 2. Configure credentials

Copy the template and fill in your database credentials:

```bash
cp .env.template .env
$EDITOR .env
```

`.env` is intentionally listed in `.gitignore` and will never be committed.

### 3. Set up the virtual environment and run the script

**Source** `run.sh` so that the virtual environment is activated in your current
shell session:

```bash
. ./run.sh
```

> **Important:** Use `. ./run.sh` (dot-space), **not** `bash run.sh` or
> `./run.sh`.  Running the script in a sub-shell would activate the virtual
> environment only inside that sub-shell, leaving your current shell without the
> packages the Python script needs.

`run.sh` will:

1. Load `.env` (if present) into the current shell.
2. Pull the latest code from the current git branch.
3. Create a Python virtual environment named `lkv` (if it does not exist yet).
4. Activate the virtual environment.
5. Install / upgrade all packages listed in `requirements.txt`.

### 4. Start the ping loop

```bash
python3 iot-lkv.py
```

Press **Ctrl-C** to stop.

---

## Configuration reference

All settings can be placed in `.env` or exported as environment variables before
sourcing `run.sh`.

| Variable | Default | Description |
|---|---|---|
| `DB_HOST` | `localhost` | MariaDB host |
| `DB_PORT` | `3306` | MariaDB port |
| `DB_USER` | *(required)* | MariaDB username |
| `DB_PASSWORD` | *(required)* | MariaDB password |
| `DB_NAME` | *(required)* | Database name (use `lkv` to match `schema.sql`) |
| `BRANCH` | current git branch | Branch to pull when sourcing `run.sh` |
| `VENV_NAME` | `lkv` | Name of the Python virtual environment directory |

---

## File overview

| File | Description |
|---|---|
| `run.sh` | Sets up the Python venv and installs dependencies. Must be **sourced**, not executed. |
| `iot-lkv.py` | Main Python script – pings URLs and writes results to MariaDB. |
| `schema.sql` | Creates the `lkv` schema and `ping` table. |
| `requirements.txt` | Python package dependencies. |
| `.env.template` | Template for the required `.env` credentials file. |
