"""Boundary and protocol-invariant tests for KNOT."""

CONTRACT = "contracts/knot.py"


def test_unsupported_recovery_mode_rejected(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT, sdk_version="v0.2.12")
    with direct_vm.expect_revert("unsupported recovery mode"):
        contract.create_group("Bad mode", 9)


def test_text_bounds_are_enforced(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT, sdk_version="v0.2.12")
    with direct_vm.expect_revert("title exceeds"):
        contract.create_group("x" * 161, 0)

    group_id = contract.create_group("Bounds", 0)
    with direct_vm.expect_revert("obligation exceeds"):
        contract.add_commitment(
            group_id,
            direct_alice,
            "x" * 701,
            "condition",
            "output",
            True,
            1,
        )


def test_non_actor_cannot_mark_satisfied(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT, sdk_version="v0.2.12")
    group_id = contract.create_group("Actors", 0)
    a = contract.add_commitment(
        group_id, direct_alice, "A", "Need B", "A done", True, 1
    )
    contract.add_commitment(
        group_id, direct_bob, "B", "Need A", "B done", True, 2
    )
    contract.seal_group(group_id)

    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert("only the commitment actor"):
            contract.mark_satisfied(a)


def test_runtime_info_exposes_chain_for_deployment_verification(
    direct_vm, direct_deploy
):
    contract = direct_deploy(CONTRACT, sdk_version="v0.2.12")
    assert int(contract.runtime_chain_id()) >= 0
