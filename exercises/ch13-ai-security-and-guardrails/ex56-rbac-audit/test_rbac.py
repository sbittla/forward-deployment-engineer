import pytest

ROLES = {
    "agent": {"inherits": [], "permissions": ["kb:read", "ticket:read", "ticket:comment"]},
    "supervisor": {"inherits": ["agent"], "permissions": ["refund:approve<=500", "ticket:*"]},
    "admin": {"inherits": ["supervisor"], "permissions": ["*"]},
    "loop_a": {"inherits": ["loop_b"], "permissions": ["a:x"]},
    "loop_b": {"inherits": ["loop_a"], "permissions": ["b:x"]},
}
ANA = {"id": "ana", "tenant": "retail", "roles": ["agent"]}
SAM = {"id": "sam", "tenant": "retail", "roles": ["supervisor"]}
ROOT = {"id": "root", "tenant": "retail", "roles": ["admin"]}


@pytest.fixture
def ac(impl):
    return impl.AccessController(ROLES)


def test_inheritance(ac):
    assert ac.permissions("supervisor") == {"kb:read", "ticket:read", "ticket:comment", "refund:approve<=500", "ticket:*"}
    assert ac.permissions("loop_a") == {"a:x", "b:x"}


def test_basic(ac):
    assert ac.check(ANA, "ticket:read", {"tenant": "retail"})
    assert not ac.check(ANA, "ticket:close", {"tenant": "retail"})
    assert ac.check(SAM, "ticket:close", {"tenant": "retail"})
    assert ac.check(ROOT, "anything:goes", {"tenant": "retail"})


def test_limits(ac):
    assert ac.check(SAM, "refund:approve", {"tenant": "retail", "amount": 500})
    assert not ac.check(SAM, "refund:approve", {"tenant": "retail", "amount": 501})
    assert not ac.check(ANA, "refund:approve", {"tenant": "retail", "amount": 5})


def test_tenant_isolation(ac):
    assert not ac.check(ROOT, "ticket:read", {"tenant": "wealth"})
    assert ac.audit.entries[-1]["reason"] == "tenant mismatch"


def test_audit_entries_and_chain(ac):
    ac.check(SAM, "refund:approve", {"tenant": "retail", "amount": 100})
    ac.check(ANA, "ticket:close", {"tenant": "retail"})
    e1, e2 = ac.audit.entries
    assert (e1["user_id"], e1["action"], e1["tenant"], e1["allowed"]) == ("sam", "refund:approve", "retail", True)
    assert e1["reason"] == "granted by refund:approve<=500"
    assert e2["reason"] == "no matching permission" and e2["allowed"] is False
    assert e1["prev_hash"] == "0" * 64 and e2["prev_hash"] == e1["hash"]
    assert ac.audit.verify()


def test_tamper_detection(ac):
    for _ in range(3):
        ac.check(ANA, "kb:read", {"tenant": "retail"})
    ac.audit.entries[1]["allowed"] = False
    assert not ac.audit.verify()


def test_delete_detection(ac):
    for _ in range(3):
        ac.check(ANA, "kb:read", {"tenant": "retail"})
    del ac.audit.entries[1]
    assert not ac.audit.verify()
