from __future__ import annotations

import streamlit as st


def inject_global_styles() -> None:
    """Inject the shared premium dashboard stylesheet."""
    st.markdown(
        """
        <style>
            :root {
                --app-bg: #06080d;
                --content-bg: #0b0f14;
                --sidebar-bg: #080b10;
                --panel-bg: #0f131a;
                --panel-bg-alt: #151b23;
                --border: rgba(255, 255, 255, 0.08);
                --accent-soft: #18a66a;
                --accent-bright: #22c55e;
                --accent-teal: #8fb8aa;
                --positive: #22c55e;
                --negative: #ef4444;
                --text-muted: #93a1b2;
                --text-primary: #e6eaf0;
                --text-secondary: #cfd8e3;
                --text-label: #8fd9b3;
            }

            .stApp {
                background:
                    radial-gradient(circle at top right, rgba(24, 166, 106, 0.06), transparent 20%),
                    radial-gradient(circle at top left, rgba(143, 184, 170, 0.04), transparent 18%),
                    radial-gradient(circle at 50% -10%, rgba(255, 255, 255, 0.02), transparent 28%),
                    linear-gradient(180deg, var(--app-bg) 0%, var(--content-bg) 100%);
                color: var(--text-primary);
            }

            [data-testid="stDecoration"] {
                display: none;
            }

            header[data-testid="stHeader"] {
                background: rgba(0, 0, 0, 0) !important;
                border-bottom: none !important;
                box-shadow: none !important;
            }

            html, body, [data-testid="stAppViewContainer"] {
                background: var(--app-bg);
                scrollbar-color: #1f2a35 #080b10;
            }

            /* Ensure scroll containers inherit dark surfaces (prevents white edge bars). */
            [data-testid="stAppViewContainer"] > .main,
            [data-testid="stAppViewContainer"] > .main > div,
            [data-testid="stSidebar"],
            [data-testid="stSidebar"] > div {
                background: var(--app-bg);
                scrollbar-color: #1f2a35 #080b10;
            }

            ::-webkit-scrollbar {
                width: 10px;
                height: 10px;
            }

            ::-webkit-scrollbar-track {
                background: #080b10;
            }

            ::-webkit-scrollbar-thumb {
                background: #1f2a35;
                border-radius: 999px;
                border: 2px solid #080b10;
            }

            [data-testid="stAppViewContainer"]::-webkit-scrollbar-track,
            [data-testid="stAppViewContainer"] .main::-webkit-scrollbar-track,
            [data-testid="stSidebar"]::-webkit-scrollbar-track,
            [data-testid="stSidebar"] *::-webkit-scrollbar-track {
                background: #080b10;
            }

            [data-testid="stAppViewContainer"]::-webkit-scrollbar-thumb,
            [data-testid="stAppViewContainer"] .main::-webkit-scrollbar-thumb,
            [data-testid="stSidebar"]::-webkit-scrollbar-thumb,
            [data-testid="stSidebar"] *::-webkit-scrollbar-thumb {
                background: #1f2a35;
                border: 2px solid #080b10;
            }

            .block-container {
                max-width: 1500px;
                padding-top: 3.85rem;
                padding-bottom: 3rem;
                padding-left: 1.65rem;
                padding-right: 1.65rem;
            }

            .topbar {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                background: rgba(9, 12, 18, 0.78);
                border: 1px solid rgba(148, 163, 184, 0.08);
                border-radius: 16px;
                padding: 0.72rem 1rem;
                margin-bottom: 1rem;
                box-shadow:
                    0 10px 24px rgba(0, 0, 0, 0.12),
                    inset 0 1px 0 rgba(255, 255, 255, 0.03);
                backdrop-filter: blur(12px);
            }

            .topbar-brand {
                display: flex;
                flex-direction: column;
                gap: 0.16rem;
            }

            .topbar-title {
                color: var(--text-primary);
                font-size: 0.98rem;
                font-weight: 760;
                letter-spacing: -0.02em;
            }

            .topbar-copy {
                color: var(--text-muted);
                font-size: 0.78rem;
            }

            .topbar-status {
                display: flex;
                align-items: center;
                gap: 0.7rem;
            }

            .topbar-pill {
                color: var(--text-secondary);
                background: rgba(255, 255, 255, 0.025);
                border: 1px solid rgba(148, 163, 184, 0.10);
                border-radius: 999px;
                padding: 0.3rem 0.62rem;
                font-size: 0.72rem;
                font-weight: 700;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            }

            [data-testid="stSidebar"] {
                background:
                    linear-gradient(180deg, rgba(8, 16, 27, 0.98), rgba(8, 16, 27, 0.98));
                border-right: 1px solid var(--border);
                min-width: 288px;
                max-width: 288px;
                box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.02);
            }

            [data-testid="stSidebar"] .block-container {
                padding-top: 1.05rem;
                padding-left: 0.85rem;
                padding-right: 0.85rem;
                padding-bottom: 1.15rem;
            }

            [data-testid="stSidebar"] .stButton button {
                width: 100%;
                justify-content: flex-start;
                background: transparent;
                color: var(--text-muted);
                border: 1px solid transparent;
                border-radius: 10px;
                padding: 0.58rem 0.72rem;
                font-size: 0.9rem;
                font-weight: 560;
                box-shadow: none;
                transition: all 0.18s ease;
            }

            [data-testid="stSidebar"] .stButton button:hover {
                color: var(--text-primary);
                background: rgba(148, 163, 184, 0.05);
                border-color: rgba(148, 163, 184, 0.18);
            }

            [data-testid="stSidebar"] .active-nav div[data-testid="stButton"] button {
                color: var(--text-primary);
                background: rgba(255, 255, 255, 0.015);
                border-color: transparent;
            }

            .sidebar-brand {
                background:
                    radial-gradient(circle at top right, rgba(24, 166, 106, 0.08), transparent 35%),
                    linear-gradient(180deg, rgba(15, 19, 26, 0.98), rgba(21, 27, 35, 0.96));
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 0.95rem 0.95rem 0.9rem 0.95rem;
                margin-bottom: 1.1rem;
                box-shadow: 0 14px 34px rgba(0, 0, 0, 0.14);
            }

            .sidebar-brand-orb {
                width: 36px;
                height: 36px;
                border-radius: 12px;
                background:
                    linear-gradient(180deg, rgba(24, 166, 106, 0.22), rgba(143, 184, 170, 0.14));
                border: 1px solid rgba(148, 163, 184, 0.12);
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
            }

            .sidebar-brand-topline {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 0.65rem;
            }

            .sidebar-brand-chip {
                color: var(--text-label);
                background: rgba(124, 227, 177, 0.10);
                border: 1px solid rgba(124, 227, 177, 0.16);
                border-radius: 999px;
                padding: 0.22rem 0.55rem;
                font-size: 0.72rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }

            .sidebar-promo {
                background:
                    linear-gradient(180deg, rgba(21, 27, 35, 0.96), rgba(15, 19, 26, 0.94));
                border: 1px solid rgba(148, 163, 184, 0.10);
                border-radius: 14px;
                padding: 0.78rem 0.82rem 0.75rem 0.82rem;
                margin-bottom: 1rem;
                box-shadow: 0 10px 24px rgba(0, 0, 0, 0.10);
            }

            .sidebar-promo-title {
                color: var(--text-primary);
                font-size: 0.98rem;
                font-weight: 700;
                margin-bottom: 0.35rem;
            }

            .sidebar-promo-copy {
                color: var(--text-muted);
                font-size: 0.84rem;
                line-height: 1.5;
                margin-bottom: 0.85rem;
            }

            .sidebar-promo-tag {
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                color: var(--accent-teal);
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.06em;
                text-transform: uppercase;
            }

            .sidebar-brand-title {
                color: var(--text-primary);
                font-size: 1.28rem;
                font-weight: 800;
                line-height: 1.1;
                letter-spacing: -0.03em;
                margin-bottom: 0.4rem;
            }

            .sidebar-brand-copy {
                color: var(--text-muted);
                font-size: 0.84rem;
                line-height: 1.45;
                margin-bottom: 0.8rem;
            }

            .sidebar-brand-footer {
                color: var(--text-label);
                font-size: 0.77rem;
                font-weight: 700;
                letter-spacing: 0.14em;
                text-transform: uppercase;
            }

            .sidebar-group {
                color: var(--text-muted);
                font-size: 0.72rem;
                font-weight: 700;
                letter-spacing: 0.18em;
                text-transform: uppercase;
                margin-top: 0.92rem;
                margin-bottom: 0.18rem;
                padding-top: 0.36rem;
                border-top: 1px solid rgba(148, 163, 184, 0.08);
            }

            .active-nav {
                position: relative;
                background: linear-gradient(180deg, rgba(24, 166, 106, 0.045), rgba(143, 184, 170, 0.02));
                border: 1px solid rgba(24, 166, 106, 0.1);
                border-radius: 11px;
                padding: 0.08rem;
                margin-bottom: 0.1rem;
                box-shadow:
                    0 6px 14px rgba(15, 23, 38, 0.1),
                    inset 0 1px 0 rgba(255, 255, 255, 0.03);
            }

            .active-nav::before {
                content: "";
                position: absolute;
                top: 7px;
                bottom: 7px;
                left: 2px;
                width: 2px;
                border-radius: 0 4px 4px 0;
                background: linear-gradient(180deg, var(--accent-soft), var(--accent-teal));
                box-shadow: 0 0 6px rgba(24, 166, 106, 0.1);
            }

            .page-hero {
                background:
                    radial-gradient(circle at top right, rgba(24, 166, 106, 0.06), transparent 24%),
                    linear-gradient(180deg, rgba(15, 19, 26, 0.96), rgba(11, 15, 20, 0.92));
                border: 1px solid var(--border);
                border-radius: 20px;
                padding: 1.35rem 1.35rem 1.2rem 1.35rem;
                margin-bottom: 1.35rem;
                box-shadow:
                    0 18px 40px rgba(0, 0, 0, 0.13),
                    inset 0 1px 0 rgba(255, 255, 255, 0.03);
            }

            .page-eyebrow {
                color: var(--text-label);
                font-size: 0.8rem;
                font-weight: 700;
                letter-spacing: 0.18em;
                text-transform: uppercase;
                margin-bottom: 0.65rem;
            }

            .page-title {
                color: var(--text-primary);
                font-size: 2.7rem;
                font-weight: 800;
                line-height: 1.04;
                letter-spacing: -0.04em;
                margin-bottom: 0.45rem;
            }

            .page-subtitle {
                color: var(--text-muted);
                font-size: 0.95rem;
                line-height: 1.52;
                max-width: 860px;
            }

            .hero-grid {
                display: grid;
                grid-template-columns: minmax(0, 1.2fr) minmax(260px, 0.8fr);
                gap: 1.1rem;
                align-items: end;
            }

            .hero-sidecard {
                background:
                    linear-gradient(180deg, rgba(21, 27, 35, 0.78), rgba(15, 19, 26, 0.78));
                border: 1px solid rgba(148, 163, 184, 0.10);
                border-radius: 14px;
                padding: 0.8rem 0.9rem;
                min-height: 94px;
            }

            .hero-sidecard-label {
                color: var(--text-muted);
                font-size: 0.74rem;
                font-weight: 700;
                letter-spacing: 0.1em;
                text-transform: uppercase;
                margin-bottom: 0.45rem;
            }

            .hero-sidecard-value {
                color: var(--text-primary);
                font-size: 1.05rem;
                line-height: 1.55;
            }

            .dashboard-panel {
                background:
                    radial-gradient(circle at top right, rgba(24, 166, 106, 0.028), transparent 24%),
                    linear-gradient(180deg, rgba(13, 17, 24, 0.98), rgba(18, 24, 32, 0.94));
                border: 1px solid rgba(148, 163, 184, 0.06);
                border-radius: 16px;
                padding: 0.95rem 0.95rem 0.82rem 0.95rem;
                margin-bottom: 0.88rem;
                box-shadow:
                    0 10px 22px rgba(0, 0, 0, 0.08),
                    inset 0 1px 0 rgba(255, 255, 255, 0.02);
            }

            .dashboard-panel.compact {
                padding-top: 1rem;
                padding-bottom: 0.8rem;
            }

            .section-title {
                color: var(--text-primary);
                font-size: 1.42rem;
                font-weight: 750;
                letter-spacing: -0.03em;
                margin-bottom: 0.18rem;
            }

            .section-copy {
                color: var(--text-muted);
                font-size: 0.88rem;
                line-height: 1.46;
                margin-bottom: 0.8rem;
                max-width: 860px;
            }

            .subpanel {
                background:
                    linear-gradient(180deg, rgba(16, 21, 29, 0.82), rgba(13, 17, 24, 0.76));
                border: 1px solid rgba(148, 163, 184, 0.06);
                border-radius: 12px;
                padding: 0.72rem 0.74rem 0.68rem 0.74rem;
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.015);
            }

            .metric-card {
                background:
                    radial-gradient(circle at top right, rgba(24, 166, 106, 0.035), transparent 30%),
                    linear-gradient(180deg, rgba(15, 19, 26, 0.98), rgba(21, 27, 35, 0.94));
                border: 1px solid rgba(148, 163, 184, 0.06);
                border-radius: 12px;
                padding: 0.82rem 0.86rem 0.8rem 0.86rem;
                min-height: 94px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);
            }

            .metric-label {
                color: var(--text-muted);
                font-size: 0.8rem;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                font-weight: 700;
            }

            .metric-value {
                color: var(--text-primary);
                font-size: 1.72rem;
                font-weight: 800;
                letter-spacing: -0.03em;
                line-height: 1;
                margin-top: 0.52rem;
                margin-bottom: 0.32rem;
            }

            .metric-footnote {
                color: var(--text-secondary);
                font-size: 0.86rem;
                line-height: 1.4;
            }

            .control-strip {
                background:
                    linear-gradient(180deg, rgba(21, 27, 35, 0.98), rgba(15, 19, 26, 0.96));
                border: 1px solid rgba(148, 163, 184, 0.06);
                border-radius: 16px;
                padding: 0.82rem 0.86rem 0.72rem 0.86rem;
                margin-bottom: 0.9rem;
                box-shadow:
                    0 10px 24px rgba(0, 0, 0, 0.09),
                    inset 0 1px 0 rgba(255, 255, 255, 0.02);
            }

            .chart-frame {
                margin-top: 0.15rem;
                margin-bottom: 0.05rem;
                padding: 0.05rem 0 0 0;
            }

            .hero-chart-panel {
                padding-top: 1.15rem;
                padding-bottom: 1rem;
            }

            .inline-panel-title {
                color: var(--text-primary);
                font-size: 1.06rem;
                font-weight: 720;
                letter-spacing: -0.02em;
                margin-bottom: 0.22rem;
            }

            .inline-panel-copy {
                color: var(--text-muted);
                font-size: 0.84rem;
                line-height: 1.45;
                margin-bottom: 0.75rem;
            }

            .stDataFrame, div[data-testid="stTable"] {
                border-radius: 12px;
                overflow: hidden;
                border: 1px solid rgba(148, 163, 184, 0.12);
                background: linear-gradient(180deg, rgba(17, 23, 33, 0.96), rgba(13, 18, 25, 0.94));
            }

            .stDataFrame [data-testid="stDataFrameResizable"], div[data-testid="stTable"] {
                font-size: 0.88rem;
            }

            div[data-testid="stTable"] table {
                border-collapse: separate;
                border-spacing: 0;
                width: 100%;
            }

            div[data-testid="stTable"] table th,
            div[data-testid="stTable"] table td {
                border-right: 1px solid rgba(148, 163, 184, 0.12);
                border-bottom: 1px solid rgba(148, 163, 184, 0.10);
                padding: 0.62rem 0.72rem;
            }

            div[data-testid="stTable"] table th {
                background: rgba(148, 163, 184, 0.08);
                color: var(--text-secondary);
                font-weight: 700;
            }

            div[data-testid="stTable"] table tr:last-child td {
                border-bottom: none;
            }

            div[data-testid="stTable"] table th:last-child,
            div[data-testid="stTable"] table td:last-child {
                border-right: none;
            }

            .stDataFrame [role="columnheader"],
            .stDataFrame [role="gridcell"] {
                border-right: 1px solid rgba(148, 163, 184, 0.10) !important;
                border-bottom: 1px solid rgba(148, 163, 184, 0.10) !important;
            }

            .stDataFrame [role="columnheader"] {
                background: rgba(148, 163, 184, 0.08) !important;
                color: var(--text-secondary) !important;
                font-weight: 700 !important;
            }

            div[data-testid="stExpander"] {
                border: 1px solid rgba(148, 163, 184, 0.06);
                border-radius: 16px;
                background: rgba(13, 18, 25, 0.90);
                margin-bottom: 0.85rem;
                overflow: hidden;
                box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08);
            }

            div[data-testid="stExpander"] details summary {
                padding-top: 0.35rem;
                padding-bottom: 0.35rem;
                color: var(--text-primary);
                font-weight: 700;
            }

            .stSelectbox label, .stMultiSelect label, .stSlider label, .stFileUploader label, .stCheckbox label {
                color: var(--text-secondary) !important;
                font-weight: 600 !important;
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 0.45rem;
                background: rgba(255, 255, 255, 0.03);
                padding: 0.35rem;
                border-radius: 12px;
                border: 1px solid rgba(148, 163, 184, 0.10);
            }

            .stTabs [data-baseweb="tab"] {
                height: 40px;
                border-radius: 10px;
                color: var(--text-muted);
                font-weight: 600;
            }

            .stTabs [aria-selected="true"] {
                background: rgba(24, 166, 106, 0.12);
                color: var(--text-primary);
            }

            .stButton button[kind="primary"] {
                background: linear-gradient(180deg, var(--accent-soft), #15803d);
                color: #041018;
                border: none;
                font-weight: 800;
            }

            div[data-testid="stInfo"], div[data-testid="stSuccess"], div[data-testid="stWarning"] {
                border-radius: 14px;
                border: 1px solid var(--border);
            }

            .spacer-lg {
                height: 0.62rem;
            }

            .spacer-xl {
                height: 1rem;
            }

            [data-testid="stPlotlyChart"] > div {
                border-radius: 14px;
                overflow: hidden;
            }

            .stDownloadButton button {
                width: 100%;
                border-radius: 12px;
                border: 1px solid rgba(148, 163, 184, 0.08);
                background: linear-gradient(180deg, rgba(21, 27, 35, 0.98), rgba(15, 19, 26, 0.96));
                color: var(--text-primary);
                font-weight: 700;
            }

            @media (max-width: 1200px) {
                .hero-grid {
                    grid-template-columns: 1fr;
                }
            }

            .landing-mode [data-testid="stSidebar"] {
                display: none;
            }

            .landing-mode .block-container {
                max-width: 100%;
                padding-top: 0.35rem;
                padding-left: 0;
                padding-right: 0;
                padding-bottom: 2rem;
            }

            .landing-shell {
                min-height: 100vh;
                background:
                    radial-gradient(circle at 50% -10%, rgba(24, 166, 106, 0.08), transparent 26%),
                    linear-gradient(180deg, #040607 0%, #05080d 100%);
                padding-bottom: 3rem;
            }

            .landing-nav {
                padding: 0.85rem 1.1rem 0.85rem 1.1rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                background: rgba(4, 6, 7, 0.92);
                position: sticky;
                top: 0;
                z-index: 5;
                backdrop-filter: blur(10px);
            }

            .landing-nav-inner {
                max-width: 1280px;
                margin: 0 auto;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
            }

            .landing-logo {
                color: #f3f4f6;
                font-size: 1.1rem;
                font-weight: 800;
                letter-spacing: -0.03em;
            }

            .landing-nav-links {
                display: flex;
                align-items: center;
                gap: 1.35rem;
                color: #d1d5db;
                font-size: 0.94rem;
                font-weight: 640;
            }

            .landing-nav-links span {
                opacity: 0.88;
            }

            .landing-nav-actions {
                display: flex;
                align-items: center;
                gap: 0.55rem;
            }

            .landing-nav-chip {
                color: #f3f4f6;
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 13px;
                padding: 0.62rem 1rem;
                font-size: 0.92rem;
                font-weight: 700;
            }

            .landing-nav-chip.primary {
                background: linear-gradient(180deg, #1cc786, #18a66a);
                color: #041018;
                border-color: transparent;
            }

            .landing-hero {
                max-width: 1040px;
                margin: 0 auto;
                padding: 1.85rem 1.5rem 0.55rem 1.5rem;
                text-align: center;
            }

            .landing-eyebrow {
                color: #18c37f;
                font-size: 0.9rem;
                font-weight: 700;
                letter-spacing: 0.04em;
                margin-bottom: 0.75rem;
            }

            .landing-title {
                color: #ededee;
                font-size: clamp(2.35rem, 5.8vw, 4.55rem);
                line-height: 1.01;
                font-weight: 840;
                letter-spacing: -0.05em;
                margin: 0 auto 0.72rem auto;
                max-width: 860px;
            }

            .landing-gradient {
                background: linear-gradient(90deg, #17c77e 0%, #19b8a6 48%, #3b82f6 100%);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
            }

            .landing-copy {
                max-width: 720px;
                margin: 0 auto 0.72rem auto;
                color: rgba(209, 213, 219, 0.66);
                font-size: 0.95rem;
                line-height: 1.62;
            }

            .landing-bullets {
                display: inline-block;
                text-align: left;
                margin: 0 auto 0.48rem auto;
                color: rgba(229, 231, 235, 0.74);
                font-size: 0.92rem;
                line-height: 1.68;
            }

            .landing-bullets strong {
                color: #f3f4f6;
            }

            .landing-bullets span {
                color: rgba(243, 244, 246, 0.88);
                margin-right: 0.34rem;
            }

            .landing-cta-wrap {
                max-width: 760px;
                margin: -0.05rem auto 1rem auto;
                padding: 0 1rem;
            }

            .landing-footer-note {
                max-width: 980px;
                margin: 1.15rem auto 0 auto;
                padding: 0 1.5rem;
                color: rgba(148, 163, 184, 0.78);
                font-size: 0.92rem;
                line-height: 1.6;
                text-align: center;
            }

            .landing-preview-section {
                max-width: 1280px;
                margin: 0.1rem auto 0 auto;
                padding: 0 1.5rem;
            }

            .landing-preview-shell {
                background: linear-gradient(180deg, rgba(11, 15, 20, 0.98), rgba(9, 12, 18, 0.98));
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 28px;
                padding: 1.2rem;
                box-shadow: 0 30px 70px rgba(0, 0, 0, 0.34);
            }

            .landing-preview-grid {
                display: grid;
                grid-template-columns: 200px 1fr;
                gap: 1rem;
                min-height: 390px;
            }

            .landing-preview-rail {
                background: rgba(9, 14, 20, 0.92);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 22px;
                padding: 1rem;
            }

            .landing-preview-rail-title {
                color: #94a3b8;
                font-size: 0.78rem;
                letter-spacing: 0.14em;
                text-transform: uppercase;
                margin-bottom: 0.7rem;
            }

            .landing-preview-rail-item {
                color: #cbd5e1;
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.03);
                border-radius: 14px;
                padding: 0.75rem 0.85rem;
                margin-bottom: 0.5rem;
                font-size: 0.95rem;
                font-weight: 600;
            }

            .landing-preview-rail-item.active {
                color: #f8fafc;
                border-color: rgba(24, 166, 106, 0.18);
                background: linear-gradient(180deg, rgba(24, 166, 106, 0.08), rgba(24, 166, 106, 0.03));
            }

            .landing-preview-main {
                background: rgba(12, 17, 24, 0.92);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 22px;
                padding: 1rem;
            }

            .landing-preview-topbar {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 1rem;
                margin-bottom: 0.85rem;
            }

            .landing-preview-headline {
                color: #f8fafc;
                font-size: 1.18rem;
                font-weight: 760;
            }

            .landing-preview-subline {
                color: #94a3b8;
                font-size: 0.88rem;
                margin-top: 0.15rem;
            }

            .landing-preview-controls {
                display: flex;
                gap: 0.55rem;
            }

            .landing-preview-pill {
                height: 38px;
                min-width: 110px;
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.06);
                background: rgba(255, 255, 255, 0.03);
            }

            .landing-preview-chart {
                background: linear-gradient(180deg, rgba(20, 25, 33, 0.98), rgba(16, 21, 29, 0.98));
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 20px;
                height: 300px;
                position: relative;
                overflow: hidden;
                margin-bottom: 0;
            }

            .landing-preview-chart::before {
                content: "";
                position: absolute;
                inset: 0;
                background:
                    repeating-linear-gradient(
                        to bottom,
                        transparent 0,
                        transparent 56px,
                        rgba(255, 255, 255, 0.035) 57px,
                        transparent 58px
                    );
            }

            .landing-preview-chart::after {
                content: "";
                position: absolute;
                inset: 0;
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.01), rgba(255, 255, 255, 0.0));
            }

            .landing-preview-axis {
                position: absolute;
                left: 6%;
                right: 4%;
                top: 18%;
                bottom: 14%;
                border-left: 1px solid rgba(255, 255, 255, 0.08);
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 18px;
                z-index: 2;
            }

            .landing-preview-bars {
                position: absolute;
                left: 8%;
                right: 5%;
                top: 24%;
                bottom: 14%;
                z-index: 3;
            }

            .landing-preview-bar {
                position: absolute;
                bottom: 42%;
                width: 1.55%;
                border-radius: 2px 2px 0 0;
                opacity: 0.92;
                background: rgba(195, 93, 154, 0.92);
            }

            .landing-preview-bar.negative {
                bottom: auto;
                top: 42%;
                border-radius: 0 0 2px 2px;
                background: rgba(34, 197, 94, 0.88);
            }

            .landing-preview-line-path {
                position: absolute;
                left: 7%;
                right: 5%;
                top: 18%;
                bottom: 14%;
                z-index: 4;
                background: rgba(255, 255, 255, 0.82);
                clip-path: polygon(0% 62%, 6% 63%, 13% 64%, 21% 71%, 28% 76%, 36% 78%, 44% 80%, 52% 68%, 60% 49%, 68% 43%, 76% 26%, 84% 23%, 92% 18%, 100% 12%, 100% 14%, 92% 20%, 84% 25%, 76% 28%, 68% 45%, 60% 52%, 52% 72%, 44% 83%, 36% 81%, 28% 79%, 21% 74%, 13% 67%, 6% 66%, 0% 65%);
                opacity: 0.95;
            }

            .landing-preview-marker {
                position: absolute;
                top: 18%;
                bottom: 14%;
                width: 2px;
                z-index: 4;
                opacity: 0.9;
                border-radius: 999px;
                border-left: 2px dashed currentColor;
            }

            .landing-preview-marker.marker-left {
                left: 54%;
                color: rgba(239, 68, 68, 0.75);
            }

            .landing-preview-marker.marker-right {
                left: 63%;
                color: rgba(96, 165, 250, 0.78);
            }

            .landing-preview-legend {
                display: flex;
                align-items: center;
                gap: 0.8rem;
                position: absolute;
                right: 4.5%;
                top: 8.5%;
                z-index: 5;
            }

            .landing-preview-legend-item {
                display: inline-flex;
                align-items: center;
                gap: 0.4rem;
                color: #cfd8e3;
                font-size: 0.74rem;
            }

            .landing-preview-dot {
                width: 10px;
                height: 10px;
                border-radius: 2px;
                background: currentColor;
            }

            .landing-preview-dot.call {
                color: rgba(195, 93, 154, 0.9);
            }

            .landing-preview-dot.put {
                color: rgba(34, 197, 94, 0.85);
            }

            .landing-preview-dot.gamma {
                color: rgba(255, 255, 255, 0.76);
            }

            .landing-card-grid {
                max-width: 1280px;
                margin: 1rem auto 0 auto;
                padding: 0 1.5rem;
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 1rem;
            }

            .landing-card {
                background: linear-gradient(180deg, rgba(15, 19, 26, 0.96), rgba(18, 24, 32, 0.92));
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 22px;
                padding: 1rem 1rem 0.95rem 1rem;
                box-shadow: 0 18px 44px rgba(0, 0, 0, 0.22);
            }

            .landing-card-kicker {
                color: #8fd9b3;
                font-size: 0.74rem;
                font-weight: 700;
                letter-spacing: 0.14em;
                text-transform: uppercase;
                margin-bottom: 0.55rem;
            }

            .landing-card-title {
                color: #f3f4f6;
                font-size: 1.18rem;
                font-weight: 760;
                margin-bottom: 0.4rem;
            }

            .landing-card-copy {
                color: #aeb8c5;
                font-size: 0.92rem;
                line-height: 1.55;
            }

            .landing-mode .stButton button {
                min-width: 182px;
                height: 56px;
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.10);
                font-size: 1rem;
                font-weight: 760;
                letter-spacing: -0.01em;
                box-shadow: none;
            }

            .landing-mode .stButton button[kind="primary"],
            .landing-mode div[data-testid="stButton"] button[kind="primary"] {
                background: linear-gradient(180deg, #1cc786, #18a66a);
                color: #041018;
                border-color: transparent;
            }

            .landing-mode .stButton button[kind="secondary"],
            .landing-mode div[data-testid="stButton"] button[kind="secondary"] {
                background: rgba(255, 255, 255, 0.02);
                color: #f3f4f6;
            }

            @media (max-width: 1100px) {
                .landing-preview-grid,
                .landing-card-grid {
                    grid-template-columns: 1fr;
                }

                .landing-nav {
                    padding-left: 0.85rem;
                    padding-right: 0.85rem;
                }

                .landing-nav-inner {
                    flex-wrap: wrap;
                }

                .landing-nav-links {
                    gap: 0.85rem;
                    font-size: 0.88rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def configure_page() -> None:
    """Configure the Streamlit page and inject global styles."""
    st.set_page_config(page_title="Market Regime Detection Dashboard", layout="wide")
    inject_global_styles()


def activate_landing_mode() -> None:
    """Apply landing-page-only layout overrides."""
    st.markdown(
        """
        <style>
            .stApp {
                background: #040607;
            }
            [data-testid="stSidebar"] {
                display: none;
            }
            .block-container {
                max-width: 100%;
                padding-top: 0.35rem;
                padding-left: 0;
                padding-right: 0;
                padding-bottom: 2rem;
            }
            .stButton button {
                min-width: 182px;
                height: 56px;
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.10);
                font-size: 1rem;
                font-weight: 760;
                letter-spacing: -0.01em;
                box-shadow: none;
            }
            .stButton button[kind="primary"],
            div[data-testid="stButton"] button[kind="primary"] {
                background: linear-gradient(180deg, #1cc786, #18a66a);
                color: #041018;
                border-color: transparent;
            }
            .stButton button[kind="secondary"],
            div[data-testid="stButton"] button[kind="secondary"] {
                background: rgba(255, 255, 255, 0.02);
                color: #f3f4f6;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_landing_cta_buttons() -> None:
    """Open the landing CTA wrapper."""
    st.markdown('<div class="landing-cta-row">', unsafe_allow_html=True)


def render_landing_cta_buttons_end() -> None:
    """Close the landing CTA wrapper."""
    st.markdown("</div>", unsafe_allow_html=True)


def render_landing_footer_note() -> None:
    """Render a compact landing footer note."""
    st.markdown(
        """
        <div class="landing-footer-note">
            Built for financial time-series regime detection with a chart-first quant workflow,
            model console, and strategy diagnostics inside one institutional-style market workspace.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand() -> None:
    """Render the premium brand panel in the sidebar."""
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-topline">
                <div class="sidebar-brand-orb"></div>
                <div class="sidebar-brand-chip">Workspace</div>
            </div>
            <div class="sidebar-brand-title">Market Regime Detection</div>
            <div class="sidebar-brand-copy">Quant workflow, clustering diagnostics, and visual market review in one workspace.</div>
            <div class="sidebar-brand-footer">Analytics Workspace</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_topbar(active_page: str) -> None:
    """Render a compact utility top bar above the main content."""
    st.markdown(
        f"""
        <div class="topbar">
            <div class="topbar-brand">
                <div class="topbar-title">Market Intelligence Workspace</div>
                <div class="topbar-copy">Regime monitoring, structure diagnostics, and chart-led market review.</div>
            </div>
            <div class="topbar-status">
                <div class="topbar-pill">{active_page}</div>
                <div class="topbar-pill">Live Desk</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(eyebrow: str, title: str, subtitle: str) -> None:
    """Render a page-level editorial header."""
    st.markdown(
        f"""
        <div class="page-hero">
            <div class="hero-grid">
                <div>
                    <div class="page-eyebrow">{eyebrow}</div>
                    <div class="page-title">{title}</div>
                    <div class="page-subtitle">{subtitle}</div>
                </div>
                <div class="hero-sidecard">
                    <div class="hero-sidecard-label">Screen Focus</div>
                    <div class="hero-sidecard-value">Chart-first monitoring, tighter surfaces, and a cleaner market-facing hierarchy.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, subtitle: str) -> None:
    """Render a panel section header."""
    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        <div class="section-copy">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )


def render_panel_start(compact: bool = False) -> None:
    """Open a panel wrapper."""
    class_name = "dashboard-panel compact" if compact else "dashboard-panel"
    st.markdown(f'<div class="{class_name}">', unsafe_allow_html=True)


def render_hero_chart_panel_start() -> None:
    """Open a more prominent hero chart panel."""
    st.markdown('<div class="dashboard-panel hero-chart-panel">', unsafe_allow_html=True)


def render_panel_end() -> None:
    """Close a panel wrapper."""
    st.markdown("</div>", unsafe_allow_html=True)


def render_subpanel_start() -> None:
    """Open a quieter nested panel."""
    st.markdown('<div class="subpanel">', unsafe_allow_html=True)


def render_subpanel_end() -> None:
    """Close a nested panel."""
    st.markdown("</div>", unsafe_allow_html=True)


def render_control_strip_start() -> None:
    """Open a compact controls wrapper."""
    st.markdown('<div class="control-strip">', unsafe_allow_html=True)


def render_control_strip_end() -> None:
    """Close a compact controls wrapper."""
    st.markdown("</div>", unsafe_allow_html=True)


def render_metric_card(label: str, value: str, footnote: str = "") -> None:
    """Render a premium metric card."""
    footnote_markup = f'<div class="metric-footnote">{footnote}</div>' if footnote else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {footnote_markup}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_row(metrics: list[tuple[str, str, str]]) -> None:
    """Render a responsive row of metric cards."""
    columns = st.columns(len(metrics))
    for column, metric in zip(columns, metrics):
        with column:
            render_metric_card(*metric)


def render_chart_frame_start() -> None:
    """Open a chart frame wrapper."""
    st.markdown('<div class="chart-frame">', unsafe_allow_html=True)


def render_chart_frame_end() -> None:
    """Close a chart frame wrapper."""
    st.markdown("</div>", unsafe_allow_html=True)


def render_spacer(size: str = "lg") -> None:
    """Render a layout spacer."""
    class_name = "spacer-xl" if size == "xl" else "spacer-lg"
    st.markdown(f'<div class="{class_name}"></div>', unsafe_allow_html=True)


def render_sidebar_promo(title: str, copy: str, tag: str) -> None:
    """Render a compact promo-style panel in the sidebar."""
    st.markdown(
        f"""
        <div class="sidebar-promo">
            <div class="sidebar-promo-title">{title}</div>
            <div class="sidebar-promo-copy">{copy}</div>
            <div class="sidebar-promo-tag">{tag}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_landing_nav() -> None:
    """Render the marketing-style landing navbar."""
    st.markdown(
        """
        <div class="landing-nav">
            <div class="landing-nav-inner">
                <div class="landing-logo">Market Regime Detection</div>
                <div class="landing-nav-links">
                    <span>Workspace</span>
                    <span>Signals</span>
                    <span>Research</span>
                </div>
                <div class="landing-nav-actions">
                    <div class="landing-nav-chip">Quant Lab</div>
                    <div class="landing-nav-chip primary">Open Dashboard</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_landing_hero() -> None:
    """Render the large editorial landing hero."""
    st.markdown(
        """
        <div class="landing-shell">
            <div class="landing-hero">
                <div class="landing-eyebrow">Institutional Quant Workspace</div>
                <div class="landing-title">
                    Detect market regimes<br>
                    and monitor portfolio risk<br>
                    <span class="landing-gradient">inside one desk view.</span>
                </div>
                <div class="landing-copy">
                    A chart-first quant dashboard for regime detection, volatility diagnostics,
                    return analysis, and strategy review across one reusable financial workflow.
                </div>
                <div class="landing-bullets">
                    <span>&bull;</span> <strong>Regime Monitor:</strong> state overlays, transition outlook, and timeline analysis<br>
                    <span>&bull;</span> <strong>Quant Analytics:</strong> correlation, volatility, returns, and strategy diagnostics<br>
                    <span>&bull;</span> <strong>Model Console:</strong> preprocessing, validation, tuning, and clustering workflow
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_landing_preview() -> None:
    """Render a stylized dashboard preview section."""
    st.markdown(
        """
            <div class="landing-preview-section">
                <div class="landing-preview-shell">
                    <div class="landing-preview-grid">
                        <div class="landing-preview-rail">
                            <div class="landing-preview-rail-title">Workspace</div>
                            <div class="landing-preview-rail-item">Dataset Intake</div>
                            <div class="landing-preview-rail-item">Model Console</div>
                            <div class="landing-preview-rail-item active">Regime Monitor</div>
                            <div class="landing-preview-rail-item">Market Structure</div>
                            <div class="landing-preview-rail-item">Volatility Monitor</div>
                            <div class="landing-preview-rail-item">Strategy Desk</div>
                        </div>
                        <div class="landing-preview-main">
                            <div class="landing-preview-topbar">
                                <div>
                                    <div class="landing-preview-headline">Net Gamma Exposure</div>
                                    <div class="landing-preview-subline">Desk-style market structure monitor with strike-level exposure and cumulative state signal.</div>
                                </div>
                                <div class="landing-preview-controls">
                                    <div class="landing-preview-pill"></div>
                                    <div class="landing-preview-pill"></div>
                                    <div class="landing-preview-pill"></div>
                                </div>
                            </div>
                            <div class="landing-preview-chart">
                                <div class="landing-preview-axis"></div>
                                <div class="landing-preview-legend">
                                    <div class="landing-preview-legend-item"><span class="landing-preview-dot call"></span>Call Wall</div>
                                    <div class="landing-preview-legend-item"><span class="landing-preview-dot put"></span>Put Wall</div>
                                    <div class="landing-preview-legend-item"><span class="landing-preview-dot gamma"></span>Cumulative Gamma</div>
                                </div>
                                <div class="landing-preview-bars">
                                    <div class="landing-preview-bar negative" style="left:0%; height:16%;"></div>
                                    <div class="landing-preview-bar" style="left:3%; height:4%;"></div>
                                    <div class="landing-preview-bar" style="left:6%; height:3%;"></div>
                                    <div class="landing-preview-bar negative" style="left:10%; height:28%;"></div>
                                    <div class="landing-preview-bar" style="left:14%; height:2%;"></div>
                                    <div class="landing-preview-bar" style="left:18%; height:5%;"></div>
                                    <div class="landing-preview-bar negative" style="left:22%; height:14%;"></div>
                                    <div class="landing-preview-bar" style="left:28%; height:8%;"></div>
                                    <div class="landing-preview-bar" style="left:32%; height:7%;"></div>
                                    <div class="landing-preview-bar negative" style="left:36%; height:40%;"></div>
                                    <div class="landing-preview-bar" style="left:42%; height:12%;"></div>
                                    <div class="landing-preview-bar" style="left:46%; height:10%;"></div>
                                    <div class="landing-preview-bar" style="left:50%; height:34%;"></div>
                                    <div class="landing-preview-bar" style="left:54%; height:22%;"></div>
                                    <div class="landing-preview-bar" style="left:58%; height:52%;"></div>
                                    <div class="landing-preview-bar" style="left:63%; height:18%;"></div>
                                    <div class="landing-preview-bar" style="left:68%; height:10%;"></div>
                                    <div class="landing-preview-bar" style="left:73%; height:8%;"></div>
                                    <div class="landing-preview-bar" style="left:78%; height:36%;"></div>
                                    <div class="landing-preview-bar" style="left:85%; height:12%;"></div>
                                    <div class="landing-preview-bar" style="left:92%; height:16%;"></div>
                                </div>
                                <div class="landing-preview-marker marker-left"></div>
                                <div class="landing-preview-marker marker-right"></div>
                                <div class="landing-preview-line-path"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )


def render_landing_cards() -> None:
    """Render supporting landing capability cards."""
    st.markdown(
        """
        <div class="landing-card-grid">
            <div class="landing-card">
                <div class="landing-card-kicker">State Detection</div>
                <div class="landing-card-title">Regime-first market interpretation</div>
                <div class="landing-card-copy">Translate unsupervised clusters into persistent market states with transition outlook, state timeline, and interpretable feature intensity.</div>
            </div>
            <div class="landing-card">
                <div class="landing-card-kicker">Quant Diagnostics</div>
                <div class="landing-card-title">Structure, volatility, and return monitoring</div>
                <div class="landing-card-copy">Move from correlation heatmaps to volatility and return monitors without leaving the same product-style financial workspace.</div>
            </div>
            <div class="landing-card">
                <div class="landing-card-kicker">Strategy Layer</div>
                <div class="landing-card-title">Portfolio-aware backtesting desk</div>
                <div class="landing-card-copy">Evaluate regime-aware exposure rules with drawdown, Sharpe, Sortino, CAGR, hit rate, and state-level contribution analysis.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
