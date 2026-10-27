import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "networks" / "aion_networks.json"
VALIDATOR_PATH = ROOT / "scripts" / "validate_network_registry.py"


def load_registry():
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def run_validator(data, tmp_path):
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_registry_has_two_distinct_planned_networks():
    data = load_registry()
    networks = data["networks"]
    assert [network["name"] for network in networks] == ["AION Nova", "AION Orbit"]
    assert [network["chain_id"] for network in networks] == [71101, 71102]
    assert len({network["chain_id"] for network in networks}) == 2
    assert all(network["status"] == "planned" for network in networks)
    assert data["status"] == "configuration_only"
    for network in networks:
        assert network["local_rpc_url"].startswith("http://127.0.0.1:")
        assert network["public_rpc_url"] is None
        assert network["explorer_url"] is None
        assert network["token_deployed"] is False
        assert network["token_contract_address"] is None


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
    result = run_validator(data, tmp_path)
    assert result.returncode == 1
    assert "duplicate chain ID" in result.stderr


def test_validator_rejects_public_rpc_for_planned_network(tmp_path):
    data = load_registry()
    data["networks"][0]["public_rpc_url"] = "https://rpc.example.invalid"
    result = run_validator(data, tmp_path)
    assert result.returncode == 1
    assert "must not claim public RPC or explorer URLs" in result.stderr


def test_validator_rejects_unverified_token_address(tmp_path):
    data = load_registry()
    data["networks"][1]["token_deployed"] = True
    data["networks"][1]["token_contract_address"] = "0x0000000000000000000000000000000000000001"
    result = run_validator(data, tmp_path)
    assert result.returncode == 1
    assert "must not claim a deployed token" in result.stderr
