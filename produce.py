#!/usr/bin/env python3
"""
Build an Agent Action Capsule conformant to
draft-mih-scitt-agent-action-capsule-02, compute its capsule_id exactly as the
spec defines (Section 5.1 / Section 6 check 2), and emit the digest that gets
anchored on-chain.

PROVENANCE / HONESTY: this Capsule is self-constructed to conform to the format
of the individual Internet-Draft draft-mih-scitt-agent-action-capsule-02. It is
NOT produced by the Action State Group, by Steven Mih, or by any SCITT tooling,
and it is not a WG document. It demonstrates permissionless anchoring of a
capsule content-address, not adoption or endorsement. See PROVENANCE.md.

Scenario (a restraint receipt): an agent acting for a treasury tenant asked to
send a payment; a policy gate DENIED it before dispatch because the amount
exceeded a spend ceiling. verdict_class "denied" => never dispatched =>
effect_mode "not_applicable", effect.status "planned" (spec Section 5.5.2).
"""
import json
import os

from capsule_jcs import json_digest

OUT = os.path.join(os.path.dirname(__file__), "artifacts")
SPEC = "draft-mih-scitt-agent-action-capsule-02"


def main():
    os.makedirs(OUT, exist_ok=True)

    # --- the private, machine-readable reason the gate refused -------------
    # disposition.reason_digest commits to this by digest only (Section 5.5).
    # Members are namespaced per Section 9.1 (producer-local constraint id).
    reason = {
        "constraint_id": "com.rama.spend_ceiling",
        "currency": "USD",
        "threshold": "1000.00",   # exact decimal string, never a JSON float (Section 5.1)
        "observed": "4200.00",
    }
    reason_digest = json_digest(reason)

    # --- the Capsule envelope (Section 5), minus capsule_id ----------------
    # capsule_id is the JSON-DIGEST of exactly this object (after normalization),
    # with capsule_id and chain-linkage fields excluded (Section 5.1). This
    # Capsule is standalone (no chain block), so only capsule_id is excluded.
    capsule = {
        "spec_version": SPEC,
        "format_version": "2",
        "action_id": "act-2026-07-12-0007",
        "action_type": "decide",
        "operator": "tenant:acme-treasury",
        "developer": "agent:rama-payments-bot@1.4.2",
        "timestamp": "2026-07-12T18:30:00Z",
        "disposition": {
            "decision": "reject",              # registry: accept|reject|needs_input|deferred
            "approver": "policy",              # closed enum: human|policy
            "human_disposed": False,           # true only if a human acted
            "verdict_class": "denied",         # registry: refused before dispatch
            "reason_digest": reason_digest,
        },
        "effect": {
            "status": "planned",               # not dispatched => no request/response digest
            "type": "send_payment",            # registry: write_order|send_payment
            "irreversibility_class": "one_way_consequential",
        },
        "assurance": {
            "attestation_mode": "self_attested",
            "effect_mode": "not_applicable",   # required for a never-dispatch verdict_class
            "ledger_mode": "standalone",       # lone Capsule, no chain linkage
        },
    }

    # --- content-address: capsule_id = JSON-DIGEST(capsule without capsule_id)
    capsule_id = json_digest(capsule)
    sealed = dict(capsule)
    sealed["capsule_id"] = capsule_id

    # --- emit artifacts -----------------------------------------------------
    def w(name, data, raw=False):
        p = os.path.join(OUT, name)
        with open(p, "wb" if raw else "w") as f:
            f.write(data if raw else json.dumps(data, indent=2) + "\n")

    w("capsule.json", sealed)
    w("reason.json", reason)
    # the exact canonical bytes the capsule_id is computed over (transparency):
    from capsule_jcs import jcs, normalize
    w("capsule.canonical", jcs(normalize(capsule)), raw=True)

    manifest = {
        "description": "Agent Action Capsule (verdict_class=denied) — worked example for permissionless anchoring of a capsule content-address.",
        "provenance": ("Self-constructed to conform to the format of the individual "
                       "Internet-Draft " + SPEC + ". NOT produced by Action State Group, "
                       "Steven Mih, or SCITT tooling. Not a WG document. Demonstrates "
                       "permissionless anchoring of a capsule content-address, not adoption."),
        "spec": SPEC,
        "capsule_id": capsule_id,
        "reason_digest": reason_digest,
        "anchor_ref_bytes32": "0x" + capsule_id,
        "anchor_registry": "0x49fEcA52bC634a9Ab773226D16619deC547794aa",
        "anchor_chain": "Base mainnet (chainId 8453)",
        "digest_construction": "capsule_id = HEX(SHA-256(JCS(normalize(envelope minus capsule_id and chain)))) per spec Section 5.1",
    }
    w("manifest.json", manifest)

    print("=== scitt-capsule-anchor : producer ===")
    print(f"spec           : {SPEC}")
    print(f"reason_digest  : {reason_digest}")
    print(f"capsule_id     : {capsule_id}")
    print(f"CHAIN/ANCHOR   : 0x{capsule_id}")
    print(f"artifacts ->   : {OUT}/")


if __name__ == "__main__":
    main()
