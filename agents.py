import os, json

DEFAULT_GROQ_MODEL="openai/gpt-oss-120b"
MERCHANT_NAMES={0:"low-risk merchant",1:"medium-risk merchant",2:"high-risk merchant"}

def investigate_transaction(tx,result):
    """A controlled agent workflow: collect evidence, apply checks, recommend next step."""
    steps=[]
    if tx["amount"]>=50000: steps.append(f"Large payment amount detected: ₹{tx['amount']:,.2f}.")
    if tx["hour"]<=4: steps.append(f"Transaction occurred at an overnight hour ({tx['hour']}:00).")
    if tx["failed_attempts"]>=2: steps.append(f"{tx['failed_attempts']} recent failed attempts may indicate repeated access attempts.")
    if tx["international"]: steps.append("The payment is marked as international.")
    if not tx["card_present"]: steps.append("The physical card was not present; this may be an online payment.")
    if tx["distance_km"]>=500: steps.append(f"Reported distance from usual location is {tx['distance_km']} km.")
    if tx["merchant_risk"]==2: steps.append("Merchant risk was entered as high.")
    if tx["transactions_last_hour"]>=5: steps.append(f"High transaction velocity: {tx['transactions_last_hour']} other transactions in the last hour.")
    if tx["customer_tenure_months"]<3: steps.append("The account is relatively new.")
    if not steps: steps.append("No configured warning rule was triggered by the entered fields.")
    action="Escalate for analyst review" if result["decision"]=="High Risk" else "Request verification / manual review" if result["decision"]=="Review" else "Continue normal monitoring"
    return {"steps":steps,"action":action,"summary":f"{result['decision']}: risk score {result['risk_score']}/100. Suggested action: {action}."}

def local_report(result,investigation):
    evidence="\n".join(f"- {s}" for s in investigation["steps"])
    return f"**Assessment:** {result['decision']} with a demo risk score of {result['risk_score']}/100.\n\n**Evidence considered:**\n{evidence}\n\n**Recommended next step:** {investigation['action']}.\n\nThis is a simulated risk assessment, not a confirmed fraud finding. A trained analyst should verify it before taking action."

def generate_ai_report(tx,result,investigation):
    api_key=os.getenv("GROQ_API_KEY","").strip()
    model=os.getenv("GROQ_MODEL","").strip() or DEFAULT_GROQ_MODEL
    if api_key:
        try:
            from groq import Groq
            client=Groq(api_key=api_key)
            evidence={"transaction_fields":tx,"model_result":result,"investigation":investigation}
            request={"model":model,"temperature":.2,"max_completion_tokens":1000,"messages":[
                {"role":"system","content":"Write a concise educational banking analyst report using only supplied evidence. Do not claim fraud is proven or invent facts. Require human verification before consequential action. Use headings Assessment, Evidence, Recommended next step."},
                {"role":"user","content":json.dumps(evidence)}]}
            if model.startswith("openai/gpt-oss-"):
                request["reasoning_effort"]="low"
                request["include_reasoning"]=False
            response=client.chat.completions.create(**request)
            content=(response.choices[0].message.content or "").strip() if response.choices else ""
            if not content:
                return local_report(result,investigation)+"\n\nGroq returned an empty report; local report used."
            return content+"\n\nAI-generated support text; human verification is required."
        except Exception as exc:
            if getattr(exc,"status_code",None)==404:
                return local_report(result,investigation)+f"\n\nGroq model `{model}` is unavailable for this account; local report used. Update `GROQ_MODEL` in `.env`, restart BankShield, and analyze again."
            return local_report(result,investigation)+f"\n\nGroq was unavailable; local report used ({type(exc).__name__})."
    return local_report(result,investigation)
