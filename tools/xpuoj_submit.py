#!/usr/bin/env python3
"""Submit a solution to XPUOJ and archive the result.

Credentials are read from XPUOJ_API_TOKEN or XPUOJ_EMAIL/XPUOJ_PASSWORD.
The script loads tools/.env automatically (without overriding existing
environment variables) and never writes credentials to disk.
Defaults to dry-run mode; pass --submit to actually submit.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import requests

API_BASE = "https://sd629vuj4f7uh2cscrbe0.apigateway-cn-beijing.volceapi.com/"
DEFAULT_CONTEST_ID = 11
DEFAULT_PROBLEM_ORDER = 1
DEFAULT_LANGUAGE = "cuda.maca-c500"
DEFAULT_POLL_SECONDS = 120.0  # 2 分钟查询一次，降低请求频率避免风控
DEFAULT_TIMEOUT_SECONDS = 900.0
ENV_FILE = Path(__file__).resolve().parent / ".env"

TERMINAL_STATUSES = {
    "Accepted",
    "PartiallyCorrect",
    "WrongAnswer",
    "RuntimeError",
    "TimeLimitExceeded",
    "MemoryLimitExceeded",
    "OutputLimitExceeded",
    "CompilationError",
    "FileError",
    "JudgementFailed",
    "ConfigurationError",
    "SystemError",
    "Canceled",
}


class XpuojError(RuntimeError):
    """Raised when XPUOJ returns an unsuccessful response."""


def log(message: str) -> None:
    print(message, flush=True)


def load_env_file(path: Path) -> None:
    """Load KEY=VALUE lines from a .env file without overriding env vars."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("code", type=Path, nargs="?", help="Solution source file to submit")
    parser.add_argument(
        "--contest-id", type=int, default=DEFAULT_CONTEST_ID, help="Contest id"
    )
    parser.add_argument(
        "--problem-order",
        type=int,
        default=DEFAULT_PROBLEM_ORDER,
        help="Problem order within the contest",
    )
    parser.add_argument(
        "--language", default=DEFAULT_LANGUAGE, help="XPUOJ language id"
    )
    parser.add_argument(
        "--skip-samples",
        action="store_true",
        help="Skip sample execution when supported by the judge",
    )
    parser.add_argument(
        "--submit",
        action="store_true",
        help="Actually submit; without this flag only print a preview",
    )
    parser.add_argument(
        "--watch",
        "--submission-id",
        type=int,
        dest="watch_id",
        metavar="ID",
        help="Poll an existing submission instead of creating a new one",
    )
    parser.add_argument(
        "--cancel",
        type=int,
        metavar="ID",
        help="Cancel a pending submission and exit",
    )
    parser.add_argument(
        "--list",
        type=int,
        nargs="?",
        const=10,
        metavar="N",
        help="List the N most recent contest submissions (default 10)",
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Continuously watch for new submissions and archive finished ones",
    )
    parser.add_argument(
        "--no-archive",
        action="store_true",
        help="Do not save the full JSON result archive to results/raw/",
    )
    parser.add_argument(
        "--archive-dir",
        type=Path,
        default=Path("results/raw"),
        help="Directory for full JSON result archives",
    )
    parser.add_argument(
        "--poll-seconds",
        type=float,
        default=DEFAULT_POLL_SECONDS,
        help="Polling interval",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Maximum time to wait for judging",
    )
    parser.add_argument(
        "--api-base",
        default=os.environ.get("XPUOJ_API_BASE", API_BASE),
        help="Override the XPUOJ API base URL",
    )
    return parser.parse_args()


def api_url(api_base: str, path: str) -> str:
    return f"{api_base.rstrip('/')}/api/{path.lstrip('/')}"


def request_json(
    session: requests.Session,
    api_base: str,
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
    retries: int = 2,
    retry_delay: float = 2.0,
) -> dict[str, Any]:
    """Send a JSON request with a small number of retries for transient errors."""
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            response = session.request(
                method,
                api_url(api_base, path),
                params=params,
                json=payload,
                timeout=30,
            )
        except requests.RequestException as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(retry_delay * (attempt + 1))
                continue
            raise XpuojError(f"request to {path} failed: {exc}") from exc
        try:
            data = response.json()
        except ValueError as exc:
            raise XpuojError(
                f"XPUOJ returned non-JSON HTTP {response.status_code} from {path}"
            ) from exc
        if response.status_code in {429, 500, 502, 503, 504} and attempt < retries:
            last_error = XpuojError(f"HTTP {response.status_code} from {path}")
            time.sleep(retry_delay * (attempt + 1))
            continue
        if response.status_code not in {200, 201}:
            raise XpuojError(f"XPUOJ HTTP {response.status_code} from {path}: {data}")
        if isinstance(data, dict) and data.get("error"):
            raise XpuojError(f"XPUOJ {path} returned error: {data['error']}")
        if not isinstance(data, dict):
            raise XpuojError(f"Unexpected response from {path}: {type(data).__name__}")
        return data
    raise XpuojError(f"request to {path} failed after retries: {last_error}")


