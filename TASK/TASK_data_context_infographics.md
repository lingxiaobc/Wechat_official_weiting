---
task_schema: plan-tasks-tracker/v1
plan_schema: rumelt-task-plan/v1
plan_id: PLAN-data-context-infographics
plan_version: 1
plan_status: APPROVED
approved_by: user
approved_scope: A-01, A-02, A-03
execution_status: COMPLETED
created_at: 2026-10-07
updated_at: 2026-10-07
---

# 任务计划：数据来源到上下文信息图

## 任务目标与批准快照

- 目标：生成四张 16:9 中文信息图，插入正式正文，并转换两处长文字结构。
- 主要诊断：D-01 | 流程、分流和材料组合以连续文字表达，读者需要自行建立关系。
- 指导方针：G-01 | 每图解释一个关系，准确性和手机可读优先，保留事实边界。
- 近端目标：O-01 | 四张图通过视觉检查，正文引用有效，材料包与排查表转换为图。
- 主动不做：NG-01 | 不添加装饰性插图、封面、新案例或新观点。
- 批准依据：用户明确回复“可以，请生成图片并插入到特定位置。”，批准上一轮方案 A-01 至 A-03。

## 变更范围

- 涉及模块或目录：articles/数据来源到上下文/；本执行跟踪文件。
- 预计影响文件数：正文、四张图片、本跟踪文件，共六个。
- 允许的工具与权限：内置图像生成、原图视觉检查、项目文件复制与 Markdown 编辑。
- 禁止或需另行批准：发布、提交、改写主线、改变已确认的真实经历、修改其他文章。

## 任务明细

- [x] T-01 | A-01 | 生成六阶段与反馈循环图 | acceptance: 得到独立候选原图，内容为资料到回答的链路
- [x] T-02 | A-02 | 验收并保存第一张图 | acceptance: 中文、逻辑、16:9 比例和手机预览通过检查
- [x] T-03 | A-01 | 生成检索分流汇合图 | acceptance: 得到独立候选原图，区分标签筛选与语义查找并保留核对
- [x] T-04 | A-02 | 验收并保存第二张图 | acceptance: 中文、逻辑、16:9 比例和手机预览通过检查
- [x] T-05 | A-01 | 生成上下文任务材料包图 | acceptance: 得到独立候选原图，完整保留六类任务材料
- [x] T-06 | A-02 | 验收并保存第三张图 | acceptance: 中文、逻辑、16:9 比例和手机预览通过检查
- [x] T-07 | A-01 | 生成回答排查图 | acceptance: 得到独立候选原图，四类问题对应原文的检查入口
- [x] T-08 | A-02 | 验收并保存第四张图 | acceptance: 中文、逻辑、16:9 比例和手机预览通过检查
- [x] T-09 | A-03 | 插入四图并转换指定引文与表格 | acceptance: 图片位置与批准方案一致，示意与非因果判断边界保留
- [x] T-10 | A-03 | 核对正文、资源路径和整体阅读顺序 | acceptance: 四个路径存在，正文仅产生批准的改动，无未完成任务

## 发现与变更记录

- 2026-10-07 | 第一张修正与插入完成 | 反馈箭头已明确从 06 回到 02，六阶段主流程正确；原图与 360 像素预览通过检查，四图按批准位置插入，指定引文与表格已转换。
- 2026-10-07 | 第二至四张验收完成 | 原图中文、分流关系与材料组合正确；360 像素预览主标签可读。原生尺寸为 1672×941，接近 16:9；已保存到文章目录。
- 2026-10-07 | 创建跟踪文档 | 依据：用户批准四图方案及两处文字结构转换。
- 2026-10-07 | 风格参考 | 使用已有数据上下文图与三层检查图校准色彩；技能列出的公共基准目录不存在。
- 2026-10-07 | 四张候选生成完成 | 第一张反馈箭头出现错误连接，进入第二次修正；其他三张原图中文与关系检查通过，待手机预览。

## 完成标准
+### 图 1 生成提示词

