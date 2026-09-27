# KNOT submission notes

## Contribution type

**Intelligent Contracts** — standalone reusable GenLayer primitive. No frontend.

## One-line description

KNOT detects semantic wait-for cycles among independently authored commitments and can apply a pre-authorised deterministic recovery rule after GenLayer validators independently verify every edge in the cycle.

## The problem

Conventional deadlock detection assumes dependencies are already machine-readable. In autonomous systems, commitments are increasingly described in natural language. Individually valid commitments can therefore compose into a liveness failure that an ordinary deterministic smart contract cannot recognise.

Example:

```text
A waits for B's payment confirmation.
B waits for C's delivery verification.
C waits for A's design release.
```

KNOT makes this wait-for cycle a consensus-backed piece of shared state.

## How GenLayer is used

The submitter proposes an ordered cycle of active commitments. For every edge, the waiter has a frozen natural-language prerequisite and the provider has a frozen natural-language output. Positive dependency edges are persisted and reused by later proofs against the same immutable sealed commitment text.

The leader classifies each edge as exactly one of:

- `REQUIRES`
- `DOES_NOT_REQUIRE`
- `AMBIGUOUS`

Validators independently re-run the same bounded dependency judgement. The proposal is acceptable only if the validator obtains a valid vector agreeing with the leader. Any parser failure or ambiguity fails closed.

A deadlock certificate is stored only if **all** cycle edges are `REQUIRES`.

## What is deterministic

The model does not:

- choose cycle membership;
- choose a recovery target;
- choose break cost;
- edit commitment text;
- turn ambiguity into an edge;
- directly mutate recovery state.

Group membership, active-state checks, uniqueness, cycle closure and recovery are deterministic.

With `LOWEST_BREAK_COST`, KNOT selects the breakable cycle member with the lowest predeclared cost, tie-breaking by commitment ID.

## Why the primitive is reusable

KNOT has no business-domain assumptions. Commitments can represent agent jobs, payment dependencies, release gates, multi-party workflows, service hand-offs or other systems where one obligation waits on a condition another obligation promises to create.

Downstream contracts can read `has_override(commitment_id)` and bind that exact recovery permission to their own action.

## Security properties

- commitment text is treated as untrusted data in the LLM prompt;
- validators independently re-derive the entire proposed edge vector;
- malformed or ambiguous analysis cannot certify a cycle;
- cycle IDs must be unique;
- all commitments must belong to one sealed group;
- resolved commitments cannot be used in a new deadlock proof;
- recovery selection is deterministic;
- an override is monotonic and permanently linked to its cycle certificate.

## Bounded claim

KNOT does not claim to discover all dependencies or all deadlocks. It verifies a caller-proposed deadlock certificate against frozen declarations. This avoids relying on a leader to provide a complete dependency graph.

## Tests supplied

Direct-mode tests cover lifecycle, authorization, valid and invalid cycles, ambiguity, malformed outputs, deterministic recovery and forged leader vectors.

A live Studionet integration scenario is supplied which:

1. deploys KNOT;
2. creates an explicit three-way wait cycle;
3. seals the group;
4. proves the cycle through live consensus;
5. verifies the lowest-cost recovery override.

## Network target

**Stable Studionet only**

- Chain ID: **61999**
- RPC: `https://studio.genlayer.com/api`
- Repository-local GenLayer CLI: **0.39.1**

The repository intentionally does not target Studio-dev / 61997.

## Live evidence

The corrected source was deployed to stable Studionet (chain 61999):

- Contract: `0xd0cd05f5277Ff272D38651D7fd86AF931d10E0ec`
- Deployment transaction: [`0x82a71dd9c47f2bc4c9a56afb008f35185b8bfb6182f631b67554c96674586d2a`](https://explorer-studio.genlayer.com/tx/0x82a71dd9c47f2bc4c9a56afb008f35185b8bfb6182f631b67554c96674586d2a)
- Deployment result: `FINALIZED / ACCEPTED / MAJORITY_AGREE / SUCCESS`
- Source commit at deployment: `c107c559c55d4f3c877e896c7beff52415f2f18b`
- `runtime_chain_id()`: `61999`

The final declined-proposal live cycle used group `1` with commitments `[1, 2, 3, 4]`; commitment `1` was cancelled by its named actor, while `[2, 3, 4]` formed the active cycle:

- create group: `0xc847b13846be15bce81c0e75af16349b1ce2c4a9d2b948dbc839d6d9bc15a8af`
- seal after cancellation: `0x922054c4603e854ce32fdb39b7c46d4fdc338a7f213d75abf3a0e92a9b84041d`
- correct cycle proof: [`0xf1fe357ad27dc53d8a28373d2850f91f46f963d601b8a6ebd1a2c44fba784767`](https://explorer-studio.genlayer.com/tx/0xf1fe357ad27dc53d8a28373d2850f91f46f963d601b8a6ebd1a2c44fba784767)

The cycle certificate returned `[2, 3, 4]`, `cycle_count == 1`, and `dependency_count == 3`. `LOWEST_BREAK_COST` deterministically selected commitment `4` (cost `10`) and stored `override_cycle_id == 1` with status `OVERRIDDEN`.

A separate group `3` was sealed with unrelated declarations after both named actors approved. Its negative proof transaction was [`0xab0402b837952a7f6b615f8cdadcf8263ae97569085c86be0d05c2d94ac4e954`](https://explorer-studio.genlayer.com/tx/0xab0402b837952a7f6b615f8cdadcf8263ae97569085c86be0d05c2d94ac4e954). It finalized with consensus agreement but contract execution failed closed; the group readback remained `cycle_count == 0`.

Direct Mode: **25/25 passed** (stable GenVM `v0.2.12`; repository CLI `0.39.1`).
