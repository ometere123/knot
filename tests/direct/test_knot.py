"""Direct-mode tests for the KNOT semantic deadlock primitive."""

import json

CONTRACT = "contracts/knot.py"
JUDGE = r"You are the KNOT dependency judge for a deadlock-proof protocol"


def verdicts(*items):
    return json.dumps({"verdicts": list(items)})


def build_three_cycle(direct_vm, direct_deploy, alice, bob, carol, recovery_mode=1):
    direct_vm.sender = alice
    contract = direct_deploy(CONTRACT, sdk_version="v0.2.12")
    group_id = contract.create_group("Three-party delivery loop", recovery_mode)

    with direct_vm.prank(alice):
        a = contract.add_commitment(
            group_id,
            alice,
            "Release the design package.",
            "Payment confirmation for the design package has been issued.",
            "The design package is released to the project team.",
            True,
            30,
        )
    with direct_vm.prank(alice):
        b = contract.add_commitment(
            group_id,
            bob,
            "Issue payment confirmation.",
            "Delivery verification for the released design package has been recorded.",
            "Payment confirmation for the design package is issued.",
            True,
            20,
        )
    with direct_vm.prank(alice):
        c = contract.add_commitment(
            group_id,
            carol,
            "Record delivery verification.",
            "The design package has been released to the project team.",
            "Delivery verification for the released design package is recorded.",
            True,
            10,
        )
    with direct_vm.prank(alice):
        contract.approve_commitment(a)
    with direct_vm.prank(bob):
        contract.approve_commitment(b)
    with direct_vm.prank(carol):
        contract.approve_commitment(c)
    with direct_vm.prank(alice):
        contract.seal_group(group_id)
    return contract, group_id, a, b, c


def test_create_group_and_add_commitments(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT, sdk_version="v0.2.12")
    group_id = contract.create_group("Independent commitments", 1)

    with direct_vm.prank(direct_alice):
        commitment_id = contract.add_commitment(
            group_id,
            direct_bob,
            "Publish the signed acknowledgement.",
            "The delivery receipt exists.",
            "A signed acknowledgement is published.",
            True,
            7,
        )
    with direct_vm.prank(direct_bob):
        contract.approve_commitment(commitment_id)

    group = contract.get_group(group_id)
    commitment = contract.get_commitment(commitment_id)
    assert group["status"] == 0
    assert group["commitment_ids"] == [1]
    assert commitment["group_id"] == group_id
    assert commitment["breakable"] is True
    assert commitment["break_cost"] == 7
    assert commitment["status"] == 0


def test_non_breakable_requires_zero_cost(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT, sdk_version="v0.2.12")
    group_id = contract.create_group("Costs", 1)

    with direct_vm.expect_revert("non-breakable"):
        contract.add_commitment(
            group_id,
            direct_alice,
            "Do work.",
            "Condition exists.",
            "Result exists.",
            False,
            1,
        )


def test_only_creator_can_seal(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT, sdk_version="v0.2.12")
    group_id = contract.create_group("Seal auth", 1)
    a = contract.add_commitment(group_id, direct_alice, "A", "Need B", "A done", True, 1)
    b = contract.add_commitment(group_id, direct_bob, "B", "Need A", "B done", True, 2)
    contract.approve_commitment(a)
    with direct_vm.prank(direct_bob):
        contract.approve_commitment(b)
    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert("only group creator"):
            contract.seal_group(group_id)


def test_seal_requires_two_active_commitments(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT, sdk_version="v0.2.12")
    group_id = contract.create_group("Too small", 1)
    a = contract.add_commitment(group_id, direct_alice, "A", "Need B", "A done", True, 1)
    contract.approve_commitment(a)
    with direct_vm.expect_revert("at least 2"):
        contract.seal_group(group_id)


def test_cannot_add_after_seal(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT, sdk_version="v0.2.12")
    group_id = contract.create_group("Frozen membership", 1)
    a = contract.add_commitment(group_id, direct_alice, "A", "Need B", "A done", True, 1)
    b = contract.add_commitment(group_id, direct_bob, "B", "Need A", "B done", True, 2)
    contract.approve_commitment(a)
    with direct_vm.prank(direct_bob):
        contract.approve_commitment(b)
    contract.seal_group(group_id)

    with direct_vm.expect_revert("sealed"):
        contract.add_commitment(group_id, direct_alice, "C", "Need A", "C done", True, 3)


