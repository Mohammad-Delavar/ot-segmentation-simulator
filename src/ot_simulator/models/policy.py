# src/ot_simulator/models/policy.py
"""
Data models for firewall rules and segmentation policies.
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class RuleAction(str, Enum):
    """Firewall rule action."""
    ALLOW = "ALLOW"
    DENY = "DENY"


class FirewallRule(BaseModel):
    """
    Represents a firewall rule for network segmentation.
    
    Attributes:
        rule_id: Unique rule identifier
        source_zone: Source zone name (or "*" for any, None for wildcard)
        destination_zone: Destination zone name (or "*" for any, None for wildcard)
        protocol: Protocol name (or "*" for any, None for wildcard)
        port: Port number (or "*" for any, None for wildcard)
        action: ALLOW or DENY
        priority: Rule priority (lower number = higher priority)
    """
    rule_id: str = Field(..., description="Rule identifier")
    source_zone: Optional[str] = Field(default=None, description="Source zone")
    destination_zone: Optional[str] = Field(default=None, description="Destination zone")
    protocol: Optional[str] = Field(default=None, description="Protocol")
    port: Optional[str] = Field(default=None, description="Port")
    action: RuleAction = Field(..., description="Rule action")
    priority: int = Field(..., description="Rule priority")

    @field_validator('source_zone', 'destination_zone', 'protocol', 'port', mode='before')
    @classmethod
    def normalize_wildcard(cls, v):
        """Convert empty strings, 'nan', or None to None (wildcard)."""
        if v is None or v == '' or (isinstance(v, str) and v.lower() == 'nan'):
            return None
        return v

    def matches(
        self,
        source_zone: str,
        dest_zone: str,
        protocol: str,
        port: int
    ) -> bool:
        """
        Check if this rule matches the given traffic parameters.
        
        Args:
            source_zone: Source zone name
            dest_zone: Destination zone name
            protocol: Protocol name
            port: Port number
            
        Returns:
            True if rule matches
        """
        # None or "*" means match any
        if self.source_zone and self.source_zone != "*" and self.source_zone != source_zone:
            return False
        if self.destination_zone and self.destination_zone != "*" and self.destination_zone != dest_zone:
            return False
        if self.protocol and self.protocol != "*" and self.protocol.lower() != protocol.lower():
            return False
        if self.port and self.port != "*" and self.port != str(port):
            return False
        return True

    def __str__(self) -> str:
        src = self.source_zone or "*"
        dst = self.destination_zone or "*"
        proto = self.protocol or "*"
        prt = self.port or "*"
        return (
            f"Rule {self.rule_id} [P{self.priority}]: "
            f"{src} -> {dst} "
            f"({proto}:{prt}) = {self.action.value}"
        )


class Policy(BaseModel):
    """
    Collection of firewall rules that define segmentation policy.
    
    Attributes:
        name: Policy name
        rules: List of firewall rules
        default_action: Default action if no rule matches
    """
    name: str = Field(..., description="Policy name")
    rules: list[FirewallRule] = Field(default_factory=list, description="Rules")
    default_action: RuleAction = Field(
        RuleAction.DENY,
        description="Default action"
    )

    def evaluate(
        self,
        source_zone: str,
        dest_zone: str,
        protocol: str,
        port: int
    ) -> RuleAction:
        """
        Evaluate policy for given traffic parameters.
        
        Args:
            source_zone: Source zone name
            dest_zone: Destination zone name
            protocol: Protocol name
            port: Port number
            
        Returns:
            ALLOW or DENY based on matching rule or default action
        """
        # Sort rules by priority
        sorted_rules = sorted(self.rules, key=lambda r: r.priority)
        
        # Find first matching rule
        for rule in sorted_rules:
            if rule.matches(source_zone, dest_zone, protocol, port):
                return rule.action
        
        # No match, return default action
        return self.default_action

    def __str__(self) -> str:
        return f"Policy '{self.name}' with {len(self.rules)} rules (default: {self.default_action.value})"
