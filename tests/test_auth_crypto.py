"""Cryptographic OIDC verification tests using a local, generated RSA keypair.

No live identity provider or network is required. Middleware mapping tests live in
`test_auth_isolation.py`; these tests exercise the real PyJWT/JWKS verification path.
"""
import time
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

import app.auth as auth


@pytest.fixture
def oidc_keys(monkeypatch):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    unrelated_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    class FakeJWKSClient:
        def get_signing_key_from_jwt(self, token):
            header = jwt.get_unverified_header(token)
            if header.get("kid") != "test-key":
                raise jwt.PyJWKClientError("unknown key id")
            return SimpleNamespace(key=private_key.public_key())

    monkeypatch.setenv("AION_OIDC_JWKS_URL", "https://issuer.example/jwks.json")
    monkeypatch.setenv("AION_OIDC_ISSUER", "https://issuer.example/")
    monkeypatch.setenv("AION_OIDC_AUDIENCE", "si-exchange-demo")
    monkeypatch.setattr(auth, "_jwks_client", lambda _url: FakeJWKSClient())
    return private_key, unrelated_key


def make_token(key, **overrides):
    now = int(time.time())
    claims = {
        "sub": "subject-a",
        "iss": "https://issuer.example/",
        "aud": "si-exchange-demo",
        "iat": now,
        "exp": now + 300,
    }
    claims.update(overrides)
    return jwt.encode(claims, key, algorithm="RS256", headers={"kid": "test-key"})


def test_verify_access_token_accepts_valid_signed_oidc_token(oidc_keys):
    private_key, _ = oidc_keys
    claims = auth.verify_access_token(make_token(private_key))
    assert claims["sub"] == "subject-a"
    assert claims["iss"] == "https://issuer.example/"


def test_verify_access_token_rejects_wrong_signature(oidc_keys):
    _, unrelated_key = oidc_keys
    with pytest.raises(auth.AuthenticationError):
        auth.verify_access_token(make_token(unrelated_key))


@pytest.mark.parametrize(
    "overrides",
    [
        {"iss": "https://attacker.example/"},
        {"aud": "another-application"},
        {"exp": int(time.time()) - 60, "iat": int(time.time()) - 120},
    ],
)
def test_verify_access_token_rejects_wrong_issuer_audience_or_expiry(oidc_keys, overrides):
    private_key, _ = oidc_keys
    with pytest.raises(auth.AuthenticationError):
        auth.verify_access_token(make_token(private_key, **overrides))


def test_verify_access_token_rejects_missing_required_claims(oidc_keys):
    private_key, _ = oidc_keys
    token = jwt.encode(
        {"sub": "subject-a", "iss": "https://issuer.example/", "aud": "si-exchange-demo"},
        private_key,
        algorithm="RS256",
        headers={"kid": "test-key"},
    )
    with pytest.raises(auth.AuthenticationError):
        auth.verify_access_token(token)


def test_verify_access_token_fails_closed_when_oidc_config_missing(monkeypatch):
    for name in ("AION_OIDC_JWKS_URL", "AION_OIDC_ISSUER", "AION_OIDC_AUDIENCE"):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(auth.AuthenticationError, match="not configured"):
        auth.verify_access_token("not-a-token")
