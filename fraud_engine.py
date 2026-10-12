from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BASE_DIR=Path(__file__).parent
DATA_DIR=BASE_DIR/"data"
TRANSACTIONS_FILE=DATA_DIR/"transactions.csv"
FEATURES=["amount","hour","failed_attempts","international","card_present","distance_km","merchant_risk","transactions_last_hour","customer_tenure_months"]

def make_demo_data(n=5000,seed=42):
    """Create fictional examples for a classroom prototype, not real bank records."""
    rng=np.random.default_rng(seed)
    amount=np.clip(rng.lognormal(7.3,1.05,n),50,300000)
    hour=rng.integers(0,24,n); failed=np.clip(rng.poisson(.45,n),0,8)
    international=rng.binomial(1,.12,n); card_present=rng.binomial(1,.58,n)
    distance=np.clip(rng.exponential(90,n),0,4000).astype(int)
    merchant=rng.choice([0,1,2],n,p=[.55,.34,.11]); velocity=np.clip(rng.poisson(1.5,n),0,15)
    tenure=np.clip(rng.gamma(3.2,18,n),1,240).astype(int)
    signal=(amount>50000)*1.2+(hour<=4)*.55+(failed>=2)*1.1+international*.65+(card_present==0)*.35+(distance>500)*.8+(merchant==2)*.9+(velocity>=5)*1.0+(tenure<3)*.45+rng.normal(0,.65,n)
    labels=(signal>np.quantile(signal,.82)).astype(int)
    return pd.DataFrame({"amount":amount.round(2),"hour":hour,"failed_attempts":failed,"international":international,"card_present":card_present,"distance_km":distance,"merchant_risk":merchant,"transactions_last_hour":velocity,"customer_tenure_months":tenure,"fraud_label":labels})

def load_or_train_model():
    data=make_demo_data()
    model=Pipeline([("scale",StandardScaler()),("classifier",RandomForestClassifier(n_estimators=120,max_depth=10,min_samples_leaf=3,class_weight="balanced",random_state=42))])
    model.fit(data[FEATURES],data["fraud_label"])
    return model

def score_transaction(model,tx):
    row=pd.DataFrame([{f:tx[f] for f in FEATURES}]); probability=float(model.predict_proba(row)[0][1])
    points=0
    if tx["amount"]>=50000: points+=15
    if tx["hour"]<=4: points+=8
    if tx["failed_attempts"]>=2: points+=18
    if tx["international"]: points+=8
    if not tx["card_present"]: points+=5
    if tx["distance_km"]>=500: points+=12
    if tx["merchant_risk"]==2: points+=12
    if tx["transactions_last_hour"]>=5: points+=15
    if tx["customer_tenure_months"]<3: points+=5
    score=int(round(min(100,max(0,probability*65+points*.65))))
    decision="High Risk" if score>=70 else "Review" if score>=40 else "Normal"
    return {"transaction_id":f"TX-{datetime.now().strftime('%y%m%d%H%M%S%f')[-10:]}","risk_score":score,"model_probability":round(probability,4),"prediction":"Suspicious pattern" if probability>=.5 else "Typical pattern","decision":decision,"created_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

def load_transactions():
    DATA_DIR.mkdir(exist_ok=True)
    if not TRANSACTIONS_FILE.exists(): return pd.DataFrame()
    try: return pd.read_csv(TRANSACTIONS_FILE)
    except (pd.errors.EmptyDataError,OSError): return pd.DataFrame()

def save_transaction(record):
    DATA_DIR.mkdir(exist_ok=True)
    pd.DataFrame([record]).to_csv(TRANSACTIONS_FILE,mode="a",header=not TRANSACTIONS_FILE.exists(),index=False)
