"""
app.py
The web app (Streamlit) for the AI-Powered Support Ticket Triage System.

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
from data_cleaning import clean_tickets
from agent_classify import classify_ticket, draft_response, DEMO_MODE

st.set_page_config(
    page_title="AI Ticket Triage",
    page_icon="🎫",
    layout="wide",
)

# ---------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        margin-bottom: 0;
    }
    .subtitle {
        color: #6b7280;
        font-size: 1.05rem;
        margin-top: 0.2rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e5e7eb;
        color: #111827 !important;
    }
    .metric-card h3 {
        color: #111827 !important;
        margin: 0 0 0.3rem 0;
    }
    .demo-banner {
        background-color: #fff3cd;
        border: 1px solid #ffe69c;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-bottom: 1.2rem;
        font-size: 0.92rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="main-title">🎫 AI-Powered Support Ticket Triage</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Upload support tickets and get instant AI classification, '
    'urgency scoring, and suggested responses.</p>',
    unsafe_allow_html=True,
)

if DEMO_MODE:
    st.markdown(
        '<div class="demo-banner">⚠️ <b>Running in Demo Mode</b> — no ANTHROPIC_API_KEY was found, '
        'so results are generated using a rule-based fallback (not a real LLM). '
        'Add your key to a <code>.env</code> file to enable true AI-powered classification. '
        'See <code>.env.example</code>.</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Options")
    use_sample = st.checkbox("Use built-in sample dataset", value=True)
    max_rows = st.slider("Max tickets to process", min_value=5, max_value=50, value=20, step=5)
    st.markdown("---")
    st.caption(
        "Tip: keep this low to save on API cost/time during testing. "
        "The sample dataset has 20 realistic example tickets."
    )

uploaded_file = None
if not use_sample:
    uploaded_file = st.file_uploader("Upload a CSV with a 'text' column", type="csv")

# ---------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------
df = None
if use_sample:
    df = clean_tickets("data/sample_tickets.csv")
elif uploaded_file:
    uploaded_file.seek(0)
    with open("data/_uploaded.csv", "wb") as f:
        f.write(uploaded_file.getbuffer())
    df = clean_tickets("data/_uploaded.csv")

# ---------------------------------------------------------------------
# Process & display
# ---------------------------------------------------------------------
if df is not None:
    df = df.head(max_rows)

    if st.button("🚀 Run AI Triage", type="primary"):
        results = []
        progress = st.progress(0, text="Starting analysis...")

        for i, row in df.reset_index(drop=True).iterrows():
            text = str(row["text"])
            classification = classify_ticket(text)
            response = draft_response(text, classification)
            results.append(
                {
                    "Customer": row.get("customer_name", f"Ticket #{row.get('ticket_id', i)}"),
                    "Ticket": text,
                    "Category": classification.get("category", "unknown"),
                    "Urgency": int(classification.get("urgency", 3)),
                    "Sentiment": classification.get("sentiment", "neutral"),
                    "Summary": classification.get("summary", ""),
                    "Suggested Response": response,
                }
            )
            progress.progress((i + 1) / len(df), text=f"Processed {i + 1}/{len(df)} tickets...")

        progress.empty()
        result_df = pd.DataFrame(results)
        st.session_state["results"] = result_df

    if "results" in st.session_state:
        result_df = st.session_state["results"]

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                f'<div class="metric-card"><h3>{len(result_df)}</h3>Tickets Processed</div>',
                unsafe_allow_html=True,
            )
        with col2:
            critical = (result_df["Urgency"] >= 4).sum()
            st.markdown(
                f'<div class="metric-card"><h3>{critical}</h3>High/Critical Urgency</div>',
                unsafe_allow_html=True,
            )
        with col3:
            neg = (result_df["Sentiment"] == "negative").sum()
            st.markdown(
                f'<div class="metric-card"><h3>{neg}</h3>Negative Sentiment</div>',
                unsafe_allow_html=True,
            )
        with col4:
            top_cat = result_df["Category"].mode()[0] if not result_df.empty else "-"
            st.markdown(
                f'<div class="metric-card"><h3>{top_cat}</h3>Top Category</div>',
                unsafe_allow_html=True,
            )

        st.markdown("### 📋 Triage Results")

        def highlight_urgency(val):
            if val >= 4:
                return "background-color: #ffd6d6"
            elif val == 3:
                return "background-color: #fff3cd"
            return "background-color: #d9f2e3"

        try:
            styled = result_df.style.map(highlight_urgency, subset=["Urgency"])
        except AttributeError:
            # Fallback for older pandas versions that still use applymap
            styled = result_df.style.applymap(highlight_urgency, subset=["Urgency"])
        st.dataframe(styled, width="stretch", height=420)

        st.markdown("### 🔍 Ticket Detail View")
        selected_idx = st.selectbox(
            "Select a ticket to see full details",
            options=result_df.index,
            format_func=lambda i: f"#{i} — {result_df.loc[i, 'Customer']} ({result_df.loc[i, 'Category']}, urgency {result_df.loc[i, 'Urgency']})",
        )
        row = result_df.loc[selected_idx]
        st.write(f"**Original ticket:** {row['Ticket']}")
        st.write(f"**Summary:** {row['Summary']}")
        st.write(f"**Category:** {row['Category']}  |  **Urgency:** {row['Urgency']}  |  **Sentiment:** {row['Sentiment']}")
        st.success(f"**Suggested response:** {row['Suggested Response']}")

        csv = result_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download results as CSV", csv, "triage_results.csv", "text/csv")
else:
    st.info("Upload a CSV with a 'text' column, or check 'Use built-in sample dataset' in the sidebar.")

st.markdown("---")
st.caption("Built as a portfolio project demonstrating GenAI agents + data processing + cloud-ready deployment.")
