# KNOT

**Semantic deadlock detection and deterministic recovery for independently authored commitments on GenLayer.**

KNOT detects wait-for cycles that exist in the *meaning* of commitments rather than in explicit program locks.

```text
Commitment A waits for a condition produced by B
Commitment B waits for a condition produced by C
Commitment C waits for a condition produced by A

                    A
                   / \
                  v   ^
                  B -> C

              semantic deadlock
```

Traditional deadlock detectors work when dependencies are already machine-readable. Autonomous agents and human organisations increasingly create commitments in natural language. KNOT lets any participant submit a suspected cycle, has GenLayer validators independently verify every semantic dependency edge, persists reusable dependency receipts, then records a durable deadlock certificate and optionally applies a pre-authorised deterministic escape rule.

KNOT is a **standalone Intelligent Contract primitive**. It intentionally has **no frontend**.

## Network and toolchain

KNOT is built for the stable hosted GenLayer environment only.

| Setting | Required value |
|---|---|
| Network | **Studionet** |
| Chain ID | **61999** |
| RPC | `https://studio.genlayer.com/api` |
| Local repository CLI | **genlayer 0.39.1** |
| Studio-dev / 61997 | **Not used** |
| Global CLI | Ignored by repository npm scripts |

`package.json` pins `genlayer` exactly to `0.39.1`. The repository deploy script invokes `node_modules/.bin/genlayer`, not a globally installed CLI, and refuses to deploy unless `network info` proves stable Studionet 61999.

## Why KNOT exists

Consider three independently authored commitments:

```text
A: I will release DESIGN-1 once PAYCONF-1 exists.
B: I will issue PAYCONF-1 once VERIFY-1 exists.
C: I will issue VERIFY-1 once DESIGN-1 exists.
```

No single commitment is malformed. The liveness failure only appears after combining their meanings.

KNOT separates the problem into two layers:

```text
natural-language relationship
          ↓
GenLayer validator consensus
          ↓
REQUIRES / DOES_NOT_REQUIRE / AMBIGUOUS
          ↓
deterministic closed-cycle check
          ↓
deterministic recovery policy
```

GenLayer is used only where ordinary deterministic contracts cannot safely decide the relationship between a prerequisite and another commitment's promised output. All cycle structure, membership checks, state transitions and recovery selection remain deterministic.

## Protocol flow

### 1. Create a group

A group defines a frozen commitment universe and a recovery policy.

```python
create_group(
    title="Three-party delivery loop",
    recovery_mode=1,
)
```

Recovery modes:

- `0` — `CERTIFY_ONLY`
- `1` — `LOWEST_BREAK_COST`

### 2. Actors add commitments

Each commitment declares:

```text
obligation
prerequisite
provides
breakable
break_cost
```

Example:

```text
obligation:   Issue payment confirmation.
prerequisite: Delivery verification has been recorded.
provides:     Payment confirmation is issued.
breakable:    true
break_cost:   20
```

`break_cost` is not chosen by the LLM. It is frozen before the group is sealed.

### 3. Seal the group

Only the group creator can add commitment records and seal. Each named actor must separately call `approve_commitment(commitment_id)` before sealing. That approval accepts the exact stored actor, obligation, prerequisite, provides text, breakability and break cost. After sealing:

- no new commitments can be added;
- commitments cannot be cancelled;
- dependency proofs operate against immutable commitment text.

### 4. Submit a suspected cycle

For `[A, B, C]`, KNOT verifies these exact ordered edges:

```text
B.provides → A.prerequisite
C.provides → B.prerequisite
A.provides → C.prerequisite
```

The submitter does not get to declare those edges true. GenLayer consensus judges them.

### 5. Validators independently re-derive the edge vector

The only semantic outputs are:

```text
REQUIRES
DOES_NOT_REQUIRE
AMBIGUOUS
```

A certificate is written only when:

1. the leader returns a valid vector;
2. validators independently re-run the same bounded judgement;
3. the accepted vector is valid;
4. **every edge is `REQUIRES`**.

Any ambiguity fails closed.

### 6. Deterministic recovery

With `LOWEST_BREAK_COST`, KNOT selects the breakable commitment in the proved cycle with the smallest predeclared cost. Ties are broken by commitment ID.

```text
A break cost = 30
B break cost = 20
C break cost = 10

proved cycle
     ↓
C receives override
```

The model never selects the commitment.

The selected commitment changes from `ACTIVE` to `OVERRIDDEN`, permanently binding the recovery to the cycle certificate that caused it.

## State model

### Group

```text
creator
title
OPEN | SEALED
recovery mode
commitment IDs
cycle count
creation/seal timestamps
```

### Commitment

```text
group ID
actor
obligation
prerequisite
provides
breakable
break cost
ACTIVE | SATISFIED | CANCELLED | OVERRIDDEN
override cycle ID
```

### Cycle certificate

```text
group ID
reporter
ordered commitment IDs
recovery commitment ID
creation timestamp
```

## Important epistemic boundary

KNOT does **not** claim:

> these are the only dependencies that exist in the world.

It claims something narrower and verifiable:

> for this sealed group and this caller-proposed ordered cycle, GenLayer validators agreed that every provider output materially satisfies the next waiter's frozen prerequisite.

