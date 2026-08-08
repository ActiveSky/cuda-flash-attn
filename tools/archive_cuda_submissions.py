#!/usr/bin/env python3
"""Extract the exact submitted CUDA source embedded in every raw OJ result."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "results" / "raw"
ARCHIVE_DIR = ROOT / "solutions" / "archive"
LOCAL_TIMEZONE = timezone(timedelta(hours=8))


def local_submit_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
        LOCAL_TIMEZONE
    )


def markdown_score(value: object) -> str:
    if value is None:
        return "—"
    return f"{float(value):.2f}"


def main() -> None:
    rows: list[dict[str, object]] = []

    for raw_path in sorted(RAW_DIR.glob("cuda_*_raw.json")):
        result = json.loads(raw_path.read_text(encoding="utf-8"))
        submission_id = int(result["id"])
        expected_name = f"cuda_{submission_id}_raw.json"
        if raw_path.name != expected_name:
            raise ValueError(
                f"submission ID/path mismatch: {submission_id} in {raw_path}"
            )

        code = result["raw_detail"]["content"]["code"].encode("utf-8")
        submitted_at = local_submit_time(result["submit_time"])
        collection = ARCHIVE_DIR / f"{submitted_at:%Y-%m-%d}-submissions"
        source_path = collection / f"cuda_{submission_id}.cpp"
        collection.mkdir(parents=True, exist_ok=True)

        if source_path.exists() and source_path.read_bytes() != code:
            raise ValueError(f"refusing to replace mismatched archive: {source_path}")
        source_path.write_bytes(code)

        rows.append(
            {
                "id": submission_id,
                "time": submitted_at,
                "status": result["status"],
                "score": result["score"],
                "sha256": hashlib.sha256(code).hexdigest(),
                "source": source_path.relative_to(ARCHIVE_DIR).as_posix(),
                "raw": raw_path.relative_to(ROOT).as_posix(),
            }
        )

    lines = [
        "# Submitted source manifest",
        "",
        (
            "This generated manifest maps every `results/raw/cuda_*_raw.json` "
            "record to a byte-exact submitted source snapshot. Times are UTC+8."
        ),
        "",
        "| Submission | Time (UTC+8) | Status | Score | SHA-256 | Source | Raw result |",
        "|---:|---|---|---:|---|---|---|",
    ]
    for row in sorted(rows, key=lambda item: int(item["id"]), reverse=True):
        source = str(row["source"])
        raw = str(row["raw"])
        lines.append(
            "| "
            f"#{row['id']} | {row['time']:%Y-%m-%d %H:%M:%S} | "
            f"{row['status']} | {markdown_score(row['score'])} | "
            f"`{row['sha256']}` | [{Path(source).name}]({source}) | "
            f"[{Path(raw).name}](../../{raw}) |"
        )

    manifest_path = ARCHIVE_DIR / "SUBMISSIONS.md"
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"archived {len(rows)} submissions; manifest: {manifest_path}")


if __name__ == "__main__":
    main()
