import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from fraud_engine import load_or_train_model, score_transaction, load_transactions, save_transaction
from agents import investigate_transaction, generate_ai_report

load_dotenv()
st.set_page_config(page_title="BankShield AI", page_icon="🛡️", layout="wide")
st.markdown("""
<style>
.stApp{background:linear-gradient(135deg,#07111f,#0b1728 60%,#0d2230);color:#eef6ff}
[data-testid="stSidebar"]{background:#0b1625;border-right:1px solid #20364c}
.hero{padding:1.5rem;border:1px solid #25475b;border-radius:20px;background:linear-gradient(120deg,#14364b,#0d2034);margin-bottom:1rem}
.hero h1{margin:0;color:#f4fbff;font-size:2.3rem}.hero p{color:#a8c2d6;margin:.4rem 0 0}
div[data-testid="stMetric"]{background:#102237;padding:14px;border:1px solid #254057;border-radius:14px}
.stButton button[kind="primary"]{background:#13b8a6;border:0;color:#05131e;font-weight:700}
</style>""", unsafe_allow_html=True)
MODEL = load_or_train_model()
with st.sidebar:
    st.markdown("# 🛡️ BankShield AI")
    st.caption("Fraud intelligence workspace")
    page = st.radio("NAVIGATION", ["Overview", "Analyze Transaction", "Transaction Explorer", "How It Works"])
    st.divider(); st.success("ML model ready"); st.info("Simulated demo data only")

if page == "Overview":
    df=load_transactions()
    st.markdown('<div class="hero"><h1>BankShield <span style="color:#23d8c1">AI</span></h1><p>Transaction monitoring • ML risk scoring • Agent-assisted investigation</p></div>',unsafe_allow_html=True)
    total=len(df); review=int((df.decision=="Review").sum()) if total and "decision" in df else 0
    high=int((df.decision=="High Risk").sum()) if total and "decision" in df else 0
    avg=float(df.risk_score.mean()) if total and "risk_score" in df else 0
    a,b,c,d=st.columns(4); a.metric("Transactions analyzed",f"{total:,}"); b.metric("Needs review",f"{review:,}"); c.metric("High-risk alerts",f"{high:,}"); d.metric("Average risk score",f"{avg:.1f}/100")
    left,right=st.columns([1.3,1])
    with left:
        st.subheader("Risk monitoring")
        if total and "decision" in df:
            counts=df.decision.value_counts().rename_axis("Decision").reset_index(name="Transactions")
            fig=px.bar(counts,x="Decision",y="Transactions",color="Decision",color_discrete_map={"Normal":"#19b99b","Review":"#f2b84b","High Risk":"#ef5267"})
            fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig,use_container_width=True)
        else: st.info("Analyze a transaction to populate the dashboard.")
    with right:
        st.subheader("Recent activity")
        if total: st.dataframe(df.tail(8).iloc[::-1],use_container_width=True,hide_index=True)
        else: st.write("Investigation history will appear here.")
    st.caption("Risk labels are decision-support signals, not proof of fraud.")

