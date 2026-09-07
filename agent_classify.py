"""
agent_classify.py
Uses an LLM (Anthropic Claude) to classify support tickets and draft responses.

IMPORTANT: If no ANTHROPIC_API_KEY is found in your environment, this module
automatically falls back to a rule-based "demo mode" so the app still runs
end-to-end out of the box. Add your real key to a .env file to get true
AI-powered results (see .env.example).
"""

import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEMO_MODE = not API_KEY

if not DEMO_MODE:
    from anthropic import Anthropic
    client = Anthropic(api_key=API_KEY)

MODEL = "claude-sonnet-4-6"


# ----------------------------------------------------------------------
# Demo-mode fallback (rule-based, no API key required)
# ----------------------------------------------------------------------
_URGENT_WORDS = ["urgent", "critical", "immediately", "asap", "right now", "today"]
_NEGATIVE_WORDS = ["frustrat", "disappoint", "angry", "terrible", "worst", "cancel"]
_CATEGORY_KEYWORDS = {
    "billing": ["charge", "invoice", "refund", "billed", "payment", "subscription"],
    "technical": ["crash", "bug", "error", "not syncing", "sync", "upload", "login", "log in"],
    "account": ["account", "password", "email address", "suspended", "credentials"],
    "shipping": ["package", "tracking", "order", "arrive", "delivery"],
    "general_inquiry": ["how do i", "question", "curious", "wondering", "difference between"],
}


def _demo_classify(ticket_text: str) -> dict:
    text_lower = ticket_text.lower()

    category = "general_inquiry"
    for cat, keywords in _CATEGORY_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            category = cat
            break

    urgency = 2
    if any(w in text_lower for w in _URGENT_WORDS):
        urgency = 5
    elif any(w in text_lower for w in _NEGATIVE_WORDS):
        urgency = 4
    elif category in ("billing", "technical", "account", "shipping"):
        urgency = 3

    sentiment = "neutral"
    if any(w in text_lower for w in _NEGATIVE_WORDS) or urgency >= 4:
        sentiment = "negative"
    elif any(w in text_lower for w in ["love", "great", "thanks", "curious"]):
        sentiment = "positive"

    summary = ticket_text.strip().split(".")[0][:120]

    return {
        "category": category,
        "urgency": urgency,
        "sentiment": sentiment,
        "summary": summary,
    }


def _demo_draft_response(ticket_text: str, classification: dict) -> str:
    category = classification.get("category", "general_inquiry")
    templates = {
        "billing": "Thank you for reaching out about this billing concern. I'm looking into your account now and will make sure any incorrect charge is corrected as quickly as possible.",
        "technical": "I'm sorry you're running into this technical issue. Could you let us know your device/app version so our team can investigate right away?",
        "account": "Thanks for contacting us about your account. I'll help you get this sorted out securely — could you confirm the email associated with your account?",
        "shipping": "I understand the wait on your order is frustrating. Let me check the latest tracking status and get back to you with an update shortly.",
        "general_inquiry": "Thanks for your question! Here's what I can share, and please let me know if you'd like more detail.",
    }
    return templates.get(category, templates["general_inquiry"])


# ----------------------------------------------------------------------
# Real LLM-powered functions
# ----------------------------------------------------------------------
def classify_ticket(ticket_text: str) -> dict:
    """Returns dict with category, urgency (1-5), sentiment, summary."""
    if DEMO_MODE:
        return _demo_classify(ticket_text)

    prompt = f"""Analyze this customer support ticket and respond ONLY with
valid JSON, no other text, no markdown formatting:

Ticket: "{ticket_text}"

Return JSON with these exact keys:
- category: one short word/phrase (e.g. "billing", "technical", "account", "shipping", "general_inquiry")
- urgency: integer from 1 (low) to 5 (critical)
- sentiment: one of "positive", "neutral", "negative"
- summary: one sentence summarizing the issue
"""
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    raw_text = response.content[0].text.strip()
    raw_text = re.sub(r"```json|```", "", raw_text).strip()

    try:
        result = json.loads(raw_text)
        result["urgency"] = int(result.get("urgency", 3))
        return result
    except (json.JSONDecodeError, ValueError):
        return _demo_classify(ticket_text)  # graceful fallback


def draft_response(ticket_text: str, classification: dict) -> str:
    """Returns a short suggested first-response string."""
    if DEMO_MODE:
        return _demo_draft_response(ticket_text, classification)

    prompt = f"""You are a customer support agent. Write a short, empathetic
first-response (3-4 sentences) to this customer. Do not promise specific
refund amounts or timelines you can't guarantee. Keep it professional and warm.

Ticket: "{ticket_text}"
Category: {classification.get('category')}
Urgency: {classification.get('urgency')}
Sentiment: {classification.get('sentiment')}
"""
    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


if __name__ == "__main__":
    sample = "My payment failed twice and I was charged both times, please help urgently!"
    c = classify_ticket(sample)
    print("Classification:", c)
    print("Response:", draft_response(sample, c))
    print(f"\n(Running in {'DEMO MODE (no API key found)' if DEMO_MODE else 'LIVE MODE (using Claude API)'})")
