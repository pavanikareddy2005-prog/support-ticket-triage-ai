"""
data_cleaning.py
Cleans raw support ticket CSVs before they're passed to the AI agent.
"""

import pandas as pd


def clean_tickets(input_path: str, output_path: str = None) -> pd.DataFrame:
    """
    Loads a CSV of support tickets, removes empty/duplicate rows,
    normalizes text, and optionally saves the cleaned result.

    Expected columns: ticket_id, customer_name, text
    (extra columns are preserved if present)
    """
    df = pd.read_csv(input_path)

    if "text" not in df.columns:
        raise ValueError("CSV must contain a 'text' column with the ticket content.")

    # Drop rows with missing/empty ticket text
    df = df.dropna(subset=["text"])
    df["text"] = df["text"].astype(str).str.strip()
    df = df[df["text"] != ""]

    # Remove exact duplicate tickets
    df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)

    if output_path:
        df.to_csv(output_path, index=False)
        print(f"Saved {len(df)} cleaned tickets to {output_path}")

    return df


if __name__ == "__main__":
    cleaned = clean_tickets("data/sample_tickets.csv", "data/tickets_clean.csv")
    print(cleaned.head())
