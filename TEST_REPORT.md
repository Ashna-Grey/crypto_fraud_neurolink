# Local verification report

## Executed test command

```bash
PYTHONWARNINGS=ignore python -m pytest 04_Isolation_Forest/tests 05_Fusion_Service/tests tests/test_neurosymbolic.py -q
```

**Result: 29 passed (14.01 seconds)** on the supplied sandbox Python environment; this includes existing original IF/fusion regression tests, new reasoning, fusion, input-validation and FastAPI tests.

## End-to-end saved-model smoke test

The packaged D1 processed dataset's **first record** (without a wallet address or label) was submitted to the new `FraudIntelligence.predict` pipeline. Both original RF and original IF saved artifacts produced numeric inference, and original rule modules provided partial rule evidence. A full response is saved in `examples/sample_wallet_response.json`, with input in `examples/sample_wallet_request.json`.

Example results (actual local computation, not manually specified):

- RF calibrated fraud probability: **0.006267634061702635**.
- RF raw fraud probability: **0.03**; exact tree-path contributions reconstructed the original raw score to machine precision.
- IF raw anomaly score: **0.5462220970977704**; anomaly percentile: **94.37299712134**.
- IF lacked `current_eth_balance`, and source D1 transaction count exceeded D2's audited cap, so IF applicability was downgraded.
- Original rule engine returned **PARTIAL** with missing-feature/threshold blockers identified.
- Final decision: **MANUAL_REVIEW**, rather than fabricated confidence.

## Limits of this test

- Local environment: scikit-learn **1.8.0**. The RF artifact was serialized under **1.9.0** and raised version warnings. Only the Docker requirements, not the built image, use the artifact-matching version.
- Docker is **not installed**, and no Render account or public endpoint was used. Build/deploy is **unverified**.
- This is a software smoke/regression test, not a novel fraud-detection performance evaluation.
- Example predictions are specific to the original saved-model artifacts, their input values, and the local library environment.
