# v0.2.18
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *

import json
import typing
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# KNOT: semantic deadlock detection for independently authored commitments
# ---------------------------------------------------------------------------

GROUP_OPEN = 0
GROUP_SEALED = 1

COMMITMENT_ACTIVE = 0
COMMITMENT_SATISFIED = 1
COMMITMENT_CANCELLED = 2
COMMITMENT_OVERRIDDEN = 3

RECOVERY_CERTIFY_ONLY = 0
RECOVERY_LOWEST_BREAK_COST = 1

EDGE_REQUIRES = "REQUIRES"
EDGE_DOES_NOT_REQUIRE = "DOES_NOT_REQUIRE"
EDGE_AMBIGUOUS = "AMBIGUOUS"
ALLOWED_EDGE_VERDICTS = (
    EDGE_REQUIRES,
    EDGE_DOES_NOT_REQUIRE,
    EDGE_AMBIGUOUS,
)

MAX_TITLE_LEN = 160
MAX_OBLIGATION_LEN = 700
MAX_PREREQUISITE_LEN = 700
MAX_PROVIDES_LEN = 700
MAX_GROUP_COMMITMENTS = 8
MIN_GROUP_COMMITMENTS = 2
MAX_CYCLE_SIZE = 8
MAX_BREAK_COST = 10**12

ERR_EXPECTED = "EXPECTED"
ERR_STATE = "STATE"
ERR_AUTH = "AUTH"


@allow_storage
@dataclass
class Group:
    creator: Address
    title: str
    status: u8
    recovery_mode: u8
    created_at: str
    sealed_at: str
    cycle_count: u32
    dependency_count: u32
    commitment_ids: DynArray[u256]


@allow_storage
@dataclass
class Commitment:
    group_id: u256
    actor: Address
    obligation: str
    prerequisite: str
    provides: str
    breakable: bool
    break_cost: u256
    status: u8
    created_at: str
    resolved_at: str
    override_cycle_id: u256


@allow_storage
@dataclass
class DependencyReceipt:
    group_id: u256
    waiter_id: u256
    provider_id: u256
    reporter: Address
    created_at: str


@allow_storage
@dataclass
class CycleCertificate:
    group_id: u256
    reporter: Address
    created_at: str
    recovery_commitment_id: u256
    commitment_ids: DynArray[u256]


@gl.contract_interface
class IKnot:
    class View:
        def get_group(self, group_id: u256) -> dict: ...
        def get_commitment(self, commitment_id: u256) -> dict: ...
        def get_cycle(self, cycle_id: u256) -> dict: ...
        def get_dependency(self, waiter_id: u256, provider_id: u256) -> dict: ...
        def is_dependency(self, waiter_id: u256, provider_id: u256) -> bool: ...
        def has_override(self, commitment_id: u256) -> bool: ...
        def runtime_chain_id(self) -> u256: ...

    class Write:
        def create_group(self, title: str, recovery_mode: u8) -> u256: ...
        def add_commitment(
            self,
            group_id: u256,
            obligation: str,
            prerequisite: str,
            provides: str,
            breakable: bool,
            break_cost: u256,
        ) -> u256: ...
        def seal_group(self, group_id: u256) -> None: ...
        def prove_dependency(self, waiter_id: u256, provider_id: u256) -> u256: ...
        def prove_deadlock(self, group_id: u256, cycle_ids: DynArray[u256]) -> u256: ...
        def mark_satisfied(self, commitment_id: u256) -> None: ...
        def cancel_commitment(self, commitment_id: u256) -> None: ...


class GroupCreated(gl.Event):
    def __init__(self, group_id: u256, creator: Address, /, **blob): ...


class CommitmentAdded(gl.Event):
    def __init__(self, commitment_id: u256, group_id: u256, actor: Address, /, **blob): ...


class GroupSealed(gl.Event):
    def __init__(self, group_id: u256, /, **blob): ...


class CommitmentResolved(gl.Event):
    def __init__(self, commitment_id: u256, status: u8, /, **blob): ...


class DependencyProved(gl.Event):
    def __init__(self, dependency_id: u256, group_id: u256, /, **blob): ...


class DeadlockProved(gl.Event):
    def __init__(self, cycle_id: u256, group_id: u256, /, **blob): ...
