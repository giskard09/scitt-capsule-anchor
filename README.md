# scitt-capsule-anchor

A worked example that anchors the content-address (`capsule_id`) of an
**Agent Action Capsule** — conformant to the format of the individual
Internet-Draft `draft-mih-scitt-agent-action-capsule-02` — into a permissionless
on-chain registry, giving it **external, operator-independent finality** without
a trusted transparency service.

The timestamp of the anchor is the point. This is not outreach and not a claim
of adoption.

> **Provenance, up front (read `PROVENANCE.md`).** The Capsule here is
> **self-constructed** to conform to the draft's format. It is **NOT** produced
> by the Action State Group, by Steven Mih, or by any SCITT tooling, and it is
> **not** a working-group document. Nothing here — on-chain or in this repo —
> implies that anyone integrated, endorsed, or participated. We compute and
> anchor the Capsule's `capsule_id` content-address; we do not produce a SCITT
> Signed Statement or a Transparency Service receipt. We say "conformant to the
> *format* of the draft", never "SCITT-compliant".

## The seam

The draft records what an agent *did* as a digest-committed Agent Action
Capsule, and registers it as a COSE_Sign1 Signed Statement in a **SCITT
Transparency Service** — a log. That gives strong properties *relative to that
log*: inclusion proofs, an append-only history. But the trust root is the log
operator. The Capsule's content-address (`capsule_id`) and any chain head have
**no permissionless external finality**: to know "this Capsule existed at time
T" you must trust *someone's* Transparency Service. A log operator (or a
producer who controls which log they use) is the anchor of last resort.

Anchoring closes that seam. We take the `capsule_id` — the draft's own
content-address, computed byte-for-byte per Section 5.1 — and place it as a
`bytes32` into a registry on a public chain that no producer or log operator
controls. Now "this Capsule content-address existed at time T" is a fact anyone
can check, with no trusted service in the path.

```
   SCITT Transparency Service                  public chain (Base)
   ┌───────────────────────────┐               ┌────────────────────────┐
   │ Signed Statements in a log │  capsule_id   │ AnchorRegistry         │
   │  finality relative to      │ ─────────────▶│  anchor(bytes32)       │
   │  *that log operator*       │ content-addr  │  Anchored(ref,by,time) │
   └───────────────────────────┘               └────────────────────────┘
       "whose log?" trust gap                    operator-independent
                                                 timestamp / finality
```

## Format-agnostic anchoring (the generality)

We anchor the digest **as-is**. We ask for no schema change and adopt none of
our own formats into the Capsule. Because the mechanism operates on any 32-byte
content-address, the same anchor applies unchanged to any digest-committed
identifier in this draft family — for example the subject digests used by the
adjacent drafts `agent-accountability-composition` and
`agent-bilateral-attestation`. Those are **not built here**; this repo anchors
one concrete Capsule to make the mechanism checkable. The generality is a
property of anchoring a digest, not of any one format.

## The Capsule (a restraint receipt)

`artifacts/capsule.json` records a refusal: an agent acting for a treasury
tenant was asked to send a payment; a policy gate **denied** it before dispatch
because the amount exceeded a spend ceiling.

- `disposition.verdict_class: "denied"` — refused before dispatch.
- `effect.status: "planned"`, `assurance.effect_mode: "not_applicable"` — nothing
  was dispatched (the draft's verdict/effect orthogonality rule, Section 5.5.2).
- `disposition.reason_digest` commits to `artifacts/reason.json` (the private,
  machine-readable reason) by digest only.

This is the "auditor-grade evidence that the gate worked" case: the affirmative,
digest-committed record that the agent *did not* act.

## Reproduce & verify

```bash
python3 produce.py            # build the Capsule, compute capsule_id (deterministic)
python3 verifier/verify.py    # recompute capsule_id + reason_digest, confirm the on-chain anchor
```

`artifacts/capsule.canonical` is the exact RFC 8785 JCS byte string the
`capsule_id` is computed over, for full transparency.

## The anchor

- **Registry:** `0x49fEcA52bC634a9Ab773226D16619deC547794aa` (same CREATE2
  address on Base 8453, Arbitrum One 42161, Ink 57073).
- **Function:** `anchor(bytes32 ref)` — permissionless, no owner/roles/funds.
- **Event:** `Anchored(bytes32 indexed ref, address indexed anchoredBy, uint256 timestamp)`.
- The anchored `ref` (the `capsule_id`) and its tx/block are in
  `artifacts/anchor.json`.

## License

MIT.
