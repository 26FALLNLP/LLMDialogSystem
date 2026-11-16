# Dialogue Pipeline 设计文档

Dialogue Pipeline 为 S1–S4 执行同一套餐厅推荐流程。每次运行从一段固定对话接手，允许策略在预算内追问，最后保存推荐和完整轨迹。本文与 [Answer Service](answer-service.md)、[Scoring Service](scoring-service.md) 使用同一套接口。三者在第一版中作为同一 Python 项目内的模块，通过函数调用协作。

## 职责和输入

- **Pipeline** 管理对话历史、预算、动作校验、模块调用与运行记录。
- **策略** 决定下一步是追问还是推荐。S1 使用对话历史，S2 额外维护文本摘要，S3 使用结构化状态、关系链接和选择性追问，S4 使用结构化状态和选择性追问。策略在每次运行开始时初始化本次的内部状态。
- **Answer Service** 根据场景的预设回答表回答一个独立问题。**Scoring Service** 在运行结束后根据记录、数据库和标准答案评分。

一次运行对应 `scenario_id × system_id × budget × repeat`，由 `run_id` 唯一标识。输入包括带角色和稳定消息 ID 的 `dialogue_prefix`、同一版本的餐厅数据库，以及模型和实验配置。批量运行从配置读取场景列表、预算和重复次数。预算取 0、1 或 2，从策略接手时开始计算。

场景加载时分出公开数据、回答表和评分数据。策略每轮只接收对话消息、公开餐厅数据库、剩余预算及通用任务说明。回答表由 Answer Service 持有，隐藏目标、标准状态和标准关系由 Scoring Service 持有。`scenario_id` 用于路由和记录。场景类型、模板族和回答匹配状态保留在实验侧。

### 接入 NLP.zip 数据

压缩包内的 `NLP/data/restaurants.json` 包含 40 家虚构餐厅，数据说明将其标为草稿。这个快照使用 `name`、`near_station`、`near_mall`、`vegetarian_options` 和 `open_for_dinner`。v9 的港口／校园样例使用另一套餐厅库。运行配置需要绑定场景和餐厅库的版本，同一个 ID 只在对应版本内解释。

接入时可复用包中的 `src/data.py` 和 `src/split.py`。以 `system_view()` 取得只读公开数据，将前缀的 `{turn, speaker, text}` 转成 `{turn_id, role, text}`，例如将第 7 条消息编号为 `t07`。从 `evaluation_only` 分别提取模拟用户所需的回答表和评估所需的标准答案。策略输入只使用公开视图和运行参数。这个快照包含 36 条场景，随包划分为 7 条开发和 29 条测试。

## 策略与动作接口

每个策略实现 `decide(context) -> Decision`。`context` 包含 `turns`、`restaurant_database`、`remaining_budget` 和 `allowed_actions`。最后一个字段由 Pipeline 按剩余预算生成。返回值包含 `action`，可附当前上下文对应的 `state_snapshot`。一个动作只能是以下两种之一。

| 动作 | 字段 | 约束 |
| --- | --- | --- |
| `ASK` | `type`、`questions` | `questions` 是非空列表，每项只请求一条独立信息。 |
| `RECOMMEND` | `type`、`restaurant_id`、可选 `confidence` | 只提供一个餐厅 ID。启用自报置信度的实验要求提供 1–10 的整数，四个系统使用相同规则。 |

每项 `Question` 包含 `question_id`、`text`、`slot` 和 `reference_turn_id`。`question_id` 由执行层为每个问题分配，供日志关联。`slot` 取当前数据版本的词表值，详见 [Answer Service](answer-service.md)。`reference_turn_id` 指向问题针对的可见消息，通用问题可以用 `null`。不存在或尚不可见的消息 ID 属于无效动作。

四个系统共用动作适配器。它将模型输出转成统一结构，例如把 `RECOMMEND: R03 | CONFIDENCE: 7` 转为推荐动作。若采用文本 `ASK:` 格式，适配器须从公开的对话和问题文本拆出独立问题并规范化目标，所需模型调用也计入运行成本。优先让模型提供结构化问题项，适配器按同一规则校验拆分和目标。无法可靠拆分的复合问句记为 `invalid_action`，避免通过合并问句少扣预算。目标确实不在支持范围时使用 `other`，交由模拟用户走兜底路径。

