from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


PLOT_TEMPLATE = "plotly_dark"
SEQUENTIAL_SCALE = [[0.0, "#4b5563"], [0.45, "#7a8b84"], [0.75, "#18a66a"], [1.0, "#22c55e"]]
DIVERGING_SCALE = [[0.0, "#ef4444"], [0.5, "#0f131a"], [1.0, "#18a66a"]]


def style_heatmap_with_cell_borders(
    figure: go.Figure,
    gap: int = 1,
    border_color: str = "rgba(255, 255, 255, 0.24)",
) -> go.Figure:
    """Add visible separators between heatmap rows and columns."""
    figure.update_traces(xgap=gap, ygap=gap)
    figure.update_layout(plot_bgcolor=border_color)
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(showgrid=False)
    return figure


@dataclass(frozen=True)
class PCAProjectionResult:
    dataframe: pd.DataFrame
    explained_variance_ratio: tuple[float, float]
    total_rows: int
    plotted_rows: int
    clipped_feature_count: int
    color_mode: str
    error: str | None


def style_figure(figure: go.Figure) -> go.Figure:
    """Apply a consistent dark dashboard style."""
    figure.update_layout(
        template=PLOT_TEMPLATE,
        paper_bgcolor="#0f131a",
        plot_bgcolor="#0f131a",
        font={"family": "Inter, Segoe UI, Arial, sans-serif", "color": "#e5e7eb", "size": 13},
        margin={"l": 18, "r": 18, "t": 56, "b": 18},
        height=420,
        title={"font": {"size": 18, "color": "#f8fafc"}},
        legend={"font": {"size": 12}, "bgcolor": "rgba(0,0,0,0)", "orientation": "h"},
        hoverlabel={"bgcolor": "#080b10", "bordercolor": "#24303c", "font": {"color": "#e5e7eb"}},
    )
    figure.update_xaxes(
        showline=True,
        linecolor="rgba(255, 255, 255, 0.08)",
        gridcolor="rgba(255, 255, 255, 0.05)",
        zeroline=False,
        tickfont={"color": "#cbd5e1"},
        title_font={"color": "#e5e7eb"},
    )
    figure.update_yaxes(
        showline=True,
        linecolor="rgba(255, 255, 255, 0.08)",
        gridcolor="rgba(255, 255, 255, 0.05)",
        zeroline=False,
        tickfont={"color": "#cbd5e1"},
        title_font={"color": "#e5e7eb"},
    )
    return figure


def get_numerical_columns(dataframe: pd.DataFrame) -> list[str]:
    """Return numerical columns in the dataset."""
    return list(dataframe.select_dtypes(include="number").columns)


def get_categorical_columns(dataframe: pd.DataFrame) -> list[str]:
    """Return categorical columns in the dataset."""
    return list(dataframe.select_dtypes(include=["object", "category", "bool"]).columns)


