
# 🛡️ OT Network Segmentation Simulator

> **Model, validate, and visualize network segmentation policies for Operational Technology (OT) / ICS environments — before you touch a single firewall rule.**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Built with Typer](https://img.shields.io/badge/CLI-Typer-lightgrey.svg)](https://typer.tiangolo.com/)
[![Web UI](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)

---

## 📖 Overview

**OT Network Segmentation Simulator** is a lightweight, dependency-driven engine that lets security engineers and OT/ICS defenders **model network zones, communication flows, and segmentation policies** — then automatically evaluate which flows are **allowed**, **denied**, or **violate** the intended segmentation model (e.g., Purdue Model / IEC 62443 zones & conduits).

Instead of testing segmentation on production PLCs, RTUs, and SCADA systems, this tool lets you **simulate the impact of your policies against a data model first**, catching misconfigurations and unintended lateral-movement paths early.

### Why this exists
In OT environments, a single misconfigured conduit can expose a Level 1 controller to enterprise IT traffic. Testing segmentation *live* is risky and often impossible. This simulator provides a **safe, reproducible, version-controllable** way to validate segmentation intent.

---

## ✨ Features

- 🧩 **Data-driven modeling** — Define assets, flows, and policies as simple CSV files.
- ✅ **Policy evaluation engine** — Automatically classify every flow as `ALLOWED`, `DENIED`, or `VIOLATION`.
- 🔍 **Schema validation** — Input integrity enforced via **Pydantic** models (fail fast on bad data).
- 📊 **Interactive visualization** — A **Streamlit** web app with:
  - **Sankey diagrams** to visualize traffic flow between zones
  - **Heatmaps** for zone-to-zone communication density
- ⚡ **Fast CLI** — Powered by **Typer** for clean, scriptable, CI-friendly execution.
- 📁 **Portable & reproducible** — Everything is plain CSV + Python; no database required.

---

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  assets.csv  │     │  flows.csv   │     │  policy.csv  │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            ▼
                ┌───────────────────────┐
                │  Pydantic Validation  │
                └───────────┬───────────┘
                            ▼
                ┌───────────────────────┐
                │  Segmentation Engine  │
                │ (evaluate each flow)  │
                └───────────┬───────────┘
                            ▼
            ┌───────────────┴───────────────┐
            ▼                               ▼
   ┌─────────────────┐            ┌────────────────────┐
   │   CLI (Typer)   │            │  Web UI (Streamlit)│
   │  tabular output │            │ Sankey / Heatmap   │
   └─────────────────┘            └────────────────────┘
```


## 🚀 Installation

### Prerequisites
- Python **3.10+**

### Install from source
bash
# Clone the repository
git clone https://github.com/<your-username>/ot-segmentation-simulator.git
cd ot-segmentation-simulator

# Install (editable mode recommended for development)
pip install -e .

This installs the `ot-sim` command and its dependencies (`pandas`, `pydantic`, `typer`, `streamlit`, `plotly`).

---

## 💻 Usage

### 1. Command-Line Interface (CLI)

Run a full segmentation analysis against your model:

bash
ot-sim --assets .\data\sample_assets.csv --flows .\data\sample_flows.csv --policy .\data\sample_policy.csv

**Options:**

| Flag        | Description                                   | Required |
|-------------|-----------------------------------------------|:--------:|
| `--assets`  | Path to the assets inventory CSV              | ✅       |
| `--flows`   | Path to the observed/intended flows CSV       | ✅       |
| `--policy`  | Path to the segmentation policy CSV           | ✅       |

The CLI validates all inputs and prints an evaluation of each flow against the defined policy.

### 2. Web Interface (Streamlit)

For interactive exploration and visualization:

bash
streamlit run webapp.py

Upload your `assets`, `flows`, and `policy` CSV files through the UI to render **Sankey flow diagrams** and **zone communication heatmaps** in a custom dark-themed dashboard.

---

## 📂 Input Data Schema

The engine expects three CSV files. Sample files are provided in the [`data/`](data/) directory.

### `assets.csv` — Asset Inventory
Defines each device and the zone it belongs to.

| Column     | Type   | Description                                      |
|------------|--------|--------------------------------------------------|
| `asset_id` | string | Unique identifier for the asset                  |
| `name`     | string | Human-readable asset name                        |
| `zone`     | string | Segmentation zone (e.g., `L1_Control`, `IT_DMZ`) |
| `ip`       | string | IP address of the asset                          |

### `flows.csv` — Communication Flows
Represents traffic between assets.

| Column        | Type   | Description                         |
|---------------|--------|-------------------------------------|
| `src_asset`   | string | Source `asset_id`                   |
| `dst_asset`   | string | Destination `asset_id`              |
| `port`        | int    | Destination port                    |
| `protocol`    | string | Protocol (e.g., `TCP`, `Modbus`)    |

### `policy.csv` — Segmentation Policy
Defines allowed communication between zones (conduits).

| Column       | Type   | Description                              |
|--------------|--------|------------------------------------------|
| `src_zone`   | string | Source zone                              |
| `dst_zone`   | string | Destination zone                         |
| `port`       | int    | Allowed port (or `*` for any)            |
| `action`     | string | `allow` or `deny`                        |

> 💡 Any flow not explicitly permitted by policy is flagged as a **VIOLATION** (default-deny model).

---

## 📊 Example Output

```
$ ot-sim --assets data/sample_assets.csv --flows data/sample_flows.csv --policy data/sample_policy.csv

┏━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━┓
┃ Source    ┃ Dest      ┃ Port ┃ Result     ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━┩
│ HMI-01    │ PLC-01    │ 502  │ ✅ ALLOWED  │
│ WKS-IT-04 │ PLC-01    │ 502  │ ❌ VIOLATION│
│ ENG-01    │ HIST-01   │ 1433 │ ✅ ALLOWED  │
└───────────┴───────────┴──────┴────────────┘

Summary: 2 allowed · 0 denied · 1 violation
```
---

## 🗺️ Roadmap

- [x] **v0.1** — Core CSV modeling, Pydantic validation, policy evaluation engine, CLI, Streamlit visualization.
- [ ] **v0.2** — **Attack Path Discovery**: graph-based reachability analysis to surface multi-hop lateral movement paths across zones.
- [ ] **v0.3** — IEC 62443 zone/conduit compliance scoring & reporting.
- [ ] **v0.4** — Import from real network sources (firewall configs, flow logs).
- [ ] **v0.5** — Export reports (PDF/HTML) for audit evidence.

---


## 🧰 Tech Stack

| Layer         | Technology            |
|---------------|-----------------------|
| Language      | Python 3.10+          |
| CLI           | Typer                 |
| Data / Models | pandas, Pydantic      |
| Web UI        | Streamlit             |
| Visualization | Plotly (Sankey, Heatmap) |

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Please open an issue to discuss significant changes before submitting a PR.

bash
# Dev setup
pip install -e ".[dev]"

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

## 👤 Author

Built as a demonstration of **OT/ICS network security engineering** and **security tooling development**.

> If you're working on OT security, ICS defense, or DevSecOps tooling — feel free to reach out or open an issue.
`
