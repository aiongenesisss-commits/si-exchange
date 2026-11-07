"""OIDC/JWKS authentication helpers for the simulation-only exchange."""
from __future__ import annotations

import json
import os
from functools import lru_cache

import jwt
from jwt import PyJWKClient


class AuthenticationError(Exception):
    """Raised when a bearer token cannot be verified or mapped to a demo account."""


@lru_cache(maxsize=4)
def _jwks_client(url: str) -> PyJWKClient:
    return PyJWKClient(url, cache_jwk_set=True, lifespan=300, timeout=3)


def verify_access_token(token: str) -> dict:
    """Verify a signed OIDC JWT; never trust unsigned or caller-provided identity fields."""
    jwks_url = os.getenv("AION_OIDC_JWKS_URL", "").strip()
    issuer = os.getenv("AION_OIDC_ISSUER", "").strip()
    audience = os.getenv("AION_OIDC_AUDIENCE", "").strip()
    if not (jwks_url and issuer and audience):
        raise AuthenticationError("OIDC authentication is not configured")
    try:
        signing_key = _jwks_client(jwks_url).get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256", "ES256"],
            issuer=issuer,
            audience=audience,
            options={"require": ["exp", "iat", "sub", "iss", "aud"]},
            leeway=0,
        )
        if not isinstance(claims.get("sub"), str) or not claims["sub"]:
            raise AuthenticationError("Token subject is missing")
        return claims
    except AuthenticationError:
        raise
    except Exception as exc:
        raise AuthenticationError("Bearer token is invalid or expired") from exc


def account_for_subject(subject: str) -> str:
    """Resolve a verified identity through an operator-managed subject-to-demo-account map."""
    raw = os.getenv("AION_DEMO_SUBJECT_ACCOUNT_MAP", "")
    if not raw:
        raise AuthenticationError("Demo account mapping is not configured")
    try:
        mapping = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AuthenticationError("Demo account mapping is invalid") from exc
    account = mapping.get(subject) if isinstance(mapping, dict) else None
    if account not in ("A", "B"):
        raise AuthenticationError("Verified identity has no authorized demo account")
    return account
