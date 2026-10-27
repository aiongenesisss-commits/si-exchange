import json

from scripts import testnet_order_lifecycle


def test_order_lifecycle_does_not_submit_by_default(monkeypatch, capsys):
    monkeypatch.delenv("ALLOW_TESTNET_ORDER", raising=False)

    class MustNotConnect:
        def __init__(self):
            raise AssertionError("adapter must not initialize unless explicit opt-in is set")

    monkeypatch.setattr(testnet_order_lifecycle, "BinanceSpotTestnetAdapter", MustNotConnect)
    assert testnet_order_lifecycle.main() == 0
    output = json.loads(capsys.readouterr().out)
    assert output["submitted"] is False


def test_order_lifecycle_requires_explicit_true(monkeypatch, capsys):
    monkeypatch.setenv("ALLOW_TESTNET_ORDER", "false")

    class MustNotConnect:
        def __init__(self):
            raise AssertionError("adapter must not initialize when opt-in is false")

    monkeypatch.setattr(testnet_order_lifecycle, "BinanceSpotTestnetAdapter", MustNotConnect)
    assert testnet_order_lifecycle.main() == 0
    output = json.loads(capsys.readouterr().out)
    assert output["submitted"] is False
