"""
Data models for OT assets and network zones.
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Criticality(str, Enum):
    """Asset criticality levels."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class PurdueLevel(int, Enum):
    """Purdue Model levels for industrial networks."""
    LEVEL_0 = 0  # Physical process
    LEVEL_1 = 1  # Basic control
    LEVEL_2 = 2  # Area supervisory control
    LEVEL_3 = 3  # Site operations
    LEVEL_4 = 4  # Site business planning
    LEVEL_5 = 5  # Enterprise network


class Asset(BaseModel):
    """
    Represents an industrial asset (PLC, HMI, SCADA, etc.).
    
    Attributes:
        id: Unique identifier for the asset
        name: Human-readable name
        type: Asset type (PLC, HMI, SCADA, Historian, etc.)
        ip_address: IP address of the asset
        zone: Network zone (Control, SCADA, DMZ, etc.)
        purdue_level: Purdue Model level (0-5)
        criticality: Criticality level
        vendor: Manufacturer name
        model: Device model
    """
    id: str = Field(..., description="Unique asset identifier")
    name: str = Field(..., description="Asset name")
    type: str = Field(..., description="Asset type")
    ip_address: str = Field(..., description="IP address")
    zone: str = Field(..., description="Network zone")
    purdue_level: PurdueLevel = Field(..., description="Purdue level")
    criticality: Criticality = Field(..., description="Criticality level")
    vendor: str = Field(..., description="Vendor name")
    model: Optional[str] = Field(None, description="Device model")

    def __str__(self) -> str:
        return (
            f"{self.name} ({self.type}) - {self.ip_address} "
            f"[Zone: {self.zone}, Criticality: {self.criticality.value}]"
        )


class Zone(BaseModel):
    """
    Represents a network zone containing multiple assets.
    
    Attributes:
        name: Zone name
        purdue_level: Purdue level of this zone
        assets: List of asset IDs in this zone
        description: Optional description
    """
    name: str = Field(..., description="Zone name")
    purdue_level: PurdueLevel = Field(..., description="Purdue level")
    assets: list[str] = Field(default_factory=list, description="Asset IDs")
    description: Optional[str] = Field(None, description="Zone description")

    def __str__(self) -> str:
        return f"Zone {self.name} (Level {self.purdue_level.value}): {len(self.assets)} assets"