def test_actor_can_cancel_only_before_seal(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT, sdk_version="v0.2.12")
    group_id = contract.create_group("Cancellation", 1)
    commitment_id = contract.add_commitment(
        group_id, direct_bob, "B", "Need A", "B done", True, 2
    )
    with direct_vm.expect_revert("only the commitment actor"):
        contract.cancel_commitment(commitment_id)
    with direct_vm.prank(direct_bob):
        contract.cancel_commitment(commitment_id)
    assert contract.get_commitment(commitment_id)["status"] == 2


def test_unaccepted_commitment_cannot_be_sealed(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT, sdk_version="v0.2.12")
    group_id = contract.create_group("Approval gate", 1)
    a = contract.add_commitment(group_id, direct_bob, "A", "Need B", "A done", True, 30)
    b = contract.add_commitment(group_id, direct_charlie, "B", "Need A", "B done", True, 20)

    with direct_vm.prank(direct_bob):
        contract.approve_commitment(a)
    with direct_vm.expect_revert("every commitment requires actor approval"):
        contract.seal_group(group_id)

    with direct_vm.prank(direct_charlie):
        contract.approve_commitment(b)
    contract.seal_group(group_id)
    assert contract.get_group(group_id)["status"] == 1


def test_only_named_actor_can_accept_recovery_terms(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT, sdk_version="v0.2.12")
    group_id = contract.create_group("Named actor approval", 1)
    commitment_id = contract.add_commitment(
        group_id,
        direct_bob,
        "B may be overridden.",
        "A prerequisite.",
        "B output.",
        True,
        77,
    )

    with direct_vm.expect_revert("only the named commitment actor may approve"):
        contract.approve_commitment(commitment_id)

    with direct_vm.prank(direct_bob):
        contract.approve_commitment(commitment_id)
    commitment = contract.get_commitment(commitment_id)
    assert commitment["actor_approved"] is True
    assert commitment["breakable"] is True
    assert commitment["break_cost"] == 77


