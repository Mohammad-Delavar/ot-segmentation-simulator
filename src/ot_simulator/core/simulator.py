"""
Simulation engine to evaluate policy impact on traffic flows.
"""
from typing import Dict, List, Set
from pydantic import BaseModel, Field

from ..models.asset import Asset
from ..models.flow import TrafficFlow, FlowCriticality
from ..models.policy import Policy, RuleAction


class SimulationResult(BaseModel):
    """
    Results of a simulation run.
    """
    allowed_flows: List[TrafficFlow] = Field(default_factory=list)
    blocked_flows: List[TrafficFlow] = Field(default_factory=list)
    critical_blocked: List[TrafficFlow] = Field(default_factory=list)
    zones_affected: Set[str] = Field(default_factory=set)
    risk_score: float = Field(0.0, description="Risk impact score (0-100)")


class Simulator:
    """
    Simulator for network segmentation impact analysis.
    """
    def __init__(self, assets: List[Asset], flows: List[TrafficFlow], policy: Policy):
        self.assets = {a.id: a for a in assets}
        self.flows = flows
        self.policy = policy

    def simulate(self) -> SimulationResult:
        """
        Run the simulation.
        
        Returns:
            SimulationResult containing impacts
        """
        result = SimulationResult()
        
        for flow in self.flows:
            source = self.assets.get(flow.source_asset_id)
            dest = self.assets.get(flow.destination_asset_id)
            
            if not source or not dest:
                # Flow with missing assets is considered blocked/invalid
                result.blocked_flows.append(flow)
                continue
                
            action = self.policy.evaluate(
                source_zone=source.zone,
                dest_zone=dest.zone,
                protocol=flow.protocol,
                port=flow.port
            )
            
            if action == RuleAction.ALLOW:
                result.allowed_flows.append(flow)
            else:
                result.blocked_flows.append(flow)
                result.zones_affected.add(source.zone)
                result.zones_affected.add(dest.zone)
                
                if flow.criticality == FlowCriticality.CRITICAL:
                    result.critical_blocked.append(flow)
                    
        # Calculate Risk Score
        result.risk_score = self._calculate_risk(result)
        return result

    def _calculate_risk(self, result: SimulationResult) -> float:
        """Calculate weighted risk score based on blocked flows."""
        score = 0.0
        for flow in result.blocked_flows:
            if flow.criticality == FlowCriticality.CRITICAL:
                score += 20
            elif flow.criticality == FlowCriticality.HIGH:
                score += 10
            elif flow.criticality == FlowCriticality.MEDIUM:
                score += 5
            else:
                score += 2
                
        return min(100.0, score)
