# Crypto Fraud Intelligence: reason-aware three-engine backend

**Status: tested research prototype, not production-validated.** The backend executes the uploaded saved 20-feature calibrated Random Forest, the uploaded B6b 20-feature bootstrap Isolation Forest, and eight original rule modules (individually guarded for missing features/thresholds). It performs structured evidence extraction, dependency detection, contextual reasoning, conservative opinion pooling, and abstention.

## Run

```bash
python -m pip install -r requirements.txt
uvicorn fraud_reasoning.api:app --host 127.0.0.1 --port 8000
# or: docker compose up --build
```

Swagger: `http://localhost:8000/docs`. Render instructions: [README_DEPLOY.md](README_DEPLOY.md).

## Input contract

`POST /predict` body:

```json
{"wallet_id":"example","input_format":"raw-live","features":{"<exact RF feature>":1.0}}
```

Provide **all 20 RF features** from `GET /schema`, plus every available IF feature and/or rule feature. Additional features beyond RF schema are accepted. Values must be numeric or null. The default **raw-live** mode converts IF inputs with the original saved IF preprocessing, but **does not** apply IF's log transforms to RF inputs. If you have *already preprocessed* IF features, specify `input_format: "preprocessed"` **and** supply a separate `if_features` object. This prevents accidentally mixing the different model feature spaces.

The eight rule modules do not require all 16 values to produce *some* rule evidence, but any rule missing an input is explicitly marked `unavailable`. IF missing values are member-median-imputed and downgraded; IF's fraud probability is **always null**. When evidence is incomplete, the system returns `MANUAL_REVIEW` instead of confident automatic fraud classification.

## Research cautions

- The saved B6b IF is a 20-feature ensemble, **not** the earlier exploratory five-feature IF that gave 0.8540 ROC-AUC. Do not assign the five-feature experimental results to this artifact.
- IF anomaly percentile is not a fraud probability or a statement that a wallet is legitimate.
- RF tree-path contribution is an *exact decomposition of uncalibrated RF output*, **not SHAP** and not causal evidence.
- The fuse output is an uncalibrated priority score; thresholds, 0.70/0.35 credibility weights and 0.85 dependency proxy are **provisional policies**.
- The configured volume/dust thresholds are derived from RF *training indices only* in the supplied D1 dataset. The contract-value rule has no matching source features, and remains unavailable unless an independently sourced configuration is supplied.
- Daily rate is **average transactions over observed span**, not a burst detector. No raw blockchain RPC/timestamped transaction ingestion is included.
- Uncertainty is an engineering proxy, not calibrated epistemic uncertainty or a conformal guarantee.
- The novelty and benefit of this particular arbitration layer have **not** been demonstrated on an untouched external dataset.

Read [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md), [MATHEMATICAL_FOUNDATIONS.md](MATHEMATICAL_FOUNDATIONS.md), and [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md).