## 执行流程

1. 将固定前缀复制为本次运行的初始历史，剩余预算设为实验配置值。前缀里已有的问句只作为上下文。
2. 用当前历史调用策略。如果剩余预算为 0，向策略明确本轮只允许 `RECOMMEND`，包括最后一次追问得到回答后的下一轮。
3. 校验动作。`ASK` 的问题数超过剩余预算时，整个动作记为 `budget_exceeded`。该问题留在尝试记录中，交付问题列表为空。
4. 对通过校验的 `ASK`，按顺序为每个独立问题调用 Answer Service。取齐回复后提交这一轮，追加一条包含所有问题的助手消息和一条按相同顺序合并回复的用户消息。按实际交付的问题数扣减预算，重复问题和得到兜底回复的问题都计入。策略下一轮看到的是追加后的历史和新预算。
5. 对 `RECOMMEND`，校验 ID 是否存在于同一版本的餐厅库。有效 ID 写入最终推荐，将推荐作为最后一条助手消息追加到历史并结束。是否符合隐藏硬约束由评分器判定。
6. 写入完整运行记录后，由评分器单独读入。评分结果不参与当前运行。

| 终止原因 | 含义 |
| --- | --- |
| `completed` | 返回了有效的餐厅 ID。任务是否成功由评分器决定。 |
| `invalid_action` | 动作缺失、解析失败或字段违反协议。 |
| `budget_exceeded` | 尝试追问的独立问题数超过预算。 |
| `invalid_restaurant_id` | 推荐 ID 不在当前数据库。 |
| `model_error` | 模型请求在统一的基础设施重试规则执行后仍失败。 |
| `answer_error` | 已校验场景的回答表无法读取或调用失败。该次问答未提交。 |

首版对模型的格式错误、预算违规和无效 ID 直接终止并留档。基础设施重试规则在实验运行前统一配置，适用于所有策略。每次模型调用的用途和已知 token 用量都计入轨迹，便于区分决策、摘要、状态提取和动作适配的成本。

## 运行记录

每次运行写一条 JSONL 记录，成功输出与失败路径使用同一结构。

| 字段 | 内容 |
| --- | --- |
| `schema_version`、`run_id` | 记录格式版本与运行标识。 |
| `scenario_id`、`system_id`、`budget`、`repeat` | 场景、策略、初始预算、重复编号。 |
| `config` | 模型标识与生成参数，提示词、数据集、数据库和运行配置版本。 |
| `turns` | 从固定前缀开始的完整可见历史。消息形状为 `{turn_id, role, text}`。 |
| `steps` | 逐轮执行记录。每项包含 `step_id`、`context_turn_id`、`budget_before`、`budget_after`、`action` 和 `delivered_questions`，可附 `state_snapshot`、原始模型输出和错误。 |
| `final_recommendation` | `{restaurant_id, confidence?}` 或 `null`。只有 `completed` 写入有效推荐。 |
| `termination_reason` | 结束原因。 |
| `usage` | `input_tokens`、`output_tokens`、`model_calls`。若用量缺失，记录缺失情况；按用途保留明细。 |

`context_turn_id` 是策略决策前看到的最后一条消息 ID。一个复合动作的各问题共用这个决策检查点。`delivered_questions` 中每项保存 `{question_id, question, reply}`，其中 `reply` 含 `text` 与 `status`。拒绝的动作保留在 `action`，解析失败则写 `action: null` 并保留原始输出。无效输出、失败详情和内部状态快照保存在日志侧。

下面是一条已交付的问题记录。示例中的消息 ID 和用户实际指的是港口为演示设定，与 [Answer Service 的回答表示例](answer-service.md) 对应。

```json
{
  "question_id": "q01",
  "question": {
    "question_id": "q01",
    "text": "Do you mean near the harbor or near campus?",
    "slot": "location",
    "reference_turn_id": "t07"
  },
  "reply": {"text": "Near the harbor.", "status": "answered"}
}
```

