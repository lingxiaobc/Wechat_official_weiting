---
name: plan-tasks
description: "在复杂任务或大规模项目变更执行前，运用 Rumelt 的诊断—指导方针—连贯行动内核生成可审阅、可证伪的方案；仅在用户明确批准当前方案后，创建并维护 TASK 跟踪文档。用户调用 /plan-tasks、要求先给方案/实施计划/任务拆解/防跑偏方案，或任务涉及至少 3 个文件、多个模块、新功能、架构变化、大规模重构/重写/性能优化、多个竞争路线、关键未知、强依赖、高影响或高返工成本时使用。不要为未显式要求规划的单文件小修、简单 bug、配置微调、一行改动、纯解释或状态查询自动调用。"
when_to_use: "显式规划请求始终触发；复杂或高代价任务自动触发。简单、低风险、可逆任务仅在用户显式调用 /plan-tasks 时使用 compact 模式。"
argument-hint: "[task-description]"
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - Read
  - Grep
  - Glob
---

# Plan Tasks

## Core contract

Construct a causal task strategy before execution, then track only the work the user explicitly approves. Treat `$ARGUMENTS` as the task when present; otherwise use the current request and relevant conversation context.

Separate the lifecycle into two phases:

1. **Plan phase:** inspect read-only context, produce `DRAFT` or `READY_FOR_REVIEW`, and stop.
2. **Execution phase:** enter only after the user explicitly approves the current plan or named actions. Create or update a `TASK/` tracker, execute within the approved scope, and keep its state current.

Never create a tracker, edit target files, run mutating commands, publish, deploy, commit, send external messages, or perform irreversible actions during the plan phase. The `allowed-tools` frontmatter only pre-approves listed read-only tools; it does not restrict other tools. Continue to obey Claude Code permissions, project instructions, protected paths, and the user's authorization.

## Load the right resources

Before constructing any plan:

1. Read [references/rumelt-method-card.md](references/rumelt-method-card.md) completely for the method and attribution boundaries.
2. Read [references/plan-contract.md](references/plan-contract.md) completely for the required plan schema, IDs, hard errors, and approval states.
3. Read [references/examples.md](references/examples.md) only when the request is unusually vague, conflicting, exploratory, or difficult to classify.

Before creating, resuming, or updating an execution tracker, read [references/task-tracking-contract.md](references/task-tracking-contract.md) completely.

Keep `[GSBS]` author claims separate from `[AI-EXT]` engineering controls. Do not attribute prompts, permissions, schemas, validators, or approval gates to Richard Rumelt.

## Choose one planning mode

- `full`: Use for complex, ambiguous, multi-stage, multi-agent, high-impact, cross-module, or costly-to-reverse work.
- `diagnostic-exploration`: Use when evidence cannot yet support one primary diagnosis. Make the proximate objective discriminate among competing diagnoses; do not include substantive target execution.
- `compact`: Use only when the user explicitly requests planning for a simple, low-risk, reversible task. Preserve diagnosis, choice, traceable action, acceptance, failure signals, and the approval gate.

Do not confuse more detail with better strategy.

## Phase 1: build the reviewable plan

### 1. Establish facts and boundaries

- Restate the requested outcome without expanding authority.
- Separate verified facts, requirements, constraints, assumptions, unknowns, preferences, tools, permissions, and prohibited actions.
- Inspect only the context needed to diagnose the task.
- Preserve project instructions, protected paths, privacy rules, and previously confirmed choices.
- Ask only when a missing decision would materially change the plan or authorize significant external action. Otherwise state a conservative, testable assumption.

### 2. Diagnose the critical challenge

- Distinguish the requested output from the obstacle preventing success.
- Select one primary `D-*` diagnosis when evidence supports it.
- Explain the causal mechanism, supporting evidence, competing diagnosis, and disconfirming observation.
- Switch to `diagnostic-exploration` rather than inventing a root cause when evidence is insufficient.

Do not use a desired result, broad topic, symptom, missing deliverable, or task list as the diagnosis.

### 3. Select a guiding policy

- Define an overall `G-*` method that directly addresses the diagnosis.
- State priorities, conflict-resolution rules, autonomy, reference/tool/permission boundaries, and escalation conditions.
- Reject at least one plausible route with an `NG-*` non-goal.
- Ensure the policy constrains choices instead of restating the desired end state.

### 4. Set the proximate objective and leverage point

- Define the nearest feasible, meaningful, and testable `O-*` state.
- Explain which uncertainty it reduces or which option it creates.
- Identify the `L-*` factor where concentrated effort should have disproportionate effect.
- State what observation would invalidate the leverage judgment.

