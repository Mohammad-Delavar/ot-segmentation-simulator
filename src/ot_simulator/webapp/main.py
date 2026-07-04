# src/ot_simulator/webapp.py
"""
Web UI for OT Simulator using Streamlit.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import tempfile
import os
import json
from datetime import datetime

from ot_simulator.core.loader import load_assets, load_flows, load_policy
from ot_simulator.core.simulator import Simulator
from ot_simulator.core.analyzer import Analyzer

# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS STYLING — FUTURE / ENTERPRISE THEME
# ═══════════════════════════════════════════════════════════════════════════════
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@500;700&family=JetBrains+Mono:wght@400;600&display=swap');

        :root {
            --bg: #05070d;
            --bg-elev-1: #0b1018;
            --bg-elev-2: #111824;
            --bg-elev-3: #161f2e;

            --panel: rgba(14, 20, 34, 0.96);
            --panel-soft: rgba(13, 19, 32, 0.94);
            --panel-alt: rgba(18, 26, 42, 0.96);

            --border-soft: rgba(255, 255, 255, 0.06);
            --border-mid: rgba(132, 164, 255, 0.18);
            --border-strong: rgba(77, 163, 255, 0.40);

            --text-1: #f5f7ff;
            --text-2: #ccd5e8;
            --text-3: #9aa6c2;
            --text-muted: #76839c;

            --accent: #4da3ff;
            --accent-soft: rgba(77, 163, 255, 0.14);
            --accent-2: #79c0ff;
            --accent-strong: #66b3ff;

            --success: #27c281;
            --success-soft: rgba(39, 194, 129, 0.14);
            --warning: #ffb020;
            --warning-soft: rgba(255, 176, 32, 0.14);
            --danger: #ef5b5b;
            --danger-soft: rgba(239, 91, 91, 0.14);

            --shadow-sm: 0 6px 16px rgba(0, 0, 0, 0.25);
            --shadow-md: 0 12px 30px rgba(0, 0, 0, 0.30);
            --shadow-lg: 0 18px 40px rgba(0, 0, 0, 0.35);
            --shadow-focus: 0 0 0 3px rgba(77, 163, 255, 0.18);

            --radius-xl: 24px;
            --radius-lg: 18px;
            --radius-md: 14px;
            --radius-sm: 10px;
            --radius-xs: 8px;

            --ease: cubic-bezier(0.16, 1, 0.3, 1);
            --dur-fast: 0.16s;
            --dur-med: 0.22s;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
            color: var(--text-2);
        }

        code, pre, .stCode, kbd {
            font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
        }

        /* ============ APP BACKGROUND ============ */
        .stApp {
            color: var(--text-2);
            background:
                radial-gradient(circle at 12% 10%, rgba(77,163,255,0.10), transparent 35%),
                radial-gradient(circle at 88% 20%, rgba(0,229,255,0.08), transparent 32%),
                radial-gradient(circle at 50% 100%, rgba(99,102,241,0.14), transparent 40%),
                linear-gradient(180deg, #04060c 0%, #05070d 30%, #05070d 100%);
            overflow-x: hidden;
        }

        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 0;
            background-image:
                radial-gradient(1px 1px at 10% 20%, rgba(255,255,255,0.55), transparent),
                radial-gradient(1px 1px at 40% 80%, rgba(138,180,255,0.55), transparent),
                radial-gradient(1px 1px at 80% 30%, rgba(255,255,255,0.45), transparent);
            background-size: 480px 480px;
            opacity: 0.15;
            animation: starfieldDrift 120s linear infinite;
            will-change: transform;
        }

        .stApp::after {
            content: "";
            position: fixed;
            width: 380px;
            height: 380px;
            top: -140px;
            right: -160px;
            border-radius: 50%;
            pointer-events: none;
            z-index: 0;
            background:
                radial-gradient(circle,
                    rgba(0,0,0,1) 0%,
                    rgba(0,0,0,1) 16%,
                    rgba(8,12,22,0.96) 26%,
                    rgba(77,163,255,0.28) 40%,
                    rgba(77,163,255,0.10) 55%,
                    rgba(0,0,0,0) 72%);
            opacity: 0.65;
            filter: blur(1px);
        }

        @keyframes starfieldDrift {
            from { transform: translate3d(0,0,0); }
            to   { transform: translate3d(-120px, -70px, 0); }
        }

        .stApp > div { position: relative; z-index: 1; }

        #MainMenu, header, footer { visibility: hidden; }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2.5rem;
            max-width: 1480px;
        }

        /* ============ MAIN SHELL ============ */
        .main-shell {
            position: relative;
            background: linear-gradient(180deg, rgba(255,255,255,0.015), rgba(255,255,255,0.006));
            border: 1px solid var(--border-soft);
            border-radius: var(--radius-xl);
            padding: 22px;
            box-shadow: var(--shadow-lg);
            backdrop-filter: blur(10px);
        }

        /* ============ HEADER ============ */
        .main-header {
            position: relative;
            padding: 28px 26px 22px 26px;
            margin-bottom: 24px;
            border-radius: 22px;
            background:
                linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)),
                linear-gradient(90deg, rgba(77,163,255,0.18), transparent 45%);
            border: 1px solid var(--border-soft);
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.06),
                0 12px 30px rgba(0,0,0,0.34);
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .main-header::before {
            content: "";
            position: absolute;
            left: 0; top: 0;
            width: 100px; height: 2px;
            background: linear-gradient(90deg, var(--accent), transparent);
            opacity: 0.9;
        }

        .main-header h1 {
            margin: 0;
            font-family: 'Orbitron', sans-serif;
            font-size: 2.3rem;
            line-height: 1.1;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            background: linear-gradient(120deg, #f5f7ff 0%, #d3e6ff 25%, #9cc5ff 55%, #c4b5fd 85%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .main-header-sub {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            gap: 10px;
            align-items: baseline;
        }

        .main-header p {
            margin: 0;
            color: var(--text-muted);
            font-size: 0.95rem;
            max-width: 720px;
        }

        .main-header-tag {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: var(--accent-2);
            background: rgba(9,19,36,0.92);
            border-radius: 999px;
            padding: 4px 12px;
            border: 1px solid rgba(77,163,255,0.35);
        }

        /* ============ SECTION TITLE ============ */
        .section-title {
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 6px 0 14px 0;
            color: var(--text-1);
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.16em;
        }

        .section-title::before {
            content: "";
            width: 18px; height: 2px;
            background: var(--accent);
            border-radius: 999px;
        }

        /* ============ SIDEBAR ============ */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #060913 0%, #080c16 100%);
            border-right: 1px solid var(--border-soft);
        }

        section[data-testid="stSidebar"] .block-container {
            padding-top: 1.4rem;
        }

        section[data-testid="stSidebar"] * {
            color: var(--text-2);
        }

        /* ============ METRICS ============ */
        div[data-testid="stMetric"] {
            position: relative;
            padding: 1.2rem 1.1rem;
            border-radius: 18px;
            overflow: hidden;
            background:
                linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)),
                var(--panel-soft);
            border: 1px solid var(--border-soft);
            box-shadow: var(--shadow-md);
            transition: border-color var(--dur-med) var(--ease), transform var(--dur-med) var(--ease), box-shadow var(--dur-med) var(--ease);
        }

        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border-color: var(--border-strong);
            box-shadow: 0 14px 28px rgba(0,0,0,0.32);
        }

        div[data-testid="stMetric"] label {
            color: var(--text-muted) !important;
            font-size: 0.72rem !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 0.12em;
        }

        div[data-testid="stMetricValue"] {
            color: var(--text-1) !important;
            font-family: 'Orbitron', sans-serif !important;
            font-size: 1.9rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.02em;
        }

        div[data-testid="stMetricDelta"] {
            font-weight: 600 !important;
            color: var(--text-3) !important;
        }

        /* ============ TABS ============ */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            padding: 8px;
            background: rgba(10,15,28,0.9);
            border: 1px solid var(--border-soft);
            border-radius: 16px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
        }

        .stTabs [data-baseweb="tab"] {
            min-height: 44px;
            padding: 0 16px;
            border-radius: 10px;
            background: transparent;
            color: var(--text-muted);
            font-weight: 600;
            transition: all var(--dur-fast) var(--ease);
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(255,255,255,0.03);
            color: var(--text-1);
        }

        .stTabs [aria-selected="true"] {
            color: var(--text-1) !important;
            background: linear-gradient(180deg, rgba(77,163,255,0.25), rgba(77,163,255,0.15)) !important;
            border: 1px solid rgba(77,163,255,0.25) !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
        }

        /* ============ INPUTS (text, number, textarea, select) ============ */
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        div[data-baseweb="base-input"],
        .stTextInput > div > div > input,
        .stNumberInput input,
        .stTextArea textarea {
            background: var(--panel) !important;
            color: var(--text-1) !important;
            border: 1px solid var(--border-soft) !important;
            border-radius: 12px !important;
            box-shadow: none !important;
            transition: border-color var(--dur-fast) var(--ease), box-shadow var(--dur-fast) var(--ease);
        }

        .stTextInput > label,
        .stNumberInput > label,
        .stSelectbox > label,
        .stTextArea > label,
        .stMultiSelect > label,
        .stSlider > label,
        .stDateInput > label,
        .stTimeInput > label {
            color: var(--text-2) !important;
            font-weight: 600 !important;
        }

        .stTextInput input:focus,
        .stNumberInput input:focus,
        .stTextArea textarea:focus {
            border-color: var(--border-strong) !important;
            box-shadow: var(--shadow-focus) !important;
        }

        /* Selectbox dropdown popover */
        div[data-baseweb="popover"] div[role="listbox"] {
            background: var(--panel) !important;
            border: 1px solid var(--border-mid) !important;
            border-radius: 12px !important;
            box-shadow: var(--shadow-lg) !important;
        }

        div[data-baseweb="popover"] li {
            color: var(--text-2) !important;
        }

        div[data-baseweb="popover"] li:hover,
        div[data-baseweb="popover"] li[aria-selected="true"] {
            background: var(--accent-soft) !important;
            color: var(--text-1) !important;
        }

        /* Multiselect chips */
        span[data-baseweb="tag"] {
            background: var(--accent-soft) !important;
            border: 1px solid var(--border-mid) !important;
            color: var(--accent-2) !important;
            border-radius: 8px !important;
        }

        /* ============ SLIDER ============ */
        div[data-testid="stSlider"] div[role="slider"] {
            background: var(--accent) !important;
            box-shadow: 0 0 0 4px rgba(77,163,255,0.18) !important;
        }

        div[data-testid="stSlider"] > div > div > div {
            background: linear-gradient(90deg, var(--accent), var(--accent-2)) !important;
        }

        div[data-testid="stTickBarMin"],
        div[data-testid="stTickBarMax"] {
            color: var(--text-muted) !important;
        }

        /* ============ TOGGLE / CHECKBOX / RADIO ============ */
        .stCheckbox label, .stRadio label { color: var(--text-2) !important; }

        div[data-testid="stCheckbox"] label span[data-testid="stMarkdownContainer"] p,
        div[data-testid="stRadio"] label span[data-testid="stMarkdownContainer"] p {
            color: var(--text-2);
        }

        label[data-baseweb="checkbox"] div:first-child,
        label[data-baseweb="radio"] div:first-child {
            background: var(--panel) !important;
            border-color: var(--border-mid) !important;
        }

        div[data-testid="stToggle"] label div[data-checked="true"] {
            background: var(--accent) !important;
        }

        /* ============ PROGRESS BAR ============ */
        div[data-testid="stProgress"] > div > div {
            background: var(--bg-elev-2) !important;
            border-radius: 999px;
        }

        div[data-testid="stProgress"] > div > div > div {
            background: linear-gradient(90deg, var(--accent), var(--accent-2)) !important;
            border-radius: 999px;
        }

        /* ============ BUTTONS ============ */
        .stButton > button {
            height: 44px;
            padding: 0 20px;
            border-radius: 12px;
            border: 1px solid rgba(77,163,255,0.25);
            background: linear-gradient(180deg, #1b6fd1 0%, #155bb0 100%);
            color: #ffffff;
            font-size: 0.9rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            box-shadow: 0 10px 22px rgba(21,91,176,0.25);
            transition: transform var(--dur-fast) var(--ease), box-shadow var(--dur-fast) var(--ease), filter var(--dur-fast) var(--ease);
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            filter: brightness(1.05);
            box-shadow: 0 14px 26px rgba(21,91,176,0.30);
        }

        .stButton > button:active { transform: translateY(0); }

        .stButton > button:focus-visible {
            outline: none;
            box-shadow: var(--shadow-focus), 0 10px 22px rgba(21,91,176,0.25);
        }

        .stButton > button:disabled {
            opacity: 0.45;
            cursor: not-allowed;
            filter: grayscale(0.3);
        }

        /* Secondary button variant (kind="secondary") */
        .stButton > button[kind="secondary"] {
            background: var(--panel-alt);
            color: var(--text-1);
            border: 1px solid var(--border-soft);
            box-shadow: none;
        }

        /* Download button */
        .stDownloadButton > button {
            height: 44px;
            padding: 0 18px;
            border-radius: 12px;
            border: 1px solid var(--border-soft);
            background: var(--panel-alt);
            color: var(--text-1);
            font-weight: 600;
            transition: border-color var(--dur-fast) var(--ease), transform var(--dur-fast) var(--ease);
        }

        .stDownloadButton > button:hover {
            border-color: var(--border-strong);
            transform: translateY(-1px);
        }

        /* ============ DATAFRAME / TABLE ============ */
        div[data-testid="stDataFrame"] {
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid var(--border-soft);
            background: var(--panel-soft);
            box-shadow: var(--shadow-md);
        }

        div[data-testid="stDataFrame"] table { color: var(--text-2) !important; }

        div[data-testid="stDataFrame"] thead tr th {
            background: #151c27 !important;
            color: var(--text-1) !important;
            border-bottom: 1px solid rgba(255,255,255,0.06) !important;
            font-size: 0.72rem !important;
            letter-spacing: 0.10em;
            text-transform: uppercase;
        }

        div[data-testid="stDataFrame"] tbody tr:hover td {
            background: rgba(77,163,255,0.06) !important;
        }

        div[data-testid="stTable"] table {
            background: var(--panel-soft) !important;
            color: var(--text-2) !important;
            border-radius: 12px;
            overflow: hidden;
        }

        /* ============ FILE UPLOADER ============ */
        .stFileUploader {
            border-radius: 16px;
            border: 1px dashed rgba(77,163,255,0.30);
            background: var(--panel-soft);
            padding: 16px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
            transition: border-color var(--dur-med) var(--ease), box-shadow var(--dur-med) var(--ease), background var(--dur-med) var(--ease);
        }

        .stFileUploader:hover {
            border-color: var(--border-strong);
            background: var(--panel);
            box-shadow: 0 0 20px rgba(77,163,255,0.14);
        }

        .stFileUploader section[data-testid="stFileUploadDropzone"] button {
            background: var(--panel-alt) !important;
            color: var(--text-1) !important;
            border: 1px solid var(--border-soft) !important;
        }

        /* ============ EXPANDER ============ */
        .streamlit-expanderHeader,
        div[data-testid="stExpander"] summary {
            background: var(--panel-soft);
            border: 1px solid var(--border-soft);
            border-radius: 12px;
            color: var(--text-1);
        }

        div[data-testid="stExpander"] {
            border: 1px solid var(--border-soft);
            border-radius: 14px;
            background: var(--panel-soft);
            box-shadow: var(--shadow-sm);
        }

        /* ============ CONTAINER WITH BORDER (st.container(border=True)) ============ */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid var(--border-soft) !important;
            border-radius: 16px !important;
            background: var(--panel-soft);
            box-shadow: var(--shadow-sm);
        }

        /* ============ ALERTS (native st.info/success/warning/error) ============ */
        div[data-testid="stAlert"] {
            border-radius: 14px !important;
            border: 1px solid var(--border-soft) !important;
            box-shadow: var(--shadow-sm);
        }

        /* ============ CUSTOM ALERT CARDS ============ */
        .alert-critical, .alert-warning, .alert-success, .alert-info {
            position: relative;
            padding: 16px 18px;
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.06);
            background: var(--panel);
            box-shadow: var(--shadow-md);
            overflow: hidden;
        }

        .alert-critical::before, .alert-warning::before,
        .alert-success::before, .alert-info::before {
            content: "";
            position: absolute;
            left: 0; top: 0; bottom: 0;
            width: 3px;
        }

        .alert-critical { background: linear-gradient(180deg, var(--danger-soft), rgba(239,91,91,0.04)); color: #ffd7dd; }
        .alert-critical::before { background: var(--danger); }

        .alert-warning { background: linear-gradient(180deg, var(--warning-soft), rgba(255,176,32,0.04)); color: #ffe9c1; }
        .alert-warning::before { background: var(--warning); }

        .alert-success { background: linear-gradient(180deg, var(--success-soft), rgba(39,194,129,0.04)); color: #c7f5df; }
        .alert-success::before { background: var(--success); }

        .alert-info { background: linear-gradient(180deg, var(--accent-soft), rgba(77,163,255,0.04)); color: #d4e9ff; }
        .alert-info::before { background: var(--accent); }

        /* ============ RISK BAR ============ */
        .risk-bar-container {
            position: relative;
            height: 40px;
            border-radius: 999px;
            overflow: hidden;
            background: #101621;
            border: 1px solid var(--border-soft);
            box-shadow: inset 0 2px 6px rgba(0,0,0,0.35);
        }

        .risk-bar-fill {
            height: 100%;
            border-radius: 999px;
            position: relative;
            transition: width 0.5s var(--ease);
        }

        .risk-bar-labels {
            display: flex;
            justify-content: space-between;
            margin-top: 8px;
            color: var(--text-muted);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.10em;
            text-transform: uppercase;
        }

        /* ============ INFO CARD ============ */
        .info-card {
            background: var(--panel-soft);
            border: 1px solid var(--border-soft);
            border-radius: 16px;
            padding: 18px;
            box-shadow: var(--shadow-md);
            transition: transform var(--dur-med) var(--ease), box-shadow var(--dur-med) var(--ease), border-color var(--dur-med) var(--ease);
        }

        .info-card:hover {
            transform: translateY(-2px);
            border-color: var(--border-mid);
            box-shadow: 0 14px 28px rgba(0,0,0,0.30);
        }

        .info-card h4 {
            margin-top: 0;
            margin-bottom: 10px;
            color: var(--text-1);
            font-size: 0.9rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .info-card p, .info-card li {
            color: var(--text-3);
            font-size: 0.9rem;
            line-height: 1.7;
        }

        .section-divider {
            height: 1px;
            margin: 24px 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
        }

        /* ============ CODE BLOCK ============ */
        div[data-testid="stCodeBlock"] {
            border-radius: 14px !important;
            border: 1px solid var(--border-soft) !important;
            background: #0a0e18 !important;
            box-shadow: var(--shadow-sm);
        }

        /* ============ TOAST ============ */
        div[data-testid="stToast"] {
            background: var(--panel) !important;
            border: 1px solid var(--border-mid) !important;
            border-radius: 14px !important;
            box-shadow: var(--shadow-lg) !important;
            color: var(--text-1) !important;
        }

        /* ============ TOOLTIP ============ */
        div[data-testid="stTooltipIcon"] svg { color: var(--text-muted) !important; }

        /* ============ SPINNER ============ */
        .stSpinner > div { border-top-color: var(--accent) !important; }

        /* ============ SCROLLBAR ============ */
        ::-webkit-scrollbar { width: 10px; height: 10px; }
        ::-webkit-scrollbar-track { background: #05070d; }
        ::-webkit-scrollbar-thumb { border-radius: 999px; background: #243246; }
        ::-webkit-scrollbar-thumb:hover { background: #324760; }

        /* ============ FOCUS ACCESSIBILITY (global) ============ */
        a:focus-visible,
        button:focus-visible,
        input:focus-visible,
        [role="button"]:focus-visible {
            outline: none;
            box-shadow: var(--shadow-focus);
        }

        /* ============ MOBILE ============ */
        @media (max-width: 992px) {
            .main-header { padding: 22px 18px 18px 18px; }
            .main-header h1 { font-size: 1.7rem; letter-spacing: 0.10em; }
            .block-container { padding-top: 1.4rem; }
            div[data-testid="stMetricValue"] { font-size: 1.6rem !important; }
            .main-shell { padding: 14px; }
        }

        @media (max-width: 600px) {
            .main-header h1 { font-size: 1.35rem; }
            .info-card { padding: 14px; }
        }

        /* ============ PRINT (for report export) ============ */
        @media print {
            .stApp::before, .stApp::after { display: none !important; }
            .main-shell { box-shadow: none !important; border: none !important; }
            section[data-testid="stSidebar"] { display: none !important; }
            body, .stApp { background: #ffffff !important; color: #000 !important; }
        }

        /* ============ REDUCED MOTION ============ */
        @media (prefers-reduced-motion: reduce) {
            .stApp::before { animation: none !important; }
            * {
                scroll-behavior: auto !important;
                transition-duration: 0.001ms !important;
                animation-duration: 0.001ms !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)



# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════
def get_risk_color(score: float) -> tuple[str, str]:
    """Get color and label for risk score."""
    if score < 30:
        return "#2ed573", "LOW"
    elif score < 60:
        return "#ffc300", "MEDIUM"
    else:
        return "#ff4757", "HIGH"


def get_risk_gradient(score: float) -> str:
    """Get gradient for risk bar based on score."""
    if score < 30:
        return "linear-gradient(90deg, #2ed573 0%, #00a8ff 100%)"
    elif score < 60:
        return "linear-gradient(90deg, #ffc300 0%, #ff6348 100%)"
    else:
        return "linear-gradient(90deg, #ff4757 0%, #c72c41 100%)"


def create_traffic_sankey(flows, assets, result):
    """Create Sankey diagram for traffic flows."""
    asset_map = {a.id: a.name for a in assets}
    
    source_ids = []
    target_ids = []
    values = []
    colors = []
    
    for flow in flows[:50]:  # Limit to 50 flows for clarity
        if flow.source_asset_id in asset_map and flow.destination_asset_id in asset_map:
            source_ids.append(flow.source_asset_id)
            target_ids.append(flow.destination_asset_id)
            values.append(1)
            
            is_blocked = flow in result.blocked_flows
            colors.append('rgba(255,71,87,0.4)' if is_blocked else 'rgba(46,213,115,0.4)')
    
    unique_nodes = list(set(source_ids + target_ids))
    node_map = {node: i for i, node in enumerate(unique_nodes)}
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="rgba(100,120,200,0.5)", width=0.5),
            label=[asset_map.get(node, node) for node in unique_nodes],
            color='rgba(79,107,255,0.7)'
        ),
        link=dict(
            source=[node_map[s] for s in source_ids],
            target=[node_map[t] for t in target_ids],
            value=values,
            color=colors
        )
    )])
    
    fig.update_layout(
        font=dict(size=10, color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig


def create_zone_heatmap(flows, assets, result):
    """Create zone-to-zone traffic heatmap."""
    zone_map = {a.id: a.zone for a in assets}
    
    zones = sorted(set(zone_map.values()))
    matrix = [[0 for _ in zones] for _ in zones]
    
    for flow in flows:
        src_zone = zone_map.get(flow.source_asset_id)
        dst_zone = zone_map.get(flow.destination_asset_id)
        
        if src_zone and dst_zone:
            src_idx = zones.index(src_zone)
            dst_idx = zones.index(dst_zone)
            matrix[src_idx][dst_idx] += 1
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=zones,
        y=zones,
        colorscale='Blues',
        text=matrix,
        texttemplate='%{text}',
        textfont={"size": 10},
        hoverongaps=False
    ))
    
    fig.update_layout(
        xaxis_title='Destination Zone',
        yaxis_title='Source Zone',
        font=dict(color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return fig


def create_criticality_chart(flows):
    """Create criticality distribution chart."""
    crit_counts = {}
    for flow in flows:
        crit = flow.criticality.value
        crit_counts[crit] = crit_counts.get(crit, 0) + 1
    
    colors = {
        'CRITICAL': '#ff4757',
        'HIGH': '#ffc300',
        'MEDIUM': '#00a8ff',
        'LOW': '#2ed573'
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(crit_counts.keys()),
            y=list(crit_counts.values()),
            marker_color=[colors.get(k, '#8b95b0') for k in crit_counts.keys()],
            text=list(crit_counts.values()),
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        xaxis_title='Criticality Level',
        yaxis_title='Flow Count',
        font=dict(color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=300,
        margin=dict(l=40, r=20, t=20, b=40)
    )
    
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    st.set_page_config(
        page_title="OT Segmentation Simulator",
        page_icon="🏭",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    inject_custom_css()
    
    # ─── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="main-header">
        <span class="main-header-tag">OT THREAT SEGMENTATION PLATFORM</span>
        <h1>OT Network Segmentation Simulator</h1>
        <div class="main-header-sub">
            <p>
                Scenario-driven segmentation and impact analysis engine for industrial control
                networks. Evaluate policy changes before deployment, reduce unintended downtime,
                and quantify exposure across Purdue levels By Mohammad Delavar.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ─── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 📁 Data Input")
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        assets_file = st.file_uploader(
            "📡 Assets Inventory",
            type="csv",
            help="Upload CSV containing asset inventory with IP, type, zone, criticality"
        )
        
        flows_file = st.file_uploader(
            "🔀 Traffic Flows",
            type="csv",
            help="Upload CSV containing network traffic flows to simulate"
        )
        
        policy_file = st.file_uploader(
            "🛡️ Segmentation Policy",
            type="csv",
            help="Upload CSV containing firewall/segmentation policy rules"
        )
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            strict_mode = st.checkbox("⚙️ Strict", value=False)
        with col_s2:
            show_details = st.checkbox("📊 Details", value=True)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        run_btn = st.button(
            "🚀 Run Simulation",
            type="primary",
            use_container_width=True
        )
        
        st.markdown("""
        <div class="info-card">
            <h4>💡 Guidelines</h4>
            <ul>
                <li>Use Purdue Model zones (L0–L5)</li>
                <li>Define criticality levels consistently</li>
                <li>Model realistic segmentation rules</li>
                <li>Review blocked flows before enforcement</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # ─── Main Content ──────────────────────────────────────────────────────────
    if run_btn:
        if not all([assets_file, flows_file, policy_file]):
            st.markdown("""
            <div class="alert-warning">
                <strong>⚠️ Missing Data Files</strong><br>
                Please upload all three CSV files: Assets, Flows, and Policy.
            </div>
            """, unsafe_allow_html=True)
            return
        
        # ─── Load Data ──────────────────────────────────────────────────────────
        with st.spinner("📊 Loading and validating data..."):
            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
                tmp_path = tmp.name
            
            assets_df = pd.read_csv(assets_file)
            flows_df = pd.read_csv(flows_file)
            policy_df = pd.read_csv(policy_file)
            
            for name, df in [("assets", assets_df), ("flows", flows_df), ("policy", policy_df)]:
                df.to_csv(f"{tmp_path}_{name}.csv", index=False)
            
            asset_result = load_assets(f"{tmp_path}_assets.csv", strict=strict_mode)
            flow_result = load_flows(f"{tmp_path}_flows.csv", strict=strict_mode)
            policy_result = load_policy(f"{tmp_path}_policy.csv", strict=strict_mode)
            
            for f in [f"{tmp_path}_assets.csv", f"{tmp_path}_flows.csv", f"{tmp_path}_policy.csv"]:
                if os.path.exists(f):
                    os.remove(f)
        
        # ─── Run Simulation ────────────────────────────────────────────────────
        with st.spinner("⚙️ Running simulation engine..."):
            assets = asset_result.items
            flows = flow_result.items
            policy = policy_result.items[0] if policy_result.items else None
            
            if not policy:
                st.markdown("""
                <div class="alert-critical">
                    <strong>🚨 Policy Load Failed</strong><br>
                    No valid policy rules found. Check your policy CSV file format.
                </div>
                """, unsafe_allow_html=True)
                return
            
            sim = Simulator(assets, flows, policy)
            result = sim.simulate()
            
            analyzer = Analyzer(result, assets, flows)
            report = analyzer.analyze()
        
        # ─── Results Display ────────────────────────────────────────────────────
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("## 📊 Simulation Results")
        
        # ─── Metrics Row ────────────────────────────────────────────────────────
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Allowed Flows",
                value=f"{len(result.allowed_flows):,}",
                delta="Traffic OK",
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                label="Blocked Flows",
                value=f"{len(result.blocked_flows):,}",
                delta=f"−{len(result.blocked_flows)}",
                delta_color="inverse"
            )
        
        with col3:
            critical_blocked = sum(1 for f in result.blocked_flows if f.criticality.value == "CRITICAL")
            st.metric(
                label="Critical Blocked",
                value=critical_blocked,
                delta="Needs Review" if critical_blocked > 0 else "Clear",
                delta_color="inverse" if critical_blocked > 0 else "normal"
            )
        
        with col4:
            risk_color, risk_label = get_risk_color(result.risk_score)
            st.metric(
                label="Risk Score",
                value=f"{result.risk_score:.0f}/100",
                delta=risk_label,
                delta_color="inverse" if result.risk_score > 50 else "normal"
            )
        
        # ─── Risk Bar ──────────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="risk-bar-container">
            <div class="risk-bar-fill" style="width: {result.risk_score}%; background: {get_risk_gradient(result.risk_score)};">
            </div>
        </div>
        <div class="risk-bar-labels">
            <span>🟢 Safe (0–30)</span>
            <span>🟡 Warning (30–60)</span>
            <span>🔴 Critical (60–100)</span>
        </div>
        """, unsafe_allow_html=True)
        
        # ─── Alerts Section ────────────────────────────────────────────────────
        if report.critical_issues or report.warnings:
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            
            col_alert1, col_alert2 = st.columns(2)
            
            with col_alert1:
                if report.critical_issues:
                    st.markdown("### 🚨 Critical Issues")
                    for issue in report.critical_issues:
                        st.markdown(f'<div class="alert-critical"><strong>CRITICAL:</strong> {issue}</div>', unsafe_allow_html=True)
            
            with col_alert2:
                if report.warnings:
                    st.markdown("### ⚠️ Warnings")
                    for warn in report.warnings:
                        st.markdown(f'<div class="alert-warning"><strong>WARNING:</strong> {warn}</div>', unsafe_allow_html=True)
        
        # ─── Recommendations ───────────────────────────────────────────────────
        if report.recommendations:
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown("### Security Recommendations")
            
            for i, rec in enumerate(report.recommendations, 1):
                st.markdown(f'<div class="alert-info"><strong>{i}.</strong> {rec}</div>', unsafe_allow_html=True)
        
        # ─── Visualizations ────────────────────────────────────────────────────
        if show_details and len(flows) > 0:
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown("## 📈 Visual Analytics")
            
            tab1, tab2, tab3 = st.tabs(["🔄 Traffic Flow", "🗺️ Zone Heatmap", "📊 Criticality"])
            
            with tab1:
                st.markdown("#### Network Traffic Sankey Diagram")
                try:
                    sankey_fig = create_traffic_sankey(flows, assets, result)
                    st.plotly_chart(sankey_fig, use_container_width=True)
                except Exception:
                    st.info("Traffic visualization requires more data points.")
            
            with tab2:
                st.markdown("#### Zone-to-Zone Traffic Matrix")
                try:
                    heatmap_fig = create_zone_heatmap(flows, assets, result)
                    st.plotly_chart(heatmap_fig, use_container_width=True)
                except Exception:
                    st.info("Zone heatmap requires zone information.")
            
            with tab3:
                st.markdown("#### Flow Criticality Distribution")
                try:
                    crit_fig = create_criticality_chart(flows)
                    st.plotly_chart(crit_fig, use_container_width=True)
                except Exception:
                    st.info("Criticality chart requires criticality data.")
        
        # ─── Data Tables ───────────────────────────────────────────────────────
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("##  Detailed Data")
        
        tab_blocked, tab_allowed, tab_assets = st.tabs(["🚫 Blocked Flows", "✅ Allowed Flows", "📡 Assets"])
        
        with tab_blocked:
            if result.blocked_flows:
                blocked_data = [{
                    "Flow ID": f.id,
                    "Source": f.source_asset_id,
                    "Destination": f.destination_asset_id,
                    "Protocol": f.protocol,
                    "Port": f.port,
                    "Criticality": f.criticality.value,
                    "Description": f.description or "N/A"
                } for f in result.blocked_flows]
                st.dataframe(pd.DataFrame(blocked_data), use_container_width=True, height=400)
            else:
                st.markdown('<div class="alert-success">✅ No blocked flows detected.</div>', unsafe_allow_html=True)
        
        with tab_allowed:
            if result.allowed_flows:
                allowed_data = [{
                    "Flow ID": f.id,
                    "Source": f.source_asset_id,
                    "Destination": f.destination_asset_id,
                    "Protocol": f.protocol,
                    "Port": f.port,
                    "Criticality": f.criticality.value
                } for f in result.allowed_flows]
                st.dataframe(pd.DataFrame(allowed_data), use_container_width=True, height=400)
        
        with tab_assets:
            asset_data = [{
                "Asset ID": a.id,
                "Name": a.name,
                "Type": a.type,
                "IP Address": a.ip_address,
                "Zone": a.zone,
                "Criticality": a.criticality.value,
                "Purdue Level": a.purdue_level.value
            } for a in assets]
            st.dataframe(pd.DataFrame(asset_data), use_container_width=True, height=400)
        
        # ─── Export Section ────────────────────────────────────────────────────
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("## 📥 Export Report")
        
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            report_json = json.dumps(report.model_dump(), indent=2)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label=" Download JSON Report",
                data=report_json,
                file_name=f"ot_simulation_report_{timestamp}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col_exp2:
            # Create CSV export for blocked flows
            if result.blocked_flows:
                blocked_csv_data = [{
                    "Flow ID": f.id,
                    "Source Asset": f.source_asset_id,
                    "Destination Asset": f.destination_asset_id,
                    "Protocol": f.protocol,
                    "Port": f.port,
                    "Criticality": f.criticality.value,
                    "Description": f.description or "N/A"
                } for f in result.blocked_flows]
                
                blocked_df = pd.DataFrame(blocked_csv_data)
                blocked_csv = blocked_df.to_csv(index=False)
                
                st.download_button(
                    label=" Download Blocked Flows CSV",
                    data=blocked_csv,
                    file_name=f"blocked_flows_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("No blocked flows to export.")
        
        # ─── Summary Stats ─────────────────────────────────────────────────────
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("##  Summary Statistics")
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.markdown("""
            <div class="info-card">
                <h4>📡 Asset Statistics</h4>
                <ul>
                    <li>Total Assets: {total_assets}</li>
                    <li>Unique Zones: {unique_zones}</li>
                    <li>Critical Assets: {critical_assets}</li>
                </ul>
            </div>
            """.format(
                total_assets=len(assets),
                unique_zones=len(set(a.zone for a in assets)),
                critical_assets=sum(1 for a in assets if a.criticality.value == "CRITICAL")
            ), unsafe_allow_html=True)
        
        with col_stat2:
            st.markdown("""
            <div class="info-card">
                <h4>🔀 Flow Statistics</h4>
                <ul>
                    <li>Total Flows: {total_flows}</li>
                    <li>Allowed: {allowed_flows}</li>
                    <li>Blocked: {blocked_flows}</li>
                </ul>
            </div>
            """.format(
                total_flows=len(flows),
                allowed_flows=len(result.allowed_flows),
                blocked_flows=len(result.blocked_flows)
            ), unsafe_allow_html=True)
        
        with col_stat3:
            st.markdown("""
            <div class="info-card">
                <h4>🛡️ Policy Statistics</h4>
                <ul>
                    <li>Total Rules: {total_rules}</li>
                    <li>Default Action: {default_action}</li>
                    <li>Risk Score: {risk_score:.1f}/100</li>
                </ul>
            </div>
            """.format(
                total_rules=len(policy.rules),
                default_action=policy.default_action.value.upper(),
                risk_score=result.risk_score
            ), unsafe_allow_html=True)
        
        # ─── Footer ────────────────────────────────────────────────────────────
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; color: #8b95b0; font-size: 12px; padding: 20px;">
            <p>OT Network Segmentation Simulator | Built for Industrial Security Professionals</p>
            <p>Simulation completed at {timestamp}</p>
        </div>
        """.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
