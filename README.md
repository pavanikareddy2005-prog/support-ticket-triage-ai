# 🎫 AI-Powered Support Ticket Triage System

An AI agent that automatically classifies incoming customer support tickets by category, urgency, and sentiment — then drafts a suggested first response. Built to demonstrate a real-world GenAI + data engineering workflow.

## The Problem

Support teams get flooded with tickets and spend significant time manually reading, categorizing, and prioritizing them before an agent can even start helping the customer. Urgent issues can get buried under routine questions.

## The Solution

This app ingests a batch of support tickets, uses an LLM agent to:
1. **Classify** each ticket (billing, technical, account, shipping, general inquiry)
2. **Score urgency** from 1 (low) to 5 (critical)
3. **Detect sentiment** (positive / neutral / negative)
4. **Summarize** the issue in one sentence
5. **Draft a suggested first response** an agent can review and send

Results are displayed in an interactive dashboard with urgency color-coding, summary metrics, and a downloadable CSV export.

## Demo

Run locally with `streamlit run app.py` — the app ships with a **Demo Mode** that works immediately with zero configuration (see below), plus a built-in sample dataset of 20 realistic support tickets.

## Architecture

```
CSV Upload / Sample Data
        │
        ▼
  data_cleaning.py  →  removes empty/duplicate tickets, normalizes text
        │
        ▼
  agent_classify.py →  LLM call #1: classify (category, urgency, sentiment, summary)
                        LLM call #2: draft suggested response
        │
        ▼
    app.py (Streamlit) → interactive dashboard, metrics, CSV export
```

## Tech Stack

- **Python 3.10+**
- **Streamlit** — web app / dashboard
- **Anthropic Claude API** — classification & response drafting
- **Pandas** — data cleaning and aggregation
- **python-dotenv** — secrets management

## Setup & Run

### 1. Clone and install dependencies
```bash
git clone https://github.com/YOUR_USERNAME/support-ticket-triage-ai.git
cd support-ticket-triage-ai
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. (Optional) Add your API key for real AI results
```bash
cp .env.example .env
# then edit .env and paste your key from https://console.anthropic.com/settings/keys
```
**Note:** If you skip this step, the app automatically runs in **Demo Mode** using a rule-based fallback classifier, so you can test the full app immediately without any API key or cost.

### 3. Run the app
```bash
streamlit run app.py
```
Open the URL Streamlit prints (usually `http://localhost:8501`).

## Deploying (free)

1. Push this repo to GitHub (see below)
2. Go to [share.streamlit.io](https://share.streamlit.io) → "New app" → connect your GitHub repo → select `app.py`
3. In **Advanced settings → Secrets**, add:
   ```
   ANTHROPIC_API_KEY = "your_key_here"
   ```
4. Deploy — you'll get a public URL you can share or add to your portfolio.

## Design Decisions

- **Demo Mode fallback**: the AI functions automatically detect if no API key is present and fall back to a transparent, rule-based classifier — so the project is fully runnable and demoable without requiring reviewers to configure API keys.
- **Batch limit slider**: processing is capped and adjustable to control API cost/time during testing.
- **Graceful JSON parsing**: if the LLM ever returns malformed JSON, the app falls back to the rule-based classifier instead of crashing.

## Future Improvements

- [ ] Add a feedback loop where agents can correct AI classifications to improve prompts over time
- [ ] Support multi-language tickets
- [ ] Add automatic routing to specific team queues based on category
- [ ] Deploy the backend as a Google Cloud Function triggered by incoming email/webhook instead of manual CSV upload
- [ ] Add authentication for multi-user/team use

## Project Structure

```
support-ticket-triage-ai/
├── app.py                  # Streamlit web app
├── agent_classify.py       # LLM classification + response drafting (with demo fallback)
├── data_cleaning.py        # CSV cleaning utilities
├── data/
│   └── sample_tickets.csv  # 20 sample tickets for demo/testing
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## License

MIT — feel free to fork and adapt.
