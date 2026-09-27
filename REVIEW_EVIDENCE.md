# KNOT reviewer evidence

## Source and toolchain

- Previous hardening source commit: `8ec12832e7905ffceb55d8ebb2e40564765dfc25`.
- Final actor-approval source commit: `a1679cf4a59d74c463d0bc1810933a45f321639d`.
- Current deployed source bytes: `35122` (Windows deployment payload with CRLF line endings).
- Current deployed source SHA-256: `79c474ece86a3980f7b2535cb7d6a7886a4258f07beeff81105fde4b3ffb0e47`.
- CLI: GenLayer `0.39.1`.
- Network guard: stable Studionet, chain `61999`, RPC `https://studio.genlayer.com/api`.
- Pinned runner: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`.
- Direct Mode: `25/25 passed` under WSL with `genlayer-test 0.29.2` and stable GenVM `v0.2.12`.
- Preflight: `KNOT offline preflight: OK`.
- Compileall: passed.
- `runtime_chain_id()` on the final deployment: `61999`.

## Superseded deployment

- Address: `0x2cd385371fA71242cBE1c820e54d0899F9B48431`.
- Transaction: `0x487d44204d31a0995f8693c5c99151518e484bc1c830c1f3b97e7b23419af375`.
- Result: `FINALIZED / ACCEPTED / MAJORITY_AGREE / SUCCESS`.
- Reason superseded: actor approval was not yet part of the commitment lifecycle.

## Final actor-consent deployment (superseded)

- Address: `0x0eF825bde4e7bB8D90F5Cc2aD52E80945E9a4768`.
- Transaction: `0x95182bb4844e9adc9af3f88697019a54c98d51351cdb47845c3bbb064f53dd38`.
- Source commit: `a1679cf4a59d74c463d0bc1810933a45f321639d`.
- Source bytes: `35019`.
- Source SHA-256: `145b1f682af7baf075e31df85824ba3747a79d4998c14b0bd9ba807008a27a99`.
- Result: `FINALIZED / ACCEPTED / MAJORITY_AGREE / SUCCESS`.
- Runtime chain readback: `61999`.
- Explorer: https://explorer-studio.genlayer.com/tx/0x95182bb4844e9adc9af3f88697019a54c98d51351cdb47845c3bbb064f53dd38

## Latest canonical deployment with declined-proposal handling

- Address: `0xd0cd05f5277Ff272D38651D7fd86AF931d10E0ec`.
- Transaction: `0x82a71dd9c47f2bc4c9a56afb008f35185b8bfb6182f631b67554c96674586d2a`.
- Source commit: `c107c559c55d4f3c877e896c7beff52415f2f18b`.
- Source bytes: `35122`.
- Source SHA-256: `79c474ece86a3980f7b2535cb7d6a7886a4258f07beeff81105fde4b3ffb0e47`.
- Result: `FINALIZED / ACCEPTED / MAJORITY_AGREE / SUCCESS`.
- `runtime_chain_id()`: `61999`.
- Explorer: https://explorer-studio.genlayer.com/tx/0x82a71dd9c47f2bc4c9a56afb008f35185b8bfb6182f631b67554c96674586d2a

## Latest live declined-proposal cycle

The latest canonical deployment used group `1` with commitments `[1,2,3,4]`. Commitment `1` was cancelled by its named actor without approval. Commitments `2`, `3`, and `4` were independently approved, the group sealed, and the active three-way cycle was proved.

| Action | Transaction | Observed result |
|---|---|---|
| Create group 1 | `0xc847b13846be15bce81c0e75af16349b1ce2c4a9d2b948dbc839d6d9bc15a8af` | `ACCEPTED / MAJORITY_AGREE / SUCCESS` |
| Seal group 1 after declined proposal | `0x922054c4603e854ce32fdb39b7c46d4fdc338a7f213d75abf3a0e92a9b84041d` | `ACCEPTED / MAJORITY_AGREE / SUCCESS` |
| Incorrect CLI proof encoding (diagnostic only) | `0x9991ddac87c6c50333e9dacdaf9fc3c02388303b39f70352644e3a147acb1889` | `FINALIZED / ACCEPTED / FINISHED_WITH_ERROR` — four positional arguments supplied |
| Correct cycle proof `[2,3,4]` | `0xf1fe357ad27dc53d8a28373d2850f91f46f963d601b8a6ebd1a2c44fba784767` | `FINALIZED / ACCEPTED / SUCCESS` |

Final readbacks: group `1` had `cycle_count == 1`, `dependency_count == 3`; cycle `1` contained `[2,3,4]` and selected recovery commitment `4`; commitment `1` had `status == CANCELLED` and `actor_approved == false`; commitment `4` had `status == OVERRIDDEN`, `override_cycle_id == 1`, and `override_granted == true`.

## Superseded actor-consent live cycle and deterministic recovery

The actor-consent lifecycle below is superseded historical evidence and uses `0x0eF825bde4e7bB8D90F5Cc2aD52E80945E9a4768`.

| Action | Transaction | Observed result |
|---|---|---|
| Create group 2 | `0x833336b11be721f70ab7b9ffd164cac9d93ae47685aa22b21130dceb80880115` | `ACCEPTED / MAJORITY_AGREE / SUCCESS` |
| Add commitment 2 (actor party_a) | `0xd59d11ba94af2fcd45846a3bee1ee94f61f476ed45c8c7aec88538266c6c230b` | `ACCEPTED / MAJORITY_AGREE / SUCCESS` |
| Add commitment 3 (actor party_b) | `0x4b902cc17373b7c508d300738d4a528669cd864c38d5a893c514b833e742d715` | `ACCEPTED / MAJORITY_AGREE / SUCCESS` |
| Add commitment 4 (actor deployer) | `0xe32f546048b727f9a3ee0e51558c322157ba3d1cef5ca3a7f422459d13c79702` | `ACCEPTED / MAJORITY_AGREE / SUCCESS` |
| Actor party_a approves 2 | `0x2e913cebdf6f463ffadacc3d70caa156ab592f25c01d77b1514ede12a905cefe` | `ACCEPTED / MAJORITY_AGREE / SUCCESS` |
| Actor party_b approves 3 | `0x2e325e1f8ad0057e86f56369ca4be1fe801363aff7e701ef10f527a21afda46e` | `ACCEPTED / MAJORITY_AGREE / SUCCESS` |
| Actor deployer approves 4 | `0x15ef333b7b2bb94316be03419b0b9d430ac94e0ac7469aea0ed34f2392d04f21` | `ACCEPTED / MAJORITY_AGREE / SUCCESS` |
| Seal group 2 | `0x8a167df0fb150930101040621e5bf397a425749d1c9d0dcf633deab146ba00c7` | `ACCEPTED / MAJORITY_AGREE / SUCCESS` |
| Prove cycle `[2,3,4]` | `0x743d033dc6b41ac19c6a5baa6ddc936e827b1aeab4f6af8367ed11a3e0b7b9c4` | `ACCEPTED / MAJORITY_AGREE / SUCCESS` |

The final readbacks were `cycle_count == 1`, `dependency_count == 3`, cycle IDs `[2,3,4]`, recovery commitment `4`, and commitment 4 `actor_approved == true`, `break_cost == 10`, `status == OVERRIDDEN`, `override_cycle_id == 1`.

## Final live fail-closed non-cycle proof

Group `3` was created with two actor-approved commitments whose declarations do not form a closed cycle. The final proof attempt was:

- Create group: `0x742d902dce30689f53ab9f5173f319a7ebf9845012a45edaf4f0f9432b4065d8`
- Add commitments 5 and 6: `0x1c1e4e3f394b68fc99c846203aaab83c2f4a2442c9556700fe178987e85d22c8`, `0x9014f427e58772e2a412331568b5cbc1733013e742df36dfe3d70910f482d87f`
- Actor approvals 5 and 6: `0x3e2b75a655690b67c1cb10ecea4314544b37e5615f0f0db9c27414699694aed9`, `0x2e71438aa197db34e82fa648809c6e7ae551f8cd34d2f3f5a6b49388b3aa9885`
- Seal: `0xeecb5d1bd6eae3b35182ab9f8d5c0088d6927424569655d93d866531d995a59b`
- Attempted non-cycle proof `[5,6]`: `0xab0402b837952a7f6b615f8cdadcf8263ae97569085c86be0d05c2d94ac4e954`

The attempted proof finalized with consensus agreement but contract execution failed closed. Final `get_group(3)` readback showed `cycle_count == 0` and `dependency_count == 0`; no certificate or override was created.

## Superseded pre-approval cycle evidence

The following earlier cycle used the prior deployment and remains historical evidence only.

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
- `test_unaccepted_commitment_cannot_be_sealed`: the creator cannot seal while any commitment remains unaccepted.
- `test_only_named_actor_can_accept_recovery_terms`: another wallet cannot approve or attribute the named actor's recovery terms.
- `test_actor_can_decline_without_bricking_group`: a named actor can cancel an unapproved proposal, while two approved active commitments still allow the group to seal.

The source remains a standalone Intelligent Contract primitive with no frontend.