```text
Use case: infographic-diagram. Create ONE finished Chinese infographic for a WeChat article, exact 16:9 landscape, ideally 2048x1152. Pure flat 2D editorial infographic. Warm ivory background #FFF8EE, muted coral #D98175, desaturated teal #78AFA1, dusty rose and dark navy-gray #23384A. Strong typographic hierarchy, generous whitespace, crisp Simplified Chinese, large bold main labels readable at 360px display width. Flat colored rounded rectangles, clear thin arrows and restrained line icons. Use the restrained palette of Monument Valley ONLY, absolutely no isometric buildings, stairs, platforms, spatial illusion, perspective, 3D, glow, English labels, watermark or invented text. Do not render prompt instructions. Exactly reproduce all listed Chinese, do not add words. Keep headline and bottom conclusion within safe margins.
Title exactly: “从资料到回答的六个环节”.
Layout: numbered six equal stage cards in a clear snake sequence, 3 cards upper row left to right numbered 01,02,03; then a connector down on far right to 04 at bottom right, then leftward to 05 bottom center, then leftward to 06 bottom left. Main labels and support copy:
01 “来源” / “保留原始资料”
02 “接入清洗” / “检查完整与对应”
03 “结构化存储” / “组织字段与关联”
04 “检索核对” / “寻找合适候选”
05 “构造上下文” / “组合任务与依据”
06 “回答与反馈” / “检查结果并修正”
A distinct coral feedback arrow below the six cards returns from stage06 toward stage02, labeled “反馈推动更新”. Avoid crossing text. Header large, six labels large. Bottom navy conclusion bar exactly “让需要的信息被找到，并成为回答依据”. Numbering must make reading order unambiguous.
```

### 图 2 生成提示词

```text
Use case: infographic-diagram. Create ONE finished Chinese infographic for a WeChat article, exact 16:9 landscape, ideally 2048x1152. Pure flat 2D editorial infographic. Warm ivory background #FFF8EE, muted coral #D98175, desaturated teal #78AFA1, dusty rose and dark navy-gray #23384A. Strong typographic hierarchy, generous whitespace, crisp Simplified Chinese, large bold main labels readable at 360px display width. Flat colored rounded rectangles, clear thin arrows and restrained line icons. Use the restrained palette of Monument Valley ONLY, absolutely no isometric buildings, stairs, platforms, spatial illusion, perspective, 3D, glow, English labels, watermark or invented text. Do not render prompt instructions. Exactly reproduce all listed Chinese, do not add words. Keep headline and bottom conclusion within safe margins.
Title exactly: “两种查找方式，汇合后再核对”.
Layout a clean branching and merging graph. At top center wide input card “明确当前需求” with subline “确认条件及其关系”. Split visibly into two equal large cards side by side:
Left coral card main “标签筛选”, support “年级、主题、使用记录”, smaller heading above branch “明确条件”.
Right teal card main “语义查找”, support “按大致含义寻找”, smaller heading above branch “内容描述”.
Both branch arrows merge into centered card “候选资料”, then flow to “核对是否符合任务” with subline “检查内容、条件与记录”. Use 5 main nodes, two branches at equal level. Bottom bar exactly “意思相近，不等于准确命中”. Branching is a possible combination, not a claim every query requires both; do not add extra routing rules.
```

### 图 3 生成提示词