def build_numerical_summary(dataframe: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Return descriptive statistics for selected numerical columns."""
    if not columns:
        return pd.DataFrame()
    return dataframe[columns].describe().transpose().reset_index().rename(columns={"index": "Column"})


def get_missing_values_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Return missing value counts and percentages for each column."""
    missing_counts = dataframe.isna().sum()
    row_count = len(dataframe)
    if row_count == 0:
        missing_percentages = pd.Series(0.0, index=dataframe.columns)
    else:
        missing_percentages = (missing_counts / row_count * 100).fillna(0)

    summary = pd.DataFrame(
        {
            "Column": dataframe.columns,
            "Missing Values": missing_counts.values,
            "Missing Percentage": missing_percentages.values,
        }
    )
    return summary.sort_values("Missing Values", ascending=False).reset_index(drop=True)


def build_distribution_figure(dataframe: pd.DataFrame, column: str) -> go.Figure:
    """Create a histogram for a numerical column."""
    figure = px.histogram(
        dataframe,
        x=column,
        nbins=40,
        title=f"Distribution of {column}",
        color_discrete_sequence=["#18a66a"],
    )
    figure.update_layout(xaxis_title=column, yaxis_title="Count", bargap=0.06)
    return style_figure(figure)


def build_correlation_figure(dataframe: pd.DataFrame, columns: list[str]) -> go.Figure:
    """Create a correlation heatmap for selected numerical columns."""
    correlation_matrix = dataframe[columns].corr(numeric_only=True)
    figure = px.imshow(
        correlation_matrix,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale=DIVERGING_SCALE,
        title="Correlation Matrix",
    )
    figure.update_layout(
        xaxis_title="Features",
        yaxis_title="Features",
        coloraxis_colorbar_title="Correlation",
        height=500,
    )
    figure = style_heatmap_with_cell_borders(figure, gap=2)
    return style_figure(figure)


def get_categorical_value_counts(
    dataframe: pd.DataFrame,
    column: str,
    top_n: int = 10,
) -> pd.DataFrame:
    """Return value counts for a categorical column."""
    total_count = len(dataframe[column])
    counts = (
        dataframe[column]
        .fillna("Missing")
        .astype(str)
        .value_counts()
        .head(top_n)
        .rename_axis("Category")
        .reset_index(name="Count")
    )
    counts["Percentage"] = (
        (counts["Count"] / total_count * 100).round(2) if total_count else 0.0
    )
    return counts


def build_categorical_bar_figure(
    dataframe: pd.DataFrame,
    column: str,
    top_n: int = 10,
) -> go.Figure:
    """Create a bar chart for top categories in a categorical column."""
    counts = get_categorical_value_counts(dataframe, column, top_n=top_n)
    figure = px.bar(
        counts,
        x="Category",
        y="Count",
        title=f"Top Categories in {column}",
        color="Count",
        color_continuous_scale=SEQUENTIAL_SCALE,
    )
    figure.update_layout(
        xaxis_title=column,
        yaxis_title="Frequency",
        coloraxis_showscale=False,
        height=420,
    )
    figure.update_traces(textposition="outside", texttemplate="%{y}")
    return style_figure(figure)


def build_missing_values_figure(summary: pd.DataFrame) -> go.Figure:
    """Create a bar chart for missing values by column."""
    figure = px.bar(
        summary,
        x="Column",
        y="Missing Values",
        color="Missing Percentage",
        color_continuous_scale=[[0.0, "#4b5563"], [0.5, "#18a66a"], [1.0, "#ef4444"]],
        title="Missing Values by Column",
    )
    figure.update_layout(xaxis_title="Column", yaxis_title="Missing Values")
    return style_figure(figure)


def prepare_pca_projection(
    dataframe: pd.DataFrame,
    columns: list[str],
    max_points: int = 1200,
) -> PCAProjectionResult:
    """Prepare a cleaner PCA projection by clipping extreme tails for visualization only."""
    if len(columns) < 2:
        return PCAProjectionResult(pd.DataFrame(), (0.0, 0.0), 0, 0, 0, "none", "Select at least two numerical features for PCA.")

    feature_frame = dataframe[columns].apply(pd.to_numeric, errors="coerce").dropna()
    if len(feature_frame) < 3:
        return PCAProjectionResult(
            pd.DataFrame(),
            (0.0, 0.0),
            len(feature_frame),
            0,
            0,
            "none",
            "PCA needs at least three complete observations across the selected features.",
        )

    clipped_frame = feature_frame.copy()
    clipped_feature_count = 0
    for column in clipped_frame.columns:
        lower_bound = clipped_frame[column].quantile(0.01)
        upper_bound = clipped_frame[column].quantile(0.99)
        clipped_series = clipped_frame[column].clip(lower=lower_bound, upper=upper_bound)
        if not clipped_series.equals(clipped_frame[column]):
            clipped_feature_count += 1
        clipped_frame[column] = clipped_series

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(clipped_frame)
    pca_model = PCA(n_components=2, random_state=42)
    components = pca_model.fit_transform(scaled_features)

    projection_frame = pd.DataFrame(
        {
            "PC1": components[:, 0],
            "PC2": components[:, 1],
            "Observation Order": range(1, len(clipped_frame) + 1),
        },
        index=clipped_frame.index,
    )
    color_mode = "order"
    if "market_regime" in dataframe.columns:
        regime_values = pd.to_numeric(dataframe.loc[projection_frame.index, "market_regime"], errors="coerce")
        if regime_values.notna().any():
            projection_frame["Regime Label"] = regime_values.astype("Int64").astype(str).map(lambda value: f"Regime {value}" if value != "<NA>" else "Unlabeled")
            projection_frame = projection_frame.loc[projection_frame["Regime Label"] != "Unlabeled"].copy()
            if not projection_frame.empty:
                color_mode = "regime"
    if len(projection_frame) > max_points:
        projection_frame = projection_frame.sample(n=max_points, random_state=42).sort_index()

    return PCAProjectionResult(
        dataframe=projection_frame,
        explained_variance_ratio=(
            float(pca_model.explained_variance_ratio_[0]),
            float(pca_model.explained_variance_ratio_[1]),
        ),
        total_rows=len(clipped_frame),
        plotted_rows=len(projection_frame),
        clipped_feature_count=clipped_feature_count,
        color_mode=color_mode,
        error=None,
    )


def build_pca_scatter_figure(dataframe: pd.DataFrame, columns: list[str]) -> go.Figure:
    """Create a cleaner PCA scatter plot for the selected numerical columns."""
    projection_result = prepare_pca_projection(dataframe, columns)
    if projection_result.error:
        return style_figure(go.Figure())

    plot_frame = projection_result.dataframe.copy()

    if projection_result.color_mode == "regime" and "Regime Label" in plot_frame.columns:
        figure = px.scatter(
            plot_frame,
            x="PC1",
            y="PC2",
            color="Regime Label",
            title="Feature Space Projection",
            color_discrete_sequence=["#22c55e", "#ef4444", "#18a66a", "#8fb8aa", "#94a3b8", "#64748b"],
            opacity=0.65,
        )
    else:
        figure = px.scatter(
            plot_frame,
            x="PC1",
            y="PC2",
            color="Observation Order",
            title="Feature Space Projection",
            color_continuous_scale=[[0.0, "#355c4b"], [0.55, "#18a66a"], [1.0, "#8fb8aa"]],
            opacity=0.58,
        )
    figure.update_traces(
        marker={"size": 5, "line": {"width": 0}},
        hovertemplate="PC1: %{x:.3f}<br>PC2: %{y:.3f}<extra></extra>",
    )
    figure.update_layout(
        xaxis_title=f"Principal Component 1 ({projection_result.explained_variance_ratio[0] * 100:.1f}% variance)",
        yaxis_title=f"Principal Component 2 ({projection_result.explained_variance_ratio[1] * 100:.1f}% variance)",
        height=520,
    )
    if projection_result.color_mode != "regime":
        figure.update_layout(coloraxis_colorbar_title="Order")
    return style_figure(figure)


def build_validation_figure(summary: pd.DataFrame) -> go.Figure:
    """Create a fold-by-fold validation chart for time-series clustering diagnostics."""
    if summary.empty:
        return style_figure(go.Figure())

    plot_frame = summary.copy()
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=plot_frame["Fold"],
            y=plot_frame["Silhouette Score"],
            mode="lines+markers",
            name="Silhouette Score",
            line={"color": "#18a66a", "width": 2},
            marker={"size": 7},
        )
    )
    if "Davies-Bouldin Score" in plot_frame.columns:
        figure.add_trace(
            go.Scatter(
                x=plot_frame["Fold"],
                y=plot_frame["Davies-Bouldin Score"],
                mode="lines+markers",
                name="Davies-Bouldin Score",
                line={"color": "#94a3b8", "width": 2, "dash": "dot"},
                marker={"size": 6},
                yaxis="y2",
            )
        )

    figure.update_layout(
        title="TimeSeriesSplit Validation",
        xaxis_title="Fold",
        yaxis_title="Silhouette Score",
        yaxis2={
            "title": "Davies-Bouldin Score",
            "overlaying": "y",
            "side": "right",
            "showgrid": False,
        },
        height=440,
    )
    return style_figure(figure)


