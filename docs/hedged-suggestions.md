# Drafts where the user hedges on a suggestion

**Team decision needed.** In these chats the assistant suggests a different cuisine, area or budget, and the user answers without clearly saying yes or no ("maybe", "not sure", "possibly", ...).

- **Current rule (keep original):** a hedge is *not* acceptance. The original requirement stays, the suggestion is recorded as "proposed, not accepted", and the system should recommend without asking (`should_ask: false`). This matches the S1 prompt ("do not infer agreement from uncertainty") and main's XX-SUG-03A (and the archived XX-SUG-01A).
- **Alternative (ask):** a hedge leaves the requirement unclear, so it becomes an unresolved item with two readings (original vs suggested). Then the system should ask **only if** no restaurant fits both readings - the last column shows what would change.

If the team picks "ask", the gold labels of the rows marked *would become should-ask* must change; nothing has been changed yet.

| Scenario | Assistant suggestion | User reply | Original -> suggested | Restaurants fitting both | If hedge = unclear |
|---|---|---|---|---|---|
| BB-SUG-01A | There are also some nice Indian places near the station. Would Indian work instead? | Hmm, I'll think about it. | cuisine: Chinese -> Indian | none | **would become should-ask** (no restaurant fits both) |
| BB-SUG-02A | There are also some nice Italian places near the station. Would Italian work instead? | Maybe, I'm not sure yet. | cuisine: Indian -> Italian | none | **would become should-ask** (no restaurant fits both) |
| BB-SUG-03A | There are also some nice Mexican places near the station. Would Mexican work instead? | I don't know, possibly. | cuisine: Mediterranean -> Mexican | none | **would become should-ask** (no restaurant fits both) |
| BB-SUG-04A | There are also some nice Korean places near the mall. Would Korean work instead? | Let me think about that one. | cuisine: Italian -> Korean | none | **would become should-ask** (no restaurant fits both) |
| BB-SUG-05A | The mall area also has Chinese food in that range. Want me to look there instead? | I'm not sure about that yet. | location: station -> mall | none | **would become should-ask** (no restaurant fits both) |
| BB-SUG-06A | The station area also has Italian food in that range. Want me to look there instead? | Hmm, maybe another time. | location: mall -> station | none | **would become should-ask** (no restaurant fits both) |
| BB-SUG-07A | The mall area also has Italian food in that range. Want me to look there instead? | Possibly, we'll see. | location: station -> mall | none | **would become should-ask** (no restaurant fits both) |

7 drafts hedge; 7 of them would become should-ask under the alternative rule (they were built as suggestion traps, so the readings never overlap).

## Not a hedge, but also not an answer

The user ignores the suggestion and changes the subject. Under both rules the original stays.

| Scenario | Assistant suggestion | User reply |
|---|---|---|
| BB-SUG-08A | The station area also has Japanese food in that range. Want me to look there instead? | Oh, by the way, this is for my dad's birthday. |

## For comparison: main's scenarios with an unaccepted suggestion

| Scenario | Assistant suggestion | User reply | Reply type | Original -> suggested | Restaurants fitting both |
|---|---|---|---|---|---|
| XX-SUG-03A | The area around the mall has some nice options. Want me to look there? | Maybe, I'm not sure yet. | hedge | location: None -> mall | R02 |
| XX-SUG-05 | How about Indian near the mall? There are good options there. | The mall works, but not Indian. | clear answer | cuisine: None -> Indian | none |

Regenerate this file with `python scripts/make_reports.py`.
