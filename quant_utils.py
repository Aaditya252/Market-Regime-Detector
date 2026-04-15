from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from eda_utils import DIVERGING_SCALE, style_figure, style_heatmap_with_cell_borders


REGIME_COLORS = [
    ("Regime 0", "rgba(34, 197, 94, 0.13)", "#22c55e"),
    ("Regime 1", "rgba(239, 68, 68, 0.13)", "#ef4444"),
    ("Regime 2", "rgba(24, 166, 106, 0.13)", "#18a66a"),
    ("Regime 3", "rgba(143, 184, 170, 0.13)", "#8fb8aa"),
    ("Regime 4", "rgba(148, 163, 184, 0.13)", "#94a3b8"),
    ("Regime 5", "rgba(100, 116, 139, 0.13)", "#64748b"),
]

SEMANTIC_REGIME_COLORS = {
    "Bull": ("rgba(34, 197, 94, 0.13)", "#22c55e"),
    "Bear": ("rgba(239, 68, 68, 0.13)", "#ef4444"),
    "Sideways": ("rgba(148, 163, 184, 0.13)", "#94a3b8"),
    "Positive Trend": ("rgba(34, 197, 94, 0.13)", "#22c55e"),
    "Negative Trend": ("rgba(239, 68, 68, 0.13)", "#ef4444"),
    "Neutral": ("rgba(148, 163, 184, 0.13)", "#94a3b8"),
}


def _format_regime_display(regime_value: int, regime_labels: dict[int, str] | None = None) -> str:
    """Format regime display name with semantic label when available."""
    if regime_labels and regime_value in regime_labels:
        return f"{regime_labels[regime_value]} (Regime {regime_value})"
    return f"Regime {regime_value}"


def _semantic_colors_for_regime(regime_value: int, regime_labels: dict[int, str] | None = None) -> tuple[str, str]:
    """Return fill and line colors for a regime."""
    if regime_labels and regime_value in regime_labels:
        semantic = regime_labels[regime_value]
        if semantic in SEMANTIC_REGIME_COLORS:
            return SEMANTIC_REGIME_COLORS[semantic]
    palette = REGIME_COLORS[regime_value % len(REGIME_COLORS)]
    return palette[1], palette[2]


def classify_regime_state(avg_return: float, volatility: float, volatility_threshold: float) -> str:
    """Classify a regime into an interpretable market state."""
    if avg_return > 0 and volatility <= volatility_threshold:
        return "Bullish"
    if avg_return < 0 and volatility > volatility_threshold:
        return "Bearish"
    return "Sideways"


@dataclass(frozen=True)
class PlotPreparationResult:
    dataframe: pd.DataFrame
    time_column: str | None
    errors: list[str]


@dataclass(frozen=True)
class MarketRegimePlotData:
    full_series: pd.DataFrame
    regime_series: pd.DataFrame
    time_column: str | None
    errors: list[str]


def infer_time_column(dataframe: pd.DataFrame) -> str | None:
    """Infer a likely time column."""
    datetime_columns = list(
        dataframe.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns
    )
    if datetime_columns:
        return datetime_columns[0]

    for column in dataframe.columns:
        lowered = str(column).lower()
        if "date" in lowered or "time" in lowered:
            return column
    return None


def get_time_column_options(dataframe: pd.DataFrame) -> list[str]:
    """Return time column options that are likely to work for plotting."""
    options = list(dataframe.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns)
    for column in dataframe.columns:
        lowered = str(column).lower()
        if column not in options and ("date" in lowered or "time" in lowered):
            options.append(column)
    return options


def _coerce_time_column(dataframe: pd.DataFrame, time_column: str | None) -> tuple[pd.DataFrame, str | None]:
    """Coerce a valid time axis for charting."""
    frame = dataframe.copy()
    resolved_time_column = time_column if time_column and time_column in frame.columns else infer_time_column(frame)

    if resolved_time_column and resolved_time_column in frame.columns:
        coerced_time = pd.to_datetime(frame[resolved_time_column], errors="coerce")
        if coerced_time.notna().sum() >= 2:
            frame["Time"] = coerced_time
            return frame, resolved_time_column

    if isinstance(frame.index, pd.DatetimeIndex):
        frame = frame.copy()
        frame["Time"] = frame.index
        return frame, None

    frame = frame.reset_index().rename(columns={"index": "Time"})
    return frame, None


def prepare_time_series_frame(
    dataframe: pd.DataFrame,
    value_columns: list[str],
    time_column: str | None = None,
) -> PlotPreparationResult:
    """Prepare a validated time-aware frame for quantitative charts."""
    errors: list[str] = []
    if dataframe.empty:
        return PlotPreparationResult(pd.DataFrame(), time_column, ["No data is available for plotting."])

    missing_columns = [column for column in value_columns if column not in dataframe.columns]
    if missing_columns:
        return PlotPreparationResult(
            pd.DataFrame(),
            time_column,
            [f"Required columns are missing: {', '.join(missing_columns)}."],
        )

    frame, resolved_time_column = _coerce_time_column(dataframe, time_column)

    for column in value_columns:
        if column == "market_regime":
            frame[column] = pd.to_numeric(frame[column], errors="coerce").astype("Int64")
        else:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")

    selected = ["Time"] + value_columns
    frame = frame[selected].dropna(subset=["Time"]).sort_values("Time").reset_index(drop=True)
    return PlotPreparationResult(frame, resolved_time_column, errors)


def prepare_market_regime_plot_data(
    dataframe: pd.DataFrame,
    price_column: str,
    time_column: str | None = None,
) -> MarketRegimePlotData:
    """Prepare robust full-series and regime-series frames for market regime plotting."""
    errors: list[str] = []
    if dataframe.empty:
        return MarketRegimePlotData(pd.DataFrame(), pd.DataFrame(), time_column, ["The dataset is empty."])
    if price_column not in dataframe.columns:
        return MarketRegimePlotData(
            pd.DataFrame(),
            pd.DataFrame(),
            time_column,
            [f"The selected price column '{price_column}' is not available."],
        )
    if "market_regime" not in dataframe.columns:
        return MarketRegimePlotData(
            pd.DataFrame(),
            pd.DataFrame(),
            time_column,
            ["The market_regime column is not available. Train the clustering model first."],
        )

    full_series_result = prepare_time_series_frame(dataframe, [price_column], time_column=time_column)
    regime_source = dataframe.loc[dataframe["market_regime"].notna()].copy()
    regime_series_result = prepare_time_series_frame(
        regime_source,
        [price_column, "market_regime"],
        time_column=time_column,
    )

    errors.extend(full_series_result.errors)
    errors.extend(regime_series_result.errors)
    full_series = full_series_result.dataframe.dropna(subset=[price_column]).copy()
    regime_series = regime_series_result.dataframe.dropna(subset=[price_column, "market_regime"]).copy()

    if full_series.empty:
        errors.append("The selected price column does not contain plottable values.")
    if regime_series.empty:
        errors.append("No rows with valid market regime labels are available for plotting.")

    return MarketRegimePlotData(
        full_series=full_series,
        regime_series=regime_series,
        time_column=full_series_result.time_column or regime_series_result.time_column,
        errors=list(dict.fromkeys(errors)),
    )


