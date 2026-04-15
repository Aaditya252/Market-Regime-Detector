from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_selection import VarianceThreshold
from sklearn.metrics import davies_bouldin_score, silhouette_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class ClusteringResult:
    dataframe: pd.DataFrame
    feature_frame: pd.DataFrame
    model: KMeans
    inertia: float
    silhouette_score: float | None
    training_row_count: int
    testing_row_count: int
    labeled_row_count: int
    davies_bouldin_score: float | None


@dataclass(frozen=True)
class ValidationResult:
    summary: pd.DataFrame
    mean_silhouette: float | None
    mean_davies_bouldin: float | None


@dataclass(frozen=True)
class TimeSplitResult:
    sorted_dataframe: pd.DataFrame
    train_dataframe: pd.DataFrame
    test_dataframe: pd.DataFrame
    time_column: str | None


@dataclass(frozen=True)
class RegimePredictionResult:
    current_regime: int | None
    predicted_next_regime: int | None
    confidence: float | None


def sort_dataframe_for_time(
    dataframe: pd.DataFrame,
    time_column: str | None,
) -> tuple[pd.DataFrame, str | None]:
    """Sort a dataframe by the selected time column when available."""
    if dataframe.empty:
        return dataframe.copy(), time_column

    if time_column and time_column in dataframe.columns:
        sorted_dataframe = dataframe.copy()
        sorted_dataframe[time_column] = pd.to_datetime(sorted_dataframe[time_column], errors="coerce")
        sorted_dataframe = sorted_dataframe.dropna(subset=[time_column]).sort_values(time_column)
        return sorted_dataframe.reset_index(drop=True), time_column

    if isinstance(dataframe.index, pd.DatetimeIndex):
        return dataframe.sort_index().reset_index(drop=True), None

    return dataframe.reset_index(drop=True), time_column


def time_based_split(
    dataframe: pd.DataFrame,
    time_column: str | None,
    test_ratio: float,
) -> TimeSplitResult:
    """Split a time-series dataset into earlier train rows and later test rows."""
    sorted_dataframe, resolved_time_column = sort_dataframe_for_time(dataframe, time_column)
    if sorted_dataframe.empty:
        return TimeSplitResult(sorted_dataframe, sorted_dataframe.copy(), sorted_dataframe.copy(), resolved_time_column)

    test_ratio = min(max(test_ratio, 0.1), 0.5)
    split_index = max(1, int(len(sorted_dataframe) * (1 - test_ratio)))
    split_index = min(split_index, len(sorted_dataframe) - 1) if len(sorted_dataframe) > 1 else 1

    train_dataframe = sorted_dataframe.iloc[:split_index].copy()
    test_dataframe = sorted_dataframe.iloc[split_index:].copy()
    return TimeSplitResult(
        sorted_dataframe=sorted_dataframe,
        train_dataframe=train_dataframe,
        test_dataframe=test_dataframe,
        time_column=resolved_time_column,
    )


