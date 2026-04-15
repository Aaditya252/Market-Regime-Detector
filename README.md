# Market Regime Detector

Market Regime Detector is a financial analytics dashboard that combines an academic machine learning pipeline with a professional quantitative workspace for unsupervised market regime detection.

The project is built around time-series clustering rather than classification or price forecasting. It supports data preparation, exploratory analysis, feature engineering, clustering, validation, regime monitoring, and strategy diagnostics in one Streamlit application.

## What The App Includes

- Dataset ingestion with reusable session-state data flow
- Exploratory data analysis with numerical, categorical, correlation, and PCA views
- Data cleaning with missing-value handling and IQR-based outlier filtering
- Financial feature engineering with returns, rolling mean, rolling volatility, and momentum
- Feature selection using correlation filtering and variance thresholding
- Time-based splitting and TimeSeriesSplit validation
- KMeans-based market regime detection
- Evaluation with silhouette score, inertia, and Davies-Bouldin score
- Regime monitoring with transition analysis, state timeline, and Markov-style forecast
- Quantitative tools for correlation, volatility, returns, and strategy review

## Project Structure

```text
app.py
data_utils.py
eda_utils.py
model_utils.py
quant_utils.py
ui_utils.py
requirements.txt
```

## Run Locally

From the project folder:

```powershell
pip install -r requirements.txt
streamlit run app.py
```

If `streamlit` is not recognized:

```powershell
python -m streamlit run app.py
```

## Deployment

This repository is ready for deployment on Streamlit Community Cloud.

### Streamlit Community Cloud Steps

1. Push the repository to GitHub.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click `New app`.
4. Select this repository: `Prerna1313/Market-Regime-Detector`
5. Set the main file path to:

```text
app.py
```

6. Deploy the app.

## Recommended GitHub Repository Description

Use this in the repository description field:

```text
Financial analytics dashboard for unsupervised market regime detection using clustering, quantitative diagnostics, and strategy monitoring.
```

## Recommended GitHub Topics

```text
streamlit
finance
quantitative-finance
machine-learning
clustering
market-regime
time-series
plotly
```

## Notes

- The project uses unsupervised learning, so regime semantics such as Bull, Bear, or Sideways are interpretation layers derived from cluster behavior.
- Classification metrics such as accuracy and F1 are not the primary evaluation metrics for this workflow.
- Time-based evaluation is used instead of random splitting to preserve chronological structure.
