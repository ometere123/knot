# Consumer integration pattern

KNOT is intentionally frontend-free and product-agnostic.

A consumer Intelligent Contract can use the `IKnot` interface declared in `contracts/knot.py` and gate an operation on `has_override(commitment_id)`.

A typical flow is:

1. the consumer creates or references a KNOT commitment;
2. normal execution waits for the commitment's declared prerequisite;
3. if a deadlock is proved and this commitment receives the deterministic recovery override, the consumer permits the exact recovery path;
4. all other actions remain blocked by the consumer's own rules.

Consumers should bind a KNOT commitment ID to their own action/resource identifier and must prevent replay on their side. `has_override()` means only that KNOT granted the pre-authorised deadlock escape for that commitment; it is not a general-purpose approval or proof of completion.
