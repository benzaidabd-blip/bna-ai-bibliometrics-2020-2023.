"""
01_bna_pdf_extractor.py
-----------------------
Extracts raw bibliographic records and metadata from Algerian National
Bibliography (BNA, Issues 114-120) PDF files using PyMuPDF and Regex.
"""

import argparse
import re
from pathlib import Path
import fitz  # PyMuPDF
import pandas as pd


ISSUE_METADATA = {
    "114": {"year": 2020, "period": "S1"},
    "115": {"year": 2020, "period": "S2"},
    "116": {"year": 2021, "period": "S1"},
    "117": {"year": 2021, "period": "S2"},
    "118": {"year": 2022, "period": "S1"},
    "119": {"year": 2022, "period": "S2"},
    "120": {"year": 2023, "period": "S1"},  # 2023 covers S1 only (4,937 records)
}


def detect_language(text: str) -> str:
    """Heuristic language classification for Arabic, French, English, or other."""
    arabic_chars = len(re.findall(r"[\u0600-\u06FF]", text))
    latin_chars = len(re.findall(r"[A-Za-zÀ-ÿ]", text))
    if arabic_chars > latin_chars:
        return "Arabic"
    if latin_chars > 0:
        # Refine French vs. English detection in downstream/NLP stage
        return "French/Latin"
    return "Other"


def extract_dewey_code(block_text: str) -> str:
    """Extracts Dewey Decimal Classification (DDC) pattern if present."""
    match = re.search(r"\b(\d{3}(?:\.\d+)?)\b", block_text)
    return match.group(1) if match else ""


def parse_pdf_file(pdf_path: Path, issue_code: str) -> list[dict]:
    """Parses a single BNA PDF issue into structured candidate records."""
    records = []
    meta = ISSUE_METADATA.get(issue_code, {"year": None, "period": "Unknown"})

    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc, start=1):
            raw_text = page.get_text("text")
            # Split blocks/entries by blank lines or entry delimiters
            entries = [seg.strip() for seg in re.split(r"\n\s*\n", raw_text) if len(seg.strip()) > 25]

            for idx, entry in enumerate(entries, start=1):
                records.append({
                    "issue": issue_code,
                    "year": meta["year"],
                    "period": meta["period"],
                    "page": page_num,
                    "entry_seq": idx,
                    "dewey": extract_dewey_code(entry),
                    "lang_prelim": detect_language(entry),
                    "raw_text": entry,
                })
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract BNA PDF records to CSV.")
    parser.add_argument("--input", type=Path, required=True, help="Directory containing BNA PDFs")
    parser.add_argument("--output", type=Path, required=True, help="Output CSV path")
    args = parser.parse_args()

    all_records: list[dict] = []
    for pdf_file in sorted(args.input.glob("*.pdf")):
        issue_match = re.search(r"(11[4-9]|120)", pdf_file.stem)
        issue_code = issue_match.group(1) if issue_match else pdf_file.stem
        all_records.extend(parse_pdf_file(pdf_file, issue_code))

    df = pd.DataFrame(all_records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(f"Extracted {len(df)} candidate records -> {args.output}")


if __name__ == "__main__":
    main()
