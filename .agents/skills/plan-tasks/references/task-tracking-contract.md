# TASK 跟踪文档契约

本契约用于用户批准方案后的执行跟踪。它是 `[AI-EXT]` 工程控制，不是 Richard Rumelt 在 *Good Strategy/Bad Strategy* 中提出的文档格式。

## 目录

- [创建时机与路径](#创建时机与路径)
- [Frontmatter](#frontmatter)
- [五个必需章节](#五个必需章节)
- [任务项格式](#任务项格式)
- [更新与批准规则](#更新与批准规则)
- [完成与验证](#完成与验证)
- [最小完整示例](#最小完整示例)

## 创建时机与路径

- 只在用户明确批准当前方案或具体 `A-*` 后创建跟踪文档。
- 路径固定为项目根目录下的 `TASK/TASK_<descriptive-name>.md`。
- 文件名使用简短、可辨识的描述，不使用日期或 `final` 代替任务含义。
- 一个批准方案使用一个跟踪文档；继续任务时先查找并读取现有文档，不重复创建。

## Frontmatter

文档必须以以下 YAML frontmatter 开始：

```yaml
---
task_schema: plan-tasks-tracker/v1
plan_schema: rumelt-task-plan/v1
plan_id: PLAN-20260809-01
plan_version: 1
plan_status: APPROVED
approved_by: user
approved_scope: A-01, A-02
execution_status: IN_PROGRESS
created_at: 2026-08-09
updated_at: 2026-08-09
---
```

| 字段 | 规则 |
| --- | --- |
| `task_schema` | 固定为 `plan-tasks-tracker/v1` |
| `plan_schema` | 固定为 `rumelt-task-plan/v1` |
| `plan_id` | 当前批准方案的稳定 ID |
| `plan_version` | 用户实际批准的版本；实质变更后递增 |
| `plan_status` | 正常执行时为 `APPROVED`；需要重批时改为 `READY_FOR_REVIEW` |
| `approved_by` | 只有用户明确批准后才能写 `user` |
| `approved_scope` | 逗号分隔的具体 `A-*`，不写模糊的 `all` |
| `execution_status` | `IN_PROGRESS`、`PAUSED`、`COMPLETED` 或 `CANCELLED` |
| `created_at` | 首次创建日期，ISO `YYYY-MM-DD` |
| `updated_at` | 最近更新日期，ISO `YYYY-MM-DD` |

状态约束：

- `IN_PROGRESS` 或 `COMPLETED` 要求 `plan_status: APPROVED` 且 `approved_by: user`。
- `plan_status: READY_FOR_REVIEW` 时，`execution_status` 必须为 `PAUSED`。
- AI 不得自行把 `READY_FOR_REVIEW` 改为 `APPROVED`。

## 五个必需章节

章节必须按以下顺序出现，标题不得改名：

1. `任务目标与批准快照`
2. `变更范围`
3. `任务明细`
4. `发现与变更记录`
5. `完成标准`

### 任务目标与批准快照

至少包含：

```markdown
- 目标：<1-3 句话说明最终可观察结果>
- 主要诊断：D-01 | <关键障碍>
- 指导方针：G-01 | <总体应对方法与取舍>
- 近端目标：O-01 | <本轮可达状态>
- 主动不做：NG-01 | <被排除路线及原因>
- 批准依据：<用户批准消息的简短定位，不粘贴私人或无关内容>
```

### 变更范围

至少包含：

```markdown
- 涉及模块或目录：<明确路径或模块>
- 预计影响文件数：<数量或经说明的区间>
- 允许的工具与权限：<当前已具备的权限>
- 禁止或需另行批准：<保护路径、外部发送、破坏性动作等>
```

### 任务明细

- 按依赖关系分阶段组织。
- 阶段间串行时写明进入闸门；可以并行的任务不强行串行。
- 所有可执行工作必须使用本契约的任务项格式。

### 发现与变更记录

创建时至少写一条记录：

```markdown
- 2026-08-09 | 创建跟踪文档 | 依据：用户批准 PLAN-20260809-01 v1
```

执行中记录新增战术子任务、取消项、阻塞、假设失效、暂停和重新批准。不得用变更记录暗中扩大批准范围。

### 完成标准

- 使用无复选框的项目符号列出整体可观察验收条件。
- 完成标准必须覆盖用户要求和系统级检查，不能只写“全部任务已完成”。
- `execution_status: COMPLETED` 前逐条验证并记录证据。

## 任务项格式

每个任务占一行并使用精确格式：

```markdown
- [ ] T-01 | A-01 | <动词开头的具体任务> | acceptance: <可观察通过条件>
```

- `T-*` 在文档内唯一，按发现顺序递增，不重用已取消 ID。
- 第二个 ID 必须是 `approved_scope` 中的一个 `A-*`。
- 描述必须具体到可执行、可验证；不用“优化、完善、处理一下”等空泛表达。
- `acceptance:` 后必须是人、工具或后续步骤可观察的条件。
- 完成并通过验收后立即改为 `- [x]`。
- 新发现的战术子任务只能映射到已有批准 `A-*`。需要新 `A-*` 时必须暂停并重新规划。

取消任务使用：

```markdown
- [ ] ~~T-03 | A-02 | 删除过时适配层 | acceptance: 适配层不再被引用~~ | cancelled: 新证据表明仍有外部消费者
```

不要删除、复用或勾选取消项。

## 更新与批准规则

每次更新执行以下顺序：

1. 读取跟踪文档最新内容。
2. 核对 `plan_id`、`plan_version`、批准范围和当前状态。
3. 更新一个事实状态：勾选、追加、取消、记录阻塞或暂停。
4. 更新 `updated_at`。
5. 运行 `validate-task-tracker.py`。
6. 修复全部 `ERROR` 后再继续下游任务。

以下属于战术调整，可在批准的 `A-*` 内追加 `T-*`：

- 为达到既定验收条件增加同一模块内的测试或检查；
- 把一个过大的已批准动作拆成更小任务；
- 调整不改变输入、输出、权限或外部副作用的执行顺序。

以下属于实质变更，必须暂停并重新批准：

- 新增或改变 `D-*`、`G-*`、`O-*` 或 `A-*`；
- 扩大模块、目录、数据、用户或外部系统范围；
- 需要新的写入、联网、发送、部署、删除或其他权限；
- 改变验收条件、关键依赖、不可逆性或风险等级；
- 新事实推翻当前战略假设。

实质变更时：

1. 设置 `plan_status: READY_FOR_REVIEW`。
2. 设置 `execution_status: PAUSED`。
3. 在“发现与变更记录”说明证据和影响。
4. 输出修订方案并等待用户明确批准。
5. 获批后递增 `plan_version`、更新 `approved_scope`，再恢复 `IN_PROGRESS`。

## 完成与验证

设置 `COMPLETED` 前必须同时满足：

- 每个非取消任务都是 `- [x]`；
- 所有整体完成标准已验证；
- 没有未解决阻塞、待重批实质变更或超出批准范围的工作；
- 跟踪验证器无 `ERROR`；
- 向用户报告完成证据、保留风险和未执行的取消项。

验证命令：

```text
python "${CLAUDE_SKILL_DIR}/scripts/validate-task-tracker.py" <TASK-file.md>
```

## 最小完整示例

```markdown
---
task_schema: plan-tasks-tracker/v1
plan_schema: rumelt-task-plan/v1
plan_id: PLAN-20260809-01
plan_version: 1
plan_status: APPROVED
approved_by: user
approved_scope: A-01, A-02
execution_status: IN_PROGRESS
created_at: 2026-08-09
updated_at: 2026-08-09
---

# 任务计划：合并规划技能

## 任务目标与批准快照

- 目标：形成一个先审后执行的统一技能。
- 主要诊断：D-01 | 两套技能的执行时机冲突。
- 指导方针：G-01 | 用批准闸门分离规划和执行跟踪。
- 近端目标：O-01 | 合并目录通过结构和行为验证。
- 主动不做：NG-01 | 不保留两个自动触发的重复入口。
- 批准依据：用户明确批准 PLAN-20260809-01 v1。

## 变更范围

- 涉及模块或目录：`.claude/skills/`
- 预计影响文件数：8
- 允许的工具与权限：项目内技能文件读写
- 禁止或需另行批准：Codex 技能、源码和外部发送

## 任务明细

### 阶段一：合并

- [x] T-01 | A-01 | 建立合并前哈希基线 | acceptance: 三个相关目录均有逐文件 SHA-256
- [ ] T-02 | A-02 | 合并 Claude 技能资源 | acceptance: 新目录包含契约、示例和验证器

### 阶段二：验证

- [ ] T-03 | A-03 | 运行正反向测试 | acceptance: 批准前零写入且小修不自动触发

## 发现与变更记录

- 2026-08-09 | 创建跟踪文档 | 依据：用户批准 PLAN-20260809-01 v1

## 完成标准

- 新技能目录通过两个验证器。
- Codex 技能逐文件哈希保持不变。
```
