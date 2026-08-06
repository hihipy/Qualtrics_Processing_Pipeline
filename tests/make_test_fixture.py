"""Build a synthetic Qualtrics Excel export for testing the pipeline.

Writes a file that mimics the real export shape: standard Qualtrics metadata
columns, row 0 holding full question text, response rows starting at row 1, and
a deliberate mix of genuine responses, survey previews, spam, straight-lining,
partial completions, and text answers contaminated with units.

Usage:
    python make_test_fixture.py [output.xlsx] [--rows N]
"""

import argparse
import random
from datetime import datetime, timedelta

import pandas as pd

RANDOM_SEED = 20260805

METADATA_COLUMNS = [
    "StartDate",
    "EndDate",
    "Status",
    "IPAddress",
    "Progress",
    "Duration (in seconds)",
    "Finished",
    "RecordedDate",
    "ResponseId",
    "RecipientLastName",
    "RecipientFirstName",
    "RecipientEmail",
    "ExternalReference",
    "LocationLatitude",
    "LocationLongitude",
    "DistributionChannel",
    "UserLanguage",
]

# Question text row. Deliberately includes "which of", "please", "identify",
# "provide" and question marks, because analyze_codebook_structure scores row 0
# on those patterns to decide the codebook source.
QUESTION_TEXT = {
    "StartDate": "Start Date",
    "EndDate": "End Date",
    "Status": "Response Type",
    "IPAddress": "IP Address",
    "Progress": "Progress",
    "Duration (in seconds)": "Duration (in seconds)",
    "Finished": "Finished",
    "RecordedDate": "Recorded Date",
    "ResponseId": "Response ID",
    "RecipientLastName": "Recipient Last Name",
    "RecipientFirstName": "Recipient First Name",
    "RecipientEmail": "Recipient Email",
    "ExternalReference": "External Data Reference",
    "LocationLatitude": "Location Latitude",
    "LocationLongitude": "Location Longitude",
    "DistributionChannel": "Distribution Channel",
    "UserLanguage": "User Language",
    "Q1": "Please identify your primary department within the health system.",
    "Q2#1_1": "Which of the following best describes your experience? - Data access - Satisfaction",
    "Q2#1_2": "Which of the following best describes your experience? - Reporting tools - Satisfaction",
    "Q2#1_3": "Which of the following best describes your experience? - Analyst support - Satisfaction",
    "Q2#2_1": "Which of the following best describes your experience? - Data access - Importance",
    "Q2#2_2": "Which of the following best describes your experience? - Reporting tools - Importance",
    "Q2#2_3": "Which of the following best describes your experience? - Analyst support - Importance",
    "Q3": "How many years have you worked in your current role? Please provide a whole number.",
    "Q4": "Would you recommend the current reporting workflow to a colleague?",
    "Q5": "Approximately how many hours per week do you spend preparing data for analysis?",
    "Q5_3_TEXT": "Approximately how many hours per week do you spend preparing data for analysis? - Other (please specify)",
    "Q6_TEXT": "Please describe, in your own words, the single biggest obstacle you face when working with survey data.",
    "Q7": "On which date did you last attend an analytics training session?",
    "Q8": "Please rate your overall satisfaction with institutional data services.",
}

QUESTION_COLUMNS = [c for c in QUESTION_TEXT if c not in METADATA_COLUMNS]
ALL_COLUMNS = METADATA_COLUMNS + QUESTION_COLUMNS

DEPARTMENTS = [
    "Cardiology",
    "Oncology",
    "Pediatrics",
    "Neurology",
    "Radiology",
    "Internal Medicine",
]
LIKERT = [
    "Strongly disagree",
    "Somewhat disagree",
    "Neither agree nor disagree",
    "Somewhat agree",
    "Strongly agree",
]
IMPORTANCE = ["Not important", "Slightly important", "Important", "Very important"]
SATISFACTION = ["Very dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very satisfied"]
OBSTACLES = [
    "Column names are cryptic and there is no codebook to read them against.",
    "Every export needs the same manual cleanup before I can touch it.",
    "Preview responses get mixed into the real data and nobody catches it.",
    "Dates come through as text so my date filters silently return nothing.",
    "I cannot reproduce last quarter's numbers because the steps were not written down.",
    "",
]


