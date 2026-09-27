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
| Contract | `0x0eF825bde4e7bB8D90F5Cc2aD52E80945E9a4768` |
| Deployment transaction | `0x95182bb4844e9adc9af3f88697019a54c98d51351cdb47845c3bbb064f53dd38` |
| Source commit | `a1679cf4a59d74c463d0bc1810933a45f321639d` |
| Source SHA-256 | `145b1f682af7baf075e31df85824ba3747a79d4998c14b0bd9ba807008a27a99` |
| Source bytes | `35019` |
| Deployment result | `FINALIZED / ACCEPTED / MAJORITY_AGREE / SUCCESS` |
| Runtime chain readback | `61999` |
| Direct Mode | `25/25 passed` |

Explorer: [final KNOT deployment](https://explorer-studio.genlayer.com/tx/0x95182bb4844e9adc9af3f88697019a54c98d51351cdb47845c3bbb064f53dd38)

The deployed source includes the three deployed hardening fixes documented in `REVIEW_EVIDENCE.md`. The current repository additionally treats cancelled proposals as excluded membership: only commitments that remain `ACTIVE` require approval at seal time. This latest lifecycle fix is not part of the already-deployed source and requires a future deployment before it can be presented as live evidence.

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
