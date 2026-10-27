import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_aion_networks_have_distinct_chain_ids_and_are_not_claimed_live():
    config = json.loads((ROOT / "config" / "aion-networks.json").read_text(encoding="utf-8"))
    networks = config["networks"]
    assert [item["name"] for item in networks] == ["AION Nova", "AION Orbit"]
    assert [item["chain_id"] for item in networks] == [71101, 71102]
    assert len({item["chain_id"] for item in networks}) == len(networks)
    assert config["launch_status"] == "local-development-only"
    assert config["production_deployment_verified"] is False
    for item in networks:
        assert item["public_rpc_url"] is None
        assert item["explorer_url"] is None
        assert item["token_deployed"] is False
        assert item["token_contract_address"] is None


def test_free_deployment_promotion_is_not_advertised_as_available():
    config = json.loads((ROOT / "config" / "aion-networks.json").read_text(encoding="utf-8"))
    promotion = config["free_deployment_promotion"]
    assert promotion["planned_cap"] == 50
    assert promotion["scope"] == "not-yet-decided"
    assert promotion["enabled"] is False
    assert promotion["gas_sponsor_configured"] is False
    assert promotion["public_claim_allowed"] is False


def test_safety_controls_are_fail_closed():
    config = json.loads((ROOT / "config" / "aion-networks.json").read_text(encoding="utf-8"))
    safety = config["safety"]
    assert safety["local_anvil_accounts_are_test_only"] is True
    assert safety["never_expose_local_rpc_ports_to_public_internet"] is True
    assert safety["never_reuse_local_test_keys_for_real_assets"] is True
    assert safety["real_deposits_withdrawals_bridging_and_live_trading_enabled"] is False
