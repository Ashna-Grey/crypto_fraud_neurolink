# Mathematical foundations and provenance

**Only the base models and general ideas of proper scoring, subjective opinions, and selective prediction are sourced to prior work. The arbitration and pooling equations below are OUR PROPOSED HEURISTICS, NOT published/validated claims.** See [RESEARCH_REFERENCES.md](RESEARCH_REFERENCES.md).

## 1. Original Random Forest probability and interpretation

Let \(f_{RF}(x)\) be the mean of individual decision-tree fraud probabilities, and \(g(f_{RF}(x))\) be the stored fitted sigmoid calibrator. The existing RF pipeline produces \(p_{RF}(x)=g(f_{RF}(x))\). Calibration used the original project; performance is not independently established in this deployment.

### Exact local tree-path decomposition (implemented alternative, not SHAP)

For tree \(t\), each node \(n\) has an empirical class-1 fraction \(q_{t,n}\). For the path selected by wallet \(x\), the contribution of feature \(j\) is

\[
\phi_{t,j}(x)=\sum_{(n\to n')\text{ on path split by }j}[q_{t,n'}-q_{t,n}],\qquad
f_{RF}(x)=\frac1T\sum_t q_{t,root}+\sum_j\frac1T\sum_t\phi_{t,j}(x).
\]

This **telescoping decomposition** is a direct algebraic identity for the raw ensemble probability. It is not SHAP, does not explain the calibrated probability, and does not confer causal interpretation. The implementation checks numerical reconstruction. Related but DISTINCT established explanation method: Lundberg and Lee, SHAP (2017).

## 2. Isolation Forest: source-backed model, original percentile transform

Liu, Ting, Zhou (2008) introduced isolation-based anomaly detection. The bundled B6b artifact implements its original project-specific bootstrap ensemble and its smoothed empirical anomaly percentile. Our API exposes:

\[
A(x)=-\frac1B\sum_{b=1}^B \mathrm{IF}_b.\mathrm{score\_samples}(x),\quad
N(x)=-A(x).
\]

The original project also computes the mean of member-specific empirical anomaly percentiles \(U(x)\). These are **anomaly severity, not fraud probability**. These exact aggregation formulas follow the provided project's existing code, not an equation attributed to Liu et al.

## 3. Contextual temporal evidence: proposed policy

When observed-span length \(\Delta t\) in minutes is strictly positive, define

\[
\bar{v}_{day}(x)=\frac{1440\,N_{tx}(x)}{\Delta t(x)}.
\]

This is an algebraic rate conversion over the **observed transaction span**. It is neither instantaneous velocity nor a burst detector. The provisional policies compare the observed rate to 5 and 100 transactions/day when total transactions exceed 100. These are **not established fraud thresholds**, and are user-configurable in `logic.POLICY`.

## 4. Confidence discount, proposed implementation

The established subjective-opinion representation (Jøsang, 2016) motivates (but does NOT define our operator) the representation of reliability-discounted binary evidence:

\[
 b_k=\eta_k p_k,\qquad d_k=\eta_k(1-p_k),\qquad u_k=1-\eta_k. 
\]

These algebraic definitions are used here as a **proposed simplified discount**, with \(b_k+d_k+u_k=1\). The engineered credibility values are

\[
\eta_{RF}=0.70\,q_{RF}\,c(x),\qquad
\eta_{rule}=0.35\,\gamma_{rule}\,\delta_{dependency}.
\]

- \(q_{RF}\) is the fraction of 20 RF features observed (not a probability).
- \(c(x)=1-0.5\,s_{vol}(x)\) when the slow-high-volume policy triggers, otherwise 1. \(s_{vol}\) is the fraction of **positive attributions among the top reported RF features** attributed to transaction-count features.
- \(\gamma_{rule}\) is the fraction of original rule modules that could be evaluated.
- \(\delta_{dependency}=0.85\) when overlapping positive RF and triggered rule feature provenance is detected, else 1.
- 0.70, 0.35, 0.5, 0.85 are **policy constants requiring empirical tuning on disjoint development data**, not measured Brier-skill reliabilities, likelihoods, nor known theory constants.

IF has no \(p_k\) and is **excluded** from the fraud-evidence opinions.

## 5. Pooling and uncertainty: newly proposed, unvalidated

For eligible RF and rule opinions, use the exploratory credibility-weighted rank support:

\[
S(x)=\frac{\sum_k\eta_k p_k(x)}{\sum_k\eta_k},\qquad
K(x)=|p_{RF}-s_{rule}|\eta_{RF}\eta_{rule}.
\]

This **is NOT the consensus, cumulative, or Dempster-Shafer fusion operator from prior literature**. The rule score \(s_{rule}\) is not calibrated to the RF probability scale, so their numeric difference is only a heuristic disagreement proxy. Do not interpret \(S(x)\) as a fraud posterior.

The engineering abstention proxy is

\[
U(x)=\operatorname{clip}_{[0,1]}\left(1-\frac{\sum_k\eta_k}{m}+K(x)
+0.20(1-\gamma_{rule})+0.20\,\mathbb{1}[a_{IF}(x)<0.40\;\mathrm{or}\;IF\ \mathrm{unavailable}]\right).
\]

\(m\) is the number of eligible fraud-vote engines. \(a_{IF}\) is a **noncalibrated training-range/missingness applicability proxy**, additionally capped to 0.2 for >200 transactions (unsupported in D2 audit). This is an explicit policy constraint, NOT a density estimate. \(U\) is not a measured epistemic variance.

## 6. Selective decision

The system outputs `MANUAL_REVIEW` whenever any rule is unavailable, IF has low/unavailable applicability, a large RF/rule score gap is detected, RF conformal decision is ambiguous, RF input values were imputed, or uncertainty exceeds the engineering threshold. Otherwise it assigns `FRAUD` if \(S\ge0.70\), `LEGITIMATE` if \(S\le0.30\), and `MANUAL_REVIEW` for intermediate scores.

Selective prediction/abstention is established literature (Geifman & El-Yaniv, 2017). **Our particular thresholds/decisions are not derived from their results**.

## 7. Brier reliability not currently used

The requested reliability equation \(r_k=\max(0,1-BS_k/[\pi(1-\pi)])\) requires valid held-out outcome-labeled data for each probability-producing engine. The rule risk score and IF percentile are NOT calibrated probabilities. Therefore it would be mathematically misleading to apply the Brier-skill formula to all three engines. The implementation uses clearly disclosed provisional credibility constants instead. Calibrated Brier-skill weighting is future work after appropriate labeling and separation.

### Limits

All equations in sections 3-6 are exploratory project design and **do not claim published mathematical novelty or statistical guarantees**. Formal proofs, calibrated cutoffs, external datasets, and controlled ablations are outstanding.
