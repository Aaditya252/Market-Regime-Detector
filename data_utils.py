from __future__ import annotations

from dataclasses import dataclass
from typing import BinaryIO

import pandas as pd


@dataclass(frozen=True)
class DatasetSummary:
    rows: int
    columns_count: int
    columns: list[str]
    missing_values: pd.Series


def load_csv(file: BinaryIO) -> pd.DataFrame:
    """Load an uploaded CSV file into a DataFrame."""
    dataframe = pd.read_csv(file)
    return prepare_uploaded_dataframe(dataframe)


def normalize_column_names(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names without changing their meaning."""
    normalized_dataframe = dataframe.copy()
    normalized_dataframe.columns = [str(column).strip() for column in normalized_dataframe.columns]
    return normalized_dataframe


def _should_parse_as_datetime(series: pd.Series, column_name: str) -> bool:
    """Determine whether a column should be parsed as datetime."""
    lowered_name = str(column_name).lower()
    if any(token in lowered_name for token in ("date", "time", "timestamp")):
        return True

    if not pd.api.types.is_object_dtype(series) and not pd.api.types.is_string_dtype(series):
        return False

    non_null_series = series.dropna().astype(str).head(100)
    if non_null_series.empty:
        return False

    parsed = pd.to_datetime(non_null_series, errors="coerce")
    success_ratio = parsed.notna().mean()
    return success_ratio >= 0.8


def parse_datetime_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Parse likely datetime columns in the uploaded dataset."""
    parsed_dataframe = dataframe.copy()
    for column in parsed_dataframe.columns:
        series = parsed_dataframe[column]
        if _should_parse_as_datetime(series, column):
            parsed_series = pd.to_datetime(series, errors="coerce")
            if parsed_series.notna().sum() >= 2:
                parsed_dataframe[column] = parsed_series
    return parsed_dataframe


def prepare_uploaded_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Prepare an uploaded dataframe for downstream processing."""
    prepared_dataframe = normalize_column_names(dataframe)
    prepared_dataframe = parse_datetime_columns(prepared_dataframe)
    return prepared_dataframe


def get_datetime_columns(dataframe: pd.DataFrame) -> list[str]:
    """Return datetime-like columns in the dataset."""
    return list(dataframe.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns)


def build_summary(dataframe: pd.DataFrame) -> DatasetSummary:
    """Create a compact summary of the dataset."""
    rows, columns_count = dataframe.shape
    return DatasetSummary(
        rows=rows,
        columns_count=columns_count,
        columns=list(dataframe.columns),
        missing_values=dataframe.isna().sum(),
    )


def build_missing_values_table(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Build a missing-values table for display."""
    summary = dataframe.isna().sum().rename("Missing Values").reset_index()
    return summary.rename(columns={"index": "Column"})


def get_columns_with_missing_values(dataframe: pd.DataFrame) -> list[str]:
    """Return columns that contain missing values."""
    missing_counts = dataframe.isna().sum()
    return list(missing_counts[missing_counts > 0].index)


def fill_missing_values(
    dataframe: pd.DataFrame,
    strategy: str,
    columns: list[str] | None = None,
) -> pd.DataFrame:
    """Fill missing values using the selected strategy."""
    cleaned_dataframe = dataframe.copy()
    target_columns = columns or get_columns_with_missing_values(cleaned_dataframe)

    for column in target_columns:
        if column not in cleaned_dataframe.columns or not cleaned_dataframe[column].isna().any():
            continue

        series = cleaned_dataframe[column]
        if strategy == "Mean":
            if not pd.api.types.is_numeric_dtype(series):
                continue
            fill_value = series.mean()
        elif strategy == "Median":
            if not pd.api.types.is_numeric_dtype(series):
                continue
            fill_value = series.median()
        elif strategy == "Mode":
            mode = series.mode(dropna=True)
            if mode.empty:
                continue
            fill_value = mode.iloc[0]
        else:
            continue

        cleaned_dataframe[column] = series.fillna(fill_value)


    return cleaned_dataframe


def get_iqr_outlier_summary(dataframe: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Return outlier counts for the selected numerical columns using IQR."""
    summary_rows: list[dict[str, float | int | str]] = []

    for column in columns:
        if column not in dataframe.columns:
            continue

        series = dataframe[column].dropna()
        if series.empty:
            summary_rows.append(
                {
                    "Column": column,
                    "Outlier Count": 0,
                    "Lower Bound": 0.0,
                    "Upper Bound": 0.0,
                }
            )
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outlier_mask = (series < lower_bound) | (series > upper_bound)

        summary_rows.append(
            {
                "Column": column,
                "Outlier Count": int(outlier_mask.sum()),
                "Lower Bound": float(lower_bound),
                "Upper Bound": float(upper_bound),
            }
        )

    if not summary_rows:
        return pd.DataFrame(columns=["Column", "Outlier Count", "Lower Bound", "Upper Bound"])

    return pd.DataFrame(summary_rows).sort_values("Outlier Count", ascending=False).reset_index(
        drop=True
    )


def remove_iqr_outliers(dataframe: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Remove rows containing IQR-based outliers in the selected columns."""
    if not columns:
        return dataframe.copy()

    cleaned_dataframe = dataframe.copy()
    keep_mask = pd.Series(True, index=cleaned_dataframe.index)

    for column in columns:
        if column not in cleaned_dataframe.columns:
            continue

        series = cleaned_dataframe[column]
        if not pd.api.types.is_numeric_dtype(series):
            continue

        non_null_series = series.dropna()
        if non_null_series.empty:
            continue

        q1 = non_null_series.quantile(0.25)
        q3 = non_null_series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        keep_mask &= series.isna() | ((series >= lower_bound) & (series <= upper_bound))

    return cleaned_dataframe.loc[keep_mask].reset_index(drop=True)


def add_financial_features(
    dataframe: pd.DataFrame,
    source_columns: list[str],
    feature_names: list[str],
    window_size: int,
) -> pd.DataFrame:
    """Add financial features for selected numerical columns."""
    featured_dataframe = dataframe.copy()
    rolling_windows = sorted({max(2, int(window_size)), 10, 20})

    for column in source_columns:
        if column not in featured_dataframe.columns:
            continue

        series = featured_dataframe[column]
        if not pd.api.types.is_numeric_dtype(series):
            continue

        if "Returns" in feature_names:
            featured_dataframe[f"{column}_returns"] = series.pct_change()

        if "Rolling Mean" in feature_names:
            for window in rolling_windows:
                featured_dataframe[f"{column}_rolling_mean_{window}"] = series.rolling(
                    window=window,
                    min_periods=1,
                ).mean()

        if "Rolling Volatility" in feature_names:
            for window in rolling_windows:
                featured_dataframe[f"{column}_rolling_volatility_{window}"] = series.rolling(
                    window=window,
                    min_periods=2,
                ).std()

        if "Momentum" in feature_names:
            featured_dataframe[f"{column}_momentum_5"] = series.diff(periods=5)

        if "Volume Change" in feature_names and "volume" in str(column).lower():
            featured_dataframe[f"{column}_volume_change"] = series.pct_change()

    return featured_dataframe
