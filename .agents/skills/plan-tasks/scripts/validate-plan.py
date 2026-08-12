#!/usr/bin/env python3
"""Validate a Rumelt task-plan Markdown document using only the standard library."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


SCHEMA = "rumelt-task-plan/v1"
ALLOWED_STATUSES = {"DRAFT", "READY_FOR_REVIEW", "APPROVED"}
ALLOWED_MODES = {"full", "compact", "diagnostic-exploration"}

REQUIRED_SECTIONS = (
    "任务事实与边界",
    "关键挑战诊断",
    "指导方针",
    "近端目标与杠杆点",
    "连贯行动",
    "链式弱环节与风险",
    "假设与失败信号",
    "决策与批准",
)

ACTION_FIELDS = (
    "id",
    "action",
    "addresses",
    "implements",
    "input",
    "output",
    "dependencies",
    "permissions",
    "acceptance",
)

COLUMN_ALIASES = {
    "id": {"id", "编号", "行动id", "步骤id", "行动编号", "步骤编号"},
    "action": {"action", "行动", "动作", "步骤", "任务"},
    "addresses": {
        "addresses",
        "addresseschallenge",
        "解决障碍",
        "解决哪个障碍",
        "对应障碍",
        "关键障碍",
    },
    "implements": {
        "implements",
        "implementspolicy",
        "落实方针",
        "落实哪条方针",
        "对应方针",
        "指导方针",
    },
    "input": {"input", "inputs", "输入"},
    "output": {"output", "outputs", "输出", "交付物"},
    "dependencies": {"dependencies", "dependency", "depends", "依赖", "前置依赖"},
    "permissions": {"permissions", "permission", "权限", "所需权限"},
    "acceptance": {
        "acceptance",
        "acceptancecriteria",
        "验收",
        "验收标准",
        "通过标准",
    },
}

META_KEY_ALIASES = {
    "planschema": "plan_schema",
    "方案schema": "plan_schema",
    "方案模式": "mode",
    "mode": "mode",
    "模式": "mode",
    "status": "status",
    "状态": "status",
    "当前状态": "status",
    "approvedby": "approved_by",
    "批准者": "approved_by",
    "审批者": "approved_by",
    "批准人": "approved_by",
    "审批主体": "approved_by",
}

EMPTY_VALUES = {"", "-", "--", "---", "—", "–"}
PLACEHOLDERS = {
    "tbd",
    "todo",
    "待定",
    "待补",
    "待填写",
    "待确认",
    "unknown",
    "placeholder",
    "?",
    "？？",
}
NO_NON_GOAL_VALUES = {
    "无",
    "没有",
    "暂无",
    "none",
    "nothing",
    "n/a",
    "na",
    "notapplicable",
}


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    message: str
    line: Optional[int] = None

    def render(self) -> str:
        location = f" line {self.line}" if self.line is not None else ""
        return f"[{self.severity}] {self.code}{location}: {self.message}"


@dataclass(frozen=True)
class Heading:
    line_index: int
    level: int
    title: str


@dataclass(frozen=True)
class Section:
    name: str
    heading_line: int
    content_start: int
    content_end: int
    lines: Sequence[str]


@dataclass
class ValidationResult:
    issues: List[Issue]

    @property
    def errors(self) -> List[Issue]:
        return [issue for issue in self.issues if issue.severity == "ERROR"]

    @property
    def warnings(self) -> List[Issue]:
        return [issue for issue in self.issues if issue.severity == "WARN"]


def _strip_inline_comment(value: str) -> str:
    value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value.strip()


def _normalize_token(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"[`*_~]", "", value)
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", value.casefold())


def _clean_value(value: str) -> str:
    value = re.sub(r"<!--.*?-->", "", value)
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.IGNORECASE)
    value = value.strip().strip("|").strip()
    wrapper = re.match(r"^(?:\*\*|__|~~|`)(.*?)(?:\*\*|__|~~|`)$", value)
    return (wrapper.group(1) if wrapper else value).strip()


def _is_empty(value: str) -> bool:
    return _clean_value(value).casefold() in EMPTY_VALUES


def _is_placeholder(value: str) -> bool:
    return _normalize_token(_clean_value(value)) in {
        _normalize_token(item) for item in PLACEHOLDERS
    }


def _is_meaningful(value: str) -> bool:
    cleaned = _clean_value(value)
    normalized = _normalize_token(cleaned)
    if cleaned.casefold() in EMPTY_VALUES or not normalized:
        return False
    return normalized not in {_normalize_token(item) for item in PLACEHOLDERS}


def _code_line_mask(lines: Sequence[str]) -> List[bool]:
    mask: List[bool] = []
    fence: Optional[str] = None
    for line in lines:
        stripped = line.lstrip()
        marker_match = re.match(r"(`{3,}|~{3,})", stripped)
        if marker_match:
            marker = marker_match.group(1)
            marker_kind = marker[0]
            mask.append(True)
            if fence is None:
                fence = marker_kind
            elif fence == marker_kind:
                fence = None
            continue
        mask.append(fence is not None)
    return mask


def _parse_frontmatter(lines: Sequence[str]) -> Tuple[Dict[str, str], Optional[int], bool]:
    if not lines or lines[0].strip() != "---":
        return {}, None, False
    closing = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing = index
            break
    if closing is None:
        return {}, None, True

    metadata: Dict[str, str] = {}
    for line in lines[1:closing]:
        match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*?)\s*$", line)
        if match:
            metadata[match.group(1).casefold()] = _strip_inline_comment(match.group(2))
    return metadata, closing, True


def _split_table_row(line: str) -> List[str]:
    text = line.strip()
    cells: List[str] = []
    current: List[str] = []
    escaped = False
    for char in text:
        if escaped:
            current.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    current.append("\\" if escaped else "")
    cells.append("".join(current).strip())
    if text.startswith("|") and cells and not cells[0]:
        cells.pop(0)
    if text.endswith("|") and cells and not cells[-1]:
        cells.pop()
    return cells


def _is_table_separator(line: str) -> bool:
    cells = _split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def _metadata_key(value: str) -> Optional[str]:
    return META_KEY_ALIASES.get(_normalize_token(value))


def _parse_document_metadata(
    lines: Sequence[str], code_mask: Sequence[bool]
) -> Tuple[Dict[str, str], Dict[str, int]]:
    metadata: Dict[str, str] = {}
    locations: Dict[str, int] = {}
    scalar_pattern = re.compile(
        r"^\s*(?:[-*+]\s+)?(?:\*\*|__)?([^:：]+?)(?:\*\*|__)?\s*[:：]\s*(.+?)\s*$"
    )
    for index, line in enumerate(lines):
        if code_mask[index]:
            continue
        match = scalar_pattern.match(line)
        if match:
            key = _metadata_key(match.group(1))
            if key and key not in metadata:
                metadata[key] = _clean_value(match.group(2))
                locations[key] = index + 1
        if "|" in line:
            cells = _split_table_row(line)
            if len(cells) == 2:
                key = _metadata_key(cells[0])
                if key and key not in metadata and not _is_table_separator(line):
                    metadata[key] = _clean_value(cells[1])
                    locations[key] = index + 1
    return metadata, locations


def _canonical_heading(title: str) -> str:
    title = re.sub(r"<[^>]+>", "", title)
    title = re.sub(r"[`*_~]", "", title).strip()
    numbering = (
        r"^(?:(?:\d+(?:\.\d+)*)[.、)）:]?\s*|"
        r"[（(]?[一二三四五六七八九十百]+[）)、.)：:]?\s*)"
    )
    title = re.sub(numbering, "", title).strip().strip("：:")
    collapsed = re.sub(r"\s+", "", title)
    for required in REQUIRED_SECTIONS:
        if collapsed == re.sub(r"\s+", "", required):
            return required
    return title


def _extract_sections(
    lines: Sequence[str], code_mask: Sequence[bool], issues: List[Issue]
) -> Dict[str, Section]:
    headings: List[Heading] = []
    for index, line in enumerate(lines):
        if code_mask[index]:
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if match:
            headings.append(Heading(index, len(match.group(1)), _canonical_heading(match.group(2))))

    sections: Dict[str, Section] = {}
    for position, heading in enumerate(headings):
        if heading.title not in REQUIRED_SECTIONS:
            continue
        if heading.title in sections:
            issues.append(
                Issue(
                    "ERROR",
                    "SECTION_DUPLICATE",
                    f"必需章节“{heading.title}”出现多次。",
                    heading.line_index + 1,
                )
            )
            continue
        end = len(lines)
        for later in headings[position + 1 :]:
            if later.level <= heading.level:
                end = later.line_index
                break
        sections[heading.title] = Section(
            heading.title,
            heading.line_index + 1,
            heading.line_index + 1,
            end,
            lines[heading.line_index + 1 : end],
        )

    for name in REQUIRED_SECTIONS:
        section = sections.get(name)
        if section is None:
            issues.append(Issue("ERROR", "SECTION_MISSING", f"缺少必需章节“{name}”。"))
        elif not any(_is_meaningful(line) and not line.lstrip().startswith("#") for line in section.lines):
            issues.append(
                Issue(
                    "ERROR",
                    "SECTION_EMPTY",
                    f"章节“{name}”没有实质内容。",
                    section.heading_line,
                )
            )
    return sections


def _find_labeled_value(
    section: Section, label_pattern: str
) -> Tuple[bool, bool, Optional[int]]:
    pattern = re.compile(label_pattern, flags=re.IGNORECASE)
    for offset, raw_line in enumerate(section.lines):
        cleaned = re.sub(r"^\s*(?:[-*+]\s+|#{1,6}\s+)", "", raw_line)
        cleaned = re.sub(r"[`*_~]", "", cleaned).strip()
        match = pattern.search(cleaned)
        if not match:
            continue
        line_number = section.content_start + offset + 1
        suffix = re.sub(r"^[\s:：—–-]+", "", cleaned[match.end() :]).strip()
        if _is_meaningful(suffix):
            return True, True, line_number
        for following in section.lines[offset + 1 :]:
            if re.match(r"^#{1,6}\s+", following):
                break
            stripped = re.sub(r"^\s*[-*+]\s+", "", following).strip()
            if not stripped:
                continue
            return True, _is_meaningful(stripped), line_number
        return True, False, line_number
    return False, False, None


def _validate_non_goals(section: Optional[Section], issues: List[Issue]) -> None:
    if section is None:
        return
    marker = re.compile(
        r"主动不做(?:项)?|明确不做|非目标|不做项|non[- ]?goals?|out\s+of\s+scope|will\s+not\s+do",
        flags=re.IGNORECASE,
    )
    for offset, raw_line in enumerate(section.lines):
        cleaned = re.sub(r"^\s*(?:[-*+]\s+|#{1,6}\s+)", "", raw_line)
        cleaned = re.sub(r"[`*_~]", "", cleaned).strip()
        match = marker.search(cleaned)
        if not match:
            continue
        suffix = re.sub(r"^[\s:：—–-]+", "", cleaned[match.end() :]).strip()
        candidates = [suffix] if suffix else []
        for following in section.lines[offset + 1 :]:
            if re.match(r"^#{1,6}\s+", following):
                break
            if not following.strip():
                if candidates:
                    break
                continue
            candidates.append(re.sub(r"^\s*[-*+]\s+", "", following).strip())
        for candidate in candidates:
            normalized = _normalize_token(candidate)
            if _is_meaningful(candidate) and normalized not in {
                _normalize_token(item) for item in NO_NON_GOAL_VALUES
            }:
                return
    issues.append(
        Issue(
            "ERROR",
            "NON_GOAL_MISSING",
            "“指导方针”必须至少列出一个具体的主动不做项；“无/待定”不算取舍。",
            section.heading_line,
        )
    )


def _column_field(header: str) -> Optional[str]:
    normalized = _normalize_token(header)
    for field, aliases in COLUMN_ALIASES.items():
        normalized_aliases = {_normalize_token(alias) for alias in aliases}
        if normalized in normalized_aliases:
            return field
        if field != "id" and any(
            len(alias) >= 4 and alias in normalized for alias in normalized_aliases
        ):
            return field
    return None


def _table_candidates(section: Section) -> List[Tuple[int, List[str], List[List[str]]]]:
    candidates: List[Tuple[int, List[str], List[List[str]]]] = []
    lines = section.lines
    index = 0
    while index + 1 < len(lines):
        if "|" not in lines[index] or not _is_table_separator(lines[index + 1]):
            index += 1
            continue
        header = _split_table_row(lines[index])
        rows: List[List[str]] = []
        cursor = index + 2
        while cursor < len(lines) and "|" in lines[cursor] and lines[cursor].strip():
            if not _is_table_separator(lines[cursor]):
                rows.append(_split_table_row(lines[cursor]))
            cursor += 1
        candidates.append((index, header, rows))
        index = max(cursor, index + 2)
    return candidates


def _validate_action_table(section: Optional[Section], issues: List[Issue]) -> None:
    if section is None:
        return
    tables = _table_candidates(section)
    if not tables:
        issues.append(
            Issue(
                "ERROR",
                "ACTION_TABLE_MISSING",
                "“连贯行动”必须包含 Markdown 行动表。",
                section.heading_line,
            )
        )
        return

    scored: List[Tuple[int, int, List[str], List[List[str]]]] = []
    for offset, header, rows in tables:
        score = sum(1 for cell in header if _column_field(cell))
        scored.append((score, offset, header, rows))
    _, offset, header, rows = max(scored, key=lambda item: item[0])

    field_indexes: Dict[str, int] = {}
    for index, cell in enumerate(header):
        field = _column_field(cell)
        if field and field not in field_indexes:
            field_indexes[field] = index

    missing = [field for field in ACTION_FIELDS if field not in field_indexes]
    if missing:
        issues.append(
            Issue(
                "ERROR",
                "ACTION_COLUMNS_MISSING",
                "行动表缺少字段：" + ", ".join(missing) + "。",
                section.content_start + offset + 1,
            )
        )
    if not rows:
        issues.append(
            Issue(
                "ERROR",
                "ACTION_ROWS_MISSING",
                "行动表至少需要一条行动。",
                section.content_start + offset + 1,
            )
        )
        return

    seen_ids = set()
    for row_number, row in enumerate(rows, start=1):
        absolute_line = section.content_start + offset + 2 + row_number + 1
        for field in ACTION_FIELDS:
            column = field_indexes.get(field)
            if column is None:
                continue
            value = row[column] if column < len(row) else ""
            if _is_empty(value):
                issues.append(
                    Issue(
                        "ERROR",
                        "ACTION_CELL_EMPTY",
                        f"行动表第 {row_number} 条的 {field} 不能为空；无依赖或无额外权限时请显式写“无”。",
                        absolute_line,
                    )
                )
            elif _is_placeholder(value):
                issues.append(
                    Issue(
                        "WARN",
                        "ACTION_CELL_PLACEHOLDER",
                        f"行动表第 {row_number} 条的 {field} 仍是占位值“{_clean_value(value)}”。",
                        absolute_line,
                    )
                )
        id_column = field_indexes.get("id")
        if id_column is not None and id_column < len(row):
            action_id = _clean_value(row[id_column]).casefold()
            if action_id and action_id not in EMPTY_VALUES:
                if action_id in seen_ids:
                    issues.append(
                        Issue(
                            "ERROR",
                            "ACTION_ID_DUPLICATE",
                            f"行动 ID“{_clean_value(row[id_column])}”重复。",
                            absolute_line,
                        )
                    )
                seen_ids.add(action_id)


def _validate_hypothesis_section(section: Optional[Section], issues: List[Issue]) -> None:
    if section is None:
        return
    checks = (
        (r"假设|hypothesis", "HYPOTHESIS_MISSING", "必须明确写出当前战略假设。"),
        (
            r"失败信号|失效信号|failure\s+signal",
            "FAILURE_SIGNAL_MISSING",
            "必须明确写出可观察的失败信号。",
        ),
    )
    for pattern, code, message in checks:
        found, has_value, line = _find_labeled_value(section, pattern)
        if not found or not has_value:
            issues.append(Issue("ERROR", code, message, line or section.heading_line))


def _looks_like_user_approval(section: Optional[Section]) -> bool:
    if section is None:
        return False
    text = "\n".join(section.lines)
    patterns = (
        r"用户(?:已|明确)?批准\s*[:：]?\s*(?:是|已批准|yes|approved)",
        r"(?:批准者|审批者|批准人|审批主体)\s*[:：]\s*(?:用户|用户本人|human\s+user|requesting\s+user)",
    )
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _is_user_actor(value: str) -> bool:
    normalized = _normalize_token(value)
    accepted = {
        "user",
        "humanuser",
        "requestinguser",
        "用户",
        "用户本人",
        "发起用户",
        "请求用户",
        "人类用户",
    }
    return normalized in accepted


def _is_agent_actor(value: str) -> bool:
    normalized = _normalize_token(value)
    return any(
        marker in normalized
        for marker in ("agent", "assistant", "codex", "claude", "模型", "代理", "人工智能")
    ) or normalized == "ai"


def _claims_execution(lines: Sequence[str], code_mask: Sequence[bool]) -> Optional[int]:
    patterns = (
        r"(?:执行状态|execution[_ ]?status)\s*[:：]\s*(?:执行中|正在执行|已执行|开始执行|executing|in[_ -]?progress|running|executed|done)",
        r"(?:现已|已经|正在|将立即|立即|接下来(?:将)?|现在(?:开始)?)\s*(?:开始)?执行",
        r"\b(?:ready\s+to\s+execute|will\s+execute|executing\s+now|proceed(?:ing)?\s+to\s+execution|execution\s+(?:has\s+)?started)\b",
    )
    negative = re.compile(
        r"不得执行|禁止执行|不可执行|不应执行|不执行|尚未执行|未批准|等待(?:用户)?批准|"
        r"暂停执行|停止执行|仅规划|plan-only|do\s+not\s+execute|must\s+not\s+execute|"
        r"will\s+not\s+execute|not\s+execute|await(?:ing)?\s+approval|pending\s+approval|no\s+execution",
        flags=re.IGNORECASE,
    )
    for index, line in enumerate(lines):
        if code_mask[index] or negative.search(line):
            continue
        if any(re.search(pattern, line, flags=re.IGNORECASE) for pattern in patterns):
            return index + 1
    return None


def _validate_metadata_and_approval(
    lines: Sequence[str],
    code_mask: Sequence[bool],
    frontmatter: Mapping[str, str],
    doc_metadata: Mapping[str, str],
    doc_locations: Mapping[str, int],
    sections: Mapping[str, Section],
    issues: List[Issue],
) -> None:
    values: Dict[str, str] = {}
    for key in ("plan_schema", "status", "mode"):
        front_value = frontmatter.get(key)
        doc_value = doc_metadata.get(key)
        if front_value:
            values[key] = front_value
            if doc_value:
                left = front_value.upper() if key == "status" else front_value.casefold()
                right = doc_value.upper() if key == "status" else doc_value.casefold()
                if left != right:
                    issues.append(
                        Issue(
                            "ERROR",
                            "META_CONFLICT",
                            f"frontmatter 中的 {key}={front_value} 与文档中的 {key}={doc_value} 冲突。",
                            doc_locations.get(key),
                        )
                    )
        elif doc_value:
            values[key] = doc_value
            issues.append(
                Issue(
                    "WARN",
                    "META_DOCUMENT_FALLBACK",
                    f"{key} 来自文档元数据；建议写入 YAML frontmatter。",
                    doc_locations.get(key),
                )
            )
        else:
            issues.append(Issue("ERROR", "META_MISSING", f"缺少元数据 {key}。"))

    schema = values.get("plan_schema")
    if schema and schema != SCHEMA:
        issues.append(
            Issue("ERROR", "META_SCHEMA_INVALID", f"plan_schema 必须是 {SCHEMA}，当前为 {schema}。")
        )
    status = values.get("status", "").upper()
    if status and status not in ALLOWED_STATUSES:
        issues.append(
            Issue(
                "ERROR",
                "META_STATUS_INVALID",
                "status 必须是 DRAFT、READY_FOR_REVIEW 或 APPROVED。",
            )
        )
    mode = values.get("mode", "").casefold()
    if mode and mode not in ALLOWED_MODES:
        issues.append(
            Issue(
                "ERROR",
                "META_MODE_INVALID",
                "mode 必须是 full、compact 或 diagnostic-exploration。",
            )
        )

    approved_by = frontmatter.get("approved_by") or doc_metadata.get("approved_by")
    if approved_by and _is_agent_actor(approved_by):
        issues.append(
            Issue(
                "ERROR",
                "APPROVAL_ACTOR_INVALID",
                "只有用户可以批准方案，AI、Agent、Codex 或 Claude 不得充当批准者。",
                doc_locations.get("approved_by"),
            )
        )

    approval_section = sections.get("决策与批准")
    if status == "APPROVED":
        if approved_by:
            if not _is_user_actor(approved_by):
                issues.append(
                    Issue(
                        "ERROR",
                        "APPROVAL_USER_EVIDENCE_MISSING",
                        f"APPROVED 状态必须记录用户批准；当前批准者为“{approved_by}”。",
                        doc_locations.get("approved_by"),
                    )
                )
        elif not _looks_like_user_approval(approval_section):
            issues.append(
                Issue(
                    "ERROR",
                    "APPROVAL_USER_EVIDENCE_MISSING",
                    "APPROVED 状态必须在 frontmatter 或“决策与批准”中记录用户批准。",
                    approval_section.heading_line if approval_section else None,
                )
            )
    elif approved_by and _is_user_actor(approved_by):
        issues.append(
            Issue(
                "WARN",
                "APPROVAL_STATUS_STALE",
                "已记录用户批准者，但 status 尚未设为 APPROVED；请核对状态。",
                doc_locations.get("approved_by"),
            )
        )

    execution_line = _claims_execution(lines, code_mask)
    if status != "APPROVED" and execution_line is not None:
        issues.append(
            Issue(
                "ERROR",
                "EXECUTION_BEFORE_APPROVAL",
                "方案尚未 APPROVED，却声称正在、已经或将立即执行。请停在规划与审批阶段。",
                execution_line,
            )
        )


def validate_text(text: str) -> ValidationResult:
    lines = text.lstrip("\ufeff").splitlines()
    issues: List[Issue] = []
    code_mask = _code_line_mask(lines)
    frontmatter, closing_line, has_frontmatter = _parse_frontmatter(lines)
    if has_frontmatter and closing_line is None:
        issues.append(Issue("ERROR", "FRONTMATTER_UNCLOSED", "YAML frontmatter 缺少结束分隔线 ---。", 1))
    elif not has_frontmatter:
        issues.append(
            Issue(
                "WARN",
                "FRONTMATTER_MISSING",
                "未找到 YAML frontmatter；仅在正文元数据完整时可以继续校验。",
                1,
            )
        )

    doc_metadata, doc_locations = _parse_document_metadata(lines, code_mask)
    sections = _extract_sections(lines, code_mask, issues)
    _validate_metadata_and_approval(
        lines,
        code_mask,
        frontmatter,
        doc_metadata,
        doc_locations,
        sections,
        issues,
    )
    _validate_non_goals(sections.get("指导方针"), issues)
    _validate_action_table(sections.get("连贯行动"), issues)
    _validate_hypothesis_section(sections.get("假设与失败信号"), issues)
    return ValidationResult(issues)


def _valid_fixture(status: str = "READY_FOR_REVIEW", approved_by: str = "") -> str:
    approval_line = f"approved_by: {approved_by}\n" if approved_by else ""
    approval_body = (
        "- 用户已批准：是\n" if status == "APPROVED" and approved_by == "用户" else "- 等待用户批准；未批准不得执行。\n"
    )
    return f"""---
