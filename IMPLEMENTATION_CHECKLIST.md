# Implementation and acceptance checklist

## Implemented and locally tested

- [x] Retain original RF model, imputer, calibrator, conformal artifact and inference implementation.
- [x] Retain original B6b bootstrap IF artifact and original raw-live IF transformation.
- [x] Load all eight original rule implementations independently.
- [x] Freeze volume/dust development thresholds from **original RF training partition only**.
- [x] Per-rule input availability reporting, with null/unavailable status instead of invented data.
- [x] Per-wallet RF raw-probability additive tree-path explanations, verified by reconstruction.
- [x] IF raw anomaly score, relative percentile, descriptive marginal explanation, and applicability warning.
- [x] Deterministic contextual temporal reasoning with unverified thresholds made explicit.
- [x] Detect shared-feature provenance between RF explanations and triggered rules.
- [x] Proposed discount/pooling, disagreement proxy, missingness handling, and conservative abstention.
- [x] FastAPI with prediction, batch, schema, status, health, policy, and methodology routes.
- [x] Render blueprint and Docker/Compose configuration files.
- [x] End-to-end JSON smoke test on an actual source dataset record.
- [x] Regression tests for inference, API, context, aliasing, dependency, and IF semantics.

## Implemented but not fully validated

- [ ] Build and run actual Docker image on the target host (Docker not present in analysis sandbox).
- [ ] Confirm runtime compatibility under **exact** scikit-learn 1.9.0 build (local test uses 1.8.0).
- [ ] Calibrate rule weights and fusion output on disjoint validation data.
- [ ] Validate distribution-applicability proxy and abstention threshold statistically.
- [ ] Evaluate model calibration, fraud PR-AUC, and selective risk on independent wallet dataset.
- [ ] Establish comparative novelty against relevant published reason-aware and neuro-symbolic ensemble methods.

## Missing data/configuration blockers

- [ ] Genuine contract-value and created-contract features with frozen `contract_threshold` for Rule 06.
- [ ] Genuine ERC20 sent-address diversity for Rule 07 (when not available from request).
- [ ] Genuine `current_eth_balance` for IF when source has only differently named balance.
- [ ] Timestamped per-transaction histories to verify actual bursts or dormancy.
- [ ] Independent and representative labeled wallet dataset for unbiased comparison.

## Post-prototype production work

- [ ] Add authentication, rate limiting, privacy safeguards, structured logging, and monitoring.
- [ ] Add blockchain RPC ingestion/feature extractor and test its transformations.
- [ ] Deploy Render service in owned account and run full production image smoke tests.
