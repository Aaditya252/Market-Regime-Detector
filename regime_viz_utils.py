from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


REGIME_COLORS = [
    ("Regime 0", "rgba(34, 197, 94, 0.18)", "#22c55e"),
    ("Regime 1", "rgba(239, 68, 68, 0.18)", "#ef4444"),
    ("Regime 2", "rgba(250, 204, 21, 0.20)", "#facc15"),
    ("Regime 3", "rgba(59, 130, 246, 0.18)", "#3b82f6"),
    ("Regime 4", "rgba(168, 85, 247, 0.18)", "#a855f7"),
    ("Regime 5", "rgba(249, 115, 22, 0.18)", "#f97316"),
]


def get_default_date_column(dataframe: pd.DataFrame) -> str | None:
    """Infer a default date column from the dataset."""
    for column in dataframe.columns:
        if "date" in str(column).lower() or "time" in str(column).lower():
            return column
    return None


def prepare_market_regime_frame(
    dataframe: pd.DataFrame,
    price_column: str,
    date_column: str | None = None,
) -> pd.DataFrame:
    """Prepare clustered rows for regime visualization."""
    if "market_regime" not in dataframe.columns or price_column not in dataframe.columns:
        return pd.DataFrame()

    selected_columns = [price_column, "market_regime"]
    if date_column and date_column in dataframe.columns:
        selected_columns.append(date_column)

    plot_frame = dataframe.loc[dataframe["market_regime"].notna(), selected_columns].copy()
    if plot_frame.empty:
        return plot_frame

    plot_frame["market_regime"] = plot_frame["market_regime"].astype(int)
    if date_column and date_column in plot_frame.columns:
        plot_frame["Time"] = pd.to_datetime(plot_frame[date_column], errors="coerce")
        plot_frame = plot_frame.dropna(subset=["Time"])
    else:
        plot_frame = plot_frame.reset_index().rename(columns={"index": "Time"})

    if plot_frame.empty:
        return plot_frame

    plot_frame = plot_frame.sort_values("Time").reset_index(drop=True)
    plot_frame["Regime Label"] = plot_frame["market_regime"].map(lambda value: f"Regime {value}")
    return plot_frame


def _iter_regime_segments(plot_frame: pd.DataFrame) -> list[tuple[object, object, int]]:
    """Return contiguous regime segments as (start, end, regime)."""
    segments: list[tuple[object, object, int]] = []
    if plot_frame.empty:
        return segments

    start_time = plot_frame.iloc[0]["Time"]
    previous_time = start_time
    current_regime = int(plot_frame.iloc[0]["market_regime"])

    for _, row in plot_frame.iloc[1:].iterrows():
        row_regime = int(row["market_regime"])
        row_time = row["Time"]
        if row_regime != current_regime:
            segments.append((start_time, previous_time, current_regime))
            start_time = row_time
            current_regime = row_regime
        previous_time = row_time

    segments.append((start_time, previous_time, current_regime))
    return segments


def build_market_regime_figure(plot_frame: pd.DataFrame, price_column: str) -> go.Figure:
    """Build the main market regime analysis chart."""
    figure = go.Figure()

    for regime_name, background_color, line_color in REGIME_COLORS:
        figure.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker={"size": 10, "color": line_color},
                showlegend=True,
                name=regime_name,
            )
        )

    for start_time, end_time, regime in _iter_regime_segments(plot_frame):
        figure.add_vrect(
            x0=start_time,
            x1=end_time,
            fillcolor=REGIME_COLORS[regime % len(REGIME_COLORS)][1],
            layer="below",
            line_width=0,
        )

    figure.add_trace(
        go.Scatter(
            x=plot_frame["Time"],
            y=plot_frame[price_column],
            mode="lines",
            name=price_column,
            line={"color": "#0f172a", "width": 2.4},
            customdata=plot_frame[["Regime Label"]],
            hovertemplate=(
                "Date: %{x}<br>"
                + f"{price_column}: "
                + "%{y:.4f}<br>"
                + "Regime: %{customdata[0]}<extra></extra>"
            ),
        )
    )

    figure.update_layout(
        title="Price Series With Market Regime Segmentation",
        template="plotly_white",
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title=price_column,
        margin={"l": 24, "r": 24, "t": 68, "b": 24},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },
    )
    figure.update_xaxes(showgrid=False, rangeslider_visible=False)
    figure.update_yaxes(showgrid=True, gridcolor="rgba(148, 163, 184, 0.18)")
    return figure


def build_cluster_distribution_figure(cluster_distribution: pd.DataFrame) -> go.Figure:
    """Build a cluster distribution chart."""
    distribution_frame = cluster_distribution.copy()
    distribution_frame["Regime"] = distribution_frame["Cluster"].map(lambda value: f"Regime {value}")

    figure = px.bar(
        distribution_frame,
        x="Regime",
        y="Count",
        color="Regime",
        title="Cluster Distribution",
        color_discrete_sequence=[color[2] for color in REGIME_COLORS],
    )
    figure.update_layout(
        template="plotly_white",
        xaxis_title="Cluster / Regime",
        yaxis_title="Points",
        showlegend=False,
        margin={"l": 20, "r": 20, "t": 60, "b": 20},
    )
    return figure
