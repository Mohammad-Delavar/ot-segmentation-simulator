from typing import List, Optional
from pydantic import BaseModel, Field

from ..models.asset import Asset
from ..models.flow import TrafficFlow
from .simulator import SimulationResult


def _dedup(items: List[str]) -> List[str]:
    return list(dict.fromkeys(items))


class ImpactReport(BaseModel):

    summary: str
    critical_issues: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    affected_assets: List[str] = Field(default_factory=list)


class Analyzer:

    def __init__(self, result: SimulationResult, assets: List[Asset], flows: List[TrafficFlow]):
        self.result = result
        self.assets = {a.id: a for a in assets}
        self.flows = {f.id: f for f in flows}

    def analyze(self) -> ImpactReport:
 
        report = ImpactReport(
            summary=f"Simulation complete. {len(self.result.blocked_flows)} flows blocked across "
                    f"{len(self.result.zones_affected)} zones. Risk Score: {self.result.risk_score}"
        )

        for flow in self.result.blocked_flows:
            source = self.assets.get(flow.source_asset_id)
            dest = self.assets.get(flow.destination_asset_id)

            if not source or not dest:
                continue

            if "HMI" in source.type and "PLC" in dest.type:
                issue = f"CRITICAL: Control flow blocked: {source.name} cannot control {dest.name}"
                report.critical_issues.append(issue)
                report.recommendations.append(f"Add rule to allow {flow.protocol}:{flow.port} from {source.zone} to {dest.zone}")

            if "Historian" in dest.type:
                report.warnings.append(f"WARNING: Data logging interrupted for {source.name} -> {dest.name}")

            if "Engineering" in source.type:
                report.warnings.append(f"WARNING: Maintenance access blocked from {source.name} to {dest.name}")

            report.affected_assets.append(source.name)
            report.affected_assets.append(dest.name)

        if not report.critical_issues:
            report.recommendations.append("Policy looks safe for critical control operations.")

        report.critical_issues = _dedup(report.critical_issues)
        report.warnings = _dedup(report.warnings)
        report.recommendations = _dedup(report.recommendations)
        report.affected_assets = _dedup(report.affected_assets)

        return report
