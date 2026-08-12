#!/usr/bin/env python3
"""Validate a plan-tasks execution tracker using only the standard library."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


TASK_SCHEMA = "plan-tasks-tracker/v1"
PLAN_SCHEMA = "rumelt-task-plan/v1"
PLAN_STATUSES = {"APPROVED", "READY_FOR_REVIEW"}
EXECUTION_STATUSES = {"IN_PROGRESS", "PAUSED", "COMPLETED", "CANCELLED"}
REQUIRED_META = (
    "task_schema",
    "plan_schema",
    "plan_id",
    "plan_version",
    "plan_status",
    "approved_by",
    "approved_scope",
    "execution_status",
    "created_at",
    "updated_at",
)
REQUIRED_SECTIONS = (
    "任务目标与批准快照",
    "变更范围",
    "任务明细",
    "发现与变更记录",
    "完成标准",
)
SNAPSHOT_LABELS = ("目标", "主要诊断", "指导方针", "近端目标", "主动不做", "批准依据")
SCOPE_LABELS = ("涉及模块或目录", "预计影响文件数", "允许的工具与权限", "禁止或需另行批准")
EMPTY_VALUES = {"", "-", "--", "---", "待定", "待补", "待确认", "tbd", "todo", "unknown", "?"}
TASK_LINE = re.compile(r"^\s*-\s*\[([ xX])\]\s+(.+?)\s*$")
TASK_FIELDS = re.compile(
    r"^(T-\d+)\s*\|\s*(A-\d+)\s*\|\s*(.+?)\s*\|\s*"
    r"acceptance\s*:\s*(.+?)(?:\s*\|\s*cancelled\s*:\s*(.+))?$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    message: str
    line: Optional[int] = None


def add(issues: List[Issue], severity: str, code: str, message: str, line: Optional[int] = None) -> None:
    issues.append(Issue(severity, code, message, line))


def clean_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1].strip()
    return value


def parse_frontmatter(lines: Sequence[str], issues: List[Issue]) -> Tuple[Dict[str, str], int]:
    if not lines or lines[0].strip() != "---":
        add(issues, "ERROR", "FM001", "Document must start with YAML frontmatter.", 1)
        return {}, 0

    end = next((index for index in range(1, len(lines)) if lines[index].strip() == "---"), None)
    if end is None:
        add(issues, "ERROR", "FM002", "Frontmatter has no closing --- marker.", 1)
        return {}, 0

    metadata: Dict[str, str] = {}
    for index in range(1, end):
        raw = lines[index]
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if ":" not in raw:
            add(issues, "ERROR", "FM003", "Frontmatter entries must use key: value.", index + 1)
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        if not key:
            add(issues, "ERROR", "FM004", "Frontmatter key cannot be empty.", index + 1)
            continue
        if key in metadata:
            add(issues, "ERROR", "FM005", f"Duplicate frontmatter key: {key}.", index + 1)
        metadata[key] = clean_value(value)
    return metadata, end + 1


def parse_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
        return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))
    except ValueError:
        return False


def section_ranges(lines: Sequence[str], body_start: int, issues: List[Issue]) -> Dict[str, Tuple[int, int]]:
    headings: List[Tuple[str, int]] = []
    for index in range(body_start, len(lines)):
        match = re.match(r"^##\s+(.+?)\s*$", lines[index])
        if match:
            headings.append((match.group(1).strip(), index))

    found = [name for name, _ in headings if name in REQUIRED_SECTIONS]
    if found != list(REQUIRED_SECTIONS):
        add(
            issues,
            "ERROR",
            "SEC001",
            "Required H2 sections are missing, renamed, duplicated, or out of order: "
            + " -> ".join(REQUIRED_SECTIONS),
        )

    ranges: Dict[str, Tuple[int, int]] = {}
    for pos, (name, start) in enumerate(headings):
        if name not in REQUIRED_SECTIONS:
            continue
        end = headings[pos + 1][1] if pos + 1 < len(headings) else len(lines)
        ranges[name] = (start + 1, end)
    return ranges


def require_labels(
    lines: Sequence[str],
    section: Optional[Tuple[int, int]],
    labels: Sequence[str],
    issues: List[Issue],
    code: str,
) -> None:
    if section is None:
        return
    start, end = section
    block = "\n".join(lines[start:end])
    for label in labels:
        if not re.search(rf"^\s*-\s*{re.escape(label)}\s*[：:]\s*\S", block, re.MULTILINE):
            add(issues, "ERROR", code, f"Section is missing a non-empty '{label}' field.", start + 1)


def validate_metadata(metadata: Dict[str, str], issues: List[Issue]) -> List[str]:
    for key in REQUIRED_META:
        if key not in metadata:
            add(issues, "ERROR", "META001", f"Missing required frontmatter field: {key}.")
        elif metadata[key].strip().lower() in EMPTY_VALUES:
            add(issues, "ERROR", "META002", f"Frontmatter field is empty or a placeholder: {key}.")

    if metadata.get("task_schema") not in {None, TASK_SCHEMA}:
        add(issues, "ERROR", "META003", f"task_schema must be {TASK_SCHEMA}.")
    if metadata.get("plan_schema") not in {None, PLAN_SCHEMA}:
        add(issues, "ERROR", "META004", f"plan_schema must be {PLAN_SCHEMA}.")

    plan_status = metadata.get("plan_status")
    execution_status = metadata.get("execution_status")
    if plan_status and plan_status not in PLAN_STATUSES:
        add(issues, "ERROR", "STATE001", f"Invalid plan_status: {plan_status}.")
    if execution_status and execution_status not in EXECUTION_STATUSES:
        add(issues, "ERROR", "STATE002", f"Invalid execution_status: {execution_status}.")

    if plan_status == "READY_FOR_REVIEW" and execution_status != "PAUSED":
        add(issues, "ERROR", "STATE003", "READY_FOR_REVIEW requires execution_status PAUSED.")
    if execution_status in {"IN_PROGRESS", "COMPLETED"}:
        if plan_status != "APPROVED":
            add(issues, "ERROR", "STATE004", f"{execution_status} requires plan_status APPROVED.")
        if metadata.get("approved_by") != "user":
            add(issues, "ERROR", "STATE005", f"{execution_status} requires approved_by: user.")

    version = metadata.get("plan_version", "")
    if version and (not version.isdigit() or int(version) < 1):
        add(issues, "ERROR", "META005", "plan_version must be a positive integer.")
    for field in ("created_at", "updated_at"):
        value = metadata.get(field, "")
        if value and not parse_date(value):
            add(issues, "ERROR", "META006", f"{field} must use ISO YYYY-MM-DD.")
    if parse_date(metadata.get("created_at", "")) and parse_date(metadata.get("updated_at", "")):
        if metadata["updated_at"] < metadata["created_at"]:
            add(issues, "ERROR", "META007", "updated_at cannot be earlier than created_at.")

    raw_scope = metadata.get("approved_scope", "")
    scope = [item.strip() for item in raw_scope.split(",") if item.strip()]
    if raw_scope.strip().lower() == "all":
        add(issues, "ERROR", "SCOPE001", "approved_scope must enumerate concrete A-* IDs; 'all' is not allowed.")
        return []
    invalid = [item for item in scope if not re.fullmatch(r"A-\d+", item)]
    if invalid:
        add(issues, "ERROR", "SCOPE002", "approved_scope contains invalid IDs: " + ", ".join(invalid))
    if len(scope) != len(set(scope)):
        add(issues, "ERROR", "SCOPE003", "approved_scope contains duplicate A-* IDs.")
    return scope


def validate_tasks(
    lines: Sequence[str],
    section: Optional[Tuple[int, int]],
    approved_scope: Sequence[str],
    execution_status: str,
    issues: List[Issue],
) -> None:
    if section is None:
        return
    start, end = section
    seen: set[str] = set()
    active_unchecked = 0
    task_count = 0

    for index in range(start, end):
        match = TASK_LINE.match(lines[index])
        if not match:
            continue
        task_count += 1
        checked = match.group(1).lower() == "x"
        body = match.group(2)
        cancelled = "cancelled:" in body.lower() or "已取消" in body
        stripped = body.replace("~~", "").strip()
        fields = TASK_FIELDS.match(stripped)
        if not fields:
            add(
                issues,
                "ERROR",
                "TASK001",
                "Task must use: T-* | A-* | action | acceptance: observable condition, with optional cancelled: reason.",
                index + 1,
            )
            continue

        task_id, action_id, action, acceptance, cancel_reason = fields.groups()
        if task_id in seen:
            add(issues, "ERROR", "TASK002", f"Duplicate task ID: {task_id}.", index + 1)
        seen.add(task_id)
        if action_id not in approved_scope:
            add(issues, "ERROR", "TASK003", f"{task_id} maps to unapproved action {action_id}.", index + 1)
        if action.strip().lower() in EMPTY_VALUES:
            add(issues, "ERROR", "TASK004", f"{task_id} has an empty or placeholder action.", index + 1)
        if acceptance.strip().lower() in EMPTY_VALUES:
            add(issues, "ERROR", "TASK005", f"{task_id} has an empty or placeholder acceptance condition.", index + 1)

        if cancelled:
            if checked:
                add(issues, "ERROR", "TASK006", f"Cancelled task {task_id} must not be checked.", index + 1)
            if "~~" not in body or not (cancel_reason and cancel_reason.strip()):
                add(issues, "ERROR", "TASK007", f"Cancelled task {task_id} needs strikethrough and a reason.", index + 1)
        elif not checked:
            active_unchecked += 1

    if task_count == 0:
        add(issues, "ERROR", "TASK008", "任务明细 must contain at least one checkbox task.", start + 1)
    if execution_status == "COMPLETED" and active_unchecked:
        add(issues, "ERROR", "TASK009", f"COMPLETED tracker has {active_unchecked} active unchecked task(s).")


def validate_history_and_completion(
    lines: Sequence[str], ranges: Dict[str, Tuple[int, int]], execution_status: str, issues: List[Issue]
) -> None:
    history = ranges.get("发现与变更记录")
    if history:
        block = lines[history[0] : history[1]]
        if not any(re.match(r"^\s*-\s*\d{4}-\d{2}-\d{2}\s*\|", line) for line in block):
            add(issues, "ERROR", "HIST001", "Change log needs at least one '- YYYY-MM-DD | ...' entry.", history[0] + 1)

    completion = ranges.get("完成标准")
    if completion:
        block = lines[completion[0] : completion[1]]
        criteria = [line for line in block if re.match(r"^\s*-\s+(?!\[).+", line)]
        if not criteria:
            add(issues, "ERROR", "DONE001", "完成标准 needs at least one observable bullet criterion.", completion[0] + 1)
        if execution_status == "COMPLETED" and not any(
            re.search(r"证据|通过|verified|passed|evidence", line, re.IGNORECASE) for line in block
        ):
            add(issues, "WARN", "DONE002", "COMPLETED tracker should record completion evidence.", completion[0] + 1)


def validate(text: str) -> List[Issue]:
    lines = text.splitlines()
    issues: List[Issue] = []
    metadata, body_start = parse_frontmatter(lines, issues)
    approved_scope = validate_metadata(metadata, issues)
    ranges = section_ranges(lines, body_start, issues)
    require_labels(lines, ranges.get("任务目标与批准快照"), SNAPSHOT_LABELS, issues, "SNAP001")
    require_labels(lines, ranges.get("变更范围"), SCOPE_LABELS, issues, "RANGE001")
    validate_tasks(lines, ranges.get("任务明细"), approved_scope, metadata.get("execution_status", ""), issues)
    validate_history_and_completion(lines, ranges, metadata.get("execution_status", ""), issues)
    return issues


def read_document(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8-sig")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", help="Tracker Markdown path, or - for stdin")
    args = parser.parse_args(argv)

    try:
        text = read_document(args.document)
    except (OSError, UnicodeError) as exc:
        print(f"ERROR [IO001] {exc}")
        return 2

    issues = validate(text)
    for issue in issues:
        location = f" line {issue.line}" if issue.line else ""
        print(f"{issue.severity} [{issue.code}]{location}: {issue.message}")

    errors = sum(issue.severity == "ERROR" for issue in issues)
    warnings = sum(issue.severity == "WARN" for issue in issues)
    if errors:
        print(f"INVALID: {errors} error(s), {warnings} warning(s).")
        return 1
    print(f"VALID: 0 errors, {warnings} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
