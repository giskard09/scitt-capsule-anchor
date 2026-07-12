#!/usr/bin/env python3
"""
Independent verifier for scitt-capsule-anchor. Trusts nothing we assert:

  1. recomputes capsule_id from the Capsule's own bytes, exactly as
     draft-mih-scitt-agent-action-capsule-02 defines it (Section 6 check 2:
     "recompute capsule_id over the canonical capsule form and compare"),
  2. recomputes disposition.reason_digest from the disclosed reason object,
  3. queries Base mainnet for the AnchorRegistry `Anchored` event whose indexed
     `ref` equals that recomputed capsule_id,
  4. PASSES only if all three hold.

Stdlib only (hashlib + urllib + json). The block hint in anchor.json only says
where to look; the cryptographic bind (recomputed capsule_id == on-chain ref) is
the proof.

Usage: python3 verify.py [--rpc URL]
"""
import argparse
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from capsule_jcs import json_digest  # noqa: E402

ANCHOR_REGISTRY = "0x49fEcA52bC634a9Ab773226D16619deC547794aa"
# keccak256("Anchored(bytes32,address,uint256)")
ANCHORED_TOPIC0 = "0xfe2289542f7a0110ac112c3a4d712afdcaaf2900a1326f4e6f340b563a0e8734"
DEFAULT_RPC = "https://mainnet.base.org"

# fields excluded from capsule_id per spec Section 5.1
EXCLUDED = {"capsule_id", "chain"}


def rpc(url, method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json", "User-Agent": "scitt-capsule-anchor-verifier/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.loads(r.read())
    if "error" in out:
        raise RuntimeError(f"RPC {method} error: {out['error']}")
    return out["result"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rpc", default=os.environ.get("BASE_RPC", DEFAULT_RPC))
    args = ap.parse_args()
    art = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "artifacts"))

    capsule = json.load(open(os.path.join(art, "capsule.json")))
    reason = json.load(open(os.path.join(art, "reason.json")))
    stated_id = capsule["capsule_id"]

    # 1. Identity: recompute capsule_id over the canonical capsule form.
    canonical = {k: v for k, v in capsule.items() if k not in EXCLUDED}
    recomputed = json_digest(canonical)
    print(f"stated  capsule_id : {stated_id}")
    print(f"recomputed         : {recomputed}")
    if recomputed != stated_id:
        print("\nFAIL: capsule_id does not match the canonical capsule form")
        sys.exit(1)
    print("  capsule_id identity: OK")

    # 2. reason_digest commitment.
    rd = json_digest(reason)
    if rd != capsule["disposition"].get("reason_digest"):
        print("\nFAIL: reason_digest does not commit to reason.json")
        sys.exit(1)
    print(f"  reason_digest bind : OK ({rd})")

    # 3. on-chain anchor of exactly this capsule_id.
    anchor = json.load(open(os.path.join(art, "anchor.json")))
    hint = int(anchor["block"])
    head = int(rpc(args.rpc, "eth_blockNumber", []), 16)
    ref = "0x" + recomputed
    logs = rpc(args.rpc, "eth_getLogs", [{
        "address": ANCHOR_REGISTRY,
        "fromBlock": hex(max(0, hint - 25)),
        "toBlock": hex(min(hint + 25, head)),
        "topics": [ANCHORED_TOPIC0, ref],
    }])
    if not logs:
        print(f"\nFAIL: no Anchored event for {ref} on AnchorRegistry near block {hint}")
        sys.exit(1)
    log = logs[0]
    print(f"\non-chain match     : AnchorRegistry {ANCHOR_REGISTRY} (Base 8453)")
    print(f"  tx               : {log['transactionHash']}")
    print(f"  block            : {int(log['blockNumber'], 16)}")
    print(f"  block timestamp  : {int(log['data'], 16)}")
    print("\nPASS: the recomputed capsule_id is anchored on-chain, and the capsule")
    print("      is self-consistent (identity + reason_digest).")


if __name__ == "__main__":
    main()