plan_schema: {SCHEMA}
status: {status}
mode: full
{approval_line}---

# 示例方案

## 任务事实与边界

- 已知事实：需要先形成方案。

## 关键挑战诊断

- 关键障碍：任务边界尚未转化为可追溯行动。

## 指导方针

- 总体方法：先诊断，再设计行动接口。
- 主动不做项：本轮不执行真实任务。

## 近端目标与杠杆点

- 近端目标：形成可验收方案。
- 杠杆点：行动与障碍的追溯关系。

## 连贯行动

| ID | action | addresses | implements | input | output | dependencies | permissions | acceptance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | 整理边界 | 边界不清 | 先诊断 | 用户请求 | 边界清单 | 无 | 只读 | 每项有来源 |

## 链式弱环节与风险

- 弱环节：若诊断错误，后续行动全部失效。

## 假设与失败信号

- 假设：显式追溯可减少范围漂移。
- 失败信号：行动仍无法对应关键障碍。

## 决策与批准

- 当前状态：{status}
{approval_body}"""


def run_self_test() -> int:
    cases: List[Tuple[str, str, Iterable[str], Iterable[str]]] = []
    cases.append(("valid review plan", _valid_fixture(), (), ()))
    cases.append(("valid approved-by-user plan", _valid_fixture("APPROVED", "用户"), (), ()))

    bad_non_goal = _valid_fixture().replace(
        "- 主动不做项：本轮不执行真实任务。", "- 主动不做项：无"
    )
    cases.append(("reject absent non-goal", bad_non_goal, {"NON_GOAL_MISSING"}, ()))

    bad_action = _valid_fixture().replace(
        "| A1 | 整理边界 | 边界不清 | 先诊断 | 用户请求 | 边界清单 | 无 | 只读 | 每项有来源 |",
        "| A1 | 整理边界 | 边界不清 | 先诊断 | 用户请求 |  | 无 | 只读 | 每项有来源 |",
    )
    cases.append(("reject empty action cell", bad_action, {"ACTION_CELL_EMPTY"}, ()))

    early_execution = _valid_fixture().replace(
        "- 等待用户批准；未批准不得执行。", "- 执行状态：执行中"
    )
    cases.append(
        ("reject execution before approval", early_execution, {"EXECUTION_BEFORE_APPROVAL"}, ())
    )

    bad_actor = _valid_fixture("APPROVED", "Codex")
    cases.append(
        (
            "reject agent approval",
            bad_actor,
            {"APPROVAL_ACTOR_INVALID", "APPROVAL_USER_EVIDENCE_MISSING"},
            (),
        )
    )

    failed = 0
    for name, fixture, required_errors, forbidden_errors in cases:
        result = validate_text(fixture)
        error_codes = {issue.code for issue in result.errors}
        missing = set(required_errors) - error_codes
        forbidden = set(forbidden_errors) & error_codes
        if missing or forbidden or (not required_errors and error_codes):
            failed += 1
            print(f"SELF-TEST FAIL: {name}")
            if missing:
                print("  missing expected errors: " + ", ".join(sorted(missing)))
            if forbidden:
                print("  unexpected forbidden errors: " + ", ".join(sorted(forbidden)))
            for issue in result.issues:
                print("  " + issue.render())
        else:
            print(f"SELF-TEST PASS: {name}")
    if failed:
        print(f"Self-test failed: {failed}/{len(cases)} cases failed.")
        return 1
    print(f"Self-test passed: {len(cases)} cases.")
    return 0


def _print_result(path: Path, result: ValidationResult) -> None:
    severity_order = {"ERROR": 0, "WARN": 1}
    for issue in sorted(
        result.issues,
        key=lambda item: (severity_order.get(item.severity, 9), item.line or 0, item.code),
    ):
        print(issue.render())
    if result.errors:
        print(
            f"INVALID: {path} ({len(result.errors)} error(s), {len(result.warnings)} warning(s))"
        )
    else:
        print(f"VALID: {path} (0 errors, {len(result.warnings)} warning(s))")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a rumelt-task-plan/v1 Markdown plan."
    )
    parser.add_argument("plan", nargs="?", help="Path to the Markdown plan document")
    parser.add_argument(
        "--self-test", action="store_true", help="Run built-in positive and negative tests"
    )
    args = parser.parse_args(argv)

    if args.self_test:
        if args.plan:
            parser.error("do not provide a plan path together with --self-test")
        return run_self_test()
    if not args.plan:
        parser.error("a Markdown plan path is required unless --self-test is used")

    path = Path(args.plan)
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        print(f"[ERROR] FILE_READ: cannot read {path}: {exc}", file=sys.stderr)
        return 2
    result = validate_text(text)
    _print_result(path, result)
    return 1 if result.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