## 联调场景

采用 v9 第 12 页 `SS-AMB-01` 对照场景。两版均要求泰餐和纯素选项，示意中的隐藏地点取港口。

| 场景 | 预期运行 |
| --- | --- |
| A，预算 $25，允许追问 1 次 | 策略问「港口还是校园？」。Pipeline 交付一个地点问题，将模拟用户的「港口附近」追加到历史，预算变为 0。策略随后推荐港口候选 `R03`。 |
| B，预算 $35，允许追问 1 次 | 策略直接推荐共同候选 `R02`。交付问题列表为空，预算仍为 1。 |
| A，允许追问 0 次 | 策略收到仅可推荐的回合。如果仍输出 `ASK`，记录 `budget_exceeded`，模拟用户收到 0 个问题。 |
| 任一场景，剩余预算 1，输出两个独立问题 | 整个动作结束于 `budget_exceeded`，没有交付问题，预算保持 1。 |
| 任一场景，输出未知餐厅 ID | 保留原始动作和用量，记录 `invalid_restaurant_id` 和空推荐。 |

验收时还需核对四个策略收到的数据边界、复合动作的交付顺序、兜底回答的预算消耗，以及失败运行能否与正常运行一起被评分器读取。餐厅字段映射和预算措辞以团队最终数据规则为准。主对话流程依据英文研究方案第 3 页和 v9 第 9–16 页。

使用压缩包做联调时，可以运行实际对照组 `XX-AMB-01A/B`。两版都要求日餐，地点用「那里」来指代。A 的餐费上限是 $25，车站候选为 `R01`、商场候选为 `R02`，预设用户答复是 `Near the station.`，随后可推荐 `R01`。B 的上限是 $30，`R03` 同时符合两种解释，可以直接推荐。

## 运行联调样例

在项目根目录使用 Python 3.11 或更高版本运行。默认对 A、B 各给 1 次提问预算。数据文件保留了压缩包中的原始内容。

```sh
python3 -m src --budget 1 --output runs/amb-01.jsonl
```

终端打印完整对话和最终推荐，`--output` 保存两条 JSONL 运行记录，并覆盖该路径上的同名文件。使用 `--scenario XX-AMB-01A` 可以单独运行一条场景。

首版联调用 `DemoStrategy` 从这两条场景的可见对话中提取预算、菜系和地点，再查询餐厅库。它覆盖这组对照场景的措辞，模型调用数为 0。后续可以通过相同的 `decide(context)` 接口接入实验策略。

## 使用 Claude 运行

在本地终端设置 `ANTHROPIC_API_KEY`，然后从项目根目录运行以下命令。默认模型是项目方案中的 `claude-opus-5-5`。可以通过 `--model` 或 `ANTHROPIC_MODEL` 选择支持结构化输出的 Claude 模型。显式选择 `--strategy claude` 时才发送模型请求。

```sh
python3 -m src --strategy claude --budget 2 --output runs/amb-01-claude-b2.jsonl
```

默认运行 A/B。通过 `--all` 可运行所有本地场景，输出路径建议写成单独的批次文件。对话和生成参数继续留在相同格式的日志里，可以用[评分器](scoring-service.md)评分。

```sh
python3 -m src.score_runs --input runs/amb-01-claude-b2.jsonl \
  --output runs/amb-01-claude-b2-scores.jsonl \
  --summary runs/amb-01-claude-b2-score-summary.json
```

Claude 每轮收到的是可见的对话、餐厅库和剩余提问预算。它返回结构化 `ASK` 或 `RECOMMEND`，仍由 Pipeline 校验动作、调用固定回答服务并追加消息。该策略用提示词指导选择性追问。显式对话状态和关系链接的实验策略可另行接入。

日志记录模型 ID、提示词版本、API 版本、生成配置及用量。API 凭证只从本地环境读取。接口格式见 [Anthropic Messages API](https://platform.claude.com/docs/en/api/http/messages/create) 和 [结构化输出](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)。