def slice_recent_period(dataframe: pd.DataFrame, periods: int = 500) -> pd.DataFrame:
    """Return a recent window of observations for clearer visualization."""
    if dataframe.empty or len(dataframe) <= periods:
        return dataframe.copy()
    return dataframe.tail(periods).reset_index(drop=True)


def _iter_regime_segments(plot_frame: pd.DataFrame) -> list[tuple[object, object, int]]:
    """Return contiguous regime segments as start, end, and regime."""
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


def build_market_regime_figure(
    dataframe: pd.DataFrame,
    price_column: str,
    time_column: str | None = None,
    recent_only: bool = False,
    recent_periods: int = 500,
    regime_labels: dict[int, str] | None = None,
    expected_regimes: list[int] | None = None,
    display_mode: str = "Raw Price",
) -> go.Figure:
    """Build a professional market regime chart."""
    plot_data = prepare_market_regime_plot_data(dataframe, price_column, time_column=time_column)
    if plot_data.full_series.empty:
        return style_figure(go.Figure())

    full_series = plot_data.full_series.copy()
    regime_series = plot_data.regime_series.copy()
    if recent_only:
        full_series = slice_recent_period(full_series, recent_periods)
        if not regime_series.empty:
            regime_series = regime_series.loc[
                regime_series["Time"].isin(full_series["Time"])
            ].reset_index(drop=True)
    if not regime_series.empty:
        regime_series["market_regime"] = regime_series["market_regime"].astype(int)
        regime_series["Regime Label"] = regime_series["market_regime"].map(
            lambda value: _format_regime_display(int(value), regime_labels)
        )

    y_column = price_column
    y_axis_title = price_column
    hover_label = price_column
    if display_mode == "Log Scale":
        positive_mask = full_series[price_column] > 0
        full_series = full_series.loc[positive_mask].copy()
        if not regime_series.empty:
            regime_series = regime_series.loc[regime_series[price_column] > 0].copy()
        if full_series.empty:
            return style_figure(go.Figure())
        full_series["Display Value"] = full_series[price_column]
        if not regime_series.empty:
            regime_series["Display Value"] = regime_series[price_column]
        y_column = "Display Value"
        y_axis_title = f"{price_column} (Log Scale)"
    elif display_mode == "Rebased":
        first_value = pd.to_numeric(full_series[price_column], errors="coerce").dropna()
        if first_value.empty or float(first_value.iloc[0]) == 0:
            return style_figure(go.Figure())
        base_value = float(first_value.iloc[0])
        full_series["Display Value"] = (pd.to_numeric(full_series[price_column], errors="coerce") / base_value) * 100.0
        if not regime_series.empty:
            regime_series["Display Value"] = (pd.to_numeric(regime_series[price_column], errors="coerce") / base_value) * 100.0
        y_column = "Display Value"
        y_axis_title = f"{price_column} (Rebased = 100)"
        hover_label = "Rebased"

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=full_series["Time"],
            y=full_series[y_column],
            mode="lines",
            name=price_column,
            line={"color": "#18a66a", "width": 1.8, "shape": "spline", "smoothing": 0.2},
            hovertemplate="Date: %{x}<br>" + f"{hover_label}: " + "%{y:.4f}<extra></extra>",
        )
    )

    if not regime_series.empty:
        for start_time, end_time, regime in _iter_regime_segments(regime_series):
            fill_color, _ = _semantic_colors_for_regime(regime, regime_labels)
            figure.add_vrect(
                x0=start_time,
                x1=end_time,
                fillcolor=fill_color,
                line_width=0,
                layer="below",
            )

        for regime, regime_frame in regime_series.groupby("market_regime", dropna=True):
            regime_value = int(regime)
            regime_label = _format_regime_display(regime_value, regime_labels)
            figure.add_trace(
                go.Scatter(
                    x=regime_frame["Time"],
                    y=regime_frame[y_column],
                    mode="markers",
                    name=regime_label,
                    marker={
                        "size": 3.6,
                        "color": "#ef4444",
                        "line": {"width": 0},
                        "opacity": 0.85,
                    },
                    hovertemplate=(
                        "Date: %{x}<br>"
                        + f"{hover_label}: "
                        + "%{y:.4f}<br>"
                        + f"Regime: {regime_label}<extra></extra>"
                    ),
                )
            )

        if expected_regimes:
            visible_regimes = set(regime_series["market_regime"].dropna().astype(int).tolist())
            for regime_value in sorted(set(expected_regimes)):
                if regime_value in visible_regimes:
                    continue
                figure.add_trace(
                    go.Scatter(
                        x=[None],
                        y=[None],
                        mode="markers",
                        name=_format_regime_display(regime_value, regime_labels),
                        marker={"size": 3.6, "color": "#ef4444", "opacity": 0.85},
                        showlegend=True,
                    )
                )

    figure.update_layout(
        title_text="",
        xaxis_title="" if not recent_only else "Date",
        yaxis_title=y_axis_title,
        hovermode="x unified",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.03, "x": 0},
        height=760,
        margin={"t": 28, "b": 42 if not recent_only else 28},
    )
    figure.update_xaxes(
        showgrid=False,
        rangeslider_visible=not recent_only,
        rangeslider={"thickness": 0.12},
        rangeselector={
            "buttons": [
                {"count": 1, "label": "1Y", "step": "year", "stepmode": "backward"},
                {"count": 3, "label": "3Y", "step": "year", "stepmode": "backward"},
                {"count": 5, "label": "5Y", "step": "year", "stepmode": "backward"},
                {"step": "all", "label": "All"},
            ]
        } if not recent_only else None,
    )
    if not recent_only:
        figure.add_annotation(
            x=0.5,
            y=-0.18,
            xref="paper",
            yref="paper",
            text="Historical Timeline",
            showarrow=False,
            font={"size": 13, "color": "#cbd5e1"},
        )
    figure.update_yaxes(gridcolor="rgba(255, 255, 255, 0.05)", type="log" if display_mode == "Log Scale" else "linear")
    return style_figure(figure)


