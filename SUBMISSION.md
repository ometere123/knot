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

- Contract: `0x0eF825bde4e7bB8D90F5Cc2aD52E80945E9a4768`
- Deployment transaction: [`0x95182bb4844e9adc9af3f88697019a54c98d51351cdb47845c3bbb064f53dd38`](https://explorer-studio.genlayer.com/tx/0x95182bb4844e9adc9af3f88697019a54c98d51351cdb47845c3bbb064f53dd38)
- Deployment result: `FINALIZED / ACCEPTED / MAJORITY_AGREE / SUCCESS`
- Source commit at deployment: `a1679cf4a59d74c463d0bc1810933a45f321639d`
- `runtime_chain_id()`: `61999`

The final actor-consent live cycle used group `2` and commitments `[2, 3, 4]`:

- create group: `0x833336b11be721f70ab7b9ffd164cac9d93ae47685aa22b21130dceb80880115`
- add commitments: `0xd59d11ba94af2fcd45846a3bee1ee94f61f476ed45c8c7aec88538266c6c230b`, `0x4b902cc17373b7c508d300738d4a528669cd864c38d5a893c514b833e742d715`, `0xe32f546048b727f9a3ee0e51558c322157ba3d1cef5ca3a7f422459d13c79702`
- actor approvals: `0x2e913cebdf6f463ffadacc3d70caa156ab592f25c01d77b1514ede12a905cefe`, `0x2e325e1f8ad0057e86f56369ca4be1fe801363aff7e701ef10f527a21afda46e`, `0x15ef333b7b2bb94316be03419b0b9d430ac94e0ac7469aea0ed34f2392d04f21`
- seal: `0x8a167df0fb150930101040621e5bf397a425749d1c9d0dcf633deab146ba00c7`
- cycle proof: [`0x743d033dc6b41ac19c6a5baa6ddc936e827b1aeab4f6af8367ed11a3e0b7b9c4`](https://explorer-studio.genlayer.com/tx/0x743d033dc6b41ac19c6a5baa6ddc936e827b1ae4f6af8367ed11a3e0b7b9c4)

The cycle certificate returned `[2, 3, 4]`, `cycle_count == 1`, and `dependency_count == 3`. `LOWEST_BREAK_COST` deterministically selected commitment `4` (cost `10`) and stored `override_cycle_id == 1` with status `OVERRIDDEN`.

A separate group `3` was sealed with unrelated declarations after both named actors approved. Its negative proof transaction was [`0xab0402b837952a7f6b615f8cdadcf8263ae97569085c86be0d05c2d94ac4e954`](https://explorer-studio.genlayer.com/tx/0xab0402b837952a7f6b615f8cdadcf8263ae97569085c86be0d05c2d94ac4e954). It finalized with consensus agreement but contract execution failed closed; the group readback remained `cycle_count == 0`.

Direct Mode: **24/24 passed** (stable GenVM `v0.2.12`; repository CLI `0.39.1`).
