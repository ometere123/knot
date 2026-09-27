# KNOT final handoff

## Goal

Finish KNOT from the existing repository **in place** on stable GenLayer **Studionet, chain ID 61999**.

Do not redesign, restart, scaffold a replacement, add a frontend, or migrate the project to Studio-dev.

The implementation is already substantially complete and its Direct Mode suite is green.

## Fixed environment

- Network: **Studionet**
- Chain ID: **61999**
- RPC: `https://studio.genlayer.com/api`
- Repository-local GenLayer CLI: **0.39.1**
- Direct Mode GenVM artefact: **v0.2.12**
- Global CLI `0.40.0rc2`: **do not use**
- Studio-dev / 61997: **do not use**

The repository scripts intentionally call the local `node_modules/.bin/genlayer` binary.

## Already complete

- standalone KNOT Intelligent Contract;
- no frontend;
- semantic dependency receipts;
- caller-proposed deadlock certificates;
- independent validator re-derivation with `run_nondet_unsafe`;
- deterministic closed-cycle verification;
- certify-only recovery mode;
- deterministic lowest-break-cost recovery mode;
- threat model and architecture documentation;
- guarded Studionet deployment script;
- live 61999 integration scenario;
- GitHub Actions CI;
- **25/25 Direct Mode tests green**.

Do not weaken tests or remove security checks to make later runtime steps pass.

## Required final steps

### 1. Clone and enter the existing repo

```bash
git clone https://github.com/ometere123/knot.git
cd knot
```

### 2. Install the exact local CLI

```bash
npm install
npm run cli:version
npm run toolchain:check
```

The CLI output must identify `0.39.1`.

If the shell resolves `0.40.0rc2`, stop. Do not deploy with it.

### 3. Re-run Direct Mode

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-test.txt
pytest tests/direct -v -s
```

On PowerShell use:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-test.txt
pytest tests/direct -v -s
```

Expected baseline: **25 passed**.

The tests explicitly request GenVM `v0.2.12`. Do not change them to an automatic latest v0.3 RC merely because a global toolchain is newer.

### 4. Verify the network before any live write

```bash
npm run network:studionet
```

Confirm all of the following:

- `studionet`;
- `https://studio.genlayer.com/api`;
- chain ID `61999`.

If any command shows `61997`, `studio-dev`, or a v0.40 RC network profile, stop and correct the environment.

### 5. Deploy KNOT

Use the guarded local script:

```bash
npm run deploy:studionet
```

Record:

- deployed contract address;
- deployment transaction hash;
- finality result;
- exact commit SHA used.

### 6. Verify the deployed chain from KNOT

Call:

```text
runtime_chain_id()
```

It must return:

```text
61999
```

Do not treat a deployment on any other chain as valid evidence.

### 7. Exercise the live lifecycle

Run:

```bash
gltest tests/integration -v -s --network studionet
```

If your local `gltest` invocation requires account configuration, use the funded Studionet account without committing its private key.

The live proof must demonstrate:

1. group creation;
2. three commitment registrations;
3. seal;
4. semantic dependency verification by GenLayer consensus;
5. durable dependency receipts;
6. deadlock certificate;
7. deterministic selection of the lowest break-cost commitment;
8. recovery override persisted in state.

Also exercise at least one negative path live if practical:

- an ambiguous edge, or
- a non-dependency edge,

and record the failed transaction/simulation evidence without weakening fail-closed behaviour.

### 8. Reviewer evidence

Update `SUBMISSION.md` only with values actually observed:

- contract address;
- deployment transaction;
- network = Studionet 61999;
- valid-cycle transaction;
- invalid/ambiguous evidence;
- live integration result;
- final commit SHA;
- explorer links if available.

Do not fabricate or infer missing transaction hashes.

### 9. Final hostile review

Before submission, inspect for:

- any accidental reference to 61997 or Studio-dev in active configuration;
- any accidental use of global CLI 0.40.0rc2;
- any path where ambiguous semantic output could create a positive dependency;
- any way a resolved commitment can enter a cycle;
- any model-controlled recovery choice;
- any replay path that can repeatedly grant recovery from one cycle;
- any documentation claim stronger than the contract actually proves.

Keep KNOT a standalone Intelligent Contract. **Do not add a frontend.**
