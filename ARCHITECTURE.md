# Executable architecture

```mermaid
flowchart TD
    A[Raw wallet aggregate feature JSON] --> B[Input and alias validation]
    B --> C[RF original 20-feature pipeline + calibrated probability]
    B --> D[IF B6b raw-live transformation + 20-feature ensemble]
    B --> E[Eight original rule modules with per-rule availability]
    C --> F[Exact additive RF tree-path feature evidence]
    D --> G[Anomaly percentile + training-coverage proxy]
    E --> H[Rule triggers + dependencies + missing prerequisites]
    F --> I[Common structured evidence]
    G --> I
    H --> I
    I --> J[Deterministic temporal context and dependency arbitration]
    J --> K[Proposed discounted opinion pooling RF + rule]
    G --> L[IF applicability constraint]
    L --> K
    K --> M{Uncertainty, applicability, coverage, disagreement}
    M -->|sufficient| N[FRAUD or LEGITIMATE]
    M -->|insufficient| O[MANUAL_REVIEW]
    N --> P[Structured JSON]
    O --> P
```

The **IF score is not a fraud vote**. This is intentional: previous investigation showed that higher IF normality, rather than higher anomaly, was associated with D1 fraud labels under a different five-feature experiment. The shipped B6b model has its own model-specific score semantics.

## Modules

- `fraud_reasoning/service.py`: loads original serialized models and orchestrates inference.
- `fraud_reasoning/attribution.py`: exact raw RF tree-path decomposition, verified by additive reconstruction.
- `fraud_reasoning/rules.py`: loads the original 8 rule modules and records unavailability.
- `fraud_reasoning/logic.py`: input aliases, provenance, contextual argument traces, overlap detection.
- `fraud_reasoning/fusion.py`: **proposed**, not literature-certified, policy-weighted opinion pooling and abstention.
- `fraud_reasoning/api.py`: FastAPI service, batch output, monitoring and documentation endpoints.

A successful `/health` means both saved model artifacts loaded. `rule_engine.fully_configured` can still be false: this is reported under `/models/status` and `/schema` rather than concealed.