def authenticate(session: requests.Session, api_base: str) -> str:
    load_env_file(ENV_FILE)
    token = os.environ.get("XPUOJ_API_TOKEN")
    if token:
        return token

    email = os.environ.get("XPUOJ_EMAIL")
    password = os.environ.get("XPUOJ_PASSWORD")
    if not email:
        email = input("XPUOJ email: ").strip()
    if not password:
        password = getpass.getpass("XPUOJ password: ")

    response = request_json(
        session,
        api_base,
        "POST",
        "auth/login",
        payload={"email": email, "password": password},
    )
    token = response.get("token")
    if not isinstance(token, str) or not token:
        raise XpuojError("Login succeeded without a usable token")
    return token


def text_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("data"), str):
        return value["data"]
    return ""


SPJ_FIELD_RE = {
    "testcase": re.compile(r"Testcase\s+#(\d+)"),
    "config": re.compile(r"Config:\s*(.*)"),
    "baseline_ms": re.compile(r"Baseline:\s*([\d.]+)\s*ms"),
    "user_ms": re.compile(r"User kernel:\s*([\d.]+)\s*ms"),
    "speedup": re.compile(r"Speedup vs base:\s*([\d.]+)\s*x"),
    "score_ratio": re.compile(r"Score ratio:\s*([\d.]+)"),
    "display_score": re.compile(r"Display score:\s*(\d+)\s*/\s*100"),
    "pass": re.compile(r"Pass:\s*(\w+)"),
}


def parse_spj_report(text: str) -> dict[str, Any]:
    """Parse key/value fields out of an SPJ report text block."""
    parsed: dict[str, Any] = {}
    if not text:
        return parsed
    for key, pattern in SPJ_FIELD_RE.items():
        match = pattern.search(text)
        if match:
            value = match.group(1)
            if key in {"baseline_ms", "user_ms", "speedup", "score_ratio"}:
                parsed[key] = float(value)
            elif key == "display_score":
                parsed[key] = int(value)
            else:
                parsed[key] = value
    return parsed