def build_tuning_figure(summary: pd.DataFrame) -> go.Figure:
    """Create a hyperparameter tuning chart across candidate cluster counts."""
    if summary.empty:
        return style_figure(go.Figure())

    plot_frame = summary.copy()
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=plot_frame["Clusters"],
            y=plot_frame["Mean Silhouette Score"],
            mode="lines+markers",
            name="Mean Silhouette Score",
            line={"color": "#18a66a", "width": 2.4},
            marker={"size": 8},
        )
    )
    if "Mean Davies-Bouldin Score" in plot_frame.columns:
        figure.add_trace(
            go.Scatter(
                x=plot_frame["Clusters"],
                y=plot_frame["Mean Davies-Bouldin Score"],
                mode="lines+markers",
                name="Mean Davies-Bouldin Score",
                line={"color": "#94a3b8", "width": 2, "dash": "dot"},
                marker={"size": 7},
                yaxis="y2",
            )
        )

    figure.update_layout(
        title="Hyperparameter Tuning",
        xaxis_title="Number of Clusters",
        yaxis_title="Mean Silhouette Score",
        yaxis2={
            "title": "Mean Davies-Bouldin Score",
            "overlaying": "y",
            "side": "right",
            "showgrid": False,
        },
        height=440,
    )
    return style_figure(figure)