def build_cluster_distribution_figure(
    dataframe: pd.DataFrame,
    regime_labels: dict[int, str] | None = None,
) -> go.Figure:
    """Build a cluster distribution chart."""
    if "market_regime" not in dataframe.columns:
        return style_figure(go.Figure())

    cluster_distribution = (
        dataframe.loc[dataframe["market_regime"].notna(), "market_regime"]
        .astype(int)
        .value_counts()
        .sort_index()
        .rename_axis("Cluster")
        .reset_index(name="Count")
    )
    cluster_distribution["Regime"] = cluster_distribution["Cluster"].map(
        lambda value: _format_regime_display(int(value), regime_labels)
    )
    cluster_distribution["Semantic"] = cluster_distribution["Cluster"].map(
        lambda value: regime_labels.get(int(value), f"Regime {int(value)}") if regime_labels else f"Regime {int(value)}"
    )
    color_sequence = []
    for _, row in cluster_distribution.iterrows():
        _, color = _semantic_colors_for_regime(int(row["Cluster"]), regime_labels)
        color_sequence.append(color)

    figure = px.bar(
        cluster_distribution,
        x="Regime",
        y="Count",
        color="Semantic",
        title="Cluster Distribution",
        color_discrete_sequence=color_sequence,
    )
    figure.update_layout(
        xaxis_title="Cluster",
        yaxis_title="Observations",
        showlegend=False,
        height=430,
        margin={"t": 36, "l": 18, "r": 18, "b": 18},
    )
    figure.update_traces(
        width=0.78,
        marker_line_width=0,
        hovertemplate="Regime: %{x}<br>Observations: %{y:,}<extra></extra>",
    )
    return style_figure(figure)


def build_regime_transition_figure(
    dataframe: pd.DataFrame,
    regime_labels: dict[int, str] | None = None,
) -> go.Figure:
    """Build a regime transition matrix heatmap."""
    if "market_regime" not in dataframe.columns:
        return style_figure(go.Figure())

    transition_matrix = build_transition_probability_matrix(dataframe, regime_labels=regime_labels)
    if transition_matrix.empty:
        return style_figure(go.Figure())

    figure = px.imshow(
        transition_matrix,
        text_auto=".2f",
        aspect="equal",
        color_continuous_scale=[
            [0.0, "#3b1016"],
            [0.35, "#5a1b22"],
            [0.5, "#0f131a"],
            [0.75, "#145c46"],
            [1.0, "#22c55e"],
        ],
        title="Regime Transition Matrix",
    )
    figure.update_traces(
        hovertemplate="Current: %{y}<br>Next: %{x}<br>Probability: %{z:.2f}<extra></extra>",
        xgap=6,
        ygap=6,
    )
    figure.update_layout(
        xaxis_title="Next Regime",
        yaxis_title="Current Regime",
        coloraxis_colorbar_title="",
        coloraxis_colorbar={
            "thickness": 10,
            "len": 0.72,
            "x": 1.03,
            "outlinewidth": 0,
            "tickfont": {"size": 11, "color": "#cbd5e1"},
        },
        height=430,
        margin={"t": 36, "l": 18, "r": 36, "b": 18},
    )
    figure.update_xaxes(side="bottom", tickangle=-20, showgrid=False)
    figure.update_yaxes(showgrid=False)
    figure = style_heatmap_with_cell_borders(figure, gap=2)
    return style_figure(figure)


def build_transition_probability_matrix(
    dataframe: pd.DataFrame,
    regime_labels: dict[int, str] | None = None,
) -> pd.DataFrame:
    """Compute current-to-next regime transition probabilities."""
    raw_matrix = compute_transition_probability_matrix_raw(dataframe)
    if raw_matrix.empty:
        return pd.DataFrame()
    transition_matrix = raw_matrix.copy()
    transition_matrix.index = [_format_regime_display(int(value), regime_labels) for value in transition_matrix.index]
    transition_matrix.columns = [_format_regime_display(int(value), regime_labels) for value in transition_matrix.columns]
    return transition_matrix


