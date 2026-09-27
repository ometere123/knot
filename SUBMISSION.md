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

- Contract: `0x2cd385371fA71242cBE1c820e54d0899F9B48431`
- Deployment transaction: [`0x487d44204d31a0995f8693c5c99151518e484bc1c830c1f3b97e7b23419af375`](https://explorer-studio.genlayer.com/tx/0x487d44204d31a0995f8693c5c99151518e484bc1c830c1f3b97e7b23419af375)
- Deployment result: `FINALIZED / ACCEPTED / MAJORITY_AGREE / SUCCESS`
- Source commit at deployment: recorded in `REVIEW_EVIDENCE.md`
- `runtime_chain_id()`: `61999`

The final live cycle used group `1` and commitments `[1, 2, 3]`:

- create group: `0x8fdefd149fea6fc9de529dc7e1676ed6d416874ca50f5de1c5db723e724682ea`
- add A: `0x4a9e98fde8136dc3e6f5fffe7d3755de11ed98b5c80c0a29cad93519123f9976`
- add B: `0xdf54a36a6575ac353187c1c302ffafb28122a119b5ebd039f76330ce6a618461`
- add C: `0xaac3c9e3549c611bb58597666e6f1d14617ed135899743b94fa807be21590afa`
- seal: `0xfa59910a81168615828e57b98b710b2776e9e55a6a9cf839764dfcaf03733bbb`
- cycle proof: [`0x7f3b340de54202552a6841f0d6fb0538c004d0f89b2d8109e48ad1e5fea2495a`](https://explorer-studio.genlayer.com/tx/0x7f3b340de54202552a6841f0d6fb0538c004d0f89b2d8109e48ad1e5fea2495a)

The cycle certificate returned `[1, 2, 3]`, `cycle_count == 1`, and `dependency_count == 3`. `LOWEST_BREAK_COST` deterministically selected commitment `3` (cost `10`) and stored `override_cycle_id == 1` with status `OVERRIDDEN`.

A separate group `2` was sealed with unrelated declarations. Its negative proof transaction was [`0x5378bcd4bebcb9168c86f79fbca63016bdc8f56a34b1892c9a78c0c26d2f5f60`](https://explorer-studio.genlayer.com/tx/0x5378bcd4bebcb9168c86f79fbca63016bdc8f56a34b1892c9a78c0c26d2f5f60). It finalized with consensus agreement but contract execution failed closed; the group readback remained `cycle_count == 0`.

Direct Mode: **22/22 passed** (stable GenVM `v0.2.12`; repository CLI `0.39.1`).
