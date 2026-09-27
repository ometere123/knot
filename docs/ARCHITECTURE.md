# KNOT architecture

KNOT is a standalone GenLayer Intelligent Contract primitive for detecting semantic wait-for cycles among independently authored commitments.

## Core model

KNOT stores a reusable positive dependency graph. `prove_dependency(waiter, provider)` verifies one semantic wait-for edge through GenLayer consensus. A later cycle proof reuses any already-proved edges and asks consensus only for missing edges. Once all adjacent edges exist, closed-cycle detection and recovery are deterministic.

A **group** freezes a bounded set of commitments. Each commitment declares:

- `obligation`: what the actor promises to do;
- `prerequisite`: the condition that blocks the actor;
- `provides`: the condition produced when the commitment is fulfilled;
- `breakable`: whether a pre-authorised deadlock override may release it;
- `break_cost`: the deterministic recovery priority.

The group creator chooses one of two recovery policies before sealing:

1. `CERTIFY_ONLY`: prove the cycle but do not alter commitment state.
2. `LOWEST_BREAK_COST`: after a valid cycle is proved, grant an override to the breakable commitment with the lowest declared cost, tie-breaking by commitment ID.

Only the group creator may add commitments while the group is open. This prevents an unrelated wallet from consuming the bounded membership slots before the intended participants register. Each named actor must then approve the exact stored commitment before the creator can seal the group, binding the recovery terms to explicit actor consent. Once a cycle is certified, all cyclic rotations are indexed, so the same sealed cycle cannot create duplicate certificates or inflate `cycle_count`.

## Semantic boundary

For a submitted ordered cycle `[A, B, C]`, KNOT asks GenLayer consensus to judge only these edges:

- does B's declared output clearly satisfy A's prerequisite?
- does C's declared output clearly satisfy B's prerequisite?
- does A's declared output clearly satisfy C's prerequisite?

The output vocabulary is intentionally tiny:

- `REQUIRES`
- `DOES_NOT_REQUIRE`
- `AMBIGUOUS`

A certificate is created only when every edge is independently re-derived by validators and every edge is `REQUIRES`.

## Deterministic boundary

The LLM never:

- chooses which commitment to release;
- decides recovery priority;
- edits a commitment;
- invents an obligation;
- chooses cycle membership;
- mutates graph state directly.

Cycle membership is caller-proposed and deterministically checked for uniqueness, group membership, active status and closed ordering. Recovery is deterministic from frozen `breakable` and `break_cost` values.

## Why caller-proposed cycles

KNOT deliberately verifies a candidate cycle rather than asking one model to discover a complete dependency graph. This avoids a completeness hole where the leader could silently omit an edge and avoids quadratic LLM work for every possible pair. Any participant or third party can present a suspected cycle. The protocol verifies the exact cycle that would justify state transition.

## Recovery semantics

`COMMITMENT_OVERRIDDEN` does not claim the real-world obligation disappeared. It means the actor pre-authorised KNOT to release the prerequisite gate for that commitment if it is deterministically selected to break a proved cycle.

Consumers should treat `has_override(id)` as permission to proceed despite the commitment's declared prerequisite, not as evidence that the underlying work is complete.

## Network target

Repository deployment target is stable **Studionet, chain ID 61999** only. The repository-local CLI is pinned to **0.39.1**.