def extract_testcases(progress: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize testcase results from the submission detail response."""
    result: list[dict[str, Any]] = []
    subtasks = progress.get("subtasks")
    if not isinstance(subtasks, list):
        return result

    testcase_results = progress.get("testcaseResult", {})
    if not isinstance(testcase_results, dict):
        testcase_results = {}

    index = 0
    for subtask in subtasks:
        if not isinstance(subtask, dict):
            continue
        testcases = subtask.get("testcases")
        if not isinstance(testcases, list):
            continue
        for testcase in testcases:
            if not isinstance(testcase, dict):
                continue
            index += 1
            testcase_hash = testcase.get("testcaseHash")
            details = testcase_results.get(testcase_hash, {})
            if not isinstance(details, dict):
                details = {}
            checker = text_value(
                details.get("checkerMessage") or details.get("userError")
            )
            spj = parse_spj_report(checker)
            result.append(
                {
                    "testcase": index,
                    "status": details.get("status") or testcase.get("status"),
                    "score": details.get("displayScore", details.get("score")),
                    "time_ms": details.get("time"),
                    "memory_kb": details.get("memory"),
                    "checker": checker,
                    "spj": spj,
                    "input_file": details.get("testcaseInfo", {}).get("inputFile")
                    if isinstance(details.get("testcaseInfo"), dict)
                    else None,
                }
            )
    return result


def normalize_submission(detail: dict[str, Any]) -> dict[str, Any]:
    meta = detail.get("meta", {})
    progress = detail.get("progress", {})
    if not isinstance(meta, dict):
        meta = {}
    if not isinstance(progress, dict):
        progress = {}
    return {
        "id": meta.get("id"),
        "status": meta.get("status") or progress.get("status"),
        "score": meta.get("displayScore", meta.get("score")),
        "language": meta.get("codeLanguage"),
        "submit_time": meta.get("submitTime"),
        "time_used_ms": meta.get("timeUsed"),
        "memory_used_kb": meta.get("memoryUsed"),
        "progress_type": progress.get("progressType"),
        "compile": progress.get("compile"),
        "testcases": extract_testcases(progress),
        "raw_detail": detail,
    }


def wait_for_submission(
    session: requests.Session,
    api_base: str,
    submission_id: int,
    poll_seconds: float,
    timeout_seconds: float,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_status: str | None = None
    last_progress: str | None = None
    last_detail: dict[str, Any] | None = None
    while time.monotonic() < deadline:
        last_detail = request_json(
            session,
            api_base,
            "POST",
            "submission/getSubmissionDetail",
            payload={"submissionId": str(submission_id), "locale": "zh_CN"},
        )
        normalized = normalize_submission(last_detail)
        status = normalized.get("status")
        progress_type = normalized.get("progress_type")
        # 节流：只有状态变化时才打印
        if status != last_status or progress_type != last_progress:
            log(f"submission={submission_id} progress={progress_type} status={status}")
            last_status = status
            last_progress = progress_type
        if status in TERMINAL_STATUSES or progress_type == "Finished":
            return normalized
        time.sleep(poll_seconds)
    raise TimeoutError(
        f"Submission {submission_id} did not finish within {timeout_seconds:g}s"
    )


def cancel_submission(session: requests.Session, api_base: str, submission_id: int) -> None:
    request_json(
        session,
        api_base,
        "POST",
        "submission/cancelSubmission",
        payload={"submissionId": submission_id},
    )
    log(f"canceled submission #{submission_id}")


def save_raw_json(
    archive_path: Path,
    submission: dict[str, Any],
) -> None:
    """Save the full submission response (including raw_detail) as JSON.

    Formatting/analysis of the result is intentionally left to the caller
    (the agent), which reads this file and writes human-readable reports.
    """
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    archive_path.write_text(
        json.dumps(submission, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def archive_and_report(
    args: argparse.Namespace,
    submission: dict[str, Any],
    code_path: Path,
) -> None:
    archive_path = None
    if not args.no_archive:
        archive_path = args.archive_dir / f"cuda_{submission['id']}_raw.json"
        save_raw_json(archive_path, submission)
        log(f"full result archive: {archive_path}")
    # 精简摘要输出到 stdout（不含 raw_detail，避免刷屏），供 agent/用户查看
    summary = {
        "id": submission["id"],
        "status": submission.get("status"),
        "score": submission.get("score"),
        "language": submission.get("language"),
        "submit_time": submission.get("submit_time"),
        "time_used_ms": submission.get("time_used_ms"),
        "memory_used_kb": submission.get("memory_used_kb"),
        "progress_type": submission.get("progress_type"),
        "code_file": str(code_path),
        "archive": str(archive_path) if archive_path else None,
        "testcases": [
            {
                "testcase": tc.get("testcase"),
                "status": tc.get("status"),
                "score": tc.get("score"),
                "time_ms": tc.get("time_ms"),
                "spj": tc.get("spj", {}),
            }
            for tc in submission.get("testcases", [])
        ],
    }
    log(json.dumps(summary, ensure_ascii=False, indent=2))


def query_contest_submissions(
    session: requests.Session,
    api_base: str,
    contest_id: int,
    take_count: int = 20,
) -> list[dict[str, Any]]:
    """List the current user's submissions in a contest (newest first)."""
    response = request_json(
        session,
        api_base,
        "POST",
        "contest/play/querySubmissions",
        payload={"locale": "zh_CN", "contestId": contest_id, "takeCount": take_count},
    )
    submissions = response.get("submissions")
    return submissions if isinstance(submissions, list) else []


def cmd_list(args: argparse.Namespace, session: requests.Session) -> int:
    submissions = query_contest_submissions(session, args.api_base, args.contest_id, args.list)
    if not submissions:
        log("no submissions found")
        return 0
    lines = [
        "| 提交 | 状态 | 总分 | 语言 | 时间 | 题目 |",
        "|---|---:|---:|---|---|---|",
    ]
    for sub in submissions:
        log(
            "| #{id} | {status} | {score} | {lang} | {time} | {title} |".format(
                id=sub.get("id"),
                status=sub.get("status"),
                score=sub.get("displayScore") if sub.get("displayScore") is not None else "-",
                lang=sub.get("codeLanguage"),
                time=sub.get("submitTime"),
                title=(sub.get("problemTitle") or "")[:40],
            )
        )
    return 0


def archive_submission_id(
    session: requests.Session,
    args: argparse.Namespace,
    submission_id: int,
) -> dict[str, Any] | None:
    """Fetch one submission's detail, archive it and print its summary."""
    detail = request_json(
        session,
        args.api_base,
        "POST",
        "submission/getSubmissionDetail",
        payload={"submissionId": str(submission_id), "locale": "zh_CN"},
    )
    submission = normalize_submission(detail)
    archive_and_report(args, submission, Path(f"#{submission_id}"))
    return submission


def cmd_monitor(args: argparse.Namespace, session: requests.Session) -> int:
    """Watch for new submissions; archive each one when it reaches a terminal state.

    Starts from whatever is currently in the contest submission list; only
    submissions that appear after startup (or change status afterwards) are
    reported/archived, so re-running the monitor does not duplicate archives.
    """
    log(f"monitoring contest #{args.contest_id} every {args.poll_seconds:g}s "
        f"(timeout {args.timeout_seconds:g}s)")
    known: dict[int, dict[str, Any]] = {}
    deadline = time.monotonic() + args.timeout_seconds
    first_round = True
    while time.monotonic() < deadline:
        try:
            submissions = query_contest_submissions(
                session, args.api_base, args.contest_id
            )
        except XpuojError as exc:
            log(f"query failed: {exc}; retrying next round")
            time.sleep(args.poll_seconds)
            continue
        for sub in submissions:
            sid = sub.get("id")
            status = sub.get("status")
            if not isinstance(sid, int):
                continue
            entry = known.get(sid)
            if entry is None:
                entry = {"last_status": status, "archived": False}
                known[sid] = entry
                if first_round:
                    # 基线轮：只记录当前列表，不打印不归档（避免重复归档历史提交）
                    entry["archived"] = status in TERMINAL_STATUSES
                    continue
                log(f"new submission #{sid}: {status}")
            elif status != entry["last_status"]:
                log(f"submission #{sid}: {entry['last_status']} -> {status}")
                entry["last_status"] = status
            if (
                status in TERMINAL_STATUSES
                and not entry["archived"]
                and status != "Canceled"
            ):
                try:
                    archive_submission_id(session, args, sid)
                    entry["archived"] = True
                except XpuojError as exc:
                    log(f"archive #{sid} failed: {exc}; will retry next round")
        first_round = False
        time.sleep(args.poll_seconds)
    log("monitor timeout reached")
    return 0


def main() -> int:
    load_env_file(ENV_FILE)
    args = parse_args()

    if args.cancel:
        session = requests.Session()
        token = authenticate(session, args.api_base)
        session.headers.update({"Authorization": f"Bearer {token}"})
        cancel_submission(session, args.api_base, args.cancel)
        return 0

    if args.list is not None:
        session = requests.Session()
        token = authenticate(session, args.api_base)
        session.headers.update({"Authorization": f"Bearer {token}"})
        return cmd_list(args, session)

    if args.monitor:
        session = requests.Session()
        token = authenticate(session, args.api_base)
        session.headers.update({"Authorization": f"Bearer {token}"})
        return cmd_monitor(args, session)

    if args.watch_id:
        session = requests.Session()
        token = authenticate(session, args.api_base)
        session.headers.update({"Authorization": f"Bearer {token}"})
        log(f"watching existing submission #{args.watch_id}")
        submission = wait_for_submission(
            session,
            args.api_base,
            args.watch_id,
            args.poll_seconds,
            args.timeout_seconds,
        )
        archive_and_report(args, submission, Path("(watched submission)"))
        return 0

    if args.code is None:
        print("error: code file is required for submission (or use --watch/--cancel)",
              file=sys.stderr)
        return 2
    if not args.code.is_file():
        print(f"Code file does not exist: {args.code}", file=sys.stderr)
        return 2
    code = args.code.read_text(encoding="utf-8")
    if not code.strip():
        print("Code file is empty", file=sys.stderr)
        return 2

    log(f"target: contest #{args.contest_id}, problem #{args.problem_order}")
    log(f"language: {args.language}")
    log(f"code: {args.code} ({len(code.encode('utf-8'))} bytes)")
    if not args.submit:
        log("dry-run: no submission created; use --submit to submit")
        return 0

    session = requests.Session()
    token = authenticate(session, args.api_base)
    session.headers.update({"Authorization": f"Bearer {token}"})
    response = request_json(
        session,
        args.api_base,
        "POST",
        "contest/play/submit",
        payload={
            "contestId": args.contest_id,
            "problemOrder": args.problem_order,
            "content": {
                "language": args.language,
                "code": code,
                "skipSamples": args.skip_samples,
                "compileAndRunOptions": {},
            },
        },
    )
    submission_id = response.get("submissionId")
    if not isinstance(submission_id, int):
        raise XpuojError(f"Submission response has no integer submissionId: {response}")
    log(f"created submission #{submission_id}")

    submission = wait_for_submission(
        session,
        args.api_base,
        submission_id,
        args.poll_seconds,
        args.timeout_seconds,
    )
    archive_and_report(args, submission, args.code)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (XpuojError, TimeoutError, requests.RequestException) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
