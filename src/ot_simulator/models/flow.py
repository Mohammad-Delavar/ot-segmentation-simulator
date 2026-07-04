# src/ot_simulator/models/flow.py
"""
Data models for network traffic flows between assets.
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class FlowCriticality(str, Enum):
    """Traffic flow criticality levels."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class FlowDirection(str, Enum):
    """Traffic flow direction."""
    UNIDIRECTIONAL = "unidirectional"
    BIDIRECTIONAL = "bidirectional"


class TrafficFlow(BaseModel):
    """
    Represents network traffic flow between two assets.
    
    Attributes:
        id: Unique flow identifier
        source_asset_id: Source asset ID
        destination_asset_id: Destination asset ID
        protocol: Network protocol (Modbus, OPC-UA, HTTP, etc.)
        port: Destination port number
        direction: Flow direction
        criticality: Flow criticality level
        description: Human-readable description
    """
    id: str = Field(..., description="Unique flow identifier")
    source_asset_id: str = Field(..., description="Source asset ID")
    destination_asset_id: str = Field(..., description="Destination asset ID")
    protocol: str = Field(..., description="Protocol")
    port: int = Field(..., description="Port number")
    direction: FlowDirection = Field(..., description="Flow direction")
    criticality: FlowCriticality = Field(..., description="Criticality level")
    description: Optional[str] = Field(None, description="Flow description")

    def __str__(self) -> str:
        arrow = "<->" if self.direction == FlowDirection.BIDIRECTIONAL else "->"
        return (
            f"{self.source_asset_id} {arrow} {self.destination_asset_id} "
            f"({self.protocol}:{self.port}) [{self.criticality.value}]"
        )