def compute_transition_probability_matrix_raw(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Compute current-to-next regime transition probabilities with numeric regime ids."""
    if "market_regime" not in dataframe.columns:
        return pd.DataFrame()
    regime_series = pd.to_numeric(dataframe["market_regime"], errors="coerce").dropna().astype(int)
    if len(regime_series) < 2:
        return pd.DataFrame()

    transition_frame = pd.DataFrame({"current": regime_series.iloc[:-1].values, "next": regime_series.iloc[1:].values})
    transition_matrix = pd.crosstab(transition_frame["current"], transition_frame["next"], normalize="index").fillna(0)
    return transition_matrix


def compute_current_regime_outlook(
    dataframe: pd.DataFrame,
    regime_labels: dict[int, str] | None = None,
) -> pd.DataFrame:
    """Return the next-step transition distribution from the current regime."""
    raw_matrix = compute_transition_probability_matrix_raw(dataframe)
    if raw_matrix.empty:
        return pd.DataFrame(columns=["Regime", "Probability"])

    regime_series = pd.to_numeric(dataframe["market_regime"], errors="coerce").dropna().astype(int)
    if regime_series.empty:
        return pd.DataFrame(columns=["Regime", "Probability"])
    current_regime = int(regime_series.iloc[-1])
    if current_regime not in raw_matrix.index:
        return pd.DataFrame(columns=["Regime", "Probability"])

    outlook = (
        raw_matrix.loc[current_regime]
        .rename("Probability")
        .reset_index()
    )
    first_column = outlook.columns[0]
    outlook = outlook.rename(columns={first_column: "Regime"})
    outlook = outlook.sort_values("Probability", ascending=False).reset_index(drop=True)
    outlook["Regime Id"] = outlook["Regime"].astype(int)
    outlook["Regime"] = outlook["Regime Id"].map(lambda value: _format_regime_display(int(value), regime_labels))
    outlook["Current Regime Id"] = current_regime
    return outlook


def build_current_regime_outlook_figure(
    dataframe: pd.DataFrame,
    regime_labels: dict[int, str] | None = None,
) -> go.Figure:
    """Build a compact forward transition probability chart from the current regime."""
    outlook = compute_current_regime_outlook(dataframe, regime_labels=regime_labels)
    if outlook.empty:
        return style_figure(go.Figure())

    color_sequence = [
        _semantic_colors_for_regime(int(value), regime_labels)[1]
        for value in outlook["Regime Id"]
    ]
    figure = px.bar(
        outlook,
        x="Probability",
        y="Regime",
        orientation="h",
        color="Regime",
        color_discrete_sequence=color_sequence,
        title="Current State Outlook",
    )
    figure.update_traces(
        texttemplate="%{x:.0%}",
        textposition="outside",
        hovertemplate="Next State: %{y}<br>Probability: %{x:.2%}<extra></extra>",
        marker_line_width=0,
    )
    figure.update_layout(
        showlegend=False,
        xaxis_title="Transition Probability",
        yaxis_title="",
        xaxis={"tickformat": ".0%", "range": [0, 1]},
        height=300,
        margin={"t": 36, "l": 18, "r": 18, "b": 18},
    )
    return style_figure(figure)


def compute_markov_regime_forecast(
    dataframe: pd.DataFrame,
    steps_ahead: int,
    regime_labels: dict[int, str] | None = None,
) -> pd.DataFrame:
    """Project regime probabilities n steps ahead using the empirical transition matrix."""
    raw_matrix = compute_transition_probability_matrix_raw(dataframe)
    if raw_matrix.empty:
        return pd.DataFrame(columns=["Regime", "Regime Id", "Probability", "Steps", "Current Regime Id"])

    regime_series = pd.to_numeric(dataframe["market_regime"], errors="coerce").dropna().astype(int)
    if regime_series.empty:
        return pd.DataFrame(columns=["Regime", "Regime Id", "Probability", "Steps", "Current Regime Id"])

    all_regimes = sorted(set(raw_matrix.index.tolist()) | set(raw_matrix.columns.tolist()) | set(regime_series.tolist()))
    transition_matrix = raw_matrix.reindex(index=all_regimes, columns=all_regimes, fill_value=0.0).astype(float)

    # Preserve any rows with missing probability mass by assigning self-persistence.
    row_sums = transition_matrix.sum(axis=1)
    for regime in all_regimes:
        if row_sums.loc[regime] <= 0:
            transition_matrix.loc[regime, regime] = 1.0
    transition_matrix = transition_matrix.div(transition_matrix.sum(axis=1), axis=0).fillna(0.0)

    current_regime = int(regime_series.iloc[-1])
    state_vector = np.zeros(len(all_regimes), dtype=float)
    state_vector[all_regimes.index(current_regime)] = 1.0

    steps_ahead = max(1, int(steps_ahead))
    powered_matrix = np.linalg.matrix_power(transition_matrix.to_numpy(dtype=float), steps_ahead)
    forecast_vector = state_vector @ powered_matrix

    forecast = pd.DataFrame(
        {
            "Regime Id": all_regimes,
            "Probability": forecast_vector,
        }
    ).sort_values("Probability", ascending=False).reset_index(drop=True)
    forecast["Regime"] = forecast["Regime Id"].map(
        lambda value: _format_regime_display(int(value), regime_labels)
    )
    forecast["Steps"] = steps_ahead
    forecast["Current Regime Id"] = current_regime
    return forecast[["Regime", "Regime Id", "Probability", "Steps", "Current Regime Id"]]


def build_markov_regime_forecast_figure(
    dataframe: pd.DataFrame,
    steps_ahead: int,
    regime_labels: dict[int, str] | None = None,
) -> go.Figure:
    """Build a multi-step Markov-style regime probability forecast chart."""
    forecast = compute_markov_regime_forecast(dataframe, steps_ahead=steps_ahead, regime_labels=regime_labels)
    if forecast.empty:
        return style_figure(go.Figure())

    color_sequence = [
        _semantic_colors_for_regime(int(value), regime_labels)[1]
        for value in forecast["Regime Id"]
    ]
    figure = px.bar(
        forecast,
        x="Probability",
        y="Regime",
        orientation="h",
        color="Regime",
        color_discrete_sequence=color_sequence,
        title=f"{steps_ahead}-Step State Forecast",
    )
    figure.update_traces(
        texttemplate="%{x:.0%}",
        textposition="outside",
        marker_line_width=0,
        hovertemplate="Forecast State: %{y}<br>Probability: %{x:.2%}<extra></extra>",
    )
    figure.update_layout(
        showlegend=False,
        xaxis_title="Forecast Probability",
        yaxis_title="",
        xaxis={"tickformat": ".0%", "range": [0, 1]},
        height=320,
        margin={"t": 36, "l": 18, "r": 18, "b": 18},
    )
    return style_figure(figure)


def build_regime_timeline_figure(
    dataframe: pd.DataFrame,
    time_column: str | None = None,
    regime_labels: dict[int, str] | None = None,
    recent_periods: int = 220,
) -> go.Figure:
    """Build a compact ribbon strip showing recent regime occupancy."""
    result = prepare_time_series_frame(dataframe, ["market_regime"], time_column=time_column)
    plot_frame = result.dataframe.dropna(subset=["market_regime"]).copy()
    if plot_frame.empty:
        return style_figure(go.Figure())

    plot_frame["market_regime"] = pd.to_numeric(plot_frame["market_regime"], errors="coerce").astype("Int64")
    plot_frame = plot_frame.dropna(subset=["market_regime"]).copy()
    if plot_frame.empty:
        return style_figure(go.Figure())
    plot_frame["market_regime"] = plot_frame["market_regime"].astype(int)
    plot_frame = plot_frame.tail(recent_periods).reset_index(drop=True)

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=plot_frame["Time"],
            y=[1.0] * len(plot_frame),
            mode="lines",
            line={"color": "rgba(0,0,0,0)", "width": 1},
            hoverinfo="skip",
            showlegend=False,
        )
    )

    for start_time, end_time, regime_value in _iter_regime_segments(plot_frame):
        fill_color, line_color = _semantic_colors_for_regime(int(regime_value), regime_labels)
        regime_label = _format_regime_display(int(regime_value), regime_labels)
        figure.add_vrect(
            x0=start_time,
            x1=end_time,
            y0=0.2,
            y1=0.8,
            fillcolor=fill_color,
            line_width=1,
            line_color=line_color,
            layer="below",
        )
        figure.add_trace(
            go.Scatter(
                x=[start_time, end_time],
                y=[0.5, 0.5],
                mode="lines",
                line={"color": line_color, "width": 8},
                name=regime_label,
                hovertemplate=(
                    f"State: {regime_label}<br>"
                    + "Start: %{x}<br>"
                    + "End: %{customdata}<extra></extra>"
                ),
                customdata=[end_time, end_time],
                showlegend=False,
            )
        )

    figure.update_layout(
        title="State Timeline",
        height=140,
        margin={"t": 28, "l": 18, "r": 18, "b": 18},
        xaxis_title="",
        yaxis_title="",
        yaxis={"showticklabels": False, "showgrid": False, "zeroline": False, "range": [0, 1]},
    )
    figure.update_xaxes(showgrid=False)
    return style_figure(figure)


def compute_regime_statistics(
    dataframe: pd.DataFrame,
    regime_col: str,
    price_column: str,
    time_column: str | None = None,
) -> pd.DataFrame:
    """Compute cluster-level financial statistics used for semantic interpretation."""
    if regime_col not in dataframe.columns or price_column not in dataframe.columns:
        return pd.DataFrame(columns=["Regime", "Mean Return", "Volatility", "Count", "Average Price Change"])

    prepared = prepare_time_series_frame(dataframe, [price_column, regime_col], time_column=time_column)
    frame = prepared.dataframe.dropna(subset=[price_column, regime_col]).copy()
    if frame.empty:
        return pd.DataFrame(columns=["Regime", "Mean Return", "Volatility", "Count", "Average Price Change"])

    frame[regime_col] = pd.to_numeric(frame[regime_col], errors="coerce").astype("Int64")
    frame = frame.dropna(subset=[regime_col]).copy()
    if frame.empty:
        return pd.DataFrame(columns=["Regime", "Mean Return", "Volatility", "Count", "Average Price Change"])
    frame[regime_col] = frame[regime_col].astype(int)
    numeric_price = pd.to_numeric(frame[price_column], errors="coerce")
    frame["_segment"] = frame[regime_col].ne(frame[regime_col].shift()).cumsum()
    # Compute return diagnostics within contiguous regime runs so regime-level
    # averages are not contaminated by price moves from a previous regime.
    frame["returns"] = frame.groupby("_segment", dropna=False)[price_column].transform(
        lambda series: pd.to_numeric(series, errors="coerce").pct_change()
    )
    frame["price_change"] = frame.groupby("_segment", dropna=False)[price_column].transform(
        lambda series: pd.to_numeric(series, errors="coerce").diff()
    )
    frame[price_column] = numeric_price

    stats = (
        frame.groupby(regime_col, dropna=True)
        .agg(
            **{
                "Mean Return": ("returns", "mean"),
                "Volatility": ("returns", "std"),
                "Count": (regime_col, "size"),
                "Average Price Change": ("price_change", "mean"),
            }
        )
        .reset_index()
        .rename(columns={regime_col: "Regime"})
    )
    for column in ["Mean Return", "Volatility", "Average Price Change"]:
        stats[column] = pd.to_numeric(stats[column], errors="coerce").fillna(0.0)
    stats["Count"] = pd.to_numeric(stats["Count"], errors="coerce").fillna(0).astype(int)
    return stats.sort_values("Regime").reset_index(drop=True)


def infer_regime_labels(regime_stats: pd.DataFrame) -> dict[int, str]:
    """Infer semantic regime names from return and volatility behavior."""
    if regime_stats.empty:
        return {}

    stats = regime_stats.copy()
    if not {"Regime", "Mean Return", "Volatility"}.issubset(stats.columns):
        return {}
    stats["Regime"] = pd.to_numeric(stats["Regime"], errors="coerce")
    stats = stats.dropna(subset=["Regime"]).copy()
    if stats.empty:
        return {}
    stats["Regime"] = stats["Regime"].astype(int)
    stats["Mean Return"] = pd.to_numeric(stats["Mean Return"], errors="coerce").fillna(0.0)
    stats["Volatility"] = pd.to_numeric(stats["Volatility"], errors="coerce").fillna(0.0)

    abs_returns = stats["Mean Return"].abs()
    near_zero_threshold = float(abs_returns.median() * 0.35) if abs_returns.notna().any() else 0.0
    near_zero_threshold = max(near_zero_threshold, 1e-6)
    volatility_threshold = float(stats["Volatility"].median()) if stats["Volatility"].notna().any() else 0.0

    mapping: dict[int, str] = {}
    for _, row in stats.iterrows():
        regime_value = int(row["Regime"])
        mean_return = float(row["Mean Return"])
        volatility = float(row["Volatility"])

        if mean_return > near_zero_threshold and volatility <= volatility_threshold * 1.15:
            mapping[regime_value] = "Bull"
        elif mean_return < -near_zero_threshold and volatility >= volatility_threshold * 0.9:
            mapping[regime_value] = "Bear"
        else:
            mapping[regime_value] = "Sideways"

    if "Bull" not in mapping.values() and (stats["Mean Return"] > 0).any():
        best = int(stats.loc[stats["Mean Return"].idxmax(), "Regime"])
        mapping[best] = "Positive Trend"
    if "Bear" not in mapping.values() and (stats["Mean Return"] < 0).any():
        worst = int(stats.loc[stats["Mean Return"].idxmin(), "Regime"])
        mapping[worst] = "Negative Trend"
    for regime_value in stats["Regime"].tolist():
        mapping.setdefault(int(regime_value), "Neutral")
    return mapping


def apply_regime_labels(
    dataframe: pd.DataFrame,
    mapping: dict[int, str],
    regime_col: str = "market_regime",
) -> pd.DataFrame:
    """Attach semantic regime labels as a regime_type column."""
    frame = dataframe.copy()
    if regime_col not in frame.columns:
        frame["regime_type"] = pd.NA
        return frame
    numeric_regime = pd.to_numeric(frame[regime_col], errors="coerce")
    frame["regime_type"] = numeric_regime.map(lambda value: mapping.get(int(value), "Neutral") if pd.notna(value) else pd.NA)
    return frame


def build_regime_summary_table(
    dataframe: pd.DataFrame,
    price_column: str,
    time_column: str | None = None,
) -> pd.DataFrame:
    """Build a summary table for each detected regime."""
    stats = compute_regime_statistics(
        dataframe,
        regime_col="market_regime",
        price_column=price_column,
        time_column=time_column,
    )
    if stats.empty:
        return pd.DataFrame(columns=["Regime", "Regime Type", "Rows", "Average Return", "Volatility", "Average Duration"])
    label_mapping = infer_regime_labels(stats)

    plot_data = prepare_market_regime_plot_data(dataframe, price_column, time_column=time_column)
    regime_frame = plot_data.regime_series.copy()
    if regime_frame.empty:
        return pd.DataFrame(columns=["Regime", "Regime Type", "Rows", "Average Return", "Volatility", "Average Duration"])

    summary = stats.rename(columns={"Mean Return": "Average Return", "Count": "Rows"})
    summary["Regime"] = summary["Regime"].astype(int)
    summary["Regime Type"] = summary["Regime"].map(lambda value: label_mapping.get(int(value), "Neutral"))
    summary["Average Duration"] = summary["Rows"].astype(float)

    transition_counts = regime_frame["market_regime"].ne(regime_frame["market_regime"].shift()).cumsum()
    segment_lengths = (
        regime_frame.assign(segment=transition_counts)
        .groupby(["market_regime", "segment"])
        .size()
        .groupby(level=0)
        .mean()
    )
    summary["Average Duration"] = summary["Regime"].astype(int).map(segment_lengths).fillna(summary["Rows"])
    summary["Regime"] = summary["Regime"].map(lambda value: f"Regime {int(value)}")
    summary["Average Return"] = summary["Average Return"].round(4)
    summary["Volatility"] = summary["Volatility"].round(4)
    summary["Average Duration"] = summary["Average Duration"].round(1)
    return summary[["Regime", "Regime Type", "Rows", "Average Return", "Volatility", "Average Duration"]].sort_values("Regime").reset_index(drop=True)


def build_regime_insights_table(
    dataframe: pd.DataFrame,
    price_column: str,
    time_column: str | None = None,
) -> pd.DataFrame:
    """Build regime-level return and price-change insights with semantic labels."""
    stats = compute_regime_statistics(
        dataframe,
        regime_col="market_regime",
        price_column=price_column,
        time_column=time_column,
    )
    if stats.empty:
        return pd.DataFrame(
            columns=[
                "Regime",
                "Regime Type",
                "Data Points",
                "Average Return",
                "Volatility",
                "Average Price Change",
            ]
        )
    label_mapping = infer_regime_labels(stats)
    insights = stats.rename(
        columns={
            "Count": "Data Points",
            "Mean Return": "Average Return",
        }
    ).copy()
    insights["Regime Type"] = insights["Regime"].map(lambda value: label_mapping.get(int(value), "Neutral"))
    insights["Regime"] = insights["Regime"].map(lambda value: f"Regime {int(value)}")
    for column in ["Average Return", "Volatility", "Average Price Change"]:
        insights[column] = insights[column].round(4)
    return insights[
        ["Regime", "Regime Type", "Data Points", "Average Return", "Volatility", "Average Price Change"]
    ].sort_values("Regime").reset_index(drop=True)


def build_backtest_comparison_figure(
    dataframe: pd.DataFrame,
    price_column: str,
    time_column: str | None = None,
    regime_state_map: dict[int, str] | None = None,
) -> go.Figure:
    """Build strategy-versus-market cumulative return comparison."""
    if regime_state_map is None:
        regime_state_map = {}
    result = prepare_time_series_frame(dataframe, [price_column, "market_regime"], time_column=time_column)
    plot_frame = result.dataframe.dropna(subset=[price_column, "market_regime"]).copy()
    if plot_frame.empty:
        return style_figure(go.Figure())

    plot_frame["market_regime"] = pd.to_numeric(plot_frame["market_regime"], errors="coerce").astype("Int64")
    plot_frame = plot_frame.dropna(subset=["market_regime"]).copy()
    if plot_frame.empty:
        return style_figure(go.Figure())
    plot_frame["market_regime"] = plot_frame["market_regime"].astype(int)
    plot_frame["Market Return"] = pd.to_numeric(plot_frame[price_column], errors="coerce").pct_change().fillna(0.0)

    positions = []
    for regime_value in plot_frame["market_regime"]:
        state = regime_state_map.get(int(regime_value), "Sideways")
        if state in {"Bull", "Bullish", "Positive Trend"}:
            positions.append(1.0)
        elif state in {"Bear", "Bearish", "Negative Trend"}:
            positions.append(0.0)
        else:
            positions.append(0.0)
    plot_frame["Position"] = pd.Series(positions, index=plot_frame.index)
    plot_frame["Strategy Return"] = plot_frame["Position"].shift(1).fillna(0.0) * plot_frame["Market Return"]
    plot_frame["Strategy Cumulative"] = (1 + plot_frame["Strategy Return"]).cumprod() - 1
    plot_frame["Buy and Hold"] = (1 + plot_frame["Market Return"]).cumprod() - 1

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=plot_frame["Time"],
            y=plot_frame["Strategy Cumulative"],
            mode="lines",
            name="Regime Strategy",
            line={"color": "#22c55e", "width": 2.2},
        )
    )
    figure.add_trace(
        go.Scatter(
            x=plot_frame["Time"],
            y=plot_frame["Buy and Hold"],
            mode="lines",
            name="Buy & Hold",
            line={"color": "#94a3b8", "width": 1.8, "dash": "dot"},
        )
    )
    figure.update_layout(
        title="Backtest: Regime Strategy vs Buy-and-Hold",
        xaxis_title="Date",
        yaxis_title="Cumulative Return",
        height=450,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
    )
    return style_figure(figure)


def build_confidence_history_figure(confidence_history: pd.DataFrame) -> go.Figure:
    """Build a compact confidence-history sparkline for regime assignments."""
    if confidence_history.empty:
        return style_figure(go.Figure())

    plot_frame = confidence_history.copy()
    plot_frame["Confidence"] = pd.to_numeric(plot_frame["Confidence"], errors="coerce")
    plot_frame = plot_frame.dropna(subset=["Confidence", "Time"])
    if plot_frame.empty:
        return style_figure(go.Figure())

    figure = px.line(
        plot_frame,
        x="Time",
        y="Confidence",
        title="Regime Confidence History",
        color_discrete_sequence=["#22c55e"],
    )
    figure.update_traces(
        line={"width": 1.9},
        hovertemplate="Time: %{x}<br>Confidence: %{y:.2%}<extra></extra>",
    )
    figure.update_layout(
        height=260,
        xaxis_title="",
        yaxis_title="Confidence",
        yaxis={"tickformat": ".0%", "range": [0, 1]},
        margin={"t": 34, "l": 18, "r": 18, "b": 18},
    )
    figure.update_xaxes(showgrid=False)
    return style_figure(figure)


def build_regime_feature_profile_figure(dataframe: pd.DataFrame, feature_columns: list[str]) -> go.Figure:
    """Build a heatmap of average feature values by regime as an interpretation proxy."""
    if "market_regime" not in dataframe.columns or len(feature_columns) < 2:
        return style_figure(go.Figure())

    valid_columns = [column for column in feature_columns if column in dataframe.columns]
    if len(valid_columns) < 2:
        return style_figure(go.Figure())

    profile_frame = dataframe.loc[dataframe["market_regime"].notna(), valid_columns + ["market_regime"]].copy()
    if profile_frame.empty:
        return style_figure(go.Figure())

    numeric_profile = profile_frame[valid_columns].apply(pd.to_numeric, errors="coerce")
    valid_variance_columns = numeric_profile.std(ddof=0).replace(0, pd.NA).dropna().index.tolist()
    if len(valid_variance_columns) < 2:
        return style_figure(go.Figure())

    numeric_profile = numeric_profile[valid_variance_columns]
    normalized = (numeric_profile - numeric_profile.mean()) / numeric_profile.std(ddof=0).replace(0, 1)
    normalized["market_regime"] = pd.to_numeric(profile_frame["market_regime"], errors="coerce").astype("Int64")
    heatmap_source = normalized.groupby("market_regime")[valid_variance_columns].mean()
    heatmap_source.index = [f"Regime {int(value)}" for value in heatmap_source.index]
    renamed_columns = []
    for column in heatmap_source.columns:
        clean_column = str(column).replace("_returns", " Returns").replace("_rolling_volatility_", " Vol ").replace("_rolling_mean_", " Mean ")
        clean_column = clean_column.replace("_", " ")
        renamed_columns.append(clean_column.title())
    heatmap_source.columns = renamed_columns

    figure = px.imshow(
        heatmap_source,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale=DIVERGING_SCALE,
        title="Regime Feature Profile",
    )
    figure.update_layout(
        xaxis_title="Features",
        yaxis_title="Regime",
        coloraxis_colorbar_title="Z-Score",
        height=420,
        margin={"t": 36, "l": 18, "r": 18, "b": 18},
    )
    figure.update_traces(
        xgap=8,
        ygap=8,
        hovertemplate="Regime: %{y}<br>Feature: %{x}<br>Z-Score: %{z:.2f}<extra></extra>",
    )
    figure.update_xaxes(
        tickangle=-18,
        showgrid=False,
        tickfont={"size": 12, "color": "#e5e7eb"},
    )
    figure.update_yaxes(
        showgrid=False,
        tickfont={"size": 12, "color": "#e5e7eb"},
    )
    figure = style_heatmap_with_cell_borders(figure, gap=2)
    return style_figure(figure)


def build_quant_correlation_figure(dataframe: pd.DataFrame, columns: list[str]) -> go.Figure:
    """Build a correlation heatmap for quantitative tools."""
    if len(columns) < 2:
        return style_figure(go.Figure())

    correlation_matrix = dataframe[columns].corr(numeric_only=True)
    figure = px.imshow(
        correlation_matrix,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale=DIVERGING_SCALE,
        title="Selected Features Correlation",
    )
    figure.update_layout(
        xaxis_title="Features",
        yaxis_title="Features",
        coloraxis_colorbar_title="Correlation",
        height=620,
    )
    figure = style_heatmap_with_cell_borders(figure, gap=2)
    return style_figure(figure)


def build_returns_histogram(dataframe: pd.DataFrame, returns_column: str) -> go.Figure:
    """Build a returns histogram."""
    if returns_column not in dataframe.columns:
        return style_figure(go.Figure())

    figure = px.histogram(
        dataframe.dropna(subset=[returns_column]),
        x=returns_column,
        nbins=50,
        title="Returns Distribution",
        color_discrete_sequence=["#18a66a"],
    )
    figure.update_layout(xaxis_title=returns_column, yaxis_title="Frequency")
    figure.update_traces(
        marker={"line": {"color": "rgba(8, 11, 16, 0.85)", "width": 0.9}},
        hovertemplate=f"{returns_column}: %{{x:.4f}}<br>Frequency: %{{y:,}}<extra></extra>",
    )
    figure.update_layout(height=430)
    return style_figure(figure)


def build_cumulative_returns_figure(
    dataframe: pd.DataFrame,
    returns_column: str,
    time_column: str | None = None,
) -> go.Figure:
    """Build a cumulative returns line chart."""
    result = prepare_time_series_frame(dataframe, [returns_column], time_column=time_column)
    plot_frame = result.dataframe.dropna(subset=[returns_column])
    if plot_frame.empty:
        return style_figure(go.Figure())

    plot_frame["Cumulative Returns"] = (1 + plot_frame[returns_column]).cumprod() - 1

    figure = px.line(
        plot_frame,
        x="Time",
        y="Cumulative Returns",
        title="Cumulative Returns",
        color_discrete_sequence=["#a7b4c2"],
    )
    figure.update_layout(xaxis_title="Date", yaxis_title="Cumulative Return")
    figure.update_layout(height=430)
    return style_figure(figure)


def build_rolling_volatility_figure(
    dataframe: pd.DataFrame,
    price_column: str,
    window: int,
    time_column: str | None = None,
) -> go.Figure:
    """Build a rolling volatility chart."""
    result = prepare_time_series_frame(dataframe, [price_column], time_column=time_column)
    plot_frame = result.dataframe.dropna(subset=[price_column])
    if plot_frame.empty:
        return style_figure(go.Figure())

    returns = plot_frame[price_column].pct_change()
    plot_frame["Rolling Volatility"] = returns.rolling(window=window, min_periods=2).std()

    figure = px.line(
        plot_frame,
        x="Time",
        y="Rolling Volatility",
        title="Rolling Volatility",
        color_discrete_sequence=["#18a66a"],
    )
    figure.update_layout(xaxis_title="Date", yaxis_title="Volatility")
    figure.update_layout(height=520)
    return style_figure(figure)


def compute_daily_returns(
    dataframe: pd.DataFrame,
    price_column: str | None = None,
    returns_column: str | None = None,
    time_column: str | None = None,
) -> pd.DataFrame:
    """Compute a clean daily-returns frame for strategy simulation."""
    if returns_column and returns_column in dataframe.columns:
        required_columns = [returns_column]
        if "market_regime" in dataframe.columns:
            required_columns.append("market_regime")
        if "regime_type" in dataframe.columns:
            required_columns.append("regime_type")
        result = prepare_time_series_frame(dataframe, required_columns, time_column=time_column)
        frame = result.dataframe.copy()
        frame["Market Return"] = pd.to_numeric(frame[returns_column], errors="coerce")
    else:
        if not price_column or price_column not in dataframe.columns:
            return pd.DataFrame()
        required_columns = [price_column]
        if "market_regime" in dataframe.columns:
            required_columns.append("market_regime")
        if "regime_type" in dataframe.columns:
            required_columns.append("regime_type")
        result = prepare_time_series_frame(dataframe, required_columns, time_column=time_column)
        frame = result.dataframe.copy()
        numeric_price = pd.to_numeric(frame[price_column], errors="coerce")
        frame["Market Return"] = numeric_price.pct_change()

    if "regime_type" in frame.columns:
        frame["regime_type"] = frame["regime_type"].astype("string")
    frame = frame.dropna(subset=["Market Return"]).reset_index(drop=True)
    return frame


def compute_strategy_returns(
    returns_frame: pd.DataFrame,
    bull_exposure: float,
    bear_exposure: float,
    sideways_exposure: float,
    transaction_cost: float = 0.0,
) -> pd.DataFrame:
    """Apply regime-dependent exposure and compute strategy returns."""
    if returns_frame.empty or "Market Return" not in returns_frame.columns:
        return pd.DataFrame()

    frame = returns_frame.copy()
    default_regime = "Sideways"
    regime_series = frame.get("regime_type", pd.Series(default_regime, index=frame.index)).fillna(default_regime)
    exposure_map = {
        "Bull": bull_exposure,
        "Bear": bear_exposure,
        "Sideways": sideways_exposure,
        "Positive Trend": bull_exposure,
        "Negative Trend": bear_exposure,
        "Neutral": sideways_exposure,
    }
    frame["Exposure"] = regime_series.map(lambda value: float(exposure_map.get(str(value), sideways_exposure)))
    frame["Transaction Cost"] = frame["Exposure"].diff().abs().fillna(0.0) * float(transaction_cost)
    frame["Strategy Return"] = frame["Market Return"] * frame["Exposure"] - frame["Transaction Cost"]
    return frame


def compute_cumulative_returns(returns: pd.Series) -> pd.Series:
    """Compute cumulative returns from periodic returns."""
    numeric_returns = pd.to_numeric(returns, errors="coerce").fillna(0.0)
    return (1.0 + numeric_returns).cumprod() - 1.0


def compute_drawdown(cumulative_returns: pd.Series) -> pd.Series:
    """Compute drawdown series from cumulative returns."""
    equity_curve = 1.0 + pd.to_numeric(cumulative_returns, errors="coerce").fillna(0.0)
    running_peak = equity_curve.cummax().replace(0, pd.NA)
    drawdown = equity_curve / running_peak - 1.0
    return drawdown.fillna(0.0)


def compute_sharpe_ratio(returns: pd.Series, periods_per_year: int = 252) -> float | None:
    """Compute a simple annualized Sharpe ratio."""
    numeric_returns = pd.to_numeric(returns, errors="coerce").dropna()
    if numeric_returns.empty or len(numeric_returns) < 2:
        return None
    volatility = float(numeric_returns.std(ddof=0))
    if volatility <= 0:
        return None
    mean_return = float(numeric_returns.mean())
    return (mean_return / volatility) * (periods_per_year ** 0.5)


def compute_sortino_ratio(returns: pd.Series, periods_per_year: int = 252) -> float | None:
    """Compute a simple annualized Sortino ratio."""
    numeric_returns = pd.to_numeric(returns, errors="coerce").dropna()
    if numeric_returns.empty or len(numeric_returns) < 2:
        return None
    downside_returns = numeric_returns[numeric_returns < 0]
    if downside_returns.empty:
        return None
    downside_volatility = float(downside_returns.std(ddof=0))
    if downside_volatility <= 0:
        return None
    mean_return = float(numeric_returns.mean())
    return (mean_return / downside_volatility) * (periods_per_year ** 0.5)


def compute_cagr(returns: pd.Series, periods_per_year: int = 252) -> float | None:
    """Compute CAGR-style annualized growth from periodic returns."""
    numeric_returns = pd.to_numeric(returns, errors="coerce").dropna()
    if numeric_returns.empty:
        return None
    total_periods = len(numeric_returns)
    total_growth = float((1.0 + numeric_returns).prod())
    if total_growth <= 0 or total_periods <= 0:
        return None
    years = total_periods / periods_per_year
    if years <= 0:
        return None
    return total_growth ** (1 / years) - 1.0


def compute_hit_rate(returns: pd.Series) -> float | None:
    """Compute the share of positive-return periods."""
    numeric_returns = pd.to_numeric(returns, errors="coerce").dropna()
    if numeric_returns.empty:
        return None
    return float((numeric_returns > 0).mean())


def summarize_strategy_by_regime(strategy_frame: pd.DataFrame) -> pd.DataFrame:
    """Summarize market and strategy behavior by semantic regime."""
    if strategy_frame.empty:
        return pd.DataFrame(
            columns=["Regime Type", "Periods", "Average Market Return", "Average Strategy Return", "Average Exposure"]
        )
    regime_series = strategy_frame.get("regime_type", pd.Series("Sideways", index=strategy_frame.index)).fillna("Sideways")
    summary = (
        strategy_frame.assign(regime_type=regime_series)
        .groupby("regime_type", dropna=False)
        .agg(
            **{
                "Periods": ("regime_type", "size"),
                "Average Market Return": ("Market Return", "mean"),
                "Average Strategy Return": ("Strategy Return", "mean"),
                "Average Exposure": ("Exposure", "mean"),
            }
        )
        .reset_index()
        .rename(columns={"regime_type": "Regime Type"})
    )
    for column in ["Average Market Return", "Average Strategy Return", "Average Exposure"]:
        summary[column] = pd.to_numeric(summary[column], errors="coerce").fillna(0.0).round(4)
    return summary.sort_values("Regime Type").reset_index(drop=True)


def build_strategy_comparison_figure(strategy_frame: pd.DataFrame) -> go.Figure:
    """Plot strategy cumulative return versus buy-and-hold."""
    if strategy_frame.empty:
        return style_figure(go.Figure())
    frame = strategy_frame.copy()
    frame["Strategy Cumulative"] = compute_cumulative_returns(frame["Strategy Return"])
    frame["Buy and Hold Cumulative"] = compute_cumulative_returns(frame["Market Return"])

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=frame["Time"],
            y=frame["Strategy Cumulative"],
            mode="lines",
            name="Regime Strategy",
            line={"color": "#22c55e", "width": 2.2},
        )
    )
    figure.add_trace(
        go.Scatter(
            x=frame["Time"],
            y=frame["Buy and Hold Cumulative"],
            mode="lines",
            name="Buy & Hold",
            line={"color": "#94a3b8", "width": 1.9, "dash": "dot"},
        )
    )
    figure.update_layout(
        title="Cumulative Performance Comparison",
        xaxis_title="Date",
        yaxis_title="Cumulative Return",
        height=480,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
    )
    return style_figure(figure)


def build_strategy_exposure_figure(strategy_frame: pd.DataFrame) -> go.Figure:
    """Plot regime-driven exposure over time."""
    if strategy_frame.empty:
        return style_figure(go.Figure())
    frame = strategy_frame.copy()
    regime_label = frame.get("regime_type", pd.Series("Sideways", index=frame.index)).fillna("Sideways")
    figure = px.area(
        frame.assign(Regime=regime_label),
        x="Time",
        y="Exposure",
        title="Strategy Exposure Signal",
        color="Regime",
        color_discrete_map={
            "Bull": "#22c55e",
            "Bear": "#ef4444",
            "Sideways": "#94a3b8",
            "Positive Trend": "#22c55e",
            "Negative Trend": "#ef4444",
            "Neutral": "#94a3b8",
        },
    )
    figure.update_layout(
        xaxis_title="Date",
        yaxis_title="Exposure",
        yaxis={"range": [0, 1]},
        height=330,
    )
    return style_figure(figure)


def build_drawdown_figure(strategy_frame: pd.DataFrame) -> go.Figure:
    """Plot strategy drawdown over time."""
    if strategy_frame.empty or "Strategy Return" not in strategy_frame.columns:
        return style_figure(go.Figure())
    frame = strategy_frame.copy()
    frame["Strategy Cumulative"] = compute_cumulative_returns(frame["Strategy Return"])
    frame["Drawdown"] = compute_drawdown(frame["Strategy Cumulative"])
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=frame["Time"],
            y=frame["Drawdown"],
            mode="lines",
            fill="tozeroy",
            name="Drawdown",
            line={"color": "#ef4444", "width": 1.8},
            fillcolor="rgba(239, 68, 68, 0.16)",
        )
    )
    figure.update_layout(
        title="Strategy Drawdown",
        xaxis_title="Date",
        yaxis_title="Drawdown",
        yaxis={"tickformat": ".0%"},
        height=330,
    )
    return style_figure(figure)


def build_regime_return_contribution_figure(strategy_frame: pd.DataFrame) -> go.Figure:
    """Plot cumulative strategy contribution by semantic regime bucket."""
    if strategy_frame.empty or "Strategy Return" not in strategy_frame.columns:
        return style_figure(go.Figure())
    regime_series = strategy_frame.get("regime_type", pd.Series("Sideways", index=strategy_frame.index)).fillna("Sideways")
    contribution = (
        strategy_frame.assign(regime_type=regime_series)
        .groupby("regime_type", dropna=False)["Strategy Return"]
        .sum()
        .reset_index()
        .rename(columns={"regime_type": "Regime Type", "Strategy Return": "Contribution"})
    )
    if contribution.empty:
        return style_figure(go.Figure())
    color_map = {
        "Bull": "#22c55e",
        "Bear": "#ef4444",
        "Sideways": "#94a3b8",
        "Positive Trend": "#22c55e",
        "Negative Trend": "#ef4444",
        "Neutral": "#94a3b8",
    }
    figure = px.bar(
        contribution,
        x="Regime Type",
        y="Contribution",
        color="Regime Type",
        color_discrete_map=color_map,
        title="Contribution by State",
    )
    figure.update_traces(
        texttemplate="%{y:.2%}",
        textposition="outside",
        marker_line_width=0,
        hovertemplate="State: %{x}<br>Contribution: %{y:.2%}<extra></extra>",
    )
    figure.update_layout(
        showlegend=False,
        xaxis_title="State",
        yaxis_title="Contribution",
        yaxis={"tickformat": ".0%"},
        height=330,
    )
    return style_figure(figure)