This is intentional. Asking one model to discover the *complete* dependency graph would create a completeness hole: a leader could omit a material edge. KNOT instead verifies candidate deadlock certificates. Anyone can submit a suspected cycle.

## Consensus design

The leader and validators receive the same ordered edge data as serialized untrusted JSON. Commitment text is treated as data, never instructions.

The prompt specifically forbids:

- following instructions embedded in commitment text;
- inferring dependencies from workflow proximity;
- using the obligation field to manufacture a prerequisite;
- converting uncertainty into a positive edge.

Validators reject a leader result unless they independently obtain a valid edge vector agreeing with the proposal. Parse errors and unsupported outputs become inconclusive and cannot create a certificate.

See `docs/ARCHITECTURE.md` and `docs/THREAT_MODEL.md`.

## Reuse surface

The main contract declares `IKnot` for downstream Intelligent Contracts.

Useful reads include:

```text
get_group(group_id)
get_commitment(commitment_id)
get_dependency(waiter_id, provider_id)
is_dependency(waiter_id, provider_id)
get_cycle(cycle_id)
has_override(commitment_id)
runtime_chain_id()
```

`prove_dependency(waiter_id, provider_id)` can also establish a semantic edge independently. Once proved against sealed immutable text, that edge is cached as protocol graph state and later cycle proofs reuse it instead of paying for the same semantic judgement again.

A consumer can bind one of its own actions to a KNOT commitment and allow an emergency deadlock path only when `has_override(commitment_id)` becomes true.

See `examples/consumer_pattern.md`.

## No frontend

There is deliberately no Next.js, React or web UI in this repository.

KNOT is intended for the **Intelligent Contracts** contribution category: source, consensus logic, state design, tests, deployment evidence and integration documentation. Turning it into a full user-facing product would make it a different submission type.

## Local setup

### Node / CLI

Do **not** use a globally installed GenLayer CLI for this repository.

```bash
npm install
npm run cli:version
npm run toolchain:check
```

Expected CLI:

```text
0.39.1
```

`npm` automatically places the repository-local `node_modules/.bin` ahead of global executables when running package scripts.

### Direct-mode tests

Create a Python environment and install the test tooling:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements-test.txt
pytest tests/direct -v -s
```

The Direct Mode suite explicitly pins the stable GenVM `v0.2.12` artefact while the repository CLI remains exactly `0.39.1`. This avoids the current upstream testing-suite auto-detection path that resolves to a v0.3 RC with a renamed universal runner artefact.

Verified locally: **24/24 Direct Mode tests passed**. The suite includes creator-controlled open-group admission, actor approval, and duplicate-cycle certificate rejection.

The direct suite covers:

- group lifecycle;
- seal authority;
- frozen membership;
- actor-only resolution;
- valid three-way cycles;
- certify-only mode;
- deterministic lowest-cost recovery;
- ambiguous-edge failure;
- malformed LLM output;
- duplicate cycle IDs;
- terminal commitments;
- forged leader verdict vectors;
- input and mode boundaries.

### Stable Studionet integration test

```bash
gltest tests/integration -v -s --network studionet
```

The integration scenario deploys a fresh KNOT instance, creates an explicit three-way cycle, resolves it through live GenLayer consensus and verifies that the lowest-cost breakable commitment receives the recovery override.

## Deployment

Use the repository-local guarded deployment script:

```bash
npm install
npm run deploy:studionet
```

The script:

1. refuses any local CLI other than `0.39.1`;
2. sets `studionet` explicitly;
3. executes `genlayer network info`;
4. refuses deployment unless the output proves chain `61999` and `studio.genlayer.com`;
5. deploys `contracts/knot.py` to `https://studio.genlayer.com/api`.

After deployment, call:

```text
runtime_chain_id()
```

and require:

```text
61999
```

Full steps are in `DEPLOYMENT.md`.

## Repository layout

```text
contracts/knot.py                     main Intelligent Contract
examples/consumer_pattern.md          downstream integration pattern
tests/direct/test_knot.py             protocol and consensus tests
tests/direct/test_knot_boundaries.py  boundary tests
tests/integration/test_knot_studionet.py live 61999 lifecycle
docs/ARCHITECTURE.md                   protocol design
docs/THREAT_MODEL.md                   security assumptions
scripts/check-toolchain.mjs            local CLI/network configuration guard
scripts/deploy-studionet.mjs           61999-only deploy path
SUBMISSION.md                           reviewer-facing submission notes
DEPLOYMENT.md                           live completion checklist
```

## Current completion status

Implemented in-repo:

- main contract;
- custom validator logic;
- deterministic recovery;
- direct-mode test suite;
- live Studionet test scenario;
- exact local CLI pin;
- deployment guards;
- architecture/threat-model documentation;
- reviewer submission draft.

Verified in GitHub Actions:

- repository-local GenLayer CLI **0.39.1** installs successfully;
- toolchain/network guard passes for stable Studionet **61999**;
- **24/24 Direct Mode tests pass** using the stable GenVM `v0.2.12` artefact.

Final live Studionet evidence is recorded in `REVIEW_EVIDENCE.md` and `DEPLOYMENT.md`.
