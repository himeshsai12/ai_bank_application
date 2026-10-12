# BankShield AI — Banking Fraud Detection and Investigation

Educational major project built with Python, Streamlit, scikit-learn, a controlled investigation workflow, and optional Groq-powered reports.

## Features
- Interactive banking dashboard and transaction explorer
- Random Forest model estimates suspicious-pattern likelihood
- Transparent rule-based risk indicators and score
- Agent workflow gathers warning signs and recommends a next step
- Optional Groq LLM analyst report; local template works without a key
- CSV transaction history and export

> All model training examples are synthetic. This is not production-grade fraud detection and must not drive real banking decisions.

## Files
- `app.py`: dashboard pages, transaction form, charts, report, history/export.
- `fraud_engine.py`: synthetic training data, Random Forest, risk scoring, CSV storage.
- `agents.py`: investigation checks, recommendation, optional Groq report generation.
- `requirements.txt`: Python package dependencies.
- `run_bankshield.bat`: Windows launcher using the project's Python environment.
- `.env.example`: optional Groq configuration template.
- `.gitignore`: helps keep secrets and generated files out of Git.
- `data/`: local transaction history is created here after first analysis.

## Setup in Windows / VS Code

For the current workspace, dependencies are installed in the sibling `us` environment. Double-click `run_bankshield.bat`, or run this command from this project folder:

```powershell
.\run_bankshield.bat
```

The launcher uses `..\us\Scripts\python.exe` first, then `.venv\Scripts\python.exe`. It runs Streamlit through that interpreter so the app uses the installed project packages.

For a new setup:

1. Install Python 3.10 or 3.11 and open this folder in VS Code.
2. In the terminal run:
   ```bash
   python -m venv .venv
   ```
3. Activate the environment in Command Prompt:
   ```bat
   .venv\Scripts\activate
   ```
   In PowerShell:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
4. Install packages:
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
5. Optional Groq setup: copy `.env.example` to `.env`, then set your own `GROQ_API_KEY` and `GROQ_MODEL=openai/gpt-oss-120b` (or another model available to your Groq account). Restart BankShield after changing `.env`, then analyze again to generate a new report. Never commit or share the real key. The app runs without it.
6. Start the app:
   ```bash
   python -m streamlit run app.py
   ```

## Demo scenarios
Try a low-risk-looking example: ₹800, 14:00, zero failed attempts, domestic, card present, 2 km distance, low merchant risk, one other transaction, account age 48 months.

Try a higher-risk-looking example: ₹95,000, 02:00, four failed attempts, international, card not present, 1,200 km distance, high merchant risk, seven other transactions, account age two months. These are examples only; output is not guaranteed.

## Interview explanation
“I built BankShield AI, a simulated banking fraud detection dashboard. A Random Forest model estimates risk from transaction amount, time, failed attempts, merchant risk, distance and transaction velocity. A controlled agent workflow gathers warning signs and recommends monitoring, manual verification or analyst escalation. An optional Groq LLM turns the supplied evidence into a readable report, while Streamlit displays results and CSV history. I used synthetic data, so I describe it as an educational prototype rather than a production banking model.”

## Important concepts
- Model probability and combined risk score are different values.
- The rule score makes warning signals easier to explain.
- The “agent” here is a bounded workflow, not an unrestricted autonomous system.
- The LLM summarizes supplied evidence; it should not invent missing facts.
- No payment is automatically blocked; a human review is recommended for consequential decisions.
- Production needs verified labels, time-based evaluation, precision/recall/F1 and PR-AUC, false-positive monitoring, privacy controls, secure storage, audit logs, and governance.

## Future enhancements
Add a vetted anonymized dataset, confusion matrix and evaluation metrics, SHAP explanations, analyst login/roles, MySQL or PostgreSQL, audit logs, unit tests, and a review queue. Only use authorized sandbox payment APIs.
