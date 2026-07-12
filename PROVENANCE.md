# Provenance — read this before drawing any conclusion

**The Agent Action Capsule in this repo is self-constructed to conform to the
*format* of the individual Internet-Draft
`draft-mih-scitt-agent-action-capsule-02`. It is NOT produced by the Action
State Group, by Steven Mih, or by any SCITT tooling. It is not a working-group
document. This repo demonstrates permissionless on-chain anchoring of a Capsule
content-address (`capsule_id`) — it is not adoption, endorsement, or
participation by anyone.**

## What is exact and real

- `artifacts/capsule.json` is a well-formed Agent Action Capsule: all REQUIRED
  fields present and typed, registry values used verbatim from the draft's
  Section 12 seeds, and the verdict/effect orthogonality rule satisfied
  (`verdict_class: "denied"` ⇒ `effect_mode: "not_applicable"`,
  `effect.status: "planned"`).
- `capsule_id` is computed **exactly** as the draft defines it (Section 5.1 /
  Section 6 check 2): `HEX(SHA-256(JCS(normalize(envelope minus capsule_id and
  chain))))`, RFC 8785 canonicalization, absent-field normalization. It is
  deterministic and reproducible — `python3 produce.py` yields the same
  `capsule_id` every run.
- `disposition.reason_digest` is a real JSON-DIGEST commitment to
  `artifacts/reason.json`; the verifier recomputes and checks it.
- The on-chain anchor is a real Base mainnet transaction; the tx/block in
  `artifacts/anchor.json` are independently checkable.

## What is deliberately NOT here — declared

- **No SCITT Signed Statement.** The draft carries a Capsule as the payload of a
  COSE_Sign1 Signed Statement registered with a Transparency Service. We compute
  and anchor the **`capsule_id` content-address** (the draft's own identifier);
  we do **not** produce the COSE envelope, a Transparency Service receipt, or an
  inclusion proof. Those require a Transparency Service and are out of scope for
  a content-address anchoring example. Accordingly `assurance.attestation_mode`
  is `self_attested` and `ledger_mode` is `standalone` — no overclaim.
- **No conformance claim against a WG.** This is an individual I-D (versions
  00–02). We say "conformant to the *format* of the draft", never
  "SCITT-compliant" or "WG-conformant".
- **The scenario is synthetic.** A constructed payment-denial, not a record of a
  real agent action.

## What this shows / does not show

- **Shows:** a Capsule content-address, computed per the draft, can be given
  permissionless external finality by anchoring it in a registry the producer
  and any log operator do not control — closing the "whose log?" trust gap
  without a trusted service.
- **Does not show:** that Action State Group / Steven Mih / SCITT integrated,
  endorsed, or participated. If read as adoption, that reading is wrong.
