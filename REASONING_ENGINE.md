# How disagreement is resolved (without an LLM)

RF explains its **raw**, uncalibrated prediction by exact additive tree-path contributions. IF reports unusualness relative to its training distribution, with marginal summaries clearly marked as **not feature attributions**. Rule modules return fired/not-fired/unavailable with their feature provenance and thresholds.

`logic.context_arbitration` converts all of these to structured evidence items and evaluates policy conditions:

- **High count + slow mean rate:** mark count-alone evidence weaker. Only discount the relevant fraction of *positive* RF path attributions in the reported top features, not the entire RF model indiscriminately. Never infer legitimacy.
- **High count + high mean rate:** record higher activity-rate warning, not a verified within-24-hour burst.
- **High count + absent time:** mark temporal evidence unavailable; no slow/fast assertion.
- **RF and triggered rule share transaction-count feature:** flag evidence dependence. The fusion engine applies a provisional 0.85 weight to rule support. This is not a proof of independence/dependence.
- **RF/rule disagree:** increase uncertainty and request review if the gap is large. Scores are on different calibration scales, therefore the gap is only a *diagnostic proxy*.
- **IF high anomaly/normality:** neither score is taken as a fraud vote; IF reference coverage is only used to restrict confidence.
- **Missing important evidence:** allow the available engine outputs to be visible in JSON, but prevent unsupported autonomous classification.

For `1,200 transactions over 300 observed days`, `average_transactions_per_day_over_observed_span = 4`, resulting in `SLOW_VOLUME` trace. For `1,200 transactions in one day`, the rate is `1,200`, resulting in `FAST_VOLUME`. **Neither rate is evidence of a literal short burst without transaction-level timestamps**.

You can inspect configurable policies via `GET /reasoning/rules`. Policy thresholds are provisional. They need to be frozen using separate development data and evaluated independently.
