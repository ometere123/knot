# KNOT deployment — stable Studionet 61999

This repository is intentionally pinned to stable **Studionet**, chain ID **61999**.

Do not use Studio-dev, chain 61997, for this repository.

## 1. Install the repository-local CLI

Your machine may have another global CLI. Ignore it.

From the KNOT repository:

```bash
npm install
npm run cli:version
```

Required output must identify:

```text
0.39.1
```

`package.json` pins the CLI exactly, and npm scripts execute the local binary before any global installation.

Run the guard:

```bash
npm run toolchain:check
```

## 2. Run static/direct validation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-test.txt
pytest tests/direct -v -s
```

On PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-test.txt
pytest tests/direct -v -s
```

Do not proceed if Direct Mode is red.

## 3. Confirm network

```bash
npm run network:studionet
```

The network information must resolve to stable Studionet:

- RPC `https://studio.genlayer.com/api`
- chain `61999`

If the output mentions 61997 or Studio-dev, stop.

## 4. Deploy

Use only:

```bash
npm run deploy:studionet
```

The deployment script independently checks the local CLI version, sets `studionet`, inspects network info and refuses to continue unless it sees 61999 and `studio.genlayer.com`.

Record the returned contract address and deployment transaction.

## 5. Verify chain from the contract

Call:

```text
runtime_chain_id()
```

Expected result:

```text
61999
```

If it is anything else, do not use that deployment as submission evidence.

## 6. Run the live integration lifecycle

```bash
gltest tests/integration -v -s --network studionet
```

The high-signal scenario should produce a fresh deployment and prove:

1. group creation;
2. three commitment registrations;
3. group seal;
4. GenLayer semantic cycle verification;
5. durable cycle certificate;
6. deterministic lowest-break-cost recovery.

## 7. Final verified deployment and reviewer evidence

The final corrected deployment is:

| Field | Observed value |
|---|---|
| Network | Studionet |
| Chain ID | 61999 |
| RPC | `https://studio.genlayer.com/api` |
| Contract | `0xd0cd05f5277Ff272D38651D7fd86AF931d10E0ec` |
| Deployment transaction | `0x82a71dd9c47f2bc4c9a56afb008f35185b8bfb6182f631b67554c96674586d2a` |
| Source commit | `c107c559c55d4f3c877e896c7beff52415f2f18b` |
| Source SHA-256 | `79c474ece86a3980f7b2535cb7d6a7886a4258f07beeff81105fde4b3ffb0e47` |
| Source bytes | `35122` |
| Deployment result | `FINALIZED / ACCEPTED / MAJORITY_AGREE / SUCCESS` |
| Runtime chain readback | `61999` |
| Direct Mode | `25/25 passed` |

Explorer: [final KNOT deployment](https://explorer-studio.genlayer.com/tx/0x82a71dd9c47f2bc4c9a56afb008f35185b8bfb6182f631b67554c96674586d2a)

The deployed source includes the four narrow hardening fixes documented in `REVIEW_EVIDENCE.md`: creator-controlled slot admission, explicit actor approval, duplicate-cycle prevention, and exclusion of cancelled proposals from seal-time approval requirements.

The final live evidence transaction table and state readbacks are maintained in `REVIEW_EVIDENCE.md`.

## 8. Capture reviewer evidence

Record:

- final commit SHA;
- CLI `0.39.1` output;
- `network info` showing 61999;
- Direct Mode test count/result;
- deployed address;
- deployment transaction;
- valid cycle transaction;
- at least one ambiguous/non-cycle failure case;
- `get_cycle(1)` output;
- recovered `get_commitment(...)` output;
- explorer links.

Update `SUBMISSION.md` only with observed values. Do not fabricate deployment or test evidence.

## 9. Final pre-submission review

Verify that there is still no frontend and that the repository remains a standalone reusable contract primitive.