def prepare_clustering_features(dataframe: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    """Prepare a numeric feature matrix for clustering."""
    if not feature_columns:
        return pd.DataFrame(index=dataframe.index)

    feature_frame = dataframe[feature_columns].copy()
    feature_frame = feature_frame.apply(pd.to_numeric, errors="coerce").dropna()
    if feature_frame.empty:
        return feature_frame

    # Remove near-constant features to avoid regime collapse.
    variances = feature_frame.var(axis=0, ddof=0)
    supported_columns = variances[variances > 1e-8].index.tolist()
    if len(supported_columns) >= 2:
        feature_frame = feature_frame[supported_columns]
    return feature_frame


def resolve_supported_feature_columns(
    dataframe: pd.DataFrame,
    feature_columns: list[str],
) -> list[str]:
    """Resolve a stable set of informative columns from the training sample only."""
    if not feature_columns:
        return []

    feature_frame = dataframe[feature_columns].copy()
    feature_frame = feature_frame.apply(pd.to_numeric, errors="coerce").dropna()
    if feature_frame.empty:
        return []

    variances = feature_frame.var(axis=0, ddof=0)
    supported_columns = variances[variances > 1e-8].index.tolist()
    return supported_columns if len(supported_columns) >= 2 else []


def prepare_clustering_features_with_columns(
    dataframe: pd.DataFrame,
    supported_columns: list[str],
) -> pd.DataFrame:
    """Prepare a numeric clustering frame using a pre-resolved column set."""
    if not supported_columns:
        return pd.DataFrame(index=dataframe.index)

    feature_frame = dataframe[supported_columns].copy()
    feature_frame = feature_frame.apply(pd.to_numeric, errors="coerce").dropna()
    return feature_frame


def select_features_by_correlation(
    dataframe: pd.DataFrame,
    candidate_columns: list[str],
    anchor_column: str,
    threshold: float,
) -> tuple[list[str], pd.DataFrame]:
    """Select features using absolute correlation against an anchor column."""
    valid_columns = [column for column in candidate_columns if column in dataframe.columns]
    if anchor_column not in valid_columns:
        return valid_columns, pd.DataFrame(columns=["Feature", "Abs Correlation"])

    correlation_series = (
        dataframe[valid_columns]
        .corr(numeric_only=True)[anchor_column]
        .dropna()
        .abs()
        .sort_values(ascending=False)
    )
    selected = [column for column, value in correlation_series.items() if value >= threshold]
    if anchor_column not in selected:
        selected.insert(0, anchor_column)

    table = correlation_series.rename("Abs Correlation").reset_index().rename(columns={"index": "Feature"})
    return selected, table


def select_features_by_variance(
    dataframe: pd.DataFrame,
    candidate_columns: list[str],
    threshold: float,
) -> tuple[list[str], pd.DataFrame]:
    """Select features using a variance threshold."""
    if not candidate_columns:
        return [], pd.DataFrame(columns=["Feature", "Variance"])

    numeric_frame = dataframe[candidate_columns].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    selector = VarianceThreshold(threshold=threshold)
    selector.fit(numeric_frame)

    supported_columns = list(numeric_frame.columns[selector.get_support()])
    variance_table = pd.DataFrame(
        {
            "Feature": numeric_frame.columns,
            "Variance": numeric_frame.var(axis=0).values,
        }
    ).sort_values("Variance", ascending=False).reset_index(drop=True)
    return supported_columns, variance_table


def run_kmeans_clustering(
    dataframe: pd.DataFrame,
    feature_columns: list[str],
    n_clusters: int,
    time_column: str | None = None,
    test_ratio: float = 0.2,
) -> ClusteringResult:
    """Fit KMeans on a time-ordered training split and append aligned regime labels."""
    split_result = time_based_split(dataframe, time_column, test_ratio)
    supported_columns = resolve_supported_feature_columns(split_result.train_dataframe, feature_columns)
    if len(supported_columns) < 2:
        raise ValueError("Training split does not contain enough varied features for clustering.")
    train_feature_frame = prepare_clustering_features_with_columns(split_result.train_dataframe, supported_columns)
    feature_frame = prepare_clustering_features_with_columns(split_result.sorted_dataframe, supported_columns)
    if train_feature_frame.empty:
        raise ValueError("Training split does not contain enough complete rows for clustering.")
    if feature_frame.empty:
        raise ValueError("Selected features do not contain enough complete rows for clustering.")
    if len(train_feature_frame) < n_clusters:
        raise ValueError(
            "The selected clustering features have fewer complete training rows than the chosen number of clusters."
        )

    scaler = StandardScaler()
    scaled_train_features = scaler.fit_transform(train_feature_frame)
    scaled_all_features = scaler.transform(feature_frame)

    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    model.fit(scaled_train_features)
    labels = model.predict(scaled_all_features)

    score = None
    if len(feature_frame) > n_clusters and len(pd.unique(labels)) > 1:
        score = float(silhouette_score(scaled_all_features, labels))

    db_score = None
    if len(feature_frame) > n_clusters and len(pd.unique(labels)) > 1:
        db_score = float(davies_bouldin_score(scaled_all_features, labels))

    clustered_dataframe = split_result.sorted_dataframe.copy()
    clustered_dataframe["market_regime"] = pd.Series(pd.array([pd.NA] * len(clustered_dataframe), dtype="Int64"))
    clustered_dataframe.loc[feature_frame.index, "market_regime"] = pd.array(labels, dtype="Int64")

    test_valid_indices = feature_frame.index.intersection(split_result.test_dataframe.index)

    return ClusteringResult(
        dataframe=clustered_dataframe,
        feature_frame=feature_frame,
        model=model,
        inertia=float(model.inertia_),
        silhouette_score=score,
        training_row_count=len(train_feature_frame),
        testing_row_count=len(test_valid_indices),
        labeled_row_count=len(feature_frame),
        davies_bouldin_score=db_score,
    )


def evaluate_time_series_validation(
    dataframe: pd.DataFrame,
    feature_columns: list[str],
    time_column: str | None,
    n_clusters: int,
    n_splits: int,
) -> ValidationResult:
    """Evaluate clustering stability with TimeSeriesSplit."""
    sorted_dataframe, _ = sort_dataframe_for_time(dataframe, time_column)
    base_training_columns = resolve_supported_feature_columns(sorted_dataframe, feature_columns)
    feature_frame = prepare_clustering_features_with_columns(sorted_dataframe, base_training_columns)
    if feature_frame.empty or len(feature_frame) <= n_clusters or len(base_training_columns) < 2:
        return ValidationResult(pd.DataFrame(), None, None)

    n_splits = min(max(2, n_splits), len(feature_frame) - 1)
    splitter = TimeSeriesSplit(n_splits=n_splits)
    rows: list[dict[str, float | int]] = []

    for fold_number, (train_idx, validation_idx) in enumerate(splitter.split(feature_frame), start=1):
        train_slice = feature_frame.iloc[train_idx]
        validation_slice = feature_frame.iloc[validation_idx]
        supported_columns = resolve_supported_feature_columns(train_slice, list(feature_frame.columns))
        train_frame = prepare_clustering_features_with_columns(train_slice, supported_columns)
        validation_frame = prepare_clustering_features_with_columns(validation_slice, supported_columns)
        if len(train_frame) < n_clusters or validation_frame.empty:
            continue

        scaler = StandardScaler()
        scaled_train = scaler.fit_transform(train_frame)
        scaled_validation = scaler.transform(validation_frame)

        model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        model.fit(scaled_train)
        validation_labels = model.predict(scaled_validation)

        silhouette = None
        davies_bouldin = None
        if len(validation_frame) > n_clusters and len(pd.unique(validation_labels)) > 1:
            silhouette = float(silhouette_score(scaled_validation, validation_labels))
            davies_bouldin = float(davies_bouldin_score(scaled_validation, validation_labels))

        rows.append(
            {
                "Fold": fold_number,
                "Train Rows": len(train_frame),
                "Validation Rows": len(validation_frame),
                "Silhouette Score": silhouette,
                "Davies-Bouldin Score": davies_bouldin,
            }
        )

    summary = pd.DataFrame(rows)
    if summary.empty:
        return ValidationResult(summary, None, None)

    return ValidationResult(
        summary=summary,
        mean_silhouette=float(summary["Silhouette Score"].dropna().mean())
        if summary["Silhouette Score"].notna().any()
        else None,
        mean_davies_bouldin=float(summary["Davies-Bouldin Score"].dropna().mean())
        if summary["Davies-Bouldin Score"].notna().any()
        else None,
    )


def tune_kmeans_clusters(
    dataframe: pd.DataFrame,
    feature_columns: list[str],
    time_column: str | None,
    cluster_values: list[int],
    n_splits: int,
) -> pd.DataFrame:
    """Evaluate silhouette behavior across candidate cluster counts."""
    tuning_rows: list[dict[str, float | int | None]] = []

    for cluster_count in cluster_values:
        validation_result = evaluate_time_series_validation(
            dataframe,
            feature_columns,
            time_column,
            cluster_count,
            n_splits,
        )
        tuning_rows.append(
            {
                "Clusters": cluster_count,
                "Mean Silhouette Score": validation_result.mean_silhouette,
                "Mean Davies-Bouldin Score": validation_result.mean_davies_bouldin,
                "Evaluated Folds": int(len(validation_result.summary)),
            }
        )

    return pd.DataFrame(tuning_rows)


def compute_regime_prediction(
    dataframe: pd.DataFrame,
    feature_columns: list[str],
    n_clusters: int,
    time_column: str | None,
    test_ratio: float,
) -> RegimePredictionResult:
    """Estimate the current regime and nearest alternate regime from the latest feature vector."""
    split_result = time_based_split(dataframe, time_column, test_ratio)
    supported_columns = resolve_supported_feature_columns(split_result.train_dataframe, feature_columns)
    feature_frame = prepare_clustering_features_with_columns(split_result.sorted_dataframe, supported_columns)
    train_feature_frame = prepare_clustering_features_with_columns(split_result.train_dataframe, supported_columns)
    if (
        feature_frame.empty
        or train_feature_frame.empty
        or len(supported_columns) < 2
        or len(train_feature_frame) < n_clusters
    ):
        return RegimePredictionResult(None, None, None)

    scaler = StandardScaler()
    scaled_train = scaler.fit_transform(train_feature_frame)
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    model.fit(scaled_train)

    scaled_all = scaler.transform(feature_frame)
    current_regime = int(model.predict(scaled_all[-1:].reshape(1, -1))[0])
    latest_vector = scaled_all[-1]
    centroid_distances = ((model.cluster_centers_ - latest_vector) ** 2).sum(axis=1) ** 0.5
    inverse_distances = 1.0 / (centroid_distances + 1e-9)
    normalized = inverse_distances / inverse_distances.sum() if inverse_distances.sum() > 0 else inverse_distances
    alternate_order = np.argsort(normalized)[::-1]
    alternate_regime = int(alternate_order[1]) if len(alternate_order) > 1 else current_regime
    confidence = float(normalized[current_regime]) if len(normalized) > current_regime else None
    return RegimePredictionResult(current_regime, alternate_regime, confidence)


def predict_regime_for_scenario(
    dataframe: pd.DataFrame,
    feature_columns: list[str],
    n_clusters: int,
    time_column: str | None,
    test_ratio: float,
    scenario_features: dict[str, float],
) -> RegimePredictionResult:
    """Estimate the closest regime and nearest alternate regime for a what-if scenario."""
    split_result = time_based_split(dataframe, time_column, test_ratio)
    supported_columns = resolve_supported_feature_columns(split_result.train_dataframe, feature_columns)
    train_feature_frame = prepare_clustering_features_with_columns(split_result.train_dataframe, supported_columns)
    if train_feature_frame.empty or len(supported_columns) < 2 or len(train_feature_frame) < n_clusters:
        return RegimePredictionResult(None, None, None)

    scenario_vector = []
    for column in supported_columns:
        if column not in scenario_features:
            return RegimePredictionResult(None, None, None)
        scenario_vector.append(float(scenario_features[column]))

    scaler = StandardScaler()
    scaled_train = scaler.fit_transform(train_feature_frame)
    scaled_scenario = scaler.transform(pd.DataFrame([scenario_vector], columns=supported_columns))

    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    model.fit(scaled_train)
    scenario_regime = int(model.predict(scaled_scenario)[0])
    centroid_distances = ((model.cluster_centers_ - scaled_scenario[0]) ** 2).sum(axis=1) ** 0.5
    inverse_distances = 1.0 / (centroid_distances + 1e-9)
    normalized = inverse_distances / inverse_distances.sum() if inverse_distances.sum() > 0 else inverse_distances
    confidence = float(normalized[scenario_regime]) if len(normalized) else None
    alternate_order = np.argsort(normalized)[::-1]
    alternate_regime = int(alternate_order[1]) if len(alternate_order) > 1 else scenario_regime
    return RegimePredictionResult(scenario_regime, alternate_regime, confidence)


def compute_regime_confidence_history(
    dataframe: pd.DataFrame,
    feature_columns: list[str],
    n_clusters: int,
    time_column: str | None,
    test_ratio: float,
) -> pd.DataFrame:
    """Compute regime-assignment confidence history for sparkline visualization."""
    split_result = time_based_split(dataframe, time_column, test_ratio)
    supported_columns = resolve_supported_feature_columns(split_result.train_dataframe, feature_columns)
    feature_frame = prepare_clustering_features_with_columns(split_result.sorted_dataframe, supported_columns)
    train_feature_frame = prepare_clustering_features_with_columns(split_result.train_dataframe, supported_columns)
    if (
        feature_frame.empty
        or train_feature_frame.empty
        or len(supported_columns) < 2
        or len(train_feature_frame) < n_clusters
    ):
        return pd.DataFrame(columns=["Time", "Confidence", "Regime"])

    scaler = StandardScaler()
    scaled_train = scaler.fit_transform(train_feature_frame)
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    model.fit(scaled_train)

    scaled_all = scaler.transform(feature_frame)
    labels = model.predict(scaled_all)
    deltas = model.cluster_centers_[:, np.newaxis, :] - scaled_all[np.newaxis, :, :]
    distances = np.sqrt(np.sum(deltas**2, axis=2))
    min_distance = distances.min(axis=0)
    max_distance = distances.max(axis=0)
    confidence = np.where(max_distance <= 0, 1.0, 1 - (min_distance / max_distance))
    confidence = np.clip(confidence, 0.0, 1.0)

    aligned = split_result.sorted_dataframe.loc[feature_frame.index].copy()
    if time_column and time_column in aligned.columns:
        aligned_time = pd.to_datetime(aligned[time_column], errors="coerce")
    elif isinstance(aligned.index, pd.DatetimeIndex):
        aligned_time = aligned.index.to_series(index=aligned.index)
    else:
        aligned_time = pd.Series(range(1, len(aligned) + 1), index=aligned.index)

    history = pd.DataFrame(
        {
            "Time": aligned_time.values,
            "Confidence": confidence,
            "Regime": labels,
        }
    ).dropna(subset=["Time"])
    return history.reset_index(drop=True)
