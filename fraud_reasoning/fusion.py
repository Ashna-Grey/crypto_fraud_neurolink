"""PROPOSED transparent reliability-discounted opinion pooling, not a published fusion operator.

Each eligible fraud-evidence engine k with p_k in [0,1] and a policy credibility eta_k in [0,1]
produces a discounted binary opinion b_k=eta_k*p_k, d_k=eta_k*(1-p_k), u_k=1-eta_k.
Weighted pooling P = sum(eta_k * p_k) / sum(eta_k); this P is NOT calibrated.
IF is NOT an eligible fraud-probability engine; it only informs out-of-distribution review.
Conflicting, incomplete, or shared-feature evidence increases review uncertainty, not a majority-vote override.
"""
from __future__ import annotations
from .logic import POLICY

def clip(v):return min(1.0,max(0.0,float(v)))

def fuse(rf, if_out, rules, reasoning, *, policy=None):
    conf={**POLICY,**(policy or {})}
    if rf.get('status')!='OK':
        return {'fused_risk_score':None,'uncertainty':1.0,'calibrated':False,'decision':'MANUAL_REVIEW','reasons':['RF_UNAVAILABLE']}
    p=clip(rf['fraud_probability']); rf_quality=clip(rf.get('input_quality',0))
    # Fixed policy priors, not held-out Brier-skill weights or validated likelihoods.
    rf_eta=0.70*rf_quality
    if_app=if_out.get('applicability',{}).get('score') if if_out.get('status')=='OK' else None
    low_app= if_app is None or if_app < conf['minimum_applicability']
    slow_context=any(t['rule_id']=='SLOW_VOLUME' for t in reasoning['arbitration'])
    raw_attr=rf.get('attribution',{}).get('reasoning',[])
    positives=sum(max(0.0,float(t['raw_probability_contribution'])) for t in raw_attr)
    volume_pos=sum(max(0.0,float(t['raw_probability_contribution'])) for t in raw_attr
                   if 'transactions' in str(t['feature']).lower())
    volume_fraction=volume_pos / positives if positives>0 else 0.0
    contextual_discount = 1-0.5*volume_fraction if slow_context else 1.0
    rf_eta*=contextual_discount
    rb_support=rules.get('risk_score')
    coverage=clip(rules.get('coverage',0))
    deps=reasoning.get('dependency_adjustments',[])
    dependency_discount=0.85 if deps else 1.0  # policy heuristic, not estimated dependence
    rule_eta=0.35*coverage*dependency_discount if rb_support is not None else 0.0
    opinions=[{'engine':'random_forest','p':p,'eta':rf_eta}]
    if rb_support is not None:
        opinions.append({'engine':'rule_based_engine','p':clip(rb_support),'eta':rule_eta})
    # This is the explicit opinion discount step, inspired by subjective-opinion notation,
    # but our pooling operator is proposed and must not be attributed to Jøsang.
    for o in opinions:
        o['belief_fraud']=o['eta']*o['p']
        o['belief_legitimate']=o['eta']*(1-o['p'])
        o['uncommitted_uncertainty']=1-o['eta']
    total=sum(o['eta'] for o in opinions)
    support=sum(o['eta']*o['p'] for o in opinions)/total if total>0 else None
    gap=abs(p-clip(rb_support)) if rb_support is not None else 0.0
    pair_conflict=gap * rf_eta * rule_eta
    missing_penalty=0.20*(1-coverage)
    ood_penalty=0.20 if low_app else 0.0
    uncertainty=clip(1-total/len(opinions)+pair_conflict+missing_penalty+ood_penalty)
    reasons=[]
    if rb_support is None or coverage<1: reasons.append('RULE_EVIDENCE_INCOMPLETE')
    if low_app: reasons.append('IF_TRAINING_APPLICABILITY_LOW_OR_UNAVAILABLE')
    if gap>=conf['conflict_review_gap'] and rule_eta>0: reasons.append('ENGINE_DISAGREEMENT')
    if rf.get('conformal_decision') in ('AMBIGUOUS','ABSTAIN'):
        reasons.append('RF_CONFORMAL_UNCERTAIN')
    if uncertainty > conf['max_decision_uncertainty']: reasons.append('EXCESSIVE_UNCERTAINTY')
    if rf_quality<1: reasons.append('RF_IMPUTED_FEATURES')
    if support is None: reasons.append('NO_ELIGIBLE_FRAUD_EVIDENCE')
    decision='MANUAL_REVIEW'
    # Conservative policy: complete rules + adequate IF applicability + nonconflicting evidence
    # required before autonomous risk classification.
    if not reasons and support is not None:
        if support>=conf['fraud_decision_threshold']: decision='FRAUD'
        elif support<=conf['legitimate_decision_threshold']: decision='LEGITIMATE'
        else:
            reasons.append('FUSED_SCORE_IN_REVIEW_REGION')
    return {
        'method':'proposed_reliability_discounted_opinion_pooling_with_contextual_arbitration',
        'fused_risk_score':round(support,6) if support is not None else None,
        'uncertainty':round(uncertainty,6),'calibrated':False,
        'pairwise_conflict_proxy':round(pair_conflict,6),
        'score_semantics':'heuristic_priority_not_fraud_probability',
        'opinion_components':[{'engine':o['engine'],'belief_fraud':round(o['belief_fraud'],6),
                               'belief_legitimate':round(o['belief_legitimate'],6),
                               'uncommitted_uncertainty':round(o['uncommitted_uncertainty'],6),
                               'credibility':round(o['eta'],6)} for o in opinions],
        'adjustments':{'rf_contextual_discount':round(contextual_discount,6),
                       'rf_volume_attribution_fraction_of_positive_top_features':round(volume_fraction,6),
                       'rule_dependency_discount':dependency_discount,
                       'rule_coverage':coverage, 'if_applicability':if_app},
        'reliability_source':'provisional_explicit_policy_weights_not_Brier_validated',
        'decision':decision,'reasons':reasons,
    }
