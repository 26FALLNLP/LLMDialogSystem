# BB- draft scenarios (under review)

206 scenarios written by Bhavishya and converted to the same format as `data/scenarios/`
(nlp-quota-v3): every variant of an ambiguity group shares one chat, and the variants
cover every hidden target. They are **not** part of the main dataset until the team
approves them and the wording is regenerated with Qwen.

| File | What it is |
|---|---|
| `scenarios/*.json` | The scenarios. IDs start with `BB-`; `-H1`, `-H2`, ... are the hidden-target variants of one chat |
| `dataset-manifest.json` | Groups, required slots, composition and data version, like `data/dataset-manifest.json` |
| `review_sheet.md` | One section per group: chat plan, hidden goals, candidate restaurants per meaning, ask decision, questions needed |
| `conversion_report.json` | Which old drafts were kept or dropped, and why |
| `convert_drafts.py` | Rebuilds `scenarios/` and the manifest from the old drafts on branch `bhavishya/complete-data-and-eval` |
| `make_review_sheet.py` | Rebuilds `review_sheet.md` |

## How they were converted

- Each old draft chat that needs a question became a group with one variant per possible
  meaning (2, or 4 for two-question chats). The old draft's own hidden goal is kept
  unchanged as one of the variants (`draft_info.original_hidden_goal`); the others are added targets.
- Chats that need no question stay single-scenario groups.
- Dropped (7): 5 had the same setup as a scenario already in main's 48 (including the old
  fix of XX-AMB-02 and a two-question chat equal to XX-AMB-12), and 2 repeated the setup of
  another draft family.
- Old draft-only notes (part, ambiguity kind, mention order, fix notes, ...) are kept under
  `evaluation_only.draft_info`.

## Check them

```sh
python3 data/validate.py --scenarios data/scenarios data/drafts/bhavishya/scenarios \
  --manifest data/dataset-manifest.json data/drafts/bhavishya/dataset-manifest.json --log /tmp/quality_log.csv
```

Current result: 254 scenarios, 0 FAIL, 3 WARN (the WARNs are main's XX-AMB-03A, 04A and 07C).

## Before final testing

1. Review every group in `review_sheet.md`.
2. Regenerate the wording with Qwen: rewrite only `model_visible.dialogue_prefix[*].text`
   from the `turn_plan`, set `text_source` to the Qwen model and version, keep
   `evaluation_only` unchanged, then re-run the validator and the review sheet. All variants
   of a group must get the same new chat.
3. After any data change, remake the split (`python -m src.make_split --force`, only if the
   team agrees) because the split records the data version.
