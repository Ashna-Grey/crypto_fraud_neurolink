# Known limitations

1. **Not live-hosted.** Render configuration is supplied. Upload/deploy to your Render account is still required; Docker was unavailable in the build sandbox, so the Docker image itself is unverified.
2. **Version incompatibility in local testing.** RF serialized by scikit-learn 1.9.0, local analysis Python had 1.8.0; the Docker requirements pin 1.9.0 but the Docker image has not been built here. Smoke inference in 1.8.0 emitted version warnings.
3. **Input availability.** Original 25-feature D1 data does not have all 20 IF fields or all 16 original rule inputs. No missing values are fabricated. The IF artifact handles its own median imputation, with applicability penalties. Missing rule inputs leave those rules unavailable.
4. **Rule 06 remains blocked** for D1-like inputs because the source does not supply contract-specific amounts/created contract counts, and no supported contract-value threshold is available. Original Rule 07 may also be unavailable without ERC20 unique sent addresses. Supply genuine features and training-derived threshold to evaluate.
5. **Training distribution shift.** D2 was capped at 200 transactions; >200 wallets raise IF coverage warning. This cap is a cross-dataset audit observation, not an IF model feature; the saved B6b excludes transaction count. The IF applicability score is an engineering proxy, not a validated likelihood of in-distribution status.
6. **Different IF artifact.** The bundled IF B6b has 20 features, not the earlier 5-feature research model evaluated at 0.8540 ROC-AUC. These experiments should not be conflated.
7. **Not all rules are independent.** Overlap is based on feature provenance. `dependency_discount=0.85` is an explicit provisional coefficient, not an empirical dependency estimate.
8. **Unverified novel fusion advantage.** Proposed score and uncertainty are uncalibrated. No new ROC-AUC, selective-risk claim, or proven novelty is reported.
9. **Feature explanations.** RF decomposition explains raw ensemble probability, not calibrated score; IF tail summaries are descriptive and not per-feature contributions to anomaly score.
10. **No transaction history ingestion.** `wallet_lifetime_minutes` is observed span. Average rate is not instantaneous transaction speed, within-day burst detection, dormancy, or fraud proof.
11. **Security.** No rate limiting, API authentication, persistent monitoring, wallet RPC provider, background jobs, or account-specific secrets. Render endpoint needs these controls before real public use.
12. **Policy score semantics.** Rule weighted score, IF percentile, and RF probability do not share a calibrated probability scale. Difference-based conflict is a heuristic diagnostic.