def make_row(rng, index, response_type):
    """One response row. response_type drives the data-quality characteristics."""
    started = datetime(2026, 3, 2, 8, 0) + timedelta(minutes=37 * index)
    duration = rng.choice([412, 533, 618, 744, 902])
    progress = 100
    finished = 1

    if response_type == "preview":
        status = "Survey Preview"
    elif response_type == "spam":
        status = "Spam"
    elif response_type == "partial":
        status = "IP Address"
        progress = rng.choice([18, 34, 51, 67])
        finished = 0
        duration = rng.choice([31, 44, 58])
    else:
        status = "IP Address"

    row = {
        "StartDate": started.strftime("%Y-%m-%d %H:%M:%S"),
        "EndDate": (started + timedelta(seconds=int(duration))).strftime("%Y-%m-%d %H:%M:%S"),
        "Status": status,
        "IPAddress": f"10.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}",
        "Progress": progress,
        "Duration (in seconds)": duration,
        "Finished": finished,
        "RecordedDate": (started + timedelta(seconds=int(duration) + 3)).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "ResponseId": f"R_{index:012d}",
        "RecipientLastName": "",
        "RecipientFirstName": "",
        "RecipientEmail": "",
        "ExternalReference": "",
        "LocationLatitude": round(25.79 + rng.uniform(-0.4, 0.4), 6),
        "LocationLongitude": round(-80.21 + rng.uniform(-0.4, 0.4), 6),
        "DistributionChannel": "anonymous",
        "UserLanguage": "EN",
    }

    if response_type == "straightliner":
        # Same answer down the whole matrix, which is what the straight-lining
        # quality flag is supposed to catch.
        pinned = LIKERT[4]
        row["Q1"] = rng.choice(DEPARTMENTS)
        for col in ["Q2#1_1", "Q2#1_2", "Q2#1_3"]:
            row[col] = pinned
        for col in ["Q2#2_1", "Q2#2_2", "Q2#2_3"]:
            row[col] = IMPORTANCE[3]
        row["Q3"] = rng.randint(1, 30)
        row["Q4"] = "Yes"
        row["Q5"] = rng.choice([2, 5, 8, 12])
        row["Q5_3_TEXT"] = ""
        row["Q6_TEXT"] = ""
        row["Q7"] = (started - timedelta(days=rng.randint(30, 700))).strftime("%Y-%m-%d")
        row["Q8"] = SATISFACTION[4]
        return row

    if response_type == "partial":
        row["Q1"] = rng.choice(DEPARTMENTS)
        row["Q2#1_1"] = rng.choice(LIKERT)
        for col in QUESTION_COLUMNS:
            row.setdefault(col, "")
        return row

    row["Q1"] = rng.choice(DEPARTMENTS)
    for col in ["Q2#1_1", "Q2#1_2", "Q2#1_3"]:
        row[col] = rng.choice(LIKERT)
    for col in ["Q2#2_1", "Q2#2_2", "Q2#2_3"]:
        row[col] = rng.choice(IMPORTANCE)
    row["Q3"] = rng.randint(1, 34)
    row["Q4"] = rng.choice(["Yes", "No", "Yes", "Yes"])
    # Q5 is deliberately contaminated: mostly numeric, some free text with units.
    row["Q5"] = rng.choice([3, 6, 9, 14, "about 10 hours", "8-12", "n/a", 4, 7])
    row["Q5_3_TEXT"] = rng.choice(["", "", "", "roughly 15 hrs/wk"])
    row["Q6_TEXT"] = rng.choice(OBSTACLES)
    row["Q7"] = (started - timedelta(days=rng.randint(14, 900))).strftime("%Y-%m-%d")
    row["Q8"] = rng.choice(SATISFACTION)
    return row


def build_frame(n_genuine=60):
    rng = random.Random(RANDOM_SEED)

    plan = ["genuine"] * n_genuine
    plan += ["preview"] * 4
    plan += ["spam"] * 2
    plan += ["straightliner"] * 5
    plan += ["partial"] * 6
    rng.shuffle(plan)

    rows = [QUESTION_TEXT]
    for i, kind in enumerate(plan, start=1):
        rows.append(make_row(rng, i, kind))

    return pd.DataFrame(rows, columns=ALL_COLUMNS), plan


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", nargs="?", default="qualtrics_test_export.xlsx")
    parser.add_argument("--rows", type=int, default=60, help="genuine response count")
    args = parser.parse_args()

    frame, plan = build_frame(args.rows)
    frame.to_excel(args.output, index=False, sheet_name="Sheet0", engine="openpyxl")

    counts = {kind: plan.count(kind) for kind in sorted(set(plan))}
    print(f"Wrote {args.output}")
    print(f"  Shape: {frame.shape[0]} rows x {frame.shape[1]} columns")
    print("  Row 0 holds question text; responses start at row 1")
    print(f"  Response mix: {counts}")
    print(f"  Expected removals (preview + spam): {counts.get('preview', 0) + counts.get('spam', 0)}")
    print(f"  Expected surviving responses: {len(plan) - counts.get('preview', 0) - counts.get('spam', 0)}")


if __name__ == "__main__":
    main()
