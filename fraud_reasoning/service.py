"""Complete three-engine inference orchestrator. No generative model controls decisions."""
from __future__ import annotations
import functools
import importlib.util
import json
import math
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from .attribution import explain_forest
from .rules import RuleAdapter, SPEC
from .logic import facts_from_input, context_arbitration
from .fusion import fuse

ROOT=Path(__file__).resolve().parents[1]

def load_python(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class FraudIntelligence:
    def __init__(self):
        self.rf_predict=load_python(ROOT/'03_Random_Forest/inference/predict.py','existing_rf_inference')
        self.rf_predict.load_artifacts=functools.lru_cache(maxsize=1)(self.rf_predict.load_artifacts)
        self.rf_model,self.rf_imputer,self.rf_features,self.rf_calibrator,self.rf_conformal = self.rf_predict.load_artifacts()
        if_root=ROOT/'04_Isolation_Forest'
        if str(if_root) not in sys.path:sys.path.insert(0,str(if_root))
        self.if_predict=load_python(if_root/'inference/predict.py','existing_if_inference')
        from src.isolation_forest_utils import load_bundle
        self.if_bundle=load_bundle(if_root/'artifacts/isolation_forest_b6b.joblib')
        self.if_features=list(self.if_bundle['feature_columns'])
        self.rule_adapter=RuleAdapter(ROOT)
        self.version='0.5.0'
        self.model_versions={'random_forest':'original_20features','isolation_forest':'original_B6b_bootstrap',
                             'rule_engine':'original_eight_rules_plus_context_policy'}

    def model_status(self):
        return {'random_forest':{'status':'loaded','features':len(self.rf_features)},
                'isolation_forest':{'status':'loaded','features':len(self.if_features),
                                    'anomaly_percentile_is_fraud_probability':False},
                'rule_based_engine':{'status':'loaded','configured_thresholds':list(self.rule_adapter.thresholds),
                                     'fully_configured':all(k in self.rule_adapter.thresholds for k in ('high_value_threshold','dust_threshold','contract_threshold'))},
                'version':self.version}

    def predict(self, features:dict, *, wallet_id=None, input_format='raw-live', if_features=None):
        if input_format not in ('raw-live','preprocessed'):
            raise ValueError('input_format must be raw-live or preprocessed')
        if not isinstance(features,dict) or not features:
            raise ValueError('features must be a nonempty object')
        # Preprocessed IF values MUST be provided separately, otherwise silently passing
        # RF raw values into IF's trained log space would be a dangerous schema bug.
        if input_format=='preprocessed' and if_features is None:
            raise ValueError('preprocessed IF inputs require a separate if_features dictionary')
        def validate(row):
            normalized={}
            for key,val in row.items():
                if not isinstance(key,str):raise ValueError('Feature names must be strings')
                stripped=key.strip()
                if not stripped or stripped in normalized:raise ValueError(f'Duplicate or blank normalized feature key: {stripped}')
                if isinstance(val,bool):raise ValueError(f'Boolean value not allowed for {stripped}')
                if val is not None:
                    try:
                        n=float(val)
                        if not math.isfinite(n):raise ValueError('nonfinite')
                    except (TypeError, ValueError):
                        raise ValueError(f'Feature {stripped} must be finite numeric or null')
                normalized[stripped]=val
            return normalized
        features=validate(features)
        if_features=validate(if_features) if if_features is not None else features
        facts=facts_from_input(features)
        missing_rf=[f for f in self.rf_features if f not in features]
        if missing_rf:raise ValueError('Missing RF features: '+', '.join(missing_rf))
        frame=pd.DataFrame([{f:features[f] for f in self.rf_features}]);frame=frame.apply(pd.to_numeric,errors='raise')
        rf_row=self.rf_predict.predict_dataframe(frame).iloc[0]
        quality=sum(pd.notna(features.get(f)) for f in self.rf_features)/len(self.rf_features)
        attr=explain_forest(self.rf_model,self.rf_imputer,frame,self.rf_features)
        rf={'status':'OK','fraud_probability':float(rf_row['rf_mu_calibrated']),
            'raw_fraud_probability':attr['raw_fraud_probability'],
            'calibrated':True,'calibration_note':'original training calibration, no current distribution-shift guarantee',
            'conformal_decision':str(rf_row['rf_conformal_decision']),
            'tree_disagreement_variance':float(rf_row['rf_sigma_squared']),
            'input_quality':quality,'attribution':attr,'reasoning':attr['reasoning']}
        # Fill missing columns as NaN to permit guarded median imputation by the
        # *original* IF implementation, but report missingness and restrict decisions.
        if_frame=pd.DataFrame([{f:if_features.get(f) for f in self.if_features}])
        missing_if=[f for f in self.if_features if if_features.get(f) is None]
        try:
            if_score=self.if_predict.score_dataframe(if_frame,self.if_bundle,input_format=input_format).iloc[0]
            val=if_score.get('if_mu')
            if val is not None and pd.notna(val):
                outside=int(if_score['outside_training_minmax_count'])
                missing_ratio=float(if_score['missing_feature_ratio'])
                # Coverage proxy. Not a calibrated likelihood/density/novelty probability.
                applicability=max(0.0,1.0-missing_ratio-outside/len(self.if_features))
                if 'total_transactions' in facts and facts['total_transactions']>200:
                    # D2 has no >200 sample in provided audit. Flag unsupported
                    # transaction activity WITHOUT claiming IF used txn count.
                    applicability=min(applicability,0.2)
                    applicability_reason='Wallet has >200 transactions; D2 source data capped at 200. This is a cross-dataset support warning, not a fitted IF feature.'
                else:applicability_reason='Heuristic of missing and out-of-training-range IF features; not a validated OOD probability.'
                if_output={'status':'OK','raw_anomaly_score':float(if_score['anomaly_score']),
                           'normality_score':-float(if_score['anomaly_score']),
                           'anomaly_score':float(if_score['anomaly_score']),
                           'anomaly_percentile':float(if_score['anomaly_percentile']),
                           'bootstrap_anomaly_variance':float(if_score['if_sigma_squared']),
                           'fraud_probability':None,
                           'missing_features':missing_if,
                           'anomaly_priority_band':str(if_score['anomaly_priority_band']),
                           'applicability':{'score':round(applicability,6),'reason':applicability_reason,
                                            'outside_training_minmax_count':outside,'missing_feature_ratio':missing_ratio},
                           'reasoning':[{'type':'marginal_comparison','description':str(if_score['marginal_feature_explanation']),
                                         'warning':'Marginal feature-tail summary, NOT causal or IF feature attribution.'}],
                           'score_semantics':'D2_relative_anomaly_percentile_not_fraud_probability'}
            else:if_output={'status':'UNAVAILABLE','reason':'IF input unusable (all features missing)','fraud_probability':None,'applicability':{'score':0.0}}
        except (ValueError,TypeError,KeyError,ArithmeticError) as exc:
            if_output={'status':'UNAVAILABLE','reason':str(exc),'fraud_probability':None,'applicability':{'score':0.0},'missing_features':missing_if}
        rules=self.rule_adapter.run(features)
        reasoning=context_arbitration(facts,rf,if_output,rules)
        belief=fuse(rf,if_output,rules,reasoning)
        return {'wallet_id':wallet_id,'model_versions':self.model_versions,
                'random_forest':rf,'isolation_forest':if_output,'rule_based_engine':rules,
                'reasoning_engine':reasoning,'belief_fusion':{k:v for k,v in belief.items() if k not in ('decision','reasons')},
                'final_output':{'decision':belief['decision'],'explanation':'; '.join(belief['reasons']) if belief['reasons'] else 'Policy conditions passed',
                                'reasons':belief['reasons']},
                'notice':'Research prototype. No independently validated new fusion calibration, novelty, or live fraud-performance claim.'}
