"""
JSON-DIGEST as defined by draft-mih-scitt-agent-action-capsule-02, Section 2:

    JSON-DIGEST(v) = HEX( SHA-256( JCS( normalize(v) ) ) )

  - normalize: remove members whose value is null, an empty array, or an empty
    object, bottom-up.
  - JCS: RFC 8785 JSON Canonicalization Scheme.
  - lowercase hex of the SHA-256.

Stdlib only. This profile forbids floating-point in digest-bearing fields
(monetary/quantity values are exact decimal strings), so every value we digest
is a str, bool, int, dict, or list. For that value subset with ASCII keys and
ASCII string content, `json.dumps(sort_keys=True, separators=(',',':'),
ensure_ascii=False)` is byte-identical to RFC 8785 JCS. The guards below make
that precondition explicit and fail loudly if it is ever violated.
"""
import hashlib
import json


def normalize(v):
    """Absent-field normalization (bottom-up): drop null / [] / {} members."""
    if isinstance(v, dict):
        out = {}
        for k, val in v.items():
            nv = normalize(val)
            if nv is None or nv == [] or nv == {}:
                continue
            out[k] = nv
        return out
    if isinstance(v, list):
        return [normalize(x) for x in v]
    return v


def _guard(v):
    """Reject the value shapes that would break json.dumps == JCS equivalence."""
    if isinstance(v, float):
        raise ValueError("floating-point value in a digest-bearing field (forbidden by the profile)")
    if isinstance(v, bool):
        return
    if isinstance(v, str):
        if not v.isascii():
            raise ValueError(f"non-ASCII string {v!r}: use a real RFC 8785 library for this input")
        return
    if isinstance(v, dict):
        for k, val in v.items():
            if not isinstance(k, str) or not k.isascii():
                raise ValueError("non-ASCII object key")
            _guard(val)
    elif isinstance(v, list):
        for x in v:
            _guard(x)


def jcs(v: dict) -> bytes:
    """RFC 8785 canonical bytes for the guarded value subset."""
    _guard(v)
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def json_digest(v) -> str:
    """HEX(SHA-256(JCS(normalize(v)))) — the profile's single digest construction."""
    return hashlib.sha256(jcs(normalize(v))).hexdigest()
