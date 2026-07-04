"""Enterprise-grade CSV loaders for OT Simulator.

Replaces per-row print/skip with structured logging and
LoadResult aggregation. Supports strict and lenient modes.
"""

import logging
from pathlib import Path

import pandas as pd

from ..models.asset import Asset, PurdueLevel, Criticality
from ..models.flow import TrafficFlow, FlowDirection, FlowCriticality
from ..models.policy import Policy, FirewallRule, RuleAction
from .exceptions import FileLoadError, SchemaError, DataValidationError
from .result import LoadResult

logger = logging.getLogger(__name__)

# Expected columns per file type
ASSET_COLUMNS = {"id", "name", "type", "ip_address", "zone", "purdue_level", "criticality", "vendor"}
FLOW_COLUMNS = {"id", "source_asset_id", "destination_asset_id", "protocol", "port", "direction", "criticality"}
POLICY_COLUMNS = {"rule_id", "source_zone", "dest_zone", "protocol", "action", "priority"}


def _read_csv(csv_path: str | Path, required: set[str]) -> pd.DataFrame:
    """Read a CSV and validate its schema. Raises on failure."""
    path = Path(csv_path)
    if not path.exists():
        raise FileLoadError(f"file not found: {path}")
    if not path.is_file():
        raise FileLoadError(f"not a file: {path}")

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        raise FileLoadError(f"file is empty: {path}")
    except Exception as exc:
        raise FileLoadError(f"failed to parse {path}: {exc}") from exc

    actual = set(df.columns)
    missing = required - actual
    if missing:
        raise SchemaError(
            f"{path.name} missing columns: {sorted(missing)}",
            missing_columns=sorted(missing),
            extra_columns=sorted(actual - required),
        )

    logger.info("read %d rows from %s", len(df), path.name)
    return df


def _cell(row, key, default=None):
    """Return a cleaned cell value, or default if NaN/blank."""
    val = row.get(key)
    if pd.isna(val) or (isinstance(val, str) and not val.strip()):
        return default
    return val


# --------------------------------------------------------------------------- #
# Assets
# --------------------------------------------------------------------------- #
def load_assets(csv_path: str | Path, strict: bool = False) -> LoadResult[Asset]:
    """Load assets from CSV.

    strict=True  -> raise on first bad row.
    strict=False -> collect errors in LoadResult, keep going.
    """
    df = _read_csv(csv_path, ASSET_COLUMNS)
    result: LoadResult[Asset] = LoadResult(total_rows=len(df))

    for idx, row in df.iterrows():
        rownum = idx + 2  # +1 for 0-index, +1 for header
        try:
            asset = Asset(
                id=str(row["id"]).strip(),
                name=str(row["name"]).strip(),
                type=str(row["type"]).strip(),
                ip_address=str(row["ip_address"]).strip(),
                zone=str(row["zone"]).strip(),
                purdue_level=PurdueLevel(int(row["purdue_level"])),
                criticality=Criticality(str(row["criticality"]).strip()),
                vendor=str(row["vendor"]).strip(),
                model=_cell(row, "model"),
            )
            result.items.append(asset)
        except Exception as exc:
            logger.warning("asset row %d failed: %s", rownum, exc)
            result.add_error(rownum, str(exc), field="id",
                             value=_cell(row, "id"))
            if strict:
                raise DataValidationError(
                    f"asset row {rownum}: {exc}", row=rownum
                ) from exc

    logger.info("load_assets: %s", result.summary())
    return result


# --------------------------------------------------------------------------- #
# Flows
# --------------------------------------------------------------------------- #
def load_flows(csv_path: str | Path, strict: bool = False) -> LoadResult[TrafficFlow]:
    df = _read_csv(csv_path, FLOW_COLUMNS)
    result: LoadResult[TrafficFlow] = LoadResult(total_rows=len(df))

    for idx, row in df.iterrows():
        rownum = idx + 2
        try:
            flow = TrafficFlow(
                id=str(row["id"]).strip(),
                source_asset_id=str(row["source_asset_id"]).strip(),
                destination_asset_id=str(row["destination_asset_id"]).strip(),
                protocol=str(row["protocol"]).strip(),
                port=int(row["port"]),
                direction=FlowDirection(str(row["direction"]).strip()),
                criticality=FlowCriticality(str(row["criticality"]).strip()),
                description=_cell(row, "description"),
            )
            result.items.append(flow)
        except Exception as exc:
            logger.warning("flow row %d failed: %s", rownum, exc)
            result.add_error(rownum, str(exc), field="id",
                             value=_cell(row, "id"))
            if strict:
                raise DataValidationError(
                    f"flow row {rownum}: {exc}", row=rownum
                ) from exc

    logger.info("load_flows: %s", result.summary())
    return result


# --------------------------------------------------------------------------- #
# Policy
# --------------------------------------------------------------------------- #
def load_policy(
    csv_path: str | Path,
    policy_name: str = "Imported Policy",
    strict: bool = False,
) -> LoadResult[Policy]:
    """Load firewall rules and wrap them in a single Policy.

    The Policy is returned as items[0] when at least one rule is valid.
    """
    df = _read_csv(csv_path, POLICY_COLUMNS)
    result: LoadResult[Policy] = LoadResult(total_rows=len(df))
    rules: list[FirewallRule] = []

    for idx, row in df.iterrows():
        rownum = idx + 2
        try:
            rule = FirewallRule(
                rule_id=str(row["rule_id"]).strip(),
                source_zone=str(row["source_zone"]).strip(),
                dest_zone=str(row["dest_zone"]).strip(),
                protocol=str(row["protocol"]).strip(),
                action=RuleAction(str(row["action"]).strip()),
                priority=int(row["priority"]),
                description=_cell(row, "description"),
            )
            rules.append(rule)
        except Exception as exc:
            logger.warning("policy row %d failed: %s", rownum, exc)
            result.add_error(rownum, str(exc), field="rule_id",
                             value=_cell(row, "rule_id"))
            if strict:
                raise DataValidationError(
                    f"policy row {rownum}: {exc}", row=rownum
                ) from exc

    if rules:
        result.items.append(Policy(name=policy_name, rules=rules))
    else:
        result.add_error(None, "no valid rules loaded; policy is empty")

    logger.info("load_policy: %d rules, %s", len(rules), result.summary())
    return result