def test_valid_cycle_is_certified_and_lowest_cost_override_breaks_it(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    contract, group_id, a, b, c = build_three_cycle(
        direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie, 1
    )
    direct_vm.mock_llm(JUDGE, verdicts("REQUIRES", "REQUIRES", "REQUIRES"))

    cycle_id = contract.prove_deadlock(group_id, [a, b, c])
    cycle = contract.get_cycle(cycle_id)

    assert cycle["commitment_ids"] == [a, b, c]
    assert cycle["recovery_commitment_id"] == c
    assert contract.has_override(c) is True
    assert contract.get_commitment(c)["status"] == 3
    assert contract.get_group(group_id)["cycle_count"] == 1
    assert direct_vm.run_validator() is True


def test_certify_only_mode_does_not_grant_override(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    contract, group_id, a, b, c = build_three_cycle(
        direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie, 0
    )
    direct_vm.mock_llm(JUDGE, verdicts("REQUIRES", "REQUIRES", "REQUIRES"))
    cycle_id = contract.prove_deadlock(group_id, [a, b, c])

    assert contract.get_cycle(cycle_id)["recovery_commitment_id"] == 0
    assert contract.has_override(a) is False
    assert contract.has_override(b) is False
    assert contract.has_override(c) is False


def test_non_creator_cannot_consume_open_group_slot(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT, sdk_version="v0.2.12")
    group_id = contract.create_group("Creator-controlled membership", 1)

    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert("only group creator may add"):
            contract.add_commitment(
                group_id,
                direct_bob,
                "Unauthorized slot claim.",
                "A prerequisite.",
                "A result.",
                True,
                1,
            )

    assert contract.get_group(group_id)["commitment_ids"] == []

    commitment_id = contract.add_commitment(
        group_id,
        direct_bob,
        "Authorized actor commitment.",
        "A prerequisite.",
        "A result.",
        True,
        1,
    )
    assert contract.get_commitment(commitment_id)["actor"].lower() == (
        "0x" + direct_bob.hex()
    )


def test_duplicate_cycle_certificate_is_rejected(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    contract, group_id, a, b, c = build_three_cycle(
        direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie, 0
    )
    direct_vm.mock_llm(JUDGE, verdicts("REQUIRES", "REQUIRES", "REQUIRES"))
    first_cycle_id = contract.prove_deadlock(group_id, [a, b, c])
    assert first_cycle_id == 1

    with direct_vm.expect_revert("already been proved"):
        contract.prove_deadlock(group_id, [b, c, a])

    assert contract.get_group(group_id)["cycle_count"] == 1


def test_non_cycle_is_rejected(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    contract, group_id, a, b, c = build_three_cycle(
        direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie, 1
    )
    direct_vm.mock_llm(
        JUDGE, verdicts("REQUIRES", "DOES_NOT_REQUIRE", "REQUIRES")
    )
    with direct_vm.expect_revert("do not form a proved deadlock"):
        contract.prove_deadlock(group_id, [a, b, c])


def test_ambiguous_edge_fails_closed(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    contract, group_id, a, b, c = build_three_cycle(
        direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie, 1
    )
    direct_vm.mock_llm(JUDGE, verdicts("REQUIRES", "AMBIGUOUS", "REQUIRES"))
    with direct_vm.expect_revert("do not form a proved deadlock"):
        contract.prove_deadlock(group_id, [a, b, c])


def test_malformed_model_output_fails_closed(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    contract, group_id, a, b, c = build_three_cycle(
        direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie, 1
    )
    direct_vm.mock_llm(JUDGE, "not json")
    with direct_vm.expect_revert("inconclusive"):
        contract.prove_deadlock(group_id, [a, b, c])


def test_duplicate_cycle_ids_rejected_before_consensus(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    contract, group_id, a, b, _ = build_three_cycle(
        direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie, 1
    )
    with direct_vm.expect_revert("must be unique"):
        contract.prove_deadlock(group_id, [a, b, a])


def test_satisfied_commitment_cannot_be_part_of_deadlock(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    contract, group_id, a, b, c = build_three_cycle(
        direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie, 1
    )
    with direct_vm.prank(direct_bob):
        contract.mark_satisfied(b)
    with direct_vm.expect_revert("not active"):
        contract.prove_deadlock(group_id, [a, b, c])


def test_validator_rejects_forged_leader_vector(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    contract, group_id, a, b, c = build_three_cycle(
        direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie, 0
    )
    direct_vm.mock_llm(JUDGE, verdicts("REQUIRES", "REQUIRES", "REQUIRES"))
    contract.prove_deadlock(group_id, [a, b, c])

    direct_vm.clear_mocks()
    direct_vm.mock_llm(JUDGE, verdicts("REQUIRES", "REQUIRES", "AMBIGUOUS"))
    forged = {
        "ok": True,
        "verdicts": ["REQUIRES", "REQUIRES", "REQUIRES"],
    }
    assert direct_vm.run_validator(leader_result=forged) is False


def test_dependency_receipt_is_reusable_graph_state(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    contract, group_id, a, b, c = build_three_cycle(
        direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie, 0
    )

    direct_vm.mock_llm(JUDGE, verdicts("REQUIRES"))
    dependency_id = contract.prove_dependency(a, b)
    assert dependency_id == 1
    assert contract.is_dependency(a, b) is True
    receipt = contract.get_dependency(a, b)
    assert receipt["waiter_id"] == a
    assert receipt["provider_id"] == b
    assert receipt["verdict"] == "REQUIRES"
    assert contract.get_group(group_id)["dependency_count"] == 1

    # The same immutable edge is cached; proving it again requires no model call.
    direct_vm.clear_mocks()
    assert contract.prove_dependency(a, b) == dependency_id

    # The deadlock proof reuses A<-B and asks consensus only for the two
    # still-missing edges before performing the deterministic closed-cycle step.
    direct_vm.mock_llm(JUDGE, verdicts("REQUIRES", "REQUIRES"))
    cycle_id = contract.prove_deadlock(group_id, [a, b, c])
    assert cycle_id == 1
    assert contract.get_group(group_id)["dependency_count"] == 3


def test_non_dependency_is_not_persisted(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    contract, _, a, b, _ = build_three_cycle(
        direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie, 0
    )
    direct_vm.mock_llm(JUDGE, verdicts("DOES_NOT_REQUIRE"))
    with direct_vm.expect_revert("does not prove the waiter dependency"):
        contract.prove_dependency(a, b)
    assert contract.is_dependency(a, b) is False
