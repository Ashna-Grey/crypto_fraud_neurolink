# Deploy on Render

## Deploy from a Git repository

1. Unzip the project and push the project root to a private Git repository. Do not upload untrusted joblib/pickle files. The repository contains the trusted uploaded model binaries.
2. On Render select **New > Blueprint** (or Web Service using Docker). Import the Git repository.
3. The included `render.yaml` defines a Docker web service and `/health` health check. The chosen `starter` plan may incur charges; select your desired supported plan in Render before deploying.
4. Render builds `Dockerfile`, installs `requirements.txt`, loads the saved RF/IF artifacts at application startup, and runs Uvicorn on `0.0.0.0:${PORT:-8000}`.
5. Verify `GET /health`, `GET /schema`, then `POST /predict` in Swagger `/docs` using a **complete** feature object.
6. Optionally configure the contract-value rule with genuine training-derived thresholds AND its two genuine input features. Do not invent values to force full coverage.

## Local Docker

```bash
docker compose up --build
curl http://localhost:8000/health
```

## Operational limits

- Large saved ensemble artifacts require sufficient memory, persistent disk inside the Docker image, and enough startup time for loading. `workers 1` avoids loading multiple copies. Render deployment was **not** tested against a real account.
- The Python environment in the analysis sandbox had scikit-learn **1.8.0**, whereas the original RF artifacts were serialized by scikit-learn **1.9.0**. The Docker image installs **1.9.0** to match the saved RF artifacts; the exact image build could not be verified here because Docker is unavailable. Validate full inference on Render before use.
- Service loads packaged trusted artifacts; never unpickle public uploads.
- Rate limiting, auth, database, retraining, observability, and a blockchain connector are **not included**. Protect the endpoint before public deployment.
- Default `raw-live` input must contain RF raw feature values and IF raw-live values. If your upstream pipeline generates a different feature space, fix it at the ingestion layer and validate equivalence rather than silently applying transformations.
- Model performance and calibrator guarantees from training do not transfer automatically to live Ethereum wallets or fused scores.

## Enable all threshold-dependent rules when data becomes available

Provide a genuinely training-only CSV containing `total_eth_received`, `total_eth_sent`, `avg_value_sent`, and `total_eth_sent_contracts`, then run:

```bash
python scripts/freeze_rule_thresholds.py --training-only-csv path/to/verified_training_only_features.csv
```

Restart/rebuild the service so the frozen thresholds load. The `contract_activity` rule also requires genuine `created_contracts` and `total_eth_sent_contracts` request values; this script only configures thresholds, not wallet evidence. Never run it on final evaluation records or live requests.
