"""Live Studionet lifecycle test for KNOT.

Target network is stable Studionet only: https://studio.genlayer.com/api, chain 61999.
The test deploys a fresh contract, creates a deliberately explicit semantic wait
cycle, proves it through GenLayer consensus, and verifies deterministic recovery.
"""

from gltest import get_contract_factory, get_default_account
from gltest.assertions import tx_execution_succeeded


CONTRACT = "knot.py"
TX_KW = {"consensus_max_rotations": 3, "wait_interval": 10000, "wait_retries": 24}


def assert_success(receipt):
    assert tx_execution_succeeded(receipt), receipt


def test_full_deadlock_and_recovery_lifecycle():
    factory = get_contract_factory(contract_file_path=CONTRACT)
    account = get_default_account()
    contract = factory.deploy(account=account, **TX_KW)
    assert contract.address
    actor = account.address

    created = contract.create_group(["KNOT live three-way cycle", 1]).transact(**TX_KW)
    assert_success(created)

    add_a = contract.add_commitment(
        [
            1,
            actor,
            "A will issue DESIGN-1.",
            "PAYCONF-1 has been issued.",
            "DESIGN-1 is issued.",
            True,
            30,
        ]
    ).transact(**TX_KW)
    assert_success(add_a)

    add_b = contract.add_commitment(
        [
            1,
            actor,
            "B will issue PAYCONF-1.",
            "VERIFY-1 has been issued.",
            "PAYCONF-1 is issued.",
            True,
            20,
        ]
    ).transact(**TX_KW)
    assert_success(add_b)

    add_c = contract.add_commitment(
        [
            1,
            actor,
            "C will issue VERIFY-1.",
            "DESIGN-1 has been issued.",
            "VERIFY-1 is issued.",
            True,
            10,
        ]
    ).transact(**TX_KW)
    assert_success(add_c)

    sealed = contract.seal_group([1]).transact(**TX_KW)
    assert_success(sealed)

    proved = contract.prove_deadlock([1, [1, 2, 3]]).transact(**TX_KW)
    assert_success(proved)

    cycle = contract.get_cycle([1]).call()
    assert cycle["commitment_ids"] == [1, 2, 3]
    assert cycle["recovery_commitment_id"] == 3

    released = contract.get_commitment([3]).call()
    assert released["override_granted"] is True
    assert released["status"] == 3
    assert contract.get_group([1]).call()["cycle_count"] == 1