```text
Use case: infographic-diagram. Create ONE finished Chinese infographic for a WeChat article, exact 16:9 landscape, ideally 2048x1152. Pure flat 2D editorial infographic. Warm ivory background #FFF8EE, muted coral #D98175, desaturated teal #78AFA1, dusty rose and dark navy-gray #23384A. Strong typographic hierarchy, generous whitespace, crisp Simplified Chinese, large bold main labels readable at 360px display width. Flat colored rounded rectangles, clear thin arrows and restrained line icons. Use the restrained palette of Monument Valley ONLY, absolutely no isometric buildings, stairs, platforms, spatial illusion, perspective, 3D, glow, English labels, watermark or invented text. Do not render prompt instructions. Exactly reproduce all listed Chinese, do not add words. Keep headline and bottom conclusion within safe margins.
Title exactly: “上下文是一份任务材料包”.
Composition: top headline then 6 equal large rectangular cards arranged in 2 rows x 3 columns, numbered01-06 left to right on each row. Huge main headings, compact supporting text:
01 “任务与输出” / “选复习题，说明理由”
02 “本次目标” / “看清条件，减少复杂计算”
03 “相关记录” / “近期表现与做题记录”
04 “候选材料” / “题干、图片、解答与来源”
05 “教学说明” / “需要时提供分析顺序”
06 “不确定之处” / “标明缺失与判断边界”
Group cards with clear bracket or thin clean connectors into a centered horizontal panel “当前上下文”. No arrows between individual cards: six categories are ingredients, NOT chronological steps. Small badge under headline exactly “组织方式示意”. Bottom conclusion bar exactly “系统里存着，不等于这一轮已经提供”. Use mostly teal for evidence cards, coral for task and limits, all identical sizing. Keep text especially large for mobile.
```

### 图 4 生成提示词

```text
Use case: infographic-diagram. Create ONE finished Chinese infographic for a WeChat article, exact 16:9 landscape, ideally 2048x1152. Pure flat 2D editorial infographic. Warm ivory background #FFF8EE, muted coral #D98175, desaturated teal #78AFA1, dusty rose and dark navy-gray #23384A. Strong typographic hierarchy, generous whitespace, crisp Simplified Chinese, large bold main labels readable at 360px display width. Flat colored rounded rectangles, clear thin arrows and restrained line icons. Use the restrained palette of Monument Valley ONLY, absolutely no isometric buildings, stairs, platforms, spatial illusion, perspective, 3D, glow, English labels, watermark or invented text. Do not render prompt instructions. Exactly reproduce all listed Chinese, do not add words. Keep headline and bottom conclusion within safe margins.
Title exactly: “回答不合用，先查哪里”.
Layout: four equal diagnostic cards in a 2x2 grid, each has a coral symptom line, a downward arrow, and a teal check line. Each pair rendered exactly:
Card1 symptom “内容缺失或错配”; check header “查资料处理”; supporting “原文、提取与对应关系”.
Card2 symptom “内容相关但不合要求”; check header “查需求与检索”; supporting “条件、标签与候选核对”.
Card3 symptom “找到资料仍缺依据”; check header “查上下文”; supporting “关键内容、目标与背景”.
Card4 symptom “依据齐全仍不成立”; check header “查矛盾与生成”; supporting “资料冲突与模型判断”.
Do not draw arrows between the four cards: these are parallel inspection entry points, not a fixed sequence or causal verdict. Small top subheading exactly “根据结果，选择检查入口”. Bottom navy bar exactly “检查入口不是原因结论，要回看实际材料”. All four cards same hierarchy, align text and arrows.
```

### 图 1 箭头修正提示词

```text
Edit this Chinese infographic. Preserve all six cards, all Chinese text, icons, palette, headline, bottom conclusion and landscape dimensions. Fix ONLY the coral feedback connectors. Remove the coral arrow from card 05 to card 02, and remove the bottom coral connector from card 04 to card 06. Draw exactly ONE connected coral feedback arrow starting from card 06 回答与反馈 and ending with arrowhead at card 02 接入清洗. Route it cleanly through the empty horizontal gap between the two card rows: start at the TOP edge of card 06, move upward into the gap, then rightward, then upward into the BOTTOM edge of card 02. Its direction must clearly be 06 to 02, never 05 to 02. Attach the existing label 反馈推动更新 to this feedback connector with readable placement; allow slightly increasing the row gap if needed. Preserve the teal main flow 01→02→03→04→05→06 exactly. No other arrows or new text. Flat 2D only.
```


- 四图成品保存于正式文章目录下的 infographics/，使用稳定英文序号文件名。
- 每张原图及约 360 像素宽手机预览均直接检查。
- 开头插入阅读地图，第三节插入检索图，第四节转换材料包，第五节转换排查表。
- 正文保留标题、真实经历、示意性质和结果仍需核对的边界。
- 本跟踪文档通过技能验证器，资源路径检查通过。
