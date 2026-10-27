import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "networks" / "aion_networks.json"
VALIDATOR_PATH = ROOT / "scripts" / "validate_network_registry.py"


def load_registry():
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def test_registry_has_two_distinct_planned_networks():
    data = load_registry()
    networks = data["networks"]
    assert [network["name"] for network in networks] == ["AION Nova", "AION Orbit"]
    assert [network["chain_id"] for network in networks] == [71101, 71102]
    assert len({network["chain_id"] for network in networks}) == 2
    assert all(network["status"] == "planned" for network in networks)
    assert data["status"] == "configuration_only"


def test_free_deployment_offer_is_not_enabled_without_sponsor():
    free = load_registry()["free_deployments"]
    assert free["limit_per_network"] == 50
    assert free["status"] == "not_enabled"
    assert free["requires_sponsored_gas"] is True
    assert free["requires_rate_limits"] is True
    assert free["requires_auditable_counter"] is True


def test_registry_validator_passes():
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "remain planned, not live" in result.stdout


def test_validator_rejects_duplicate_chain_ids(tmp_path):
    data = load_registry()
    data["networks"][1]["chain_id"] = data["networks"][0]["chain_id"]
    bad_path = tmp_path / "bad_registry.json"
    bad_path.write_text(json.dumps(data), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), str(bad_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "duplicate chain ID" in result.stderr