### 5. Design coherent action

- Assign stable `A-*` IDs.
- For every action specify: action, `addresses`, `implements`, input, output, dependencies, permissions, and acceptance.
- Trace each action to both the diagnosis and guiding policy.
- Order work by causal and information flow; keep independent work parallel.
- Delete, defer, or split unrelated work instead of creating a dog's-dinner list.

### 6. Add gates and falsification

- Identify the weakest required `W-*` link and place a gate before downstream work amplifies it.
- Record a central `H-*` hypothesis, expected observation, low-cost test, pass threshold, failure signal, and the layer to recheck after failure.
- Do not substitute the same model's confidence for external evidence, a deterministic tool check, or human judgment.

### 7. Audit, validate, and stop

- Reject fluff, failure to face the challenge, goals masquerading as strategy, unfocused objectives, unreachable objectives, avoided choices, and template completion without causal links.
- Format the plan exactly according to `rumelt-task-plan/v1` in the plan contract.
- Use `status: DRAFT` when hard errors, material unknowns, or unresolved decisions remain. Use `READY_FOR_REVIEW` only after semantic and structural review.
- Never set `APPROVED` on the user's behalf.
- When a plan is saved to an authorized path, run:

```text
python "${CLAUDE_SKILL_DIR}/scripts/validate-plan.py" <plan.md>
```

- Fix every `ERROR`; expose remaining `WARN` items as review questions or explicitly accepted risks.
- Present the current plan version, its pivotal assumption, approval scope, and decisions requiring the user. Stop without executing the target task.

## Approval gate

Treat approval as valid only when all conditions hold:

1. The user has seen the current plan or identified revision.
2. The user explicitly approves the whole plan or named `A-*` actions.
3. The required input, permissions, protected-path boundaries, and acceptance conditions remain unchanged.

Silence, a general request to complete the original task, `READY_FOR_REVIEW`, low apparent risk, or the model's own judgment never counts as approval.

Record the approved plan version and exact `A-*` scope. Approval does not expand tool, directory, data, external-send, destructive-action, or privacy permissions.

If the user approves only part of the plan, all other `A-*` actions remain prohibited. If the task, diagnosis, policy, approved actions, permissions, or acceptance criteria change materially, pause execution, issue a revised `READY_FOR_REVIEW` plan, and request new approval.

## Phase 2: track and execute the approved plan

After valid approval:

1. Read [references/task-tracking-contract.md](references/task-tracking-contract.md) completely.
2. Create `TASK/TASK_<descriptive-name>.md` if no tracker exists; create `TASK/` only at this point.
3. Copy the approved plan version, approved `A-*` scope, diagnosis, guiding policy, proximate objective, non-goals, change scope, permissions, and completion criteria into the tracker.
4. Decompose approved actions into ordered, verifiable `T-*` checkbox items. Every item must map to exactly one approved `A-*` action and include an observable acceptance condition.
5. Before every tracker update, read its latest contents to avoid overwriting concurrent changes.
6. Immediately mark a completed item `- [x]` after its acceptance condition passes. Do not batch completion updates at the end.
7. Append newly discovered tactical subtasks only when they stay within an already approved `A-*`, diagnosis, policy, permissions, and acceptance boundary. Record the reason in the change log.
8. Do not delete obsolete work. Mark it cancelled with strikethrough and a reason.
9. Treat any new `A-*`, changed diagnosis or policy, expanded file/module/data scope, new permission, altered acceptance criterion, or external side effect as material. Set execution to `PAUSED`, return the plan to `READY_FOR_REVIEW`, and wait for reapproval.
10. Mark execution `COMPLETED` only when every active task is checked and all overall completion criteria pass.

Validate a saved tracker after creation, after material updates, and before completion:

```text
python "${CLAUDE_SKILL_DIR}/scripts/validate-task-tracker.py" <TASK-file.md>
```

Fix every `ERROR`. Report warnings, blocked items, invalidated assumptions, and acceptance evidence to the user.

## Five non-negotiable gates

1. Do not design action without a supported diagnosis or an explicit diagnostic-exploration objective.
2. Do not call a statement a guiding policy unless it chooses and rejects routes.
3. Do not include an action that cannot trace to both the diagnosis and guiding policy.
4. Do not authorize execution without concrete inputs, permissions, dependencies, acceptance criteria, and failure signals.
5. Do not execute or create the `TASK` tracker before the user explicitly approves the current plan.
