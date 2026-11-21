"""
02_bidi_encoding_cleaner.py
---------------------------
Cleans Arabic-French bidirectional (BiDi) text reversals, reversed numeric
strings, and whitespace anomalies in extracted BNA bibliographic records.
"""

import argparse
import re
from bidi.algorithm import get_display
import pandas as pd


def fix_reversed_digits(text: str) -> str:
    """Restores digit sequences reversed during right-to-left PDF text extraction."""
    return re.sub(
        r"\b\d+\b",
        lambda m: m.group(0)[::-1] if len(m.group(0)) >= 2 and m.group(0).endswith("0") else m.group(0),
        text,
    )


def normalize_bidi_line(line: str) -> str:
    """Applies BiDi display resolution selectively to lines containing Arabic characters."""
    cleaned = re.sub(r"[ \t]+", " ", line).strip()
    if not cleaned:
        return ""
    if re.search(r"[\u0600-\u06FF]", cleaned):
        resolved = get_display(cleaned)
        return fix_reversed_digits(resolved)
    return fix_reversed_digits(cleaned)


def clean_record_text(raw_text: str) -> str:
    """Cleans multi-line bibliographic entry while preserving line structure."""
    if not isinstance(raw_text, str) or not raw_text.strip():
        return ""
    lines = [normalize_bidi_line(line) for line in raw_text.splitlines()]
    return "\n".join(line for line in lines if line)


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean BiDi encoding in extracted BNA records.")
    parser.add_argument("--input", type=Path, required=True, help="Input extracted CSV path")
    parser.add_argument("--output", type=Path, required=True, help="Output cleaned CSV path")
    args = parser.parse_args()

    df = pd.read_csv(args.input, encoding="utf-8-sig")
    df["cleaned_text"] = df["raw_text"].apply(clean_record_text)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(f"Cleaned {len(df)} records -> {args.output}")


if __name__ == "__main__":
    main()
