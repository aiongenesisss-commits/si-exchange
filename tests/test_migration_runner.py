import os
import subprocess
import sys
from pathlib import Path


def test_migration_runner_refuses_to_run_without_database_url():
    env = os.environ.copy()
    env.pop("DATABASE_URL", None)
    result = subprocess.run(
        [sys.executable, "scripts/migrate.py"],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 2
    assert "DATABASE_URL is required" in result.stderr
    assert "no database was changed" in result.stderr


def test_initial_migration_file_is_present_and_simulation_only():
    sql = Path("migrations/001_initial_schema.sql").read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS demo_orders" in sql
    assert "CREATE TABLE IF NOT EXISTS demo_fills" in sql
    assert "account_type = 'demo'" in sql
    assert "wallet" not in sql.lower()
