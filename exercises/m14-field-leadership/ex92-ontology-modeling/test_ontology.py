import pytest


@pytest.fixture
def onto(impl):
    o = impl.Ontology()
    o.add_object_type(impl.ObjectType("Customer", "customer_id", {"customer_id": "str", "name": "str", "tier": "str"}))
    o.add_object_type(impl.ObjectType("Warehouse", "wh_id", {"wh_id": "str", "city": "str"}))
    o.add_object_type(impl.ObjectType("Shipment", "shipment_id", {"shipment_id": "str", "customer_id": "str",
                                                                  "wh_id": "str", "status": "str", "weight_kg": "float"}))
    o.add_link_type(impl.LinkType("ships_to", "Shipment", "Customer", "one", "customer_id"))
    o.add_link_type(impl.LinkType("ships_from", "Shipment", "Warehouse", "one", "wh_id"))
    assert o.load("Customer", [{"customer_id": "C1", "name": "Acme", "tier": "gold"},
                               {"customer_id": "C2", "name": "Globex", "tier": "silver"}]) == []
    assert o.load("Warehouse", [{"wh_id": "W1", "city": "Rotterdam"}]) == []
    return o


def test_types_validated(impl, onto):
    with pytest.raises(ValueError):
        onto.add_link_type(impl.LinkType("bad", "Shipment", "Truck", "one", "truck_id"))
    errors = onto.load("Shipment", [
        {"shipment_id": "S1", "customer_id": "C1", "wh_id": "W1", "status": "delayed", "weight_kg": 120},
        {"shipment_id": "S2", "customer_id": "C1", "wh_id": "W1", "status": "in_transit", "weight_kg": "heavy"},
        {"customer_id": "C2", "wh_id": "W1", "status": "delivered", "weight_kg": 3.5},
        {"shipment_id": "S1", "customer_id": "C2", "wh_id": "W1", "status": "x", "weight_kg": 1.0},
        {"shipment_id": "S3", "customer_id": "C9", "wh_id": "W1", "status": "delayed", "weight_kg": None},
    ])
    assert [e.split(":")[1] for e in errors] == ["1", "2", "3"]
    assert "weight_kg" in errors[0] and "shipment_id" in errors[1] and "duplicate" in errors[2]
    assert onto.get("Shipment", "S1")["status"] == "delayed" and onto.get("Shipment", "S2") is None
    assert onto.integrity() == ["ships_to:S3->C9"]


def test_traverse(onto):
    onto.load("Shipment", [{"shipment_id": "S1", "customer_id": "C1", "wh_id": "W1", "status": "delayed", "weight_kg": 1.0},
                           {"shipment_id": "S2", "customer_id": "C1", "wh_id": "W1", "status": "delivered", "weight_kg": 2.0},
                           {"shipment_id": "S4", "customer_id": "C2", "wh_id": "W1", "status": "delayed", "weight_kg": 3.0}])
    assert onto.traverse("Shipment", "S1", "ships_to")["name"] == "Acme"
    assert [s["shipment_id"] for s in onto.traverse("Customer", "C1", "~ships_to")] == ["S1", "S2"]
    assert len(onto.traverse("Warehouse", "W1", "~ships_from")) == 3


def test_actions(onto):
    onto.load("Shipment", [{"shipment_id": "S1", "customer_id": "C1", "wh_id": "W1", "status": "delayed", "weight_kg": 1.0}])

    def validate(o, shipment_id, customer_id, reason):
        if o.get("Customer", customer_id) is None:
            return f"unknown customer {customer_id}"
        if o.get("Shipment", shipment_id)["status"] == "delivered":
            return "cannot reassign a delivered shipment"
        return None

    def apply(o, shipment_id, customer_id, reason):
        o.get("Shipment", shipment_id)["customer_id"] = customer_id

    onto.register_action("reassign_shipment", "Shipment", {"shipment_id": "str", "customer_id": "str", "reason": "str"},
                         validate, apply, allowed_roles={"dispatcher", "agent"})
    with pytest.raises(PermissionError):
        onto.execute("reassign_shipment", "bob", "viewer", shipment_id="S1", customer_id="C2", reason="x")
    with pytest.raises(ValueError):
        onto.execute("reassign_shipment", "ai-agent", "agent", shipment_id="S1", customer_id="C9", reason="x")
    with pytest.raises(ValueError):
        onto.execute("reassign_shipment", "ai-agent", "agent", shipment_id="S1", customer_id="C2")
    assert onto.audit == [] and onto.get("Shipment", "S1")["customer_id"] == "C1"
    onto.execute("reassign_shipment", "ai-agent", "agent", shipment_id="S1", customer_id="C2", reason="customer merge")
    assert onto.traverse("Shipment", "S1", "ships_to")["name"] == "Globex"
    assert onto.audit == [{"action": "reassign_shipment", "actor": "ai-agent",
                           "params": {"shipment_id": "S1", "customer_id": "C2", "reason": "customer merge"}, "seq": 1}]
