import json
import os
import time
from pathlib import Path

import pandas as pd
from decouple import config
from openai import AzureOpenAI


INPUT_FILE = "customer_messages_for_sentiment.csv"
OUTPUT_FILE = "ticket_sentiment_results.csv"
BATCH_SIZE = 10

# Keep each ticket compact so batches do not get too large.
MAX_CHARS_PER_TICKET = 6000


client = AzureOpenAI(
    api_key=config("AZURE_OPENAI_API_KEY"),
    azure_endpoint=config("AZURE_OPENAI_ENDPOINT").rstrip("/"),
    api_version=config("AZURE_OPENAI_API_VERSION", default="2024-10-21"),
)

DEPLOYMENT_NAME = config("AZURE_OPENAI_DEPLOYMENT")


SYSTEM_PROMPT = """
You are analyzing customer sentiment in support tickets.

Analyze only the customer's own messages.
Do not analyze agent replies, AI bot replies, internal notes, quoted email history, signatures, disclaimers, or previous thread text.

The goal is to classify the customer's tone and whether the ticket sentiment improved, worsened, or stayed the same during the conversation.

Do not assume that an AI response caused the sentiment.
Do not use CSAT or survey score to decide sentiment.
Do not overreact to standard support phrases like "I cannot log in" or "I lost access"; classify based on tone, frustration, urgency, and wording.

Return only valid JSON.
""".strip()


def load_messages():
    df = pd.read_csv(INPUT_FILE)

    required_columns = {"ticket_id", "body_text", "message_created_at"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns in {INPUT_FILE}: {missing}")

    df["ticket_id"] = df["ticket_id"].astype(str)
    df["body_text"] = df["body_text"].fillna("").astype(str)
    df["message_created_at"] = df["message_created_at"].fillna("").astype(str)

    return df


def compact_text(text, max_chars):
    text = str(text or "").strip()

    if len(text) <= max_chars:
        return text

    return text[:max_chars] + "\n\n[Text truncated because the ticket was long.]"


def build_ticket_payloads(df):
    payloads = []

    for ticket_id, group in df.groupby("ticket_id"):
        group = group.sort_values("message_created_at")

        first_row = group.iloc[0]

        messages = []
        total_chars = 0

        for index, row in enumerate(group.itertuples(), start=1):
            message_text = str(row.body_text or "").strip()

            if not message_text:
                continue

            message_block = (
                f"[{index}] {row.message_created_at}\n"
                f"{message_text}"
            )

            total_chars += len(message_block)

            messages.append(message_block)

        joined_messages = "\n\n".join(messages)
        joined_messages = compact_text(joined_messages, MAX_CHARS_PER_TICKET)

        tags = str(getattr(first_row, "tags", "") or "")

        payloads.append({
            "ticket_id": ticket_id,
            "has_ai_first_response": bool(getattr(first_row, "has_ai_first_response", False)),
            "tags": tags,
            "priority": str(getattr(first_row, "priority", "") or ""),
            "group_id": str(getattr(first_row, "group_id", "") or ""),
            "type": str(getattr(first_row, "type", "") or ""),
            "subject": str(getattr(first_row, "subject", "") or ""),
            "customer_messages": joined_messages,
        })

    return payloads


def already_processed_ticket_ids():
    if not Path(OUTPUT_FILE).exists():
        return set()

    existing = pd.read_csv(OUTPUT_FILE)

    if "ticket_id" not in existing.columns:
        return set()

    return set(existing["ticket_id"].astype(str))


def make_user_prompt(batch):
    return f"""
Analyze the customer sentiment for each Freshdesk support ticket below.

Important rules:
- Analyze only customer-written messages.
- Ignore agent replies, AI replies, internal notes, signatures, disclaimers, and quoted thread history.
- Do not use CSAT or survey score to infer sentiment.
- Do not assume the AI caused the sentiment.
- If the customer simply describes a problem without emotional language, classify it as neutral or mildly negative, not strongly negative.
- If the customer explicitly mentions bot, AI, automated response, generic answer, irrelevant answer, or asks for a human, capture that in ai_feedback_type.
- Keep short_reason factual and under 30 words.

Return a JSON object with this exact top-level shape:
{{
  "results": [
    {{
      "ticket_id": "string",
      "initial_sentiment_score": integer from -2 to 2,
      "final_sentiment_score": integer from -2 to 2,
      "overall_customer_sentiment": "positive" | "neutral" | "negative",
      "sentiment_changed": "improved" | "worsened" | "same" | "unclear",
      "main_emotion": "angry" | "frustrated" | "confused" | "urgent" | "calm" | "appreciative" | "unclear",
      "frustration_level": integer from 0 to 3,
      "urgency_level": integer from 0 to 3,
      "customer_effort_level": integer from 0 to 3,
      "ai_mentioned": boolean,
      "ai_feedback_type": "none" | "negative_ai_feedback" | "positive_ai_feedback" | "says_response_did_not_help" | "asks_for_human" | "unclear",
      "customer_says_response_did_not_help": boolean,
      "asks_for_human": boolean,
      "resolution_signal": "resolved" | "not_resolved" | "unclear",
      "confidence": number from 0 to 1,
      "short_reason": "string"
    }}
  ]
}}

Tickets:
{json.dumps(batch, ensure_ascii=False)}
""".strip()


def call_model(batch):
    user_prompt = make_user_prompt(batch)

    for attempt in range(1, 6):
        try:
            response = client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )

            content = response.choices[0].message.content
            parsed = json.loads(content)

            if "results" not in parsed:
                raise ValueError(f"Model response did not include 'results': {content}")

            return parsed["results"]

        except Exception as error:
            wait_seconds = min(60, 5 * attempt)
            print(f"\nAttempt {attempt} failed: {error}")
            print(f"Waiting {wait_seconds} seconds before retrying...")
            time.sleep(wait_seconds)

    raise RuntimeError("Model call failed after 5 attempts.")


def append_results(results):
    output_df = pd.DataFrame(results)

    file_exists = Path(OUTPUT_FILE).exists()

    output_df.to_csv(
        OUTPUT_FILE,
        mode="a",
        header=not file_exists,
        index=False,
    )


def main():
    df = load_messages()
    payloads = build_ticket_payloads(df)

    processed = already_processed_ticket_ids()
    payloads = [
        ticket for ticket in payloads
        if str(ticket["ticket_id"]) not in processed
    ]

    print(f"Tickets left to analyze: {len(payloads)}")

    for start in range(0, len(payloads), BATCH_SIZE):
        batch = payloads[start:start + BATCH_SIZE]

        print(
            f"\nAnalyzing batch {start // BATCH_SIZE + 1} "
            f"with {len(batch)} tickets..."
        )

        results = call_model(batch)

        # Basic safety check: make sure we got one result per ticket.
        expected_ids = {str(ticket["ticket_id"]) for ticket in batch}
        returned_ids = {str(result.get("ticket_id")) for result in results}

        missing_ids = expected_ids - returned_ids

        if missing_ids:
            print(f"WARNING: Missing results for ticket IDs: {missing_ids}")

        append_results(results)

        print(f"Saved {len(results)} results to {OUTPUT_FILE}")

        # Gentle pacing to reduce rate-limit risk.
        time.sleep(1)

    print("\nDone.")


if __name__ == "__main__":
    main()