elif page == "Analyze Transaction":
    st.markdown('<div class="hero"><h1>Transaction Investigation</h1><p>Enter a simulated payment and run the analysis workflow.</p></div>',unsafe_allow_html=True)
    with st.form("transaction_form"):
        st.subheader("Payment details"); a,b,c=st.columns(3)
        with a:
            amount=st.number_input("Transaction amount (₹)",min_value=1.0,max_value=1000000.0,value=18500.0,step=500.0)
            hour=st.slider("Transaction hour",0,23,22); failed=st.slider("Recent failed attempts",0,10,2)
        with b:
            international=st.selectbox("International transaction?",["No","Yes"])
            card_present=st.selectbox("Physical card present?",["No","Yes"])
            distance=st.slider("Distance from usual location (km)",0,5000,650,step=25)
        with c:
            merchant=st.select_slider("Merchant risk level",options=["Low","Medium","High"],value="Medium")
            velocity=st.slider("Other transactions in last hour",0,20,4)
            tenure=st.slider("Account age (months)",1,240,18)
        submitted=st.form_submit_button("Analyze transaction",type="primary",use_container_width=True)
    if submitted:
        tx={"amount":float(amount),"hour":int(hour),"failed_attempts":int(failed),"international":int(international=="Yes"),"card_present":int(card_present=="Yes"),"distance_km":int(distance),"merchant_risk":{"Low":0,"Medium":1,"High":2}[merchant],"transactions_last_hour":int(velocity),"customer_tenure_months":int(tenure)}
        result=score_transaction(MODEL,tx); investigation=investigate_transaction(tx,result); report=generate_ai_report(tx,result,investigation)
        save_transaction({**tx,**result,"investigation":investigation["summary"],"ai_report":report})
        st.session_state["last_result"]={"result":result,"investigation":investigation,"report":report}
    if "last_result" in st.session_state:
        item=st.session_state["last_result"]; result=item["result"]; investigation=item["investigation"]
        st.divider(); st.subheader("Investigation result")
        color={"High Risk":"#ef5267","Review":"#f2b84b","Normal":"#19b99b"}[result["decision"]]
        st.markdown(f'<div style="padding:1rem;border-radius:12px;border:1px solid {color};background:#102237"><h2 style="margin:0;color:{color}">{result["decision"]}</h2><p>Risk score: <b>{result["risk_score"]}/100</b> · Model estimate: {result["prediction"]}</p></div>',unsafe_allow_html=True)
        x,y,z=st.columns(3); x.metric("Risk score",f'{result["risk_score"]}/100'); y.metric("Model estimate",result["prediction"]); z.metric("Suggested next step",investigation["action"])
        st.progress(result["risk_score"]/100)
        st.subheader("Agent investigation")
        for step in investigation["steps"]: st.markdown(f"- {step}")
        st.subheader("AI analyst report"); st.markdown(item["report"])
        st.caption("Educational output only. A human analyst must verify the evidence before taking action.")

elif page == "Transaction Explorer":
    st.markdown('<div class="hero"><h1>Transaction Explorer</h1><p>Search past demo investigations and export records.</p></div>',unsafe_allow_html=True)
    df=load_transactions()
    if df.empty: st.info("No records yet. Analyze a transaction first.")
    else:
        choices=sorted(df.decision.dropna().unique().tolist()); selected=st.multiselect("Filter by decision",choices,default=choices)
        min_amount=st.number_input("Minimum amount (₹)",min_value=0,value=0,step=1000)
        view=df[df.decision.isin(selected)]; view=view[view.amount>=min_amount]
        st.dataframe(view.iloc[::-1],use_container_width=True,hide_index=True)
        st.download_button("Download records as CSV",view.to_csv(index=False),"bankshield_transactions.csv","text/csv")
        st.caption("Contains simulated records only. Do not enter real customer or cardholder data.")
else:
    st.markdown('<div class="hero"><h1>How BankShield AI Works</h1><p>Project architecture, in simple terms.</p></div>',unsafe_allow_html=True)
    st.markdown("""
1. **Streamlit input:** analyst enters simulated payment details.
2. **Feature preparation:** Python packages the fields into a model-ready row.
3. **Machine learning:** Random Forest estimates whether the pattern resembles the synthetic suspicious examples.
4. **Investigation workflow:** rule checks gather warning signs and select a recommended next step.
5. **Generative AI:** optional Groq LLM converts supplied evidence into a readable report; a local template works without a key.
6. **Dashboard and history:** Streamlit displays the result and saves the investigation to CSV.

**Machine learning predicts; Agentic AI coordinates the checks; Generative AI explains.** This project is a controlled educational workflow, not a fully autonomous banking agent.

**Limitations:** training data is synthetic, so the scores are not evidence of real-world accuracy. Production use would require verified data, time-based validation, precision/recall evaluation, privacy controls, audit logs, model governance, and human approval.
""")
