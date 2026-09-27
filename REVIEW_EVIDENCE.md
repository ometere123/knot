# KNOT reviewer evidence

## Source and toolchain

- Final corrected source commit: `8ec1283c5f67f0d1742906d1ad7caa4754c9a3a4`.
- Deployed source bytes: `33491` (Windows deployment payload with CRLF line endings).
- Deployed source SHA-256: `f52ec1b6c2201f3a5f3974cd650991b14f55984b9eedcbfd29a2bb38ad1c028d`.
- CLI: GenLayer `0.39.1`.
- Network guard: stable Studionet, chain `61999`, RPC `https://studio.genlayer.com/api`.
- Pinned runner: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`.
- Direct Mode: `22/22 passed` under WSL with `genlayer-test 0.29.2` and stable GenVM `v0.2.12`.
- Preflight: `KNOT offline preflight: OK`.
- Compileall: passed.
- `runtime_chain_id()` on the final deployment: `61999`.

## Final deployment

- Address: `0x2cd385371fA71242cBE1c820e54d0899F9B48431`.
- Transaction: `0x487d44204d31a0995f8693c5c99151518e484bc1c830c1f3b97e7b23419af375`.
- Result: `FINALIZED / ACCEPTED / MAJORITY_AGREE / SUCCESS`.
- Explorer: https://explorer-studio.genlayer.com/tx/0x487d44204d31a0995f8693c5c99151518e484bc1c830c1f3b97e7b23419af375

## Final live cycle and deterministic recovery

Final deployment address used for every transaction below: `0x2cd385371fA71242cBE1c820e54d0899F9B48431`.

| Action | Transaction | Observed result |
|---|---|---|
| Create group 1 | `0x8fdefd149fea6fc9de529dc7e1676ed6d416874ca50f5de1c5db723e724682ea` | `ACCEPTED / MAJORITY_AGREE / SUCCESS` |
| Add commitment A | `0x4a9e98fde8136dc3e6f5fffe7d3755de11ed98b5c80c0a29cad93519123f9976` | `ACCEPTED / MAJORITY_AGREE / SUCCESS` |
| Add commitment B | `0xdf54a36a6575ac353187c1c302ffafb28122a119b5ebd039f76330ce6a618461` | `ACCEPTED / MAJORITY_AGREE / SUCCESS` |
| Add commitment C | `0xaac3c9e3549c611bb58597666e6f1d14617ed135899743b94fa807be21590afa` | `ACCEPTED / MAJORITY_AGREE / SUCCESS` |
| Seal group 1 | `0xfa59910a81168615828e57b98b710b2776e9e55a6a9cf839764dfcaf03733bbb` | `ACCEPTED / MAJORITY_AGREE / SUCCESS` |
| Prove dependency A←B | captured in the live run's `dependency_count == 3` readback | durable dependency state |
| Prove closed cycle `[1,2,3]` | `0x7f3b340de54202552a6841f0d6fb0538c004d0f89b2d8109e48ad1e5fea2495a` | `ACCEPTED / MAJORITY_AGREE / SUCCESS` |

Cycle readback:

```json
{"commitment_ids":[1,2,3],"group_id":1,"id":1,"recovery_commitment_id":3}
```

Group readback had `cycle_count == 1` and `dependency_count == 3`. Commitment 3 had `break_cost == 10`, `status == OVERRIDDEN`, `override_granted == true`, and `override_cycle_id == 1`; commitments 1 and 2 were not overridden. This proves deterministic lowest-cost recovery, not model-selected recovery.

## Fail-closed non-cycle proof

Group 2 contained two sealed commitments whose declarations did not form a closed dependency cycle. The attempted proof transaction was:

`0x5378bcd4bebcb9168c86f79fbca63016bdc8f56a34b1892c9a78c0c26d2f5f60`

It finalized with consensus agreement but contract execution failed closed. The post-transaction group readback had `cycle_count == 0`; no certificate was created.

## Hardening covered by adversarial tests

- `test_non_creator_cannot_consume_open_group_slot`: an unrelated wallet cannot consume an open group's bounded slot; the creator can register an explicit actor.
- `test_duplicate_cycle_certificate_is_rejected`: a second submission of the same cycle in a rotated order is rejected and `cycle_count` remains `1`.

The source remains a standalone Intelligent Contract primitive with no frontend.
