# Answer Service 设计文档

Answer Service 是实验中的模拟用户。它根据当前场景和系统实际问到的信息查表，返回预先写好的用户回复。同一数据版本下，只要场景和问题目标相同，S1–S4 就会得到同一条回复，即使问法不同。

## 模块边界

Answer Service 作为同一个 Python 项目中的模块，由 [Dialogue Pipeline](dialogue-pipeline.md) 在执行 `ASK` 时调用。Pipeline 校验预算、记录问题并追加用户消息。[Scoring Service](scoring-service.md) 根据运行记录判断提问是否有用，并检查最终推荐。Answer Service 使用场景回答表，不读取餐厅数据库、隐藏目标或评分标签。

## 接口

```text
answer(scenario_id: str, question: Question) -> AnswerReply
```

| `Question` 字段 | 类型 | 含义 |
|---|---|---|
| `text` | `str` | 给用户看的自然语言问题，保留在对话中。 |
| `slot` | `str` | 询问的属性，词表随数据版本配置。v9 示例使用 `location`、`cuisine`、`price_limit`、`vegan_options`、`open_late`。无法归入支持属性时用 `other`。 |
| `reference_turn_id` | `str \| null` | 问题所指的对话轮次。一般性问题可为 `null`，例如「你的预算上限是多少？」 |

策略根据可见对话提供问题的槽位和引用轮次。Pipeline 分配 `question_id`，写入运行日志以便关联回复。

Answer Service 支持两种初始化方式。原始数据走 `AnswerService(tables)`，按场景 ID 和槽位匹配。使用带引用的回答表时，调用 `AnswerService.from_exact_tables(tables, turn_ids_by_scenario=...)`，按 `(scenario_id, slot, reference_turn_id)` 精确匹配。`null` 是一个独立的键。两种方式都可以配置等价键的相同回复。

| `AnswerReply` 字段 | 类型 | 含义 |
|---|---|---|
| `text` | `str` | 用户实际说的话。 |
| `status` | `"answered" \| "fallback"` | 查到预设回答，或使用了场景的固定兜底回复。Pipeline 保留该字段供评分和排错，只把 `text` 作为用户消息交给策略。 |

## 场景回答表

下面是根据 v9 第 12 页 `SS-AMB-01-A` 构造的接口示例。`t07` 和用户指的是港口属于示例假设，正式运行时以数据组冻结的回答表为准。

```json
{
  "scenario_id": "SS-AMB-01-A",
  "answers": [
    {
      "slot": "location",
      "reference_turn_id": "t07",
      "text": "Near the harbor."
    }
  ],
  "fallback_text": "I don’t have any more information about that."
}
```

回答表随场景数据一起版本化，运行前加载并校验。每个待运行场景需要恰好一份配置，可以使用空的 `answers` 列表。校验场景 ID、回答键的唯一性、槽位是否合法、引用的轮次是否存在于固定前缀，以及回复文本是否为空。`other` 保留给归一化后未知的问题，直接触发兜底回复。

创建精确匹配服务时，`tables` 是上述场景对象的列表，`turn_ids_by_scenario` 对应每个场景固定前缀中的消息 ID，例如 `{"SS-AMB-01-A": {"t01", "t02", "t07"}}`。

首版的具体引用键来自固定前缀，方便数据组在运行前校验。若系统询问后来追加的消息，且该问题必须引用那条消息，则按未配置的键走兜底。需要在多轮联调中支持的通用追问，可以由数据组提前配置使用 `null` 的键，适配器只在问题确实不依赖某条消息时使用这个键。

### 接入 NLP.zip 的已有回答

这版的每个场景已经有 `evaluation_only.predefined_clarification_answers`。表中按 `cuisine`、`max_price`、`location`、`vegetarian`、`dinner` 存放文本，`_unsupported` 提供固定兜底回复。加载器把回答表交给按槽位匹配的版本，动作和日志继续保留 `reference_turn_id`，供独立评分使用。素食和晚餐开放按各自含义处理，纯素和深夜营业属于 v9 的字段。

`XX-AMB-01A` 的 `location` 回复是 `Near the station.`。`gold_decision` 中的 `location@t7` 用于离线判断追问目标是否正确。回答表以场景作者写入的槽位为键。包中也有 `_multi_question` 的整句兜底文本。沿用本文的逐项交付设计时，复合动作按每项槽位分别查表，整句兜底留作备选实验协议。

## 回复规则

| 情况 | 行为 |
|---|---|
| 命中预设键 | 返回对应文本和 `answered`。预设回复只提供该问题所需的信息。例如询问地点时，回复「港口附近」，无需额外提供预算或推荐 ID。 |
| 问题无法匹配 | 返回该场景的 `fallback_text` 和 `fallback`。同一槽位下其他轮次的回答与 `null` 键都保持独立。 |
| 重复询问同一个键 | 返回原来的回复。Pipeline 对每条实际发出的独立问题扣减预算，评分器根据历史判断是否重复提问。 |
| 缺少场景配置、出现重复键或空回复 | 作为数据配置错误报告。加载时发现的问题应在批量运行前修正。运行时出现的服务错误交给 Pipeline 记录。 |

复合问题通过 `ASK.questions` 传入，每个元素对应一项独立信息。Pipeline 先确认整组问题在预算内，再分别查表。它把问题作为一条助手消息发送，把各条回复按提问顺序合成一条用户消息，并逐项记录回复状态。预算不足时整组问题都不发出，也不调用 Answer Service。

## 联调示例

1. 在 `SS-AMB-01-A` 中，用户要求泰餐、纯素选项和 $25 预算。港口解释允许 `R03`，校园解释允许 `R30`。假设策略问「你指的是港口还是校园？」且归一化结果为 `location`、`t07`，服务返回 `Near the harbor.`。
2. Pipeline 加入用户消息并把更新后的对话交回策略。策略可以据此推荐 `R03`，由评分器独立验证。
3. 在 v9 的配对场景 `SS-AMB-01-B` 中，预算是 $35，`R02` 满足两种地点解释。策略若直接推荐，Pipeline 直接结束这次运行。

## 验收用例

| 用例 | 预期 |
|---|---|
| 两种不同措辞归一化到同一个键 | 返回相同文本和 `answered`。 |
| 精确匹配时同一槽位指向错误轮次，或问题归为 `other` | 返回该场景的固定兜底文本和 `fallback`。 |
| 两个场景有相同的问题键 | 读取各自的预设回答，场景之间互不影响。 |
| 同一问题键存在精确引用和 `null` 版本 | 分别命中对应配置，具体轮次查不到时返回 `fallback`。 |
| 策略重复发出同一个可回答的问题 | 两次回复一致，运行记录保留两次提问。 |
| 预算为 1，策略在同一动作中请求地点和菜系 | Pipeline 拦截整个动作，答复调用次数为 0。 |
| 回答表中同一场景出现重复键 | 加载校验失败，并指明场景 ID 和重复的键。 |
