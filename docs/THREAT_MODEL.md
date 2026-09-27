# KNOT threat model

## Assets and guarantees

KNOT protects one narrow guarantee: a deadlock certificate and any recovery override must not depend on an unverified leader assertion about semantic dependency.

## Threats handled

### Malicious leader fabricates dependency verdicts

Validators independently re-run the bounded dependency judgement. A forged or malformed vector is rejected.

### Ambiguous natural language is forced into an edge

`AMBIGUOUS` is a first-class terminal judgement for an edge. Any ambiguous edge prevents certification.

### Prompt injection inside commitment text

Commitment fields are serialized as untrusted JSON data inside a fixed security prompt. The model is explicitly instructed never to follow instructions contained inside those fields. No web browsing or tool execution is performed by the dependency judge.

### Caller submits duplicate IDs to fake a cycle

Cycle IDs must be unique and between 2 and 8 elements.

### Caller mixes commitments from different groups

Every commitment in the cycle must belong to the sealed target group.

### Caller proves a cycle using already-resolved commitments

Every waiter and provider must still be `ACTIVE` before consensus runs.

### Leader returns malformed JSON or wrong cardinality

Parsing fails closed. No certificate can be written.

### Recovery selection is manipulated by the model

The model never sees or selects recovery policy. Lowest-break-cost recovery is deterministic and tie-breaks by commitment ID.

### Repeated proof repeatedly releases commitments

Once a commitment receives an override, it is no longer active and cannot participate in a later proof as the same active edge.

### Unrelated caller consumes open membership slots

Only the group creator can add commitments. The actor is an explicit commitment field, so the creator can register the intended participant without granting arbitrary wallets permission to consume the bounded slots.

### Duplicate cycle certificate inflation

The contract indexes every rotation of a certified cycle by group and ordered commitment IDs. A repeated equivalent submission is rejected before another certificate or cycle-count increment is created, including CERTIFY_ONLY cycles.

## Deliberate non-goals

KNOT does not prove that:

- a commitment is legally binding;
- an actor will actually perform after receiving an override;
- no external party could satisfy a prerequisite;
- every possible deadlock in a group has been discovered;
- natural-language descriptions are truthful statements about the world.

KNOT proves a narrower statement: within the frozen declarations supplied by the commitments in a submitted cycle, validators agree that each provider output materially satisfies the next waiter's stated prerequisite, closing the wait-for loop.

## Integration assumption

Recovery has effect only for systems that choose to respect KNOT state. The contract cannot reverse or force arbitrary off-chain actions.
