# 🎫 AI-Powered Support Ticket Triage System

🔗 **[Try the live app](https://pavanika-ticket-triage.streamlit.app/)** &nbsp;|&nbsp; 📂 [View the code](https://github.com/pavanikareddy2005-prog/support-ticket-triage-ai)


## The problem I wanted to solve

When a company gets a lot of customer support tickets, someone has to read each one, figure out what it's about, decide how serious it is, and then pass it to the right person. That takes time. And while that's happening, an urgent ticket — like "I was charged twice, please help right now" — can sit in the same queue as a simple "how do I change my email" question, with nothing to tell an agent which one to look at first.

I wanted to build something that does that first pass automatically: read a ticket, understand what it's about, and flag how urgent it is — so a human agent can jump straight to the ones that matter most.

## How I approached it

I broke the problem into three parts:

1. **Get the data ready.** Real ticket data is messy — empty rows, duplicates, inconsistent text. So the first step cleans that up before anything else touches it.
2. **Understand each ticket.** This is where AI comes in. For every ticket, an AI agent reads the text and figures out: what category it belongs to (billing, technical, account, shipping, or general), how urgent it is on a scale of 1–5, whether the customer sounds upset, and a one-line summary of the issue.
3. **Help the agent respond faster.** Once a ticket is understood, a second AI step drafts a suggested first reply, so the human agent isn't starting from a blank page.

Everything then shows up in a simple dashboard — a table you can scan, color-coded by urgency, with the option to download the results.

## Try it

Click the live link at the top — it comes preloaded with 20 example tickets, so you can just click "Run AI Triage" and see it work immediately. No sign-up, no setup.

**Note on how it's running:** the deployed version uses a rule-based classifier instead of a live LLM call, so it's free to run and demo without needing an API key. The code is fully built to call Claude's API for real AI-powered classification (see `agent_classify.py`) — I designed it to automatically fall back to the rule-based version whenever no API key is present, so the whole pipeline is always demoable.

## How it's built

```
Ticket data (CSV)
        │
        ▼
  clean the data        →  remove empty/duplicate tickets
        │
        ▼
  understand each ticket →  category, urgency, sentiment, summary
        │
        ▼
  draft a response       →  a suggested first reply for the agent
        │
        ▼
  show it on a dashboard →  color-coded table, summary stats, CSV export
```

**Built with:** Python, Streamlit (the web app), Anthropic's Claude API (the AI reasoning), Pandas (cleaning and organizing the data).

## A couple of decisions I made on purpose

- **It never breaks if there's no API key.** Instead of crashing or showing an error, it quietly switches to a rule-based version so anyone can try it without needing to set anything up first.
- **It never sends more than it needs to.** Each ticket is processed on its own — nothing about the customer beyond the ticket text itself is sent anywhere.

## How I built this

I used AI (Claude) as a coding partner throughout — to scaffold the initial structure, help debug errors, and think through edge cases. I still had to actually set it up, test it, fix real bugs that came up (a pandas version conflict, a styling bug, environment issues on Windows), and understand every part of what it does. I think that's a fair way to build things now, and I'd rather be upfront about it than pretend otherwise.

## What I'd build next

- Let agents correct a wrong classification, so the system gets better over time
- Handle tickets in more than one language
- Automatically route tickets to the right team based on category
- Trigger this from an actual incoming email instead of a manual CSV upload
