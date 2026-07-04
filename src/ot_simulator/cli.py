import typer
import json
from pathlib import Path
from typing import Optional

from .core.loader import load_assets, load_flows, load_policy
from .core.simulator import Simulator
from .core.analyzer import Analyzer
from .reports.console import print_simulation_result, print_impact_report

app = typer.Typer(help="OT Network Segmentation Impact Simulator")


def _report_errors(name: str, result) -> None:
    """Print any load errors for a given file."""
    if result.errors:
        typer.secho(f"[!] {len(result.errors)} issue(s) while loading {name}:",
                    fg=typer.colors.YELLOW)
        for err in result.errors:
            typer.echo(f"    - {err}")


@app.command()
def simulate(
    assets_csv: Path = typer.Option(..., "--assets", help="Path to assets.csv"),
    flows_csv: Path = typer.Option(..., "--flows", help="Path to flows.csv"),
    policy_csv: Path = typer.Option(..., "--policy", help="Path to policy.csv"),
    strict: bool = typer.Option(False, "--strict", help="Fail on first bad row"),
    output_json: Optional[Path] = typer.Option(None, "--output", help="Save report to JSON file"),
):
    """
    Run simulation and analysis.
    """
    try:
        typer.echo("Loading data files...")
        asset_result = load_assets(assets_csv, strict=strict)
        flow_result = load_flows(flows_csv, strict=strict)
        policy_result = load_policy(policy_csv, strict=strict)

        _report_errors("assets", asset_result)
        _report_errors("flows", flow_result)
        _report_errors("policy", policy_result)

        assets = asset_result.items
        flows = flow_result.items

        if not policy_result.items:
            typer.secho("Error: no valid firewall rules loaded; cannot simulate.",
                        fg=typer.colors.RED)
            raise typer.Exit(code=1)
        policy = policy_result.items[0]  

        if not assets or not flows:
            typer.secho("Error: assets or flows are empty after loading.",
                        fg=typer.colors.RED)
            raise typer.Exit(code=1)

        typer.echo("Running simulation engine...")
        sim = Simulator(assets, flows, policy)
        result = sim.simulate()

        typer.echo("Analyzing results...")
        analyzer = Analyzer(result, assets, flows)
        report = analyzer.analyze()

        print_simulation_result(result)
        print_impact_report(report)

        if output_json:
            with open(output_json, "w") as f:
                json.dump(report.model_dump(), f, indent=4, default=str)
            typer.echo(f"\nReport saved to {output_json}")

    except typer.Exit:
        raise
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
