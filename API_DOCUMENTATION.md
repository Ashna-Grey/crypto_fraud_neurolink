# HTTP API

- `GET /`: service metadata.
- `GET /health`: model load and health state.
- `GET /schema`: exact RF and IF feature names and rule dependencies.
- `GET /models/status`: artifact state and missing threshold configuration.
- `GET /reasoning/rules`: deterministic policy conditions.
- `GET /research/methodology`: explanation of approach and limitations.
- `POST /predict`: one wallet.
- `POST /predict/batch`: 1–100 wallets. Each row gets independent success/error status.

## POST /predict

```json
{
  "wallet_id":"wallet-x",
  "input_format":"raw-live",
  "features":{"Total ERC20 tnxs":5}
}
```

The truncated example above returns **HTTP 422** because the required RF features are missing. Fetch the exact full list through `/schema` or use a complete extracted wallet row.

The response contains `random_forest`, `isolation_forest`, `rule_based_engine`, `reasoning_engine`, `belief_fusion`, and `final_output`. It reports `MANUAL_REVIEW` when inference cannot be justified, rather than hallucinating a rule/IF score. `if_features` is mandatory only when `input_format` is `preprocessed`. The use of calibrated RF score **does not imply calibrated fused risk**.

Swagger/OpenAPI is automatically generated at `/docs`.
