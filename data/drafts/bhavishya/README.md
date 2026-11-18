# Bhavishya's draft scenarios (BB-)

**Drafts only.** Nothing in this folder is part of the dataset yet. The 36 original
scenarios in `data/scenarios/` and the frozen split in `data/splits/split.json`
are unchanged. These files enter the dataset only after human review and the
Qwen rewording step below.

All 138 drafts use the repo's exact scenario format and the database the code
uses today, `data/restaurants.json` (`near_station` / `near_mall` /
`vegetarian_options` / `open_for_dinner`). The team harbor/campus database
(`near_harbor` / `near_campus` / `vegan_options` / `open_late`) is **not in the
repository**, so it could not be used. Every file is marked
`text_source = "draft by Claude; wording to be regenerated with Qwen before testing"`.

## What is in each folder

| Folder | Part | Scenarios | What it is |
|---|---|---|---|
| `should_ask_pairs/` | 4a | 40 (20 A/B pairs) | A: no restaurant fits every meaning, so the model must ask. B: exactly one change creates a safe choice, so it should not ask. 10 location pairs ("near there", "over that side", ...), 5 cuisine-reference pairs ("Maya's recommendation"), 5 ordinal pairs ("the second place you mentioned") |
| `swapped_twins/` | 4c | 40 (20 pairs, `-SW`) | Each 4a pair with the options mentioned in the opposite order and the hidden answer flipped. Same template family as the original |
| `paraphrases/` | 4e | 20 (`-P1`, `-P2`) | 5 of the location pairs, each reworded twice, same answer key, same family |
| `two_question/` | 4b | 8 | Cuisine AND area both unclear: one question is not enough, two are (`questions_needed: 2`, scripted answers for both) |
| `suggestion_traps/` | 4d | 16 (8 A/B) | A: the bot suggests another cuisine/area, the user does not accept; treating it as accepted gives a WRONG restaurant. B: the user accepts (control) |
| `long_dialogues/` | 4f | 8 | 9-10 turns with the key detail in the first two messages: 4 clear ones (forgetting the detail gives a wrong restaurant) and 2 ambiguous A/B pairs |
| `fixes/` | 4g | 6 | Fixed versions of XX-AMB-02, 03, 04 (A and B). Each file has a `fix_note` saying which hint was removed. The originals are not edited |
| `annotation/` | 5g | 30 items | Blank labeling sheet for a second annotator (`labeling_sheet.md`, `labels_template.csv`). `item_key.csv` maps items to scenarios; the annotator must not open it |

Other files:

- `build_drafts.py` rebuilds every draft from the database: `python data/drafts/bhavishya/build_drafts.py`
- `make_review_sheet.py` writes `review_sheet.md`: every draft with its chat plan, hidden goal, candidate restaurants per meaning, ask decision and number of questions needed
- `draft_split_proposal.json`: a **proposed** dev/test split for the drafts (family level, 25% dev, stratified by family type, seed 6120). It is not frozen; decide before any test run

## How the drafts were made (and checked)

1. A search over the database found configurations where every meaning has 1-3
   restaurants, no restaurant fits all meanings (A), one change creates a shared
   restaurant (B), and no meaning has a "clearly better" restaurant.
2. Every candidate set, ask decision and `questions_needed` was computed with the
   validator's own functions. The generator refuses to write a file the validator would FAIL.
3. Hidden answers were assigned from explicit balance tables. Across the drafts:
   hidden = first-mentioned option 51%, last-mentioned 52%, hidden location
   station 26 / mall 26, hidden option has the cheapest restaurant 44%, and the
   hidden option alone is clearly better in 0%.
4. `python data/validate.py --db data/restaurants.json --scenarios data/drafts/bhavishya`
   gives 138 scenarios, 0 FAIL, 0 WARN.

## Known limits (please read)

- **"Clearly better" rule.** With 40 restaurants nearly every pair differs by a few
  dollars, so a restaurant counts as clearly better only if it is better on a feature
  (near both areas, vegetarian, open for dinner) or more than $5 cheaper, and not worse
  on anything. Smaller price gaps remain in single scenarios. The swapped twins make
  them balance out across the dataset.
- **Cuisine-reference B variants** use "Either of those cuisines is fine" as the one
  change, because a single restaurant cannot serve two cuisines (same as XX-AMB-03B).
- **"The second place"** is done as an ordinal reference to areas listed twice in
  opposite orders. The schema has no restaurant-ID slot, so a reference to one named
  restaurant cannot be scored.
- **Two-question scenarios:** only 4 distinct hint-free setups exist in this database,
  so each is used twice (different budget or restaurants, mention order and hidden answer).
- **Fixes 03 and 04** needed new constraints (Mexican vs Thai always had a clearly
  better Mexican option; Mediterranean near the mall was always $9+ cheaper). The
  hidden answer (Mexican, mall) is kept; `fix_note` lists every change.
- The hint detector cannot see **real-world logic** hints (for example "dinner tonight"
  meaning "at home"). Only a human read-through can catch those.

## What still needs a human

1. **Review every answer key** in `review_sheet.md` (tick the boxes).
2. **Regenerate the wording with Qwen** (below).
3. **Second annotator:** a teammate fills `annotation/labels_template.csv`; then
   `python scripts/annotator_agreement.py export-gold --out labels_author.csv` and
   `python scripts/annotator_agreement.py kappa labels_author.csv labels_teammate.csv`.
4. Decide the dev/test split for the drafts (start from `draft_split_proposal.json`).
5. Move approved files into `data/scenarios/` only after steps 1-4.

## Qwen regeneration step

The drafts were worded by Claude, and Claude is one of the tested models. To avoid
testing Claude on its own wording:

1. For each draft, give Qwen the `turn_plan` (one act per turn) plus the draft text as a
   reference, and ask it to rewrite each turn's `text` naturally, without adding any
   requirement, hint or detail that is not in the plan. The team's shared generation
   tool is not in this repo, so the exact Qwen prompt and model version are the team's choice.
2. Change only `model_visible.dialogue_prefix[*].text` and set `text_source` to the Qwen
   model and version. Do **not** change `evaluation_only`.
3. Re-run the validator (it checks leakage, unverifiable words and A/B one-turn
   differences) and `make_review_sheet.py`, then read the new wording for hints again.
