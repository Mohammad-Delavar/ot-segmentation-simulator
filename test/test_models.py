# tests/test_models.py
import pytest
from ot_simulator.models.asset import Asset, PurdueLevel, Criticality
from ot_simulator.models.policy import Policy, FirewallRule, RuleAction


def test_asset_creation():
    asset = Asset(
        id="T1", 
        name="Test", 
        type="PLC", 
        ip_address="1.1.1.1",
        zone="Z1", 
        purdue_level=1, 
        criticality="Critical", 
        vendor="V"
    )
    assert asset.id == "T1"
    assert asset.purdue_level == PurdueLevel.LEVEL_1


def test_policy_evaluation():
    rule = FirewallRule(
        rule_id="R1", 
        source_zone="A", 
        destination_zone="B",
        protocol="TCP", 
        port="80", 
        action="ALLOW", 
        priority=10
    )
    policy = Policy(name="Test", rules=[rule], default_action=RuleAction.DENY)
    
    assert policy.evaluate("A", "B", "TCP", 80) == RuleAction.ALLOW
    assert policy.evaluate("X", "B", "TCP", 80) == RuleAction.DENY
