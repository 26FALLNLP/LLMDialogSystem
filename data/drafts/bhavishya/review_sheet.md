# Draft review sheet (Bhavishya, BB-)

Every draft scenario with its chat plan, hidden goal, candidate restaurants per meaning, ask decision and number of questions needed. All sets were computed from `data/restaurants.json` by code. Tick the boxes after checking each answer key by hand.

Wording is a Claude draft and must be regenerated with Qwen before testing.

## Contents

- 4a Should-ask A/B pairs: 40 scenarios (`should_ask_pairs/`)
- 4c Swapped-order twins: 40 scenarios (`swapped_twins/`)
- 4e Paraphrase versions: 20 scenarios (`paraphrases/`)
- 4b Two-question scenarios: 8 scenarios (`two_question/`)
- 4d Suggestion traps (with accepted controls): 16 scenarios (`suggestion_traps/`)
- 4f Long conversations: 8 scenarios (`long_dialogues/`)
- 4g Fixed versions of guessable originals: 6 scenarios (`fixes/`)

# 4a: Should-ask A/B pairs

---

## BB-CUI-01A  (ambiguous_reference, family BB-CUI-01, variant A)

*Contrast:* A: Japanese -> R01 Sakura Ramen ($18); Mediterranean -> R39 Falafel Stop ($11); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Japanese, one Mediterranean. | user mentions two cuisines (Japanese first, Mediterranean second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | I'd like somewhere near the station. | user states location=station |
| 4 | assistant | Got it, near the station. | assistant acknowledges |
| 5 | user | No more than $18 a person. It's for lunch. | user states max_price=18, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Let's go with Maya's recommendation. | user: 'Maya's recommendation' = Japanese or Mediterranean (UNRESOLVED; hidden: Japanese) |

**Hidden goal:** `{"max_price": 18, "location": "station", "cuisine": "Japanese"}`  
**Gold active state:** `{"max_price": 18, "location": "station"}`  
**Unresolved:** 'Maya's recommendation' (turn 7, slot cuisine)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"cuisine": "Japanese"}` -> R01 Sakura Ramen ($18)  
&nbsp;&nbsp;- `{"cuisine": "Mediterranean"}` -> R39 Falafel Stop ($11)  
**Mention order in the chat:** `["Japanese", "Mediterranean"]`  
**Should ask:** YES - cuisine@t7  
**Questions needed:** 1  
**Successful recommendations:** R01 Sakura Ramen ($18)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-CUI-01B  (ambiguous_reference, family BB-CUI-01, variant B)

*Contrast:* A: Japanese -> R01 Sakura Ramen ($18); Mediterranean -> R39 Falafel Stop ($11); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Japanese, one Mediterranean. | user mentions two cuisines (Japanese first, Mediterranean second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | I'd like somewhere near the station. | user states location=station |
| 4 | assistant | Got it, near the station. | assistant acknowledges |
| 5 | user | No more than $18 a person. It's for lunch. | user states max_price=18, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Either of those cuisines is fine with me. | user: cuisine in {Japanese, Mediterranean}; disjunction, not ambiguity |

**Hidden goal:** `{"max_price": 18, "location": "station", "cuisine": ["Japanese", "Mediterranean"]}`  
**Gold active state:** `{"max_price": 18, "location": "station", "cuisine": ["Japanese", "Mediterranean"]}`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R01 Sakura Ramen ($18), R39 Falafel Stop ($11)  
**Safe without asking:** R01 Sakura Ramen ($18), R39 Falafel Stop ($11)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-CUI-02A  (ambiguous_reference, family BB-CUI-02, variant A)

*Contrast:* A: Thai -> R16 Bangkok Street ($17); Italian -> R08 Forno Pizza ($16); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Thai, one Italian. | user mentions two cuisines (Thai first, Italian second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | The area doesn't matter to me. | user: no location constraint |
| 4 | assistant | Okay, anywhere works. | assistant acknowledges |
| 5 | user | No more than $17 a person. It's for lunch. | user states max_price=17, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Let's go with Sam's recommendation. | user: 'Sam's recommendation' = Thai or Italian (UNRESOLVED; hidden: Italian) |

**Hidden goal:** `{"max_price": 17, "cuisine": "Italian"}`  
**Gold active state:** `{"max_price": 17}`  
**Unresolved:** 'Sam's recommendation' (turn 7, slot cuisine)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"cuisine": "Thai"}` -> R16 Bangkok Street ($17)  
&nbsp;&nbsp;- `{"cuisine": "Italian"}` -> R08 Forno Pizza ($16)  
**Mention order in the chat:** `["Thai", "Italian"]`  
**Should ask:** YES - cuisine@t7  
**Questions needed:** 1  
**Successful recommendations:** R08 Forno Pizza ($16)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-CUI-02B  (ambiguous_reference, family BB-CUI-02, variant B)

*Contrast:* A: Thai -> R16 Bangkok Street ($17); Italian -> R08 Forno Pizza ($16); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Thai, one Italian. | user mentions two cuisines (Thai first, Italian second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | The area doesn't matter to me. | user: no location constraint |
| 4 | assistant | Okay, anywhere works. | assistant acknowledges |
| 5 | user | No more than $17 a person. It's for lunch. | user states max_price=17, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Either of those cuisines is fine with me. | user: cuisine in {Thai, Italian}; disjunction, not ambiguity |

**Hidden goal:** `{"max_price": 17, "cuisine": ["Thai", "Italian"]}`  
**Gold active state:** `{"max_price": 17, "cuisine": ["Thai", "Italian"]}`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R08 Forno Pizza ($16), R16 Bangkok Street ($17)  
**Safe without asking:** R08 Forno Pizza ($16), R16 Bangkok Street ($17)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-CUI-03A  (ambiguous_reference, family BB-CUI-03, variant A)

*Contrast:* A: Indian -> R24 Dosa Corner ($13); Korean -> R27 Bibim Bowl ($15); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Indian, one Korean. | user mentions two cuisines (Indian first, Korean second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | The area doesn't matter to me. | user: no location constraint |
| 4 | assistant | Okay, anywhere works. | assistant acknowledges |
| 5 | user | No more than $15 a person. It's for lunch. | user states max_price=15, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Let's go with Priya's recommendation. | user: 'Priya's recommendation' = Indian or Korean (UNRESOLVED; hidden: Indian) |

**Hidden goal:** `{"max_price": 15, "cuisine": "Indian"}`  
**Gold active state:** `{"max_price": 15}`  
**Unresolved:** 'Priya's recommendation' (turn 7, slot cuisine)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"cuisine": "Indian"}` -> R24 Dosa Corner ($13)  
&nbsp;&nbsp;- `{"cuisine": "Korean"}` -> R27 Bibim Bowl ($15)  
**Mention order in the chat:** `["Indian", "Korean"]`  
**Should ask:** YES - cuisine@t7  
**Questions needed:** 1  
**Successful recommendations:** R24 Dosa Corner ($13)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-CUI-03B  (ambiguous_reference, family BB-CUI-03, variant B)

*Contrast:* A: Indian -> R24 Dosa Corner ($13); Korean -> R27 Bibim Bowl ($15); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Indian, one Korean. | user mentions two cuisines (Indian first, Korean second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | The area doesn't matter to me. | user: no location constraint |
| 4 | assistant | Okay, anywhere works. | assistant acknowledges |
| 5 | user | No more than $15 a person. It's for lunch. | user states max_price=15, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Either of those cuisines is fine with me. | user: cuisine in {Indian, Korean}; disjunction, not ambiguity |

**Hidden goal:** `{"max_price": 15, "cuisine": ["Indian", "Korean"]}`  
**Gold active state:** `{"max_price": 15, "cuisine": ["Indian", "Korean"]}`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R24 Dosa Corner ($13), R27 Bibim Bowl ($15)  
**Safe without asking:** R24 Dosa Corner ($13), R27 Bibim Bowl ($15)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-CUI-04A  (ambiguous_reference, family BB-CUI-04, variant A)

*Contrast:* A: Italian -> R08 Forno Pizza ($16); Chinese -> R32 Dumpling King ($13), R35 Noodle Bar 88 ($16); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Italian, one Chinese. | user mentions two cuisines (Italian first, Chinese second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | The area doesn't matter to me. | user: no location constraint |
| 4 | assistant | Okay, anywhere works. | assistant acknowledges |
| 5 | user | No more than $16 a person. It's for lunch. | user states max_price=16, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Let's go with Leo's recommendation. | user: 'Leo's recommendation' = Italian or Chinese (UNRESOLVED; hidden: Chinese) |

**Hidden goal:** `{"max_price": 16, "cuisine": "Chinese"}`  
**Gold active state:** `{"max_price": 16}`  
**Unresolved:** 'Leo's recommendation' (turn 7, slot cuisine)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"cuisine": "Italian"}` -> R08 Forno Pizza ($16)  
&nbsp;&nbsp;- `{"cuisine": "Chinese"}` -> R32 Dumpling King ($13), R35 Noodle Bar 88 ($16)  
**Mention order in the chat:** `["Italian", "Chinese"]`  
**Should ask:** YES - cuisine@t7  
**Questions needed:** 1  
**Successful recommendations:** R32 Dumpling King ($13), R35 Noodle Bar 88 ($16)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-CUI-04B  (ambiguous_reference, family BB-CUI-04, variant B)

*Contrast:* A: Italian -> R08 Forno Pizza ($16); Chinese -> R32 Dumpling King ($13), R35 Noodle Bar 88 ($16); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Italian, one Chinese. | user mentions two cuisines (Italian first, Chinese second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | The area doesn't matter to me. | user: no location constraint |
| 4 | assistant | Okay, anywhere works. | assistant acknowledges |
| 5 | user | No more than $16 a person. It's for lunch. | user states max_price=16, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Either of those cuisines is fine with me. | user: cuisine in {Italian, Chinese}; disjunction, not ambiguity |

**Hidden goal:** `{"max_price": 16, "cuisine": ["Italian", "Chinese"]}`  
**Gold active state:** `{"max_price": 16, "cuisine": ["Italian", "Chinese"]}`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R08 Forno Pizza ($16), R32 Dumpling King ($13), R35 Noodle Bar 88 ($16)  
**Safe without asking:** R08 Forno Pizza ($16), R32 Dumpling King ($13), R35 Noodle Bar 88 ($16)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-CUI-05A  (ambiguous_reference, family BB-CUI-05, variant A)

*Contrast:* A: Japanese -> R04 Tsuki Bento ($14); Thai -> R16 Bangkok Street ($17); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Japanese, one Thai. | user mentions two cuisines (Japanese first, Thai second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | The area doesn't matter to me. | user: no location constraint |
| 4 | assistant | Okay, anywhere works. | assistant acknowledges |
| 5 | user | No more than $17 a person. It's for lunch. | user states max_price=17, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Let's go with Nora's recommendation. | user: 'Nora's recommendation' = Japanese or Thai (UNRESOLVED; hidden: Thai) |

**Hidden goal:** `{"max_price": 17, "cuisine": "Thai"}`  
**Gold active state:** `{"max_price": 17}`  
**Unresolved:** 'Nora's recommendation' (turn 7, slot cuisine)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"cuisine": "Japanese"}` -> R04 Tsuki Bento ($14)  
&nbsp;&nbsp;- `{"cuisine": "Thai"}` -> R16 Bangkok Street ($17)  
**Mention order in the chat:** `["Japanese", "Thai"]`  
**Should ask:** YES - cuisine@t7  
**Questions needed:** 1  
**Successful recommendations:** R16 Bangkok Street ($17)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-CUI-05B  (ambiguous_reference, family BB-CUI-05, variant B)

*Contrast:* A: Japanese -> R04 Tsuki Bento ($14); Thai -> R16 Bangkok Street ($17); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Japanese, one Thai. | user mentions two cuisines (Japanese first, Thai second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | The area doesn't matter to me. | user: no location constraint |
| 4 | assistant | Okay, anywhere works. | assistant acknowledges |
| 5 | user | No more than $17 a person. It's for lunch. | user states max_price=17, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Either of those cuisines is fine with me. | user: cuisine in {Japanese, Thai}; disjunction, not ambiguity |

**Hidden goal:** `{"max_price": 17, "cuisine": ["Japanese", "Thai"]}`  
**Gold active state:** `{"max_price": 17, "cuisine": ["Japanese", "Thai"]}`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R04 Tsuki Bento ($14), R16 Bangkok Street ($17)  
**Safe without asking:** R04 Tsuki Bento ($14), R16 Bangkok Street ($17)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-01A  (ambiguous_reference, family BB-LOC-01, variant A)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R02 Hoshi Sushi Bar ($24), R07 Nonna's Kitchen ($27), R09 Osteria Verde ($34); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Italian or Japanese food, either is fine. | user states cuisine=['Italian', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $35 per person. | user states max_price=35 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. I also need vegetarian options. | user states meal=dinner (dinner=true), vegetarian=true |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Can you find me something near there? | user: 'Can you find me something near there?' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Italian", "Japanese"], "max_price": 35, "vegetarian": true, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Italian", "Japanese"], "max_price": 35, "vegetarian": true, "dinner": true}`  
**Unresolved:** 'Can you find me something near there?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R07 Nonna's Kitchen ($27), R09 Osteria Verde ($34)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R06 Trattoria Lucca ($22)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-01B  (ambiguous_reference, family BB-LOC-01, variant B)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R02 Hoshi Sushi Bar ($24), R07 Nonna's Kitchen ($27), R09 Osteria Verde ($34); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Italian or Japanese food, either is fine. | user states cuisine=['Italian', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $35 per person. | user states max_price=35 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for lunch. I also need vegetarian options. | user states meal=lunch (no dinner constraint), vegetarian=true |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Can you find me something near there? | user: 'Can you find me something near there?' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Italian", "Japanese"], "max_price": 35, "vegetarian": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Italian", "Japanese"], "max_price": 35, "vegetarian": true}`  
**Unresolved:** 'Can you find me something near there?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22), R08 Forno Pizza ($16)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R07 Nonna's Kitchen ($27), R08 Forno Pizza ($16), R09 Osteria Verde ($34)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R06 Trattoria Lucca ($22), R08 Forno Pizza ($16)  
**Safe without asking:** R08 Forno Pizza ($16)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-02A  (ambiguous_reference, family BB-LOC-02, variant A)

*Contrast:* A: station -> R16 Bangkok Street ($17), R28 Kimchi Pot ($22); mall -> R17 Lotus Thai ($23), R27 Bibim Bowl ($15), R29 Hanok Table ($27); nothing near both -> ask. B: budget $50 makes R20 Royal Orchid ($48) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Korean or Thai food, either is fine. | user states cuisine=['Korean', 'Thai'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $30 per person. | user states max_price=30 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's look over that side. | user: 'Let's look over that side.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Korean", "Thai"], "max_price": 30, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Korean", "Thai"], "max_price": 30}`  
**Unresolved:** 'Let's look over that side.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R17 Lotus Thai ($23), R27 Bibim Bowl ($15), R29 Hanok Table ($27)  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17), R28 Kimchi Pot ($22)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R16 Bangkok Street ($17), R28 Kimchi Pot ($22)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-02B  (ambiguous_reference, family BB-LOC-02, variant B)

*Contrast:* A: station -> R16 Bangkok Street ($17), R28 Kimchi Pot ($22); mall -> R17 Lotus Thai ($23), R27 Bibim Bowl ($15), R29 Hanok Table ($27); nothing near both -> ask. B: budget $50 makes R20 Royal Orchid ($48) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Korean or Thai food, either is fine. | user states cuisine=['Korean', 'Thai'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $50 per person. | user states max_price=50 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's look over that side. | user: 'Let's look over that side.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Korean", "Thai"], "max_price": 50, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Korean", "Thai"], "max_price": 50}`  
**Unresolved:** 'Let's look over that side.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R17 Lotus Thai ($23), R18 Siam Garden ($31), R20 Royal Orchid ($48), R27 Bibim Bowl ($15), R29 Hanok Table ($27)  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17), R20 Royal Orchid ($48), R26 Seoul BBQ ($36), R28 Kimchi Pot ($22)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R16 Bangkok Street ($17), R20 Royal Orchid ($48), R26 Seoul BBQ ($36), R28 Kimchi Pot ($22)  
**Safe without asking:** R20 Royal Orchid ($48)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-03A  (ambiguous_reference, family BB-LOC-03, variant A)

*Contrast:* A: station -> R11 Taco Loco ($12); mall -> R35 Noodle Bar 88 ($16), R37 Pita Port ($14); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16), R39 Falafel Stop ($11) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm looking for somewhere to eat. | user states no cuisine preference |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $16 per person. | user states max_price=16 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Something around that area would be great. | user: 'Something around that area would be great.' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"max_price": 16, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"max_price": 16, "dinner": true}`  
**Unresolved:** 'Something around that area would be great.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R35 Noodle Bar 88 ($16), R37 Pita Port ($14)  
&nbsp;&nbsp;- `{"location": "station"}` -> R11 Taco Loco ($12)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R35 Noodle Bar 88 ($16), R37 Pita Port ($14)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-03B  (ambiguous_reference, family BB-LOC-03, variant B)

*Contrast:* A: station -> R11 Taco Loco ($12); mall -> R35 Noodle Bar 88 ($16), R37 Pita Port ($14); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16), R39 Falafel Stop ($11) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm looking for somewhere to eat. | user states no cuisine preference |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $16 per person. | user states max_price=16 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Something around that area would be great. | user: 'Something around that area would be great.' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"max_price": 16, "location": "mall"}`  
**Gold active state:** `{"max_price": 16}`  
**Unresolved:** 'Something around that area would be great.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R08 Forno Pizza ($16), R27 Bibim Bowl ($15), R35 Noodle Bar 88 ($16), R37 Pita Port ($14), R39 Falafel Stop ($11)  
&nbsp;&nbsp;- `{"location": "station"}` -> R08 Forno Pizza ($16), R11 Taco Loco ($12), R32 Dumpling King ($13), R39 Falafel Stop ($11)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R08 Forno Pizza ($16), R27 Bibim Bowl ($15), R35 Noodle Bar 88 ($16), R37 Pita Port ($14), R39 Falafel Stop ($11)  
**Safe without asking:** R08 Forno Pizza ($16), R39 Falafel Stop ($11)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-04A  (ambiguous_reference, family BB-LOC-04, variant A)

*Contrast:* A: station -> R01 Sakura Ramen ($18), R21 Masala House ($20); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: budget $25 makes R23 Saffron Leaf ($25) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Indian or Japanese food, either is fine. | user states cuisine=['Indian', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $24 per person. | user states max_price=24 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Can you check that part of town for me? | user: 'Can you check that part of town for me?' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Indian", "Japanese"], "max_price": 24, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Indian", "Japanese"], "max_price": 24, "dinner": true}`  
**Unresolved:** 'Can you check that part of town for me?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18), R21 Masala House ($20)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R02 Hoshi Sushi Bar ($24)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-04B  (ambiguous_reference, family BB-LOC-04, variant B)

*Contrast:* A: station -> R01 Sakura Ramen ($18), R21 Masala House ($20); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: budget $25 makes R23 Saffron Leaf ($25) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Indian or Japanese food, either is fine. | user states cuisine=['Indian', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Can you check that part of town for me? | user: 'Can you check that part of town for me?' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Indian", "Japanese"], "max_price": 25, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Indian", "Japanese"], "max_price": 25, "dinner": true}`  
**Unresolved:** 'Can you check that part of town for me?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18), R21 Masala House ($20), R23 Saffron Leaf ($25)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R23 Saffron Leaf ($25)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R02 Hoshi Sushi Bar ($24), R23 Saffron Leaf ($25)  
**Safe without asking:** R23 Saffron Leaf ($25)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-05A  (ambiguous_reference, family BB-LOC-05, variant A)

*Contrast:* A: station -> R32 Dumpling King ($13); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $25 makes R31 Golden Dragon ($24) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Chinese or Korean food, either is fine. | user states cuisine=['Chinese', 'Korean'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $15 per person. | user states max_price=15 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Find me a spot over there. | user: 'Find me a spot over there.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Chinese", "Korean"], "max_price": 15, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Korean"], "max_price": 15}`  
**Unresolved:** 'Find me a spot over there.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R32 Dumpling King ($13)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R27 Bibim Bowl ($15)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R32 Dumpling King ($13)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-05B  (ambiguous_reference, family BB-LOC-05, variant B)

*Contrast:* A: station -> R32 Dumpling King ($13); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $25 makes R31 Golden Dragon ($24) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Chinese or Korean food, either is fine. | user states cuisine=['Chinese', 'Korean'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Find me a spot over there. | user: 'Find me a spot over there.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Chinese", "Korean"], "max_price": 25, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Korean"], "max_price": 25}`  
**Unresolved:** 'Find me a spot over there.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R28 Kimchi Pot ($22), R31 Golden Dragon ($24), R32 Dumpling King ($13)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R27 Bibim Bowl ($15), R31 Golden Dragon ($24), R35 Noodle Bar 88 ($16)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R28 Kimchi Pot ($22), R31 Golden Dragon ($24), R32 Dumpling King ($13)  
**Safe without asking:** R31 Golden Dragon ($24)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-06A  (ambiguous_reference, family BB-LOC-06, variant A)

*Contrast:* A: station -> R01 Sakura Ramen ($18); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: budget $30 makes R03 Kumo Izakaya ($29) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm in the mood for Japanese food. | user states cuisine=Japanese |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with that area. What's good there? | user: 'Let's go with that area. What's good there?' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": "Japanese", "max_price": 25, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": "Japanese", "max_price": 25, "dinner": true}`  
**Unresolved:** 'Let's go with that area. What's good there?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24)  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R02 Hoshi Sushi Bar ($24)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-06B  (ambiguous_reference, family BB-LOC-06, variant B)

*Contrast:* A: station -> R01 Sakura Ramen ($18); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: budget $30 makes R03 Kumo Izakaya ($29) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm in the mood for Japanese food. | user states cuisine=Japanese |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $30 per person. | user states max_price=30 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with that area. What's good there? | user: 'Let's go with that area. What's good there?' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": "Japanese", "max_price": 30, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": "Japanese", "max_price": 30, "dinner": true}`  
**Unresolved:** 'Let's go with that area. What's good there?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R03 Kumo Izakaya ($29)  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18), R03 Kumo Izakaya ($29)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R02 Hoshi Sushi Bar ($24), R03 Kumo Izakaya ($29)  
**Safe without asking:** R03 Kumo Izakaya ($29)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-07A  (ambiguous_reference, family BB-LOC-07, variant A)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Italian or Japanese food, either is fine. | user states cuisine=['Italian', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. I also need vegetarian options. | user states meal=dinner (dinner=true), vegetarian=true |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Somewhere near there works for me. | user: 'Somewhere near there works for me.' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Italian", "Japanese"], "max_price": 25, "vegetarian": true, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Italian", "Japanese"], "max_price": 25, "vegetarian": true, "dinner": true}`  
**Unresolved:** 'Somewhere near there works for me.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R02 Hoshi Sushi Bar ($24)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-07B  (ambiguous_reference, family BB-LOC-07, variant B)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Italian or Japanese food, either is fine. | user states cuisine=['Italian', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for lunch. I also need vegetarian options. | user states meal=lunch (no dinner constraint), vegetarian=true |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Somewhere near there works for me. | user: 'Somewhere near there works for me.' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Italian", "Japanese"], "max_price": 25, "vegetarian": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Italian", "Japanese"], "max_price": 25, "vegetarian": true}`  
**Unresolved:** 'Somewhere near there works for me.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22), R08 Forno Pizza ($16)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R08 Forno Pizza ($16)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R02 Hoshi Sushi Bar ($24), R08 Forno Pizza ($16)  
**Safe without asking:** R08 Forno Pizza ($16)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-08A  (ambiguous_reference, family BB-LOC-08, variant A)

*Contrast:* A: station -> R21 Masala House ($20); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: budget $25 makes R23 Saffron Leaf ($25) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Indian or Japanese food, either is fine. | user states cuisine=['Indian', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $24 per person. | user states max_price=24 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. I also need vegetarian options. | user states meal=dinner (dinner=true), vegetarian=true |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Pick something on that side, please. | user: 'Pick something on that side, please.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Indian", "Japanese"], "max_price": 24, "vegetarian": true, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Indian", "Japanese"], "max_price": 24, "vegetarian": true, "dinner": true}`  
**Unresolved:** 'Pick something on that side, please.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24)  
&nbsp;&nbsp;- `{"location": "station"}` -> R21 Masala House ($20)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R21 Masala House ($20)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-08B  (ambiguous_reference, family BB-LOC-08, variant B)

*Contrast:* A: station -> R21 Masala House ($20); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: budget $25 makes R23 Saffron Leaf ($25) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Indian or Japanese food, either is fine. | user states cuisine=['Indian', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. I also need vegetarian options. | user states meal=dinner (dinner=true), vegetarian=true |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Pick something on that side, please. | user: 'Pick something on that side, please.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Indian", "Japanese"], "max_price": 25, "vegetarian": true, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Indian", "Japanese"], "max_price": 25, "vegetarian": true, "dinner": true}`  
**Unresolved:** 'Pick something on that side, please.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R23 Saffron Leaf ($25)  
&nbsp;&nbsp;- `{"location": "station"}` -> R21 Masala House ($20), R23 Saffron Leaf ($25)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R21 Masala House ($20), R23 Saffron Leaf ($25)  
**Safe without asking:** R23 Saffron Leaf ($25)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-09A  (ambiguous_reference, family BB-LOC-09, variant A)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R07 Nonna's Kitchen ($27); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm in the mood for Italian food. | user states cuisine=Italian |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $30 per person. | user states max_price=30 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | I'd like something around there. | user: 'I'd like something around there.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": "Italian", "max_price": 30, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": "Italian", "max_price": 30, "dinner": true}`  
**Unresolved:** 'I'd like something around there.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R07 Nonna's Kitchen ($27)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R06 Trattoria Lucca ($22)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-09B  (ambiguous_reference, family BB-LOC-09, variant B)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R07 Nonna's Kitchen ($27); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm in the mood for Italian food. | user states cuisine=Italian |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $30 per person. | user states max_price=30 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | I'd like something around there. | user: 'I'd like something around there.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": "Italian", "max_price": 30, "location": "station"}`  
**Gold active state:** `{"cuisine": "Italian", "max_price": 30}`  
**Unresolved:** 'I'd like something around there.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22), R08 Forno Pizza ($16)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R07 Nonna's Kitchen ($27), R08 Forno Pizza ($16)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R06 Trattoria Lucca ($22), R08 Forno Pizza ($16)  
**Safe without asking:** R08 Forno Pizza ($16)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-10A  (ambiguous_reference, family BB-LOC-10, variant A)

*Contrast:* A: station -> R16 Bangkok Street ($17), R36 Olive & Thyme ($23), R38 Aegean Table ($33); mall -> R18 Siam Garden ($31), R37 Pita Port ($14), R40 Santorini Grill ($47); nothing near both -> ask. B: budget $50 makes R20 Royal Orchid ($48) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Mediterranean or Thai food, either is fine. | user states cuisine=['Mediterranean', 'Thai'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $47 per person. | user states max_price=47 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Can you look in that area? | user: 'Can you look in that area?' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Mediterranean", "Thai"], "max_price": 47, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Mediterranean", "Thai"], "max_price": 47, "dinner": true}`  
**Unresolved:** 'Can you look in that area?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17), R36 Olive & Thyme ($23), R38 Aegean Table ($33)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R18 Siam Garden ($31), R37 Pita Port ($14), R40 Santorini Grill ($47)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R18 Siam Garden ($31), R37 Pita Port ($14), R40 Santorini Grill ($47)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-10B  (ambiguous_reference, family BB-LOC-10, variant B)

*Contrast:* A: station -> R16 Bangkok Street ($17), R36 Olive & Thyme ($23), R38 Aegean Table ($33); mall -> R18 Siam Garden ($31), R37 Pita Port ($14), R40 Santorini Grill ($47); nothing near both -> ask. B: budget $50 makes R20 Royal Orchid ($48) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Mediterranean or Thai food, either is fine. | user states cuisine=['Mediterranean', 'Thai'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $50 per person. | user states max_price=50 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Can you look in that area? | user: 'Can you look in that area?' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Mediterranean", "Thai"], "max_price": 50, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Mediterranean", "Thai"], "max_price": 50, "dinner": true}`  
**Unresolved:** 'Can you look in that area?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17), R20 Royal Orchid ($48), R36 Olive & Thyme ($23), R38 Aegean Table ($33)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R18 Siam Garden ($31), R20 Royal Orchid ($48), R37 Pita Port ($14), R40 Santorini Grill ($47)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R18 Siam Garden ($31), R20 Royal Orchid ($48), R37 Pita Port ($14), R40 Santorini Grill ($47)  
**Safe without asking:** R20 Royal Orchid ($48)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-01A  (ambiguous_reference, family BB-ORD-01, variant A)

*Contrast:* A: station -> R01 Sakura Ramen ($18); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $30 makes R03 Kumo Izakaya ($29) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Japanese or Korean food, either is fine. | user states cuisine=['Japanese', 'Korean'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $20 per person. | user states max_price=20 |
| 4 | assistant | Okay. With that budget, the station side and the mall side both still have choices. | assistant re-lists the areas in the opposite order (station first, mall second) |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = station (second in turn 2) or mall (second in turn 4) (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Japanese", "Korean"], "max_price": 20, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Japanese", "Korean"], "max_price": 20}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R27 Bibim Bowl ($15)  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R27 Bibim Bowl ($15)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-01B  (ambiguous_reference, family BB-ORD-01, variant B)

*Contrast:* A: station -> R01 Sakura Ramen ($18); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $30 makes R03 Kumo Izakaya ($29) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Japanese or Korean food, either is fine. | user states cuisine=['Japanese', 'Korean'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $30 per person. | user states max_price=30 |
| 4 | assistant | Okay. With that budget, the station side and the mall side both still have choices. | assistant re-lists the areas in the opposite order (station first, mall second) |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = station (second in turn 2) or mall (second in turn 4) (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Japanese", "Korean"], "max_price": 30, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Japanese", "Korean"], "max_price": 30}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R03 Kumo Izakaya ($29), R27 Bibim Bowl ($15), R29 Hanok Table ($27)  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18), R03 Kumo Izakaya ($29), R28 Kimchi Pot ($22)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R02 Hoshi Sushi Bar ($24), R03 Kumo Izakaya ($29), R27 Bibim Bowl ($15), R29 Hanok Table ($27)  
**Safe without asking:** R03 Kumo Izakaya ($29)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-02A  (ambiguous_reference, family BB-ORD-02, variant A)

*Contrast:* A: station -> R16 Bangkok Street ($17); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $50 makes R20 Royal Orchid ($48) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Korean or Thai food, either is fine. | user states cuisine=['Korean', 'Thai'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $20 per person. | user states max_price=20 |
| 4 | assistant | Okay. With that budget, the mall side and the station side both still have choices. | assistant re-lists the areas in the opposite order (mall first, station second) |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = mall (second in turn 2) or station (second in turn 4) (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Korean", "Thai"], "max_price": 20, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Korean", "Thai"], "max_price": 20}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R27 Bibim Bowl ($15)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R27 Bibim Bowl ($15)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-02B  (ambiguous_reference, family BB-ORD-02, variant B)

*Contrast:* A: station -> R16 Bangkok Street ($17); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $50 makes R20 Royal Orchid ($48) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Korean or Thai food, either is fine. | user states cuisine=['Korean', 'Thai'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $50 per person. | user states max_price=50 |
| 4 | assistant | Okay. With that budget, the mall side and the station side both still have choices. | assistant re-lists the areas in the opposite order (mall first, station second) |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = mall (second in turn 2) or station (second in turn 4) (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Korean", "Thai"], "max_price": 50, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Korean", "Thai"], "max_price": 50}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17), R20 Royal Orchid ($48), R26 Seoul BBQ ($36), R28 Kimchi Pot ($22)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R17 Lotus Thai ($23), R18 Siam Garden ($31), R20 Royal Orchid ($48), R27 Bibim Bowl ($15), R29 Hanok Table ($27)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R17 Lotus Thai ($23), R18 Siam Garden ($31), R20 Royal Orchid ($48), R27 Bibim Bowl ($15), R29 Hanok Table ($27)  
**Safe without asking:** R20 Royal Orchid ($48)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-03A  (ambiguous_reference, family BB-ORD-03, variant A)

*Contrast:* A: station -> R21 Masala House ($20); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $25 makes R23 Saffron Leaf ($25) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Indian or Korean food, either is fine. | user states cuisine=['Indian', 'Korean'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $20 per person. | user states max_price=20 |
| 4 | assistant | Okay. With that budget, the mall side and the station side both still have choices. | assistant re-lists the areas in the opposite order (mall first, station second) |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = mall (second in turn 2) or station (second in turn 4) (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Indian", "Korean"], "max_price": 20, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Indian", "Korean"], "max_price": 20}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R21 Masala House ($20)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R27 Bibim Bowl ($15)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R21 Masala House ($20)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-03B  (ambiguous_reference, family BB-ORD-03, variant B)

*Contrast:* A: station -> R21 Masala House ($20); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $25 makes R23 Saffron Leaf ($25) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Indian or Korean food, either is fine. | user states cuisine=['Indian', 'Korean'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Okay. With that budget, the mall side and the station side both still have choices. | assistant re-lists the areas in the opposite order (mall first, station second) |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = mall (second in turn 2) or station (second in turn 4) (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Indian", "Korean"], "max_price": 25, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Indian", "Korean"], "max_price": 25}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R21 Masala House ($20), R23 Saffron Leaf ($25), R28 Kimchi Pot ($22)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R23 Saffron Leaf ($25), R27 Bibim Bowl ($15)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R21 Masala House ($20), R23 Saffron Leaf ($25), R28 Kimchi Pot ($22)  
**Safe without asking:** R23 Saffron Leaf ($25)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-04A  (ambiguous_reference, family BB-ORD-04, variant A)

*Contrast:* A: station -> R01 Sakura Ramen ($18); mall -> R35 Noodle Bar 88 ($16); nothing near both -> ask. B: budget $25 makes R31 Golden Dragon ($24) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Chinese or Japanese food, either is fine. | user states cuisine=['Chinese', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $20 per person. | user states max_price=20 |
| 4 | assistant | Okay. With that budget, the station side and the mall side both still have choices. | assistant re-lists the areas in the opposite order (station first, mall second) |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = station (second in turn 2) or mall (second in turn 4) (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Chinese", "Japanese"], "max_price": 20, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Japanese"], "max_price": 20, "dinner": true}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R35 Noodle Bar 88 ($16)  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R01 Sakura Ramen ($18)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-04B  (ambiguous_reference, family BB-ORD-04, variant B)

*Contrast:* A: station -> R01 Sakura Ramen ($18); mall -> R35 Noodle Bar 88 ($16); nothing near both -> ask. B: budget $25 makes R31 Golden Dragon ($24) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Chinese or Japanese food, either is fine. | user states cuisine=['Chinese', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Okay. With that budget, the station side and the mall side both still have choices. | assistant re-lists the areas in the opposite order (station first, mall second) |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = station (second in turn 2) or mall (second in turn 4) (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Chinese", "Japanese"], "max_price": 25, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Japanese"], "max_price": 25, "dinner": true}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R31 Golden Dragon ($24), R35 Noodle Bar 88 ($16)  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18), R31 Golden Dragon ($24)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R01 Sakura Ramen ($18), R31 Golden Dragon ($24)  
**Safe without asking:** R31 Golden Dragon ($24)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-05A  (ambiguous_reference, family BB-ORD-05, variant A)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R35 Noodle Bar 88 ($16); nothing near both -> ask. B: budget $25 makes R31 Golden Dragon ($24) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Chinese or Italian food, either is fine. | user states cuisine=['Chinese', 'Italian'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $22 per person. | user states max_price=22 |
| 4 | assistant | Okay. With that budget, the mall side and the station side both still have choices. | assistant re-lists the areas in the opposite order (mall first, station second) |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = mall (second in turn 2) or station (second in turn 4) (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Chinese", "Italian"], "max_price": 22, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Italian"], "max_price": 22, "dinner": true}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R35 Noodle Bar 88 ($16)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R06 Trattoria Lucca ($22)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-05B  (ambiguous_reference, family BB-ORD-05, variant B)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R35 Noodle Bar 88 ($16); nothing near both -> ask. B: budget $25 makes R31 Golden Dragon ($24) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Chinese or Italian food, either is fine. | user states cuisine=['Chinese', 'Italian'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Okay. With that budget, the mall side and the station side both still have choices. | assistant re-lists the areas in the opposite order (mall first, station second) |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = mall (second in turn 2) or station (second in turn 4) (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Chinese", "Italian"], "max_price": 25, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Italian"], "max_price": 25, "dinner": true}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22), R31 Golden Dragon ($24)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R31 Golden Dragon ($24), R35 Noodle Bar 88 ($16)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R06 Trattoria Lucca ($22), R31 Golden Dragon ($24)  
**Safe without asking:** R31 Golden Dragon ($24)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

# 4c: Swapped-order twins

---

## BB-CUI-01A-SW  (ambiguous_reference, family BB-CUI-01, variant A_swap)

*Contrast:* A: Mediterranean -> R39 Falafel Stop ($11); Japanese -> R01 Sakura Ramen ($18); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Mediterranean, one Japanese. | user mentions two cuisines (Mediterranean first, Japanese second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | I'd like somewhere near the station. | user states location=station |
| 4 | assistant | Got it, near the station. | assistant acknowledges |
| 5 | user | No more than $18 a person. It's for lunch. | user states max_price=18, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Let's go with Maya's recommendation. | user: 'Maya's recommendation' = Mediterranean or Japanese (UNRESOLVED; hidden: Mediterranean) |

**Hidden goal:** `{"max_price": 18, "location": "station", "cuisine": "Mediterranean"}`  
**Gold active state:** `{"max_price": 18, "location": "station"}`  
**Unresolved:** 'Maya's recommendation' (turn 7, slot cuisine)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"cuisine": "Mediterranean"}` -> R39 Falafel Stop ($11)  
&nbsp;&nbsp;- `{"cuisine": "Japanese"}` -> R01 Sakura Ramen ($18)  
**Mention order in the chat:** `["Mediterranean", "Japanese"]`  
**Should ask:** YES - cuisine@t7  
**Questions needed:** 1  
**Successful recommendations:** R39 Falafel Stop ($11)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-CUI-01B-SW  (ambiguous_reference, family BB-CUI-01, variant B_swap)

*Contrast:* A: Mediterranean -> R39 Falafel Stop ($11); Japanese -> R01 Sakura Ramen ($18); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Mediterranean, one Japanese. | user mentions two cuisines (Mediterranean first, Japanese second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | I'd like somewhere near the station. | user states location=station |
| 4 | assistant | Got it, near the station. | assistant acknowledges |
| 5 | user | No more than $18 a person. It's for lunch. | user states max_price=18, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Either of those cuisines is fine with me. | user: cuisine in {Mediterranean, Japanese}; disjunction, not ambiguity |

**Hidden goal:** `{"max_price": 18, "location": "station", "cuisine": ["Mediterranean", "Japanese"]}`  
**Gold active state:** `{"max_price": 18, "location": "station", "cuisine": ["Mediterranean", "Japanese"]}`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R01 Sakura Ramen ($18), R39 Falafel Stop ($11)  
**Safe without asking:** R01 Sakura Ramen ($18), R39 Falafel Stop ($11)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-CUI-02A-SW  (ambiguous_reference, family BB-CUI-02, variant A_swap)

*Contrast:* A: Italian -> R08 Forno Pizza ($16); Thai -> R16 Bangkok Street ($17); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Italian, one Thai. | user mentions two cuisines (Italian first, Thai second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | The area doesn't matter to me. | user: no location constraint |
| 4 | assistant | Okay, anywhere works. | assistant acknowledges |
| 5 | user | No more than $17 a person. It's for lunch. | user states max_price=17, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Let's go with Sam's recommendation. | user: 'Sam's recommendation' = Italian or Thai (UNRESOLVED; hidden: Thai) |

**Hidden goal:** `{"max_price": 17, "cuisine": "Thai"}`  
**Gold active state:** `{"max_price": 17}`  
**Unresolved:** 'Sam's recommendation' (turn 7, slot cuisine)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"cuisine": "Italian"}` -> R08 Forno Pizza ($16)  
&nbsp;&nbsp;- `{"cuisine": "Thai"}` -> R16 Bangkok Street ($17)  
**Mention order in the chat:** `["Italian", "Thai"]`  
**Should ask:** YES - cuisine@t7  
**Questions needed:** 1  
**Successful recommendations:** R16 Bangkok Street ($17)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-CUI-02B-SW  (ambiguous_reference, family BB-CUI-02, variant B_swap)

*Contrast:* A: Italian -> R08 Forno Pizza ($16); Thai -> R16 Bangkok Street ($17); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Italian, one Thai. | user mentions two cuisines (Italian first, Thai second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | The area doesn't matter to me. | user: no location constraint |
| 4 | assistant | Okay, anywhere works. | assistant acknowledges |
| 5 | user | No more than $17 a person. It's for lunch. | user states max_price=17, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Either of those cuisines is fine with me. | user: cuisine in {Italian, Thai}; disjunction, not ambiguity |

**Hidden goal:** `{"max_price": 17, "cuisine": ["Italian", "Thai"]}`  
**Gold active state:** `{"max_price": 17, "cuisine": ["Italian", "Thai"]}`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R08 Forno Pizza ($16), R16 Bangkok Street ($17)  
**Safe without asking:** R08 Forno Pizza ($16), R16 Bangkok Street ($17)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-CUI-03A-SW  (ambiguous_reference, family BB-CUI-03, variant A_swap)

*Contrast:* A: Korean -> R27 Bibim Bowl ($15); Indian -> R24 Dosa Corner ($13); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Korean, one Indian. | user mentions two cuisines (Korean first, Indian second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | The area doesn't matter to me. | user: no location constraint |
| 4 | assistant | Okay, anywhere works. | assistant acknowledges |
| 5 | user | No more than $15 a person. It's for lunch. | user states max_price=15, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Let's go with Priya's recommendation. | user: 'Priya's recommendation' = Korean or Indian (UNRESOLVED; hidden: Korean) |

**Hidden goal:** `{"max_price": 15, "cuisine": "Korean"}`  
**Gold active state:** `{"max_price": 15}`  
**Unresolved:** 'Priya's recommendation' (turn 7, slot cuisine)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"cuisine": "Korean"}` -> R27 Bibim Bowl ($15)  
&nbsp;&nbsp;- `{"cuisine": "Indian"}` -> R24 Dosa Corner ($13)  
**Mention order in the chat:** `["Korean", "Indian"]`  
**Should ask:** YES - cuisine@t7  
**Questions needed:** 1  
**Successful recommendations:** R27 Bibim Bowl ($15)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-CUI-03B-SW  (ambiguous_reference, family BB-CUI-03, variant B_swap)

*Contrast:* A: Korean -> R27 Bibim Bowl ($15); Indian -> R24 Dosa Corner ($13); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Korean, one Indian. | user mentions two cuisines (Korean first, Indian second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | The area doesn't matter to me. | user: no location constraint |
| 4 | assistant | Okay, anywhere works. | assistant acknowledges |
| 5 | user | No more than $15 a person. It's for lunch. | user states max_price=15, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Either of those cuisines is fine with me. | user: cuisine in {Korean, Indian}; disjunction, not ambiguity |

**Hidden goal:** `{"max_price": 15, "cuisine": ["Korean", "Indian"]}`  
**Gold active state:** `{"max_price": 15, "cuisine": ["Korean", "Indian"]}`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R24 Dosa Corner ($13), R27 Bibim Bowl ($15)  
**Safe without asking:** R24 Dosa Corner ($13), R27 Bibim Bowl ($15)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-CUI-04A-SW  (ambiguous_reference, family BB-CUI-04, variant A_swap)

*Contrast:* A: Chinese -> R32 Dumpling King ($13), R35 Noodle Bar 88 ($16); Italian -> R08 Forno Pizza ($16); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Chinese, one Italian. | user mentions two cuisines (Chinese first, Italian second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | The area doesn't matter to me. | user: no location constraint |
| 4 | assistant | Okay, anywhere works. | assistant acknowledges |
| 5 | user | No more than $16 a person. It's for lunch. | user states max_price=16, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Let's go with Leo's recommendation. | user: 'Leo's recommendation' = Chinese or Italian (UNRESOLVED; hidden: Italian) |

**Hidden goal:** `{"max_price": 16, "cuisine": "Italian"}`  
**Gold active state:** `{"max_price": 16}`  
**Unresolved:** 'Leo's recommendation' (turn 7, slot cuisine)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"cuisine": "Chinese"}` -> R32 Dumpling King ($13), R35 Noodle Bar 88 ($16)  
&nbsp;&nbsp;- `{"cuisine": "Italian"}` -> R08 Forno Pizza ($16)  
**Mention order in the chat:** `["Chinese", "Italian"]`  
**Should ask:** YES - cuisine@t7  
**Questions needed:** 1  
**Successful recommendations:** R08 Forno Pizza ($16)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-CUI-04B-SW  (ambiguous_reference, family BB-CUI-04, variant B_swap)

*Contrast:* A: Chinese -> R32 Dumpling King ($13), R35 Noodle Bar 88 ($16); Italian -> R08 Forno Pizza ($16); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Chinese, one Italian. | user mentions two cuisines (Chinese first, Italian second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | The area doesn't matter to me. | user: no location constraint |
| 4 | assistant | Okay, anywhere works. | assistant acknowledges |
| 5 | user | No more than $16 a person. It's for lunch. | user states max_price=16, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Either of those cuisines is fine with me. | user: cuisine in {Chinese, Italian}; disjunction, not ambiguity |

**Hidden goal:** `{"max_price": 16, "cuisine": ["Chinese", "Italian"]}`  
**Gold active state:** `{"max_price": 16, "cuisine": ["Chinese", "Italian"]}`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R08 Forno Pizza ($16), R32 Dumpling King ($13), R35 Noodle Bar 88 ($16)  
**Safe without asking:** R08 Forno Pizza ($16), R32 Dumpling King ($13), R35 Noodle Bar 88 ($16)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-CUI-05A-SW  (ambiguous_reference, family BB-CUI-05, variant A_swap)

*Contrast:* A: Thai -> R16 Bangkok Street ($17); Japanese -> R04 Tsuki Bento ($14); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Thai, one Japanese. | user mentions two cuisines (Thai first, Japanese second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | The area doesn't matter to me. | user: no location constraint |
| 4 | assistant | Okay, anywhere works. | assistant acknowledges |
| 5 | user | No more than $17 a person. It's for lunch. | user states max_price=17, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Let's go with Nora's recommendation. | user: 'Nora's recommendation' = Thai or Japanese (UNRESOLVED; hidden: Japanese) |

**Hidden goal:** `{"max_price": 17, "cuisine": "Japanese"}`  
**Gold active state:** `{"max_price": 17}`  
**Unresolved:** 'Nora's recommendation' (turn 7, slot cuisine)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"cuisine": "Thai"}` -> R16 Bangkok Street ($17)  
&nbsp;&nbsp;- `{"cuisine": "Japanese"}` -> R04 Tsuki Bento ($14)  
**Mention order in the chat:** `["Thai", "Japanese"]`  
**Should ask:** YES - cuisine@t7  
**Questions needed:** 1  
**Successful recommendations:** R04 Tsuki Bento ($14)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-CUI-05B-SW  (ambiguous_reference, family BB-CUI-05, variant B_swap)

*Contrast:* A: Thai -> R16 Bangkok Street ($17); Japanese -> R04 Tsuki Bento ($14); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Thai, one Japanese. | user mentions two cuisines (Thai first, Japanese second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | The area doesn't matter to me. | user: no location constraint |
| 4 | assistant | Okay, anywhere works. | assistant acknowledges |
| 5 | user | No more than $17 a person. It's for lunch. | user states max_price=17, meal=lunch |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Either of those cuisines is fine with me. | user: cuisine in {Thai, Japanese}; disjunction, not ambiguity |

**Hidden goal:** `{"max_price": 17, "cuisine": ["Thai", "Japanese"]}`  
**Gold active state:** `{"max_price": 17, "cuisine": ["Thai", "Japanese"]}`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R04 Tsuki Bento ($14), R16 Bangkok Street ($17)  
**Safe without asking:** R04 Tsuki Bento ($14), R16 Bangkok Street ($17)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-01A-SW  (ambiguous_reference, family BB-LOC-01, variant A_swap)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R02 Hoshi Sushi Bar ($24), R07 Nonna's Kitchen ($27), R09 Osteria Verde ($34); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Italian or Japanese food, either is fine. | user states cuisine=['Italian', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $35 per person. | user states max_price=35 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. I also need vegetarian options. | user states meal=dinner (dinner=true), vegetarian=true |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Can you find me something near there? | user: 'Can you find me something near there?' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Italian", "Japanese"], "max_price": 35, "vegetarian": true, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Italian", "Japanese"], "max_price": 35, "vegetarian": true, "dinner": true}`  
**Unresolved:** 'Can you find me something near there?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R07 Nonna's Kitchen ($27), R09 Osteria Verde ($34)  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R02 Hoshi Sushi Bar ($24), R07 Nonna's Kitchen ($27), R09 Osteria Verde ($34)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-01B-SW  (ambiguous_reference, family BB-LOC-01, variant B_swap)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R02 Hoshi Sushi Bar ($24), R07 Nonna's Kitchen ($27), R09 Osteria Verde ($34); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Italian or Japanese food, either is fine. | user states cuisine=['Italian', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $35 per person. | user states max_price=35 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for lunch. I also need vegetarian options. | user states meal=lunch (no dinner constraint), vegetarian=true |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Can you find me something near there? | user: 'Can you find me something near there?' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Italian", "Japanese"], "max_price": 35, "vegetarian": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Italian", "Japanese"], "max_price": 35, "vegetarian": true}`  
**Unresolved:** 'Can you find me something near there?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R07 Nonna's Kitchen ($27), R08 Forno Pizza ($16), R09 Osteria Verde ($34)  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22), R08 Forno Pizza ($16)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R02 Hoshi Sushi Bar ($24), R07 Nonna's Kitchen ($27), R08 Forno Pizza ($16), R09 Osteria Verde ($34)  
**Safe without asking:** R08 Forno Pizza ($16)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-02A-SW  (ambiguous_reference, family BB-LOC-02, variant A_swap)

*Contrast:* A: station -> R16 Bangkok Street ($17), R28 Kimchi Pot ($22); mall -> R17 Lotus Thai ($23), R27 Bibim Bowl ($15), R29 Hanok Table ($27); nothing near both -> ask. B: budget $50 makes R20 Royal Orchid ($48) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Korean or Thai food, either is fine. | user states cuisine=['Korean', 'Thai'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $30 per person. | user states max_price=30 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's look over that side. | user: 'Let's look over that side.' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Korean", "Thai"], "max_price": 30, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Korean", "Thai"], "max_price": 30}`  
**Unresolved:** 'Let's look over that side.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17), R28 Kimchi Pot ($22)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R17 Lotus Thai ($23), R27 Bibim Bowl ($15), R29 Hanok Table ($27)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R17 Lotus Thai ($23), R27 Bibim Bowl ($15), R29 Hanok Table ($27)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-02B-SW  (ambiguous_reference, family BB-LOC-02, variant B_swap)

*Contrast:* A: station -> R16 Bangkok Street ($17), R28 Kimchi Pot ($22); mall -> R17 Lotus Thai ($23), R27 Bibim Bowl ($15), R29 Hanok Table ($27); nothing near both -> ask. B: budget $50 makes R20 Royal Orchid ($48) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Korean or Thai food, either is fine. | user states cuisine=['Korean', 'Thai'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $50 per person. | user states max_price=50 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's look over that side. | user: 'Let's look over that side.' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Korean", "Thai"], "max_price": 50, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Korean", "Thai"], "max_price": 50}`  
**Unresolved:** 'Let's look over that side.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17), R20 Royal Orchid ($48), R26 Seoul BBQ ($36), R28 Kimchi Pot ($22)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R17 Lotus Thai ($23), R18 Siam Garden ($31), R20 Royal Orchid ($48), R27 Bibim Bowl ($15), R29 Hanok Table ($27)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R17 Lotus Thai ($23), R18 Siam Garden ($31), R20 Royal Orchid ($48), R27 Bibim Bowl ($15), R29 Hanok Table ($27)  
**Safe without asking:** R20 Royal Orchid ($48)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-03A-SW  (ambiguous_reference, family BB-LOC-03, variant A_swap)

*Contrast:* A: station -> R11 Taco Loco ($12); mall -> R35 Noodle Bar 88 ($16), R37 Pita Port ($14); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16), R39 Falafel Stop ($11) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm looking for somewhere to eat. | user states no cuisine preference |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $16 per person. | user states max_price=16 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Something around that area would be great. | user: 'Something around that area would be great.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"max_price": 16, "dinner": true, "location": "station"}`  
**Gold active state:** `{"max_price": 16, "dinner": true}`  
**Unresolved:** 'Something around that area would be great.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R11 Taco Loco ($12)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R35 Noodle Bar 88 ($16), R37 Pita Port ($14)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R11 Taco Loco ($12)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-03B-SW  (ambiguous_reference, family BB-LOC-03, variant B_swap)

*Contrast:* A: station -> R11 Taco Loco ($12); mall -> R35 Noodle Bar 88 ($16), R37 Pita Port ($14); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16), R39 Falafel Stop ($11) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm looking for somewhere to eat. | user states no cuisine preference |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $16 per person. | user states max_price=16 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Something around that area would be great. | user: 'Something around that area would be great.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"max_price": 16, "location": "station"}`  
**Gold active state:** `{"max_price": 16}`  
**Unresolved:** 'Something around that area would be great.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R08 Forno Pizza ($16), R11 Taco Loco ($12), R32 Dumpling King ($13), R39 Falafel Stop ($11)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R08 Forno Pizza ($16), R27 Bibim Bowl ($15), R35 Noodle Bar 88 ($16), R37 Pita Port ($14), R39 Falafel Stop ($11)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R08 Forno Pizza ($16), R11 Taco Loco ($12), R32 Dumpling King ($13), R39 Falafel Stop ($11)  
**Safe without asking:** R08 Forno Pizza ($16), R39 Falafel Stop ($11)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-04A-SW  (ambiguous_reference, family BB-LOC-04, variant A_swap)

*Contrast:* A: station -> R01 Sakura Ramen ($18), R21 Masala House ($20); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: budget $25 makes R23 Saffron Leaf ($25) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Indian or Japanese food, either is fine. | user states cuisine=['Indian', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $24 per person. | user states max_price=24 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Can you check that part of town for me? | user: 'Can you check that part of town for me?' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Indian", "Japanese"], "max_price": 24, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Indian", "Japanese"], "max_price": 24, "dinner": true}`  
**Unresolved:** 'Can you check that part of town for me?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24)  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18), R21 Masala House ($20)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R01 Sakura Ramen ($18), R21 Masala House ($20)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-04B-SW  (ambiguous_reference, family BB-LOC-04, variant B_swap)

*Contrast:* A: station -> R01 Sakura Ramen ($18), R21 Masala House ($20); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: budget $25 makes R23 Saffron Leaf ($25) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Indian or Japanese food, either is fine. | user states cuisine=['Indian', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Can you check that part of town for me? | user: 'Can you check that part of town for me?' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Indian", "Japanese"], "max_price": 25, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Indian", "Japanese"], "max_price": 25, "dinner": true}`  
**Unresolved:** 'Can you check that part of town for me?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R23 Saffron Leaf ($25)  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18), R21 Masala House ($20), R23 Saffron Leaf ($25)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R01 Sakura Ramen ($18), R21 Masala House ($20), R23 Saffron Leaf ($25)  
**Safe without asking:** R23 Saffron Leaf ($25)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-05A-SW  (ambiguous_reference, family BB-LOC-05, variant A_swap)

*Contrast:* A: station -> R32 Dumpling King ($13); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $25 makes R31 Golden Dragon ($24) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Chinese or Korean food, either is fine. | user states cuisine=['Chinese', 'Korean'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $15 per person. | user states max_price=15 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Find me a spot over there. | user: 'Find me a spot over there.' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Chinese", "Korean"], "max_price": 15, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Korean"], "max_price": 15}`  
**Unresolved:** 'Find me a spot over there.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R27 Bibim Bowl ($15)  
&nbsp;&nbsp;- `{"location": "station"}` -> R32 Dumpling King ($13)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R27 Bibim Bowl ($15)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-05B-SW  (ambiguous_reference, family BB-LOC-05, variant B_swap)

*Contrast:* A: station -> R32 Dumpling King ($13); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $25 makes R31 Golden Dragon ($24) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Chinese or Korean food, either is fine. | user states cuisine=['Chinese', 'Korean'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Find me a spot over there. | user: 'Find me a spot over there.' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Chinese", "Korean"], "max_price": 25, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Korean"], "max_price": 25}`  
**Unresolved:** 'Find me a spot over there.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R27 Bibim Bowl ($15), R31 Golden Dragon ($24), R35 Noodle Bar 88 ($16)  
&nbsp;&nbsp;- `{"location": "station"}` -> R28 Kimchi Pot ($22), R31 Golden Dragon ($24), R32 Dumpling King ($13)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R27 Bibim Bowl ($15), R31 Golden Dragon ($24), R35 Noodle Bar 88 ($16)  
**Safe without asking:** R31 Golden Dragon ($24)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-06A-SW  (ambiguous_reference, family BB-LOC-06, variant A_swap)

*Contrast:* A: station -> R01 Sakura Ramen ($18); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: budget $30 makes R03 Kumo Izakaya ($29) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm in the mood for Japanese food. | user states cuisine=Japanese |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with that area. What's good there? | user: 'Let's go with that area. What's good there?' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": "Japanese", "max_price": 25, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": "Japanese", "max_price": 25, "dinner": true}`  
**Unresolved:** 'Let's go with that area. What's good there?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R01 Sakura Ramen ($18)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-06B-SW  (ambiguous_reference, family BB-LOC-06, variant B_swap)

*Contrast:* A: station -> R01 Sakura Ramen ($18); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: budget $30 makes R03 Kumo Izakaya ($29) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm in the mood for Japanese food. | user states cuisine=Japanese |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $30 per person. | user states max_price=30 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with that area. What's good there? | user: 'Let's go with that area. What's good there?' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": "Japanese", "max_price": 30, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": "Japanese", "max_price": 30, "dinner": true}`  
**Unresolved:** 'Let's go with that area. What's good there?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18), R03 Kumo Izakaya ($29)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R03 Kumo Izakaya ($29)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R01 Sakura Ramen ($18), R03 Kumo Izakaya ($29)  
**Safe without asking:** R03 Kumo Izakaya ($29)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-07A-SW  (ambiguous_reference, family BB-LOC-07, variant A_swap)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Italian or Japanese food, either is fine. | user states cuisine=['Italian', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. I also need vegetarian options. | user states meal=dinner (dinner=true), vegetarian=true |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Somewhere near there works for me. | user: 'Somewhere near there works for me.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Italian", "Japanese"], "max_price": 25, "vegetarian": true, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Italian", "Japanese"], "max_price": 25, "vegetarian": true, "dinner": true}`  
**Unresolved:** 'Somewhere near there works for me.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24)  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R06 Trattoria Lucca ($22)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-07B-SW  (ambiguous_reference, family BB-LOC-07, variant B_swap)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Italian or Japanese food, either is fine. | user states cuisine=['Italian', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for lunch. I also need vegetarian options. | user states meal=lunch (no dinner constraint), vegetarian=true |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Somewhere near there works for me. | user: 'Somewhere near there works for me.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Italian", "Japanese"], "max_price": 25, "vegetarian": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Italian", "Japanese"], "max_price": 25, "vegetarian": true}`  
**Unresolved:** 'Somewhere near there works for me.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R08 Forno Pizza ($16)  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22), R08 Forno Pizza ($16)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R06 Trattoria Lucca ($22), R08 Forno Pizza ($16)  
**Safe without asking:** R08 Forno Pizza ($16)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-08A-SW  (ambiguous_reference, family BB-LOC-08, variant A_swap)

*Contrast:* A: station -> R21 Masala House ($20); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: budget $25 makes R23 Saffron Leaf ($25) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Indian or Japanese food, either is fine. | user states cuisine=['Indian', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $24 per person. | user states max_price=24 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. I also need vegetarian options. | user states meal=dinner (dinner=true), vegetarian=true |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Pick something on that side, please. | user: 'Pick something on that side, please.' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Indian", "Japanese"], "max_price": 24, "vegetarian": true, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Indian", "Japanese"], "max_price": 24, "vegetarian": true, "dinner": true}`  
**Unresolved:** 'Pick something on that side, please.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R21 Masala House ($20)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R02 Hoshi Sushi Bar ($24)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-08B-SW  (ambiguous_reference, family BB-LOC-08, variant B_swap)

*Contrast:* A: station -> R21 Masala House ($20); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: budget $25 makes R23 Saffron Leaf ($25) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Indian or Japanese food, either is fine. | user states cuisine=['Indian', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. I also need vegetarian options. | user states meal=dinner (dinner=true), vegetarian=true |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Pick something on that side, please. | user: 'Pick something on that side, please.' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Indian", "Japanese"], "max_price": 25, "vegetarian": true, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Indian", "Japanese"], "max_price": 25, "vegetarian": true, "dinner": true}`  
**Unresolved:** 'Pick something on that side, please.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R21 Masala House ($20), R23 Saffron Leaf ($25)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R23 Saffron Leaf ($25)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R02 Hoshi Sushi Bar ($24), R23 Saffron Leaf ($25)  
**Safe without asking:** R23 Saffron Leaf ($25)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-09A-SW  (ambiguous_reference, family BB-LOC-09, variant A_swap)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R07 Nonna's Kitchen ($27); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm in the mood for Italian food. | user states cuisine=Italian |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $30 per person. | user states max_price=30 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | I'd like something around there. | user: 'I'd like something around there.' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": "Italian", "max_price": 30, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": "Italian", "max_price": 30, "dinner": true}`  
**Unresolved:** 'I'd like something around there.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R07 Nonna's Kitchen ($27)  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R07 Nonna's Kitchen ($27)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-09B-SW  (ambiguous_reference, family BB-LOC-09, variant B_swap)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R07 Nonna's Kitchen ($27); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm in the mood for Italian food. | user states cuisine=Italian |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $30 per person. | user states max_price=30 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | I'd like something around there. | user: 'I'd like something around there.' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": "Italian", "max_price": 30, "location": "mall"}`  
**Gold active state:** `{"cuisine": "Italian", "max_price": 30}`  
**Unresolved:** 'I'd like something around there.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R07 Nonna's Kitchen ($27), R08 Forno Pizza ($16)  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22), R08 Forno Pizza ($16)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R07 Nonna's Kitchen ($27), R08 Forno Pizza ($16)  
**Safe without asking:** R08 Forno Pizza ($16)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-10A-SW  (ambiguous_reference, family BB-LOC-10, variant A_swap)

*Contrast:* A: station -> R16 Bangkok Street ($17), R36 Olive & Thyme ($23), R38 Aegean Table ($33); mall -> R18 Siam Garden ($31), R37 Pita Port ($14), R40 Santorini Grill ($47); nothing near both -> ask. B: budget $50 makes R20 Royal Orchid ($48) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Mediterranean or Thai food, either is fine. | user states cuisine=['Mediterranean', 'Thai'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $47 per person. | user states max_price=47 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Can you look in that area? | user: 'Can you look in that area?' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Mediterranean", "Thai"], "max_price": 47, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Mediterranean", "Thai"], "max_price": 47, "dinner": true}`  
**Unresolved:** 'Can you look in that area?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R18 Siam Garden ($31), R37 Pita Port ($14), R40 Santorini Grill ($47)  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17), R36 Olive & Thyme ($23), R38 Aegean Table ($33)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R16 Bangkok Street ($17), R36 Olive & Thyme ($23), R38 Aegean Table ($33)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-10B-SW  (ambiguous_reference, family BB-LOC-10, variant B_swap)

*Contrast:* A: station -> R16 Bangkok Street ($17), R36 Olive & Thyme ($23), R38 Aegean Table ($33); mall -> R18 Siam Garden ($31), R37 Pita Port ($14), R40 Santorini Grill ($47); nothing near both -> ask. B: budget $50 makes R20 Royal Orchid ($48) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Mediterranean or Thai food, either is fine. | user states cuisine=['Mediterranean', 'Thai'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $50 per person. | user states max_price=50 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Can you look in that area? | user: 'Can you look in that area?' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Mediterranean", "Thai"], "max_price": 50, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Mediterranean", "Thai"], "max_price": 50, "dinner": true}`  
**Unresolved:** 'Can you look in that area?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R18 Siam Garden ($31), R20 Royal Orchid ($48), R37 Pita Port ($14), R40 Santorini Grill ($47)  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17), R20 Royal Orchid ($48), R36 Olive & Thyme ($23), R38 Aegean Table ($33)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R16 Bangkok Street ($17), R20 Royal Orchid ($48), R36 Olive & Thyme ($23), R38 Aegean Table ($33)  
**Safe without asking:** R20 Royal Orchid ($48)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-01A-SW  (ambiguous_reference, family BB-ORD-01, variant A_swap)

*Contrast:* A: station -> R01 Sakura Ramen ($18); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $30 makes R03 Kumo Izakaya ($29) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Japanese or Korean food, either is fine. | user states cuisine=['Japanese', 'Korean'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $20 per person. | user states max_price=20 |
| 4 | assistant | Okay. With that budget, the mall side and the station side both still have choices. | assistant re-lists the areas in the opposite order (mall first, station second) |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = mall (second in turn 2) or station (second in turn 4) (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Japanese", "Korean"], "max_price": 20, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Japanese", "Korean"], "max_price": 20}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R27 Bibim Bowl ($15)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R01 Sakura Ramen ($18)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-01B-SW  (ambiguous_reference, family BB-ORD-01, variant B_swap)

*Contrast:* A: station -> R01 Sakura Ramen ($18); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $30 makes R03 Kumo Izakaya ($29) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Japanese or Korean food, either is fine. | user states cuisine=['Japanese', 'Korean'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $30 per person. | user states max_price=30 |
| 4 | assistant | Okay. With that budget, the mall side and the station side both still have choices. | assistant re-lists the areas in the opposite order (mall first, station second) |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = mall (second in turn 2) or station (second in turn 4) (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Japanese", "Korean"], "max_price": 30, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Japanese", "Korean"], "max_price": 30}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18), R03 Kumo Izakaya ($29), R28 Kimchi Pot ($22)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R03 Kumo Izakaya ($29), R27 Bibim Bowl ($15), R29 Hanok Table ($27)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R01 Sakura Ramen ($18), R03 Kumo Izakaya ($29), R28 Kimchi Pot ($22)  
**Safe without asking:** R03 Kumo Izakaya ($29)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-02A-SW  (ambiguous_reference, family BB-ORD-02, variant A_swap)

*Contrast:* A: station -> R16 Bangkok Street ($17); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $50 makes R20 Royal Orchid ($48) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Korean or Thai food, either is fine. | user states cuisine=['Korean', 'Thai'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $20 per person. | user states max_price=20 |
| 4 | assistant | Okay. With that budget, the station side and the mall side both still have choices. | assistant re-lists the areas in the opposite order (station first, mall second) |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = station (second in turn 2) or mall (second in turn 4) (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Korean", "Thai"], "max_price": 20, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Korean", "Thai"], "max_price": 20}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R27 Bibim Bowl ($15)  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R16 Bangkok Street ($17)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-02B-SW  (ambiguous_reference, family BB-ORD-02, variant B_swap)

*Contrast:* A: station -> R16 Bangkok Street ($17); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $50 makes R20 Royal Orchid ($48) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Korean or Thai food, either is fine. | user states cuisine=['Korean', 'Thai'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $50 per person. | user states max_price=50 |
| 4 | assistant | Okay. With that budget, the station side and the mall side both still have choices. | assistant re-lists the areas in the opposite order (station first, mall second) |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = station (second in turn 2) or mall (second in turn 4) (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Korean", "Thai"], "max_price": 50, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Korean", "Thai"], "max_price": 50}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R17 Lotus Thai ($23), R18 Siam Garden ($31), R20 Royal Orchid ($48), R27 Bibim Bowl ($15), R29 Hanok Table ($27)  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17), R20 Royal Orchid ($48), R26 Seoul BBQ ($36), R28 Kimchi Pot ($22)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R16 Bangkok Street ($17), R20 Royal Orchid ($48), R26 Seoul BBQ ($36), R28 Kimchi Pot ($22)  
**Safe without asking:** R20 Royal Orchid ($48)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-03A-SW  (ambiguous_reference, family BB-ORD-03, variant A_swap)

*Contrast:* A: station -> R21 Masala House ($20); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $25 makes R23 Saffron Leaf ($25) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Indian or Korean food, either is fine. | user states cuisine=['Indian', 'Korean'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $20 per person. | user states max_price=20 |
| 4 | assistant | Okay. With that budget, the station side and the mall side both still have choices. | assistant re-lists the areas in the opposite order (station first, mall second) |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = station (second in turn 2) or mall (second in turn 4) (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Indian", "Korean"], "max_price": 20, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Indian", "Korean"], "max_price": 20}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R27 Bibim Bowl ($15)  
&nbsp;&nbsp;- `{"location": "station"}` -> R21 Masala House ($20)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R27 Bibim Bowl ($15)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-03B-SW  (ambiguous_reference, family BB-ORD-03, variant B_swap)

*Contrast:* A: station -> R21 Masala House ($20); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $25 makes R23 Saffron Leaf ($25) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Indian or Korean food, either is fine. | user states cuisine=['Indian', 'Korean'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Okay. With that budget, the station side and the mall side both still have choices. | assistant re-lists the areas in the opposite order (station first, mall second) |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = station (second in turn 2) or mall (second in turn 4) (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Indian", "Korean"], "max_price": 25, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Indian", "Korean"], "max_price": 25}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R23 Saffron Leaf ($25), R27 Bibim Bowl ($15)  
&nbsp;&nbsp;- `{"location": "station"}` -> R21 Masala House ($20), R23 Saffron Leaf ($25), R28 Kimchi Pot ($22)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R23 Saffron Leaf ($25), R27 Bibim Bowl ($15)  
**Safe without asking:** R23 Saffron Leaf ($25)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-04A-SW  (ambiguous_reference, family BB-ORD-04, variant A_swap)

*Contrast:* A: station -> R01 Sakura Ramen ($18); mall -> R35 Noodle Bar 88 ($16); nothing near both -> ask. B: budget $25 makes R31 Golden Dragon ($24) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Chinese or Japanese food, either is fine. | user states cuisine=['Chinese', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $20 per person. | user states max_price=20 |
| 4 | assistant | Okay. With that budget, the mall side and the station side both still have choices. | assistant re-lists the areas in the opposite order (mall first, station second) |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = mall (second in turn 2) or station (second in turn 4) (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Chinese", "Japanese"], "max_price": 20, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Japanese"], "max_price": 20, "dinner": true}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R35 Noodle Bar 88 ($16)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R35 Noodle Bar 88 ($16)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-04B-SW  (ambiguous_reference, family BB-ORD-04, variant B_swap)

*Contrast:* A: station -> R01 Sakura Ramen ($18); mall -> R35 Noodle Bar 88 ($16); nothing near both -> ask. B: budget $25 makes R31 Golden Dragon ($24) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Chinese or Japanese food, either is fine. | user states cuisine=['Chinese', 'Japanese'] |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Okay. With that budget, the mall side and the station side both still have choices. | assistant re-lists the areas in the opposite order (mall first, station second) |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = mall (second in turn 2) or station (second in turn 4) (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Chinese", "Japanese"], "max_price": 25, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Japanese"], "max_price": 25, "dinner": true}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18), R31 Golden Dragon ($24)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R31 Golden Dragon ($24), R35 Noodle Bar 88 ($16)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R02 Hoshi Sushi Bar ($24), R31 Golden Dragon ($24), R35 Noodle Bar 88 ($16)  
**Safe without asking:** R31 Golden Dragon ($24)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-05A-SW  (ambiguous_reference, family BB-ORD-05, variant A_swap)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R35 Noodle Bar 88 ($16); nothing near both -> ask. B: budget $25 makes R31 Golden Dragon ($24) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Chinese or Italian food, either is fine. | user states cuisine=['Chinese', 'Italian'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $22 per person. | user states max_price=22 |
| 4 | assistant | Okay. With that budget, the station side and the mall side both still have choices. | assistant re-lists the areas in the opposite order (station first, mall second) |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = station (second in turn 2) or mall (second in turn 4) (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Chinese", "Italian"], "max_price": 22, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Italian"], "max_price": 22, "dinner": true}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R35 Noodle Bar 88 ($16)  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R35 Noodle Bar 88 ($16)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-ORD-05B-SW  (ambiguous_reference, family BB-ORD-05, variant B_swap)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R35 Noodle Bar 88 ($16); nothing near both -> ask. B: budget $25 makes R31 Golden Dragon ($24) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Chinese or Italian food, either is fine. | user states cuisine=['Chinese', 'Italian'] |
| 2 | assistant | Sure! There are good options near the mall and near the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Okay. With that budget, the station side and the mall side both still have choices. | assistant re-lists the areas in the opposite order (station first, mall second) |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Let's go with the second place you mentioned. | user: 'second place' = station (second in turn 2) or mall (second in turn 4) (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Chinese", "Italian"], "max_price": 25, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Italian"], "max_price": 25, "dinner": true}`  
**Unresolved:** 'Let's go with the second place you mentioned.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R31 Golden Dragon ($24), R35 Noodle Bar 88 ($16)  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22), R31 Golden Dragon ($24)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R31 Golden Dragon ($24), R35 Noodle Bar 88 ($16)  
**Safe without asking:** R31 Golden Dragon ($24)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

# 4e: Paraphrase versions

---

## BB-LOC-01A-P1  (ambiguous_reference, family BB-LOC-01, variant A_para1)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R02 Hoshi Sushi Bar ($24), R07 Nonna's Kitchen ($27), R09 Osteria Verde ($34); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Can you help me find a place to eat? Italian or Japanese would both be fine. | user states cuisine=['Italian', 'Japanese'] |
| 2 | assistant | Happy to help. I can see places by the station and by the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $35 per person. | user states max_price=35 |
| 4 | assistant | Thanks, that helps. | assistant acknowledges |
| 5 | user | It's for dinner. I also need vegetarian options. | user states meal=dinner (dinner=true), vegetarian=true |
| 6 | assistant | Understood. | assistant acknowledges |
| 7 | user | Something around that area, please. | user: 'Something around that area, please.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Italian", "Japanese"], "max_price": 35, "vegetarian": true, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Italian", "Japanese"], "max_price": 35, "vegetarian": true, "dinner": true}`  
**Unresolved:** 'Something around that area, please.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R07 Nonna's Kitchen ($27), R09 Osteria Verde ($34)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R06 Trattoria Lucca ($22)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-01A-P2  (ambiguous_reference, family BB-LOC-01, variant A_para2)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R02 Hoshi Sushi Bar ($24), R07 Nonna's Kitchen ($27), R09 Osteria Verde ($34); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I need ideas for a meal. Maybe Italian, maybe Japanese, I'm easy. | user states cuisine=['Italian', 'Japanese'] |
| 2 | assistant | Of course. A couple of spots are close to the station, and a couple are close to the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $35 per person. | user states max_price=35 |
| 4 | assistant | Okay, budget noted. | assistant acknowledges |
| 5 | user | It's for dinner. I also need vegetarian options. | user states meal=dinner (dinner=true), vegetarian=true |
| 6 | assistant | Sounds good. | assistant acknowledges |
| 7 | user | Let's try over that side. | user: 'Let's try over that side.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Italian", "Japanese"], "max_price": 35, "vegetarian": true, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Italian", "Japanese"], "max_price": 35, "vegetarian": true, "dinner": true}`  
**Unresolved:** 'Let's try over that side.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R07 Nonna's Kitchen ($27), R09 Osteria Verde ($34)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R06 Trattoria Lucca ($22)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-01B-P1  (ambiguous_reference, family BB-LOC-01, variant B_para1)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R02 Hoshi Sushi Bar ($24), R07 Nonna's Kitchen ($27), R09 Osteria Verde ($34); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Can you help me find a place to eat? Italian or Japanese would both be fine. | user states cuisine=['Italian', 'Japanese'] |
| 2 | assistant | Happy to help. I can see places by the station and by the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $35 per person. | user states max_price=35 |
| 4 | assistant | Thanks, that helps. | assistant acknowledges |
| 5 | user | It's for lunch. I also need vegetarian options. | user states meal=lunch (no dinner constraint), vegetarian=true |
| 6 | assistant | Understood. | assistant acknowledges |
| 7 | user | Something around that area, please. | user: 'Something around that area, please.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Italian", "Japanese"], "max_price": 35, "vegetarian": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Italian", "Japanese"], "max_price": 35, "vegetarian": true}`  
**Unresolved:** 'Something around that area, please.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22), R08 Forno Pizza ($16)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R07 Nonna's Kitchen ($27), R08 Forno Pizza ($16), R09 Osteria Verde ($34)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R06 Trattoria Lucca ($22), R08 Forno Pizza ($16)  
**Safe without asking:** R08 Forno Pizza ($16)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-01B-P2  (ambiguous_reference, family BB-LOC-01, variant B_para2)

*Contrast:* A: station -> R06 Trattoria Lucca ($22); mall -> R02 Hoshi Sushi Bar ($24), R07 Nonna's Kitchen ($27), R09 Osteria Verde ($34); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I need ideas for a meal. Maybe Italian, maybe Japanese, I'm easy. | user states cuisine=['Italian', 'Japanese'] |
| 2 | assistant | Of course. A couple of spots are close to the station, and a couple are close to the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $35 per person. | user states max_price=35 |
| 4 | assistant | Okay, budget noted. | assistant acknowledges |
| 5 | user | It's for lunch. I also need vegetarian options. | user states meal=lunch (no dinner constraint), vegetarian=true |
| 6 | assistant | Sounds good. | assistant acknowledges |
| 7 | user | Let's try over that side. | user: 'Let's try over that side.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Italian", "Japanese"], "max_price": 35, "vegetarian": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Italian", "Japanese"], "max_price": 35, "vegetarian": true}`  
**Unresolved:** 'Let's try over that side.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R06 Trattoria Lucca ($22), R08 Forno Pizza ($16)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R07 Nonna's Kitchen ($27), R08 Forno Pizza ($16), R09 Osteria Verde ($34)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R06 Trattoria Lucca ($22), R08 Forno Pizza ($16)  
**Safe without asking:** R08 Forno Pizza ($16)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-02A-P1  (ambiguous_reference, family BB-LOC-02, variant A_para1)

*Contrast:* A: station -> R16 Bangkok Street ($17), R28 Kimchi Pot ($22); mall -> R17 Lotus Thai ($23), R27 Bibim Bowl ($15), R29 Hanok Table ($27); nothing near both -> ask. B: budget $50 makes R20 Royal Orchid ($48) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Can you help me find a place to eat? Korean or Thai would both be fine. | user states cuisine=['Korean', 'Thai'] |
| 2 | assistant | Happy to help. I can see places by the mall and by the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $30 per person. | user states max_price=30 |
| 4 | assistant | Thanks, that helps. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Understood. | assistant acknowledges |
| 7 | user | Anything over that side? | user: 'Anything over that side?' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Korean", "Thai"], "max_price": 30, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Korean", "Thai"], "max_price": 30}`  
**Unresolved:** 'Anything over that side?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R17 Lotus Thai ($23), R27 Bibim Bowl ($15), R29 Hanok Table ($27)  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17), R28 Kimchi Pot ($22)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R16 Bangkok Street ($17), R28 Kimchi Pot ($22)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-02A-P2  (ambiguous_reference, family BB-LOC-02, variant A_para2)

*Contrast:* A: station -> R16 Bangkok Street ($17), R28 Kimchi Pot ($22); mall -> R17 Lotus Thai ($23), R27 Bibim Bowl ($15), R29 Hanok Table ($27); nothing near both -> ask. B: budget $50 makes R20 Royal Orchid ($48) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I need ideas for a meal. Maybe Korean, maybe Thai, I'm easy. | user states cuisine=['Korean', 'Thai'] |
| 2 | assistant | Of course. A couple of spots are close to the mall, and a couple are close to the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $30 per person. | user states max_price=30 |
| 4 | assistant | Okay, budget noted. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Sounds good. | assistant acknowledges |
| 7 | user | What's good around that area? | user: 'What's good around that area?' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Korean", "Thai"], "max_price": 30, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Korean", "Thai"], "max_price": 30}`  
**Unresolved:** 'What's good around that area?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R17 Lotus Thai ($23), R27 Bibim Bowl ($15), R29 Hanok Table ($27)  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17), R28 Kimchi Pot ($22)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R16 Bangkok Street ($17), R28 Kimchi Pot ($22)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-02B-P1  (ambiguous_reference, family BB-LOC-02, variant B_para1)

*Contrast:* A: station -> R16 Bangkok Street ($17), R28 Kimchi Pot ($22); mall -> R17 Lotus Thai ($23), R27 Bibim Bowl ($15), R29 Hanok Table ($27); nothing near both -> ask. B: budget $50 makes R20 Royal Orchid ($48) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Can you help me find a place to eat? Korean or Thai would both be fine. | user states cuisine=['Korean', 'Thai'] |
| 2 | assistant | Happy to help. I can see places by the mall and by the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $50 per person. | user states max_price=50 |
| 4 | assistant | Thanks, that helps. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Understood. | assistant acknowledges |
| 7 | user | Anything over that side? | user: 'Anything over that side?' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Korean", "Thai"], "max_price": 50, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Korean", "Thai"], "max_price": 50}`  
**Unresolved:** 'Anything over that side?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R17 Lotus Thai ($23), R18 Siam Garden ($31), R20 Royal Orchid ($48), R27 Bibim Bowl ($15), R29 Hanok Table ($27)  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17), R20 Royal Orchid ($48), R26 Seoul BBQ ($36), R28 Kimchi Pot ($22)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R16 Bangkok Street ($17), R20 Royal Orchid ($48), R26 Seoul BBQ ($36), R28 Kimchi Pot ($22)  
**Safe without asking:** R20 Royal Orchid ($48)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-02B-P2  (ambiguous_reference, family BB-LOC-02, variant B_para2)

*Contrast:* A: station -> R16 Bangkok Street ($17), R28 Kimchi Pot ($22); mall -> R17 Lotus Thai ($23), R27 Bibim Bowl ($15), R29 Hanok Table ($27); nothing near both -> ask. B: budget $50 makes R20 Royal Orchid ($48) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I need ideas for a meal. Maybe Korean, maybe Thai, I'm easy. | user states cuisine=['Korean', 'Thai'] |
| 2 | assistant | Of course. A couple of spots are close to the mall, and a couple are close to the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $50 per person. | user states max_price=50 |
| 4 | assistant | Okay, budget noted. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Sounds good. | assistant acknowledges |
| 7 | user | What's good around that area? | user: 'What's good around that area?' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Korean", "Thai"], "max_price": 50, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Korean", "Thai"], "max_price": 50}`  
**Unresolved:** 'What's good around that area?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R17 Lotus Thai ($23), R18 Siam Garden ($31), R20 Royal Orchid ($48), R27 Bibim Bowl ($15), R29 Hanok Table ($27)  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17), R20 Royal Orchid ($48), R26 Seoul BBQ ($36), R28 Kimchi Pot ($22)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R16 Bangkok Street ($17), R20 Royal Orchid ($48), R26 Seoul BBQ ($36), R28 Kimchi Pot ($22)  
**Safe without asking:** R20 Royal Orchid ($48)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-03A-P1  (ambiguous_reference, family BB-LOC-03, variant A_para1)

*Contrast:* A: station -> R11 Taco Loco ($12); mall -> R35 Noodle Bar 88 ($16), R37 Pita Port ($14); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16), R39 Falafel Stop ($11) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Can you help me find a place to eat?  | user states no cuisine preference |
| 2 | assistant | Happy to help. I can see places by the mall and by the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $16 per person. | user states max_price=16 |
| 4 | assistant | Thanks, that helps. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Understood. | assistant acknowledges |
| 7 | user | Can you find something near there? | user: 'Can you find something near there?' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"max_price": 16, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"max_price": 16, "dinner": true}`  
**Unresolved:** 'Can you find something near there?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R35 Noodle Bar 88 ($16), R37 Pita Port ($14)  
&nbsp;&nbsp;- `{"location": "station"}` -> R11 Taco Loco ($12)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R35 Noodle Bar 88 ($16), R37 Pita Port ($14)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-03A-P2  (ambiguous_reference, family BB-LOC-03, variant A_para2)

*Contrast:* A: station -> R11 Taco Loco ($12); mall -> R35 Noodle Bar 88 ($16), R37 Pita Port ($14); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16), R39 Falafel Stop ($11) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I need ideas for a meal. Any cuisine works. | user states no cuisine preference |
| 2 | assistant | Of course. A couple of spots are close to the mall, and a couple are close to the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $16 per person. | user states max_price=16 |
| 4 | assistant | Okay, budget noted. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Sounds good. | assistant acknowledges |
| 7 | user | Let's go over that side. | user: 'Let's go over that side.' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"max_price": 16, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"max_price": 16, "dinner": true}`  
**Unresolved:** 'Let's go over that side.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R35 Noodle Bar 88 ($16), R37 Pita Port ($14)  
&nbsp;&nbsp;- `{"location": "station"}` -> R11 Taco Loco ($12)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R35 Noodle Bar 88 ($16), R37 Pita Port ($14)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-03B-P1  (ambiguous_reference, family BB-LOC-03, variant B_para1)

*Contrast:* A: station -> R11 Taco Loco ($12); mall -> R35 Noodle Bar 88 ($16), R37 Pita Port ($14); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16), R39 Falafel Stop ($11) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Can you help me find a place to eat?  | user states no cuisine preference |
| 2 | assistant | Happy to help. I can see places by the mall and by the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $16 per person. | user states max_price=16 |
| 4 | assistant | Thanks, that helps. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Understood. | assistant acknowledges |
| 7 | user | Can you find something near there? | user: 'Can you find something near there?' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"max_price": 16, "location": "mall"}`  
**Gold active state:** `{"max_price": 16}`  
**Unresolved:** 'Can you find something near there?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R08 Forno Pizza ($16), R27 Bibim Bowl ($15), R35 Noodle Bar 88 ($16), R37 Pita Port ($14), R39 Falafel Stop ($11)  
&nbsp;&nbsp;- `{"location": "station"}` -> R08 Forno Pizza ($16), R11 Taco Loco ($12), R32 Dumpling King ($13), R39 Falafel Stop ($11)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R08 Forno Pizza ($16), R27 Bibim Bowl ($15), R35 Noodle Bar 88 ($16), R37 Pita Port ($14), R39 Falafel Stop ($11)  
**Safe without asking:** R08 Forno Pizza ($16), R39 Falafel Stop ($11)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-03B-P2  (ambiguous_reference, family BB-LOC-03, variant B_para2)

*Contrast:* A: station -> R11 Taco Loco ($12); mall -> R35 Noodle Bar 88 ($16), R37 Pita Port ($14); nothing near both -> ask. B: lunch instead of dinner makes R08 Forno Pizza ($16), R39 Falafel Stop ($11) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I need ideas for a meal. Any cuisine works. | user states no cuisine preference |
| 2 | assistant | Of course. A couple of spots are close to the mall, and a couple are close to the station. | assistant mentions both areas (mall first, station second); not a user choice |
| 3 | user | My budget is $16 per person. | user states max_price=16 |
| 4 | assistant | Okay, budget noted. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Sounds good. | assistant acknowledges |
| 7 | user | Let's go over that side. | user: 'Let's go over that side.' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"max_price": 16, "location": "mall"}`  
**Gold active state:** `{"max_price": 16}`  
**Unresolved:** 'Let's go over that side.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "mall"}` -> R08 Forno Pizza ($16), R27 Bibim Bowl ($15), R35 Noodle Bar 88 ($16), R37 Pita Port ($14), R39 Falafel Stop ($11)  
&nbsp;&nbsp;- `{"location": "station"}` -> R08 Forno Pizza ($16), R11 Taco Loco ($12), R32 Dumpling King ($13), R39 Falafel Stop ($11)  
**Mention order in the chat:** `["mall", "station"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R08 Forno Pizza ($16), R27 Bibim Bowl ($15), R35 Noodle Bar 88 ($16), R37 Pita Port ($14), R39 Falafel Stop ($11)  
**Safe without asking:** R08 Forno Pizza ($16), R39 Falafel Stop ($11)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-04A-P1  (ambiguous_reference, family BB-LOC-04, variant A_para1)

*Contrast:* A: station -> R01 Sakura Ramen ($18), R21 Masala House ($20); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: budget $25 makes R23 Saffron Leaf ($25) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Can you help me find a place to eat? Indian or Japanese would both be fine. | user states cuisine=['Indian', 'Japanese'] |
| 2 | assistant | Happy to help. I can see places by the station and by the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $24 per person. | user states max_price=24 |
| 4 | assistant | Thanks, that helps. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Understood. | assistant acknowledges |
| 7 | user | What's around that area? | user: 'What's around that area?' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Indian", "Japanese"], "max_price": 24, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Indian", "Japanese"], "max_price": 24, "dinner": true}`  
**Unresolved:** 'What's around that area?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18), R21 Masala House ($20)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R02 Hoshi Sushi Bar ($24)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-04A-P2  (ambiguous_reference, family BB-LOC-04, variant A_para2)

*Contrast:* A: station -> R01 Sakura Ramen ($18), R21 Masala House ($20); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: budget $25 makes R23 Saffron Leaf ($25) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I need ideas for a meal. Maybe Indian, maybe Japanese, I'm easy. | user states cuisine=['Indian', 'Japanese'] |
| 2 | assistant | Of course. A couple of spots are close to the station, and a couple are close to the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $24 per person. | user states max_price=24 |
| 4 | assistant | Okay, budget noted. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Sounds good. | assistant acknowledges |
| 7 | user | Find me something near there. | user: 'Find me something near there.' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Indian", "Japanese"], "max_price": 24, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Indian", "Japanese"], "max_price": 24, "dinner": true}`  
**Unresolved:** 'Find me something near there.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18), R21 Masala House ($20)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R02 Hoshi Sushi Bar ($24)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-04B-P1  (ambiguous_reference, family BB-LOC-04, variant B_para1)

*Contrast:* A: station -> R01 Sakura Ramen ($18), R21 Masala House ($20); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: budget $25 makes R23 Saffron Leaf ($25) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Can you help me find a place to eat? Indian or Japanese would both be fine. | user states cuisine=['Indian', 'Japanese'] |
| 2 | assistant | Happy to help. I can see places by the station and by the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Thanks, that helps. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Understood. | assistant acknowledges |
| 7 | user | What's around that area? | user: 'What's around that area?' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Indian", "Japanese"], "max_price": 25, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Indian", "Japanese"], "max_price": 25, "dinner": true}`  
**Unresolved:** 'What's around that area?' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18), R21 Masala House ($20), R23 Saffron Leaf ($25)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R23 Saffron Leaf ($25)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R02 Hoshi Sushi Bar ($24), R23 Saffron Leaf ($25)  
**Safe without asking:** R23 Saffron Leaf ($25)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-04B-P2  (ambiguous_reference, family BB-LOC-04, variant B_para2)

*Contrast:* A: station -> R01 Sakura Ramen ($18), R21 Masala House ($20); mall -> R02 Hoshi Sushi Bar ($24); nothing near both -> ask. B: budget $25 makes R23 Saffron Leaf ($25) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I need ideas for a meal. Maybe Indian, maybe Japanese, I'm easy. | user states cuisine=['Indian', 'Japanese'] |
| 2 | assistant | Of course. A couple of spots are close to the station, and a couple are close to the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Okay, budget noted. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Sounds good. | assistant acknowledges |
| 7 | user | Find me something near there. | user: 'Find me something near there.' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Indian", "Japanese"], "max_price": 25, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Indian", "Japanese"], "max_price": 25, "dinner": true}`  
**Unresolved:** 'Find me something near there.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18), R21 Masala House ($20), R23 Saffron Leaf ($25)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R23 Saffron Leaf ($25)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R02 Hoshi Sushi Bar ($24), R23 Saffron Leaf ($25)  
**Safe without asking:** R23 Saffron Leaf ($25)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-05A-P1  (ambiguous_reference, family BB-LOC-05, variant A_para1)

*Contrast:* A: station -> R32 Dumpling King ($13); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $25 makes R31 Golden Dragon ($24) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Can you help me find a place to eat? Chinese or Korean would both be fine. | user states cuisine=['Chinese', 'Korean'] |
| 2 | assistant | Happy to help. I can see places by the station and by the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $15 per person. | user states max_price=15 |
| 4 | assistant | Thanks, that helps. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Understood. | assistant acknowledges |
| 7 | user | Let's look over that side. | user: 'Let's look over that side.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Chinese", "Korean"], "max_price": 15, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Korean"], "max_price": 15}`  
**Unresolved:** 'Let's look over that side.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R32 Dumpling King ($13)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R27 Bibim Bowl ($15)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R32 Dumpling King ($13)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-05A-P2  (ambiguous_reference, family BB-LOC-05, variant A_para2)

*Contrast:* A: station -> R32 Dumpling King ($13); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $25 makes R31 Golden Dragon ($24) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I need ideas for a meal. Maybe Chinese, maybe Korean, I'm easy. | user states cuisine=['Chinese', 'Korean'] |
| 2 | assistant | Of course. A couple of spots are close to the station, and a couple are close to the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $15 per person. | user states max_price=15 |
| 4 | assistant | Okay, budget noted. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Sounds good. | assistant acknowledges |
| 7 | user | Something around there would be good. | user: 'Something around there would be good.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Chinese", "Korean"], "max_price": 15, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Korean"], "max_price": 15}`  
**Unresolved:** 'Something around there would be good.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R32 Dumpling King ($13)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R27 Bibim Bowl ($15)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R32 Dumpling King ($13)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-05B-P1  (ambiguous_reference, family BB-LOC-05, variant B_para1)

*Contrast:* A: station -> R32 Dumpling King ($13); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $25 makes R31 Golden Dragon ($24) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Can you help me find a place to eat? Chinese or Korean would both be fine. | user states cuisine=['Chinese', 'Korean'] |
| 2 | assistant | Happy to help. I can see places by the station and by the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Thanks, that helps. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Understood. | assistant acknowledges |
| 7 | user | Let's look over that side. | user: 'Let's look over that side.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Chinese", "Korean"], "max_price": 25, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Korean"], "max_price": 25}`  
**Unresolved:** 'Let's look over that side.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R28 Kimchi Pot ($22), R31 Golden Dragon ($24), R32 Dumpling King ($13)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R27 Bibim Bowl ($15), R31 Golden Dragon ($24), R35 Noodle Bar 88 ($16)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R28 Kimchi Pot ($22), R31 Golden Dragon ($24), R32 Dumpling King ($13)  
**Safe without asking:** R31 Golden Dragon ($24)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LOC-05B-P2  (ambiguous_reference, family BB-LOC-05, variant B_para2)

*Contrast:* A: station -> R32 Dumpling King ($13); mall -> R27 Bibim Bowl ($15); nothing near both -> ask. B: budget $25 makes R31 Golden Dragon ($24) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I need ideas for a meal. Maybe Chinese, maybe Korean, I'm easy. | user states cuisine=['Chinese', 'Korean'] |
| 2 | assistant | Of course. A couple of spots are close to the station, and a couple are close to the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Okay, budget noted. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Sounds good. | assistant acknowledges |
| 7 | user | Something around there would be good. | user: 'Something around there would be good.' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Chinese", "Korean"], "max_price": 25, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Korean"], "max_price": 25}`  
**Unresolved:** 'Something around there would be good.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R28 Kimchi Pot ($22), R31 Golden Dragon ($24), R32 Dumpling King ($13)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R27 Bibim Bowl ($15), R31 Golden Dragon ($24), R35 Noodle Bar 88 ($16)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R28 Kimchi Pot ($22), R31 Golden Dragon ($24), R32 Dumpling King ($13)  
**Safe without asking:** R31 Golden Dragon ($24)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

# 4b: Two-question scenarios

---

## BB-TWOQ-01  (ambiguous_reference, family BB-TWOQ-01, variant single)

*Contrast:* Two things unclear. Chinese+station -> R32 Dumpling King ($13); Chinese+mall -> R35 Noodle Bar 88 ($16); Korean+station -> R28 Kimchi Pot ($22); Korean+mall -> R27 Bibim Bowl ($15). Knowing only the cuisine still leaves station vs mall with no shared restaurant; knowing only the area still leaves two cuisines -> exactly 2 questions needed.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | My friend is choosing where we get lunch. | user: friend decides; lunch, no dinner constraint |
| 2 | assistant | Fun! What is she considering? | assistant asks |
| 3 | user | She's deciding between Chinese and Korean, either near the station or near the mall. | user lists two cuisines (Chinese, Korean) and two areas (station, mall); none chosen |
| 4 | assistant | Got it. Any budget? | assistant asks budget |
| 5 | user | Up to $22 each. | user states max_price=22 |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | She just texted me her choice. Can you find a place that matches it? | user: 'her choice' = cuisine AND area unknown (UNRESOLVED x2; hidden: Chinese + station) |

**Hidden goal:** `{"max_price": 22, "cuisine": "Chinese", "location": "station"}`  
**Gold active state:** `{"max_price": 22}`  
**Unresolved:** 'her choice' (turn 7, slot cuisine)  
**Unresolved:** 'her choice' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"cuisine": "Chinese", "location": "station"}` -> R32 Dumpling King ($13)  
&nbsp;&nbsp;- `{"cuisine": "Chinese", "location": "mall"}` -> R35 Noodle Bar 88 ($16)  
&nbsp;&nbsp;- `{"cuisine": "Korean", "location": "station"}` -> R28 Kimchi Pot ($22)  
&nbsp;&nbsp;- `{"cuisine": "Korean", "location": "mall"}` -> R27 Bibim Bowl ($15)  
**Mention order in the chat:** `{"cuisine": ["Chinese", "Korean"], "location": ["station", "mall"]}`  
**Should ask:** YES - cuisine@t7, location@t7  
**Questions needed:** 2  
**Successful recommendations:** R32 Dumpling King ($13)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-TWOQ-02  (ambiguous_reference, family BB-TWOQ-02, variant single)

*Contrast:* Two things unclear. Japanese+mall -> R02 Hoshi Sushi Bar ($24); Japanese+station -> R01 Sakura Ramen ($18); Italian+mall -> R07 Nonna's Kitchen ($27); Italian+station -> R06 Trattoria Lucca ($22). Knowing only the cuisine still leaves station vs mall with no shared restaurant; knowing only the area still leaves two cuisines -> exactly 2 questions needed.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | My friend is choosing where we eat tonight. | user: friend decides; tonight = dinner |
| 2 | assistant | Fun! What is she considering? | assistant asks |
| 3 | user | She's deciding between Japanese and Italian, either near the mall or near the station. | user lists two cuisines (Japanese, Italian) and two areas (mall, station); none chosen |
| 4 | assistant | Got it. Any budget? | assistant asks budget |
| 5 | user | Up to $27 each. | user states max_price=27 |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | She just texted me her choice. Can you find a place that matches it? | user: 'her choice' = cuisine AND area unknown (UNRESOLVED x2; hidden: Italian + mall) |

**Hidden goal:** `{"max_price": 27, "dinner": true, "cuisine": "Italian", "location": "mall"}`  
**Gold active state:** `{"max_price": 27, "dinner": true}`  
**Unresolved:** 'her choice' (turn 7, slot cuisine)  
**Unresolved:** 'her choice' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"cuisine": "Japanese", "location": "mall"}` -> R02 Hoshi Sushi Bar ($24)  
&nbsp;&nbsp;- `{"cuisine": "Japanese", "location": "station"}` -> R01 Sakura Ramen ($18)  
&nbsp;&nbsp;- `{"cuisine": "Italian", "location": "mall"}` -> R07 Nonna's Kitchen ($27)  
&nbsp;&nbsp;- `{"cuisine": "Italian", "location": "station"}` -> R06 Trattoria Lucca ($22)  
**Mention order in the chat:** `{"cuisine": ["Japanese", "Italian"], "location": ["mall", "station"]}`  
**Should ask:** YES - cuisine@t7, location@t7  
**Questions needed:** 2  
**Successful recommendations:** R07 Nonna's Kitchen ($27)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-TWOQ-03  (ambiguous_reference, family BB-TWOQ-03, variant single)

*Contrast:* Two things unclear. Japanese+station -> R01 Sakura Ramen ($18); Japanese+mall -> R02 Hoshi Sushi Bar ($24); Korean+station -> R28 Kimchi Pot ($22); Korean+mall -> R29 Hanok Table ($27). Knowing only the cuisine still leaves station vs mall with no shared restaurant; knowing only the area still leaves two cuisines -> exactly 2 questions needed.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | My friend is choosing where we eat tonight. | user: friend decides; tonight = dinner |
| 2 | assistant | Fun! What is she considering? | assistant asks |
| 3 | user | She's deciding between Japanese and Korean, either near the station or near the mall. | user lists two cuisines (Japanese, Korean) and two areas (station, mall); none chosen |
| 4 | assistant | Got it. Any budget? | assistant asks budget |
| 5 | user | Up to $27 each. | user states max_price=27 |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | She just texted me her choice. Can you find a place that matches it? | user: 'her choice' = cuisine AND area unknown (UNRESOLVED x2; hidden: Korean + mall) |

**Hidden goal:** `{"max_price": 27, "dinner": true, "cuisine": "Korean", "location": "mall"}`  
**Gold active state:** `{"max_price": 27, "dinner": true}`  
**Unresolved:** 'her choice' (turn 7, slot cuisine)  
**Unresolved:** 'her choice' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"cuisine": "Japanese", "location": "station"}` -> R01 Sakura Ramen ($18)  
&nbsp;&nbsp;- `{"cuisine": "Japanese", "location": "mall"}` -> R02 Hoshi Sushi Bar ($24)  
&nbsp;&nbsp;- `{"cuisine": "Korean", "location": "station"}` -> R28 Kimchi Pot ($22)  
&nbsp;&nbsp;- `{"cuisine": "Korean", "location": "mall"}` -> R29 Hanok Table ($27)  
**Mention order in the chat:** `{"cuisine": ["Japanese", "Korean"], "location": ["station", "mall"]}`  
**Should ask:** YES - cuisine@t7, location@t7  
**Questions needed:** 2  
**Successful recommendations:** R29 Hanok Table ($27)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-TWOQ-04  (ambiguous_reference, family BB-TWOQ-04, variant single)

*Contrast:* Two things unclear. Korean+mall -> R27 Bibim Bowl ($15); Korean+station -> R28 Kimchi Pot ($22); Japanese+mall -> R02 Hoshi Sushi Bar ($24); Japanese+station -> R01 Sakura Ramen ($18). Knowing only the cuisine still leaves station vs mall with no shared restaurant; knowing only the area still leaves two cuisines -> exactly 2 questions needed.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | My friend is choosing where we get lunch. | user: friend decides; lunch, no dinner constraint |
| 2 | assistant | Fun! What is she considering? | assistant asks |
| 3 | user | She's deciding between Korean and Japanese, either near the mall or near the station. | user lists two cuisines (Korean, Japanese) and two areas (mall, station); none chosen |
| 4 | assistant | Got it. Any budget? | assistant asks budget |
| 5 | user | Up to $24 each. | user states max_price=24 |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | She just texted me her choice. Can you find a place that matches it? | user: 'her choice' = cuisine AND area unknown (UNRESOLVED x2; hidden: Korean + station) |

**Hidden goal:** `{"max_price": 24, "cuisine": "Korean", "location": "station"}`  
**Gold active state:** `{"max_price": 24}`  
**Unresolved:** 'her choice' (turn 7, slot cuisine)  
**Unresolved:** 'her choice' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"cuisine": "Korean", "location": "mall"}` -> R27 Bibim Bowl ($15)  
&nbsp;&nbsp;- `{"cuisine": "Korean", "location": "station"}` -> R28 Kimchi Pot ($22)  
&nbsp;&nbsp;- `{"cuisine": "Japanese", "location": "mall"}` -> R02 Hoshi Sushi Bar ($24)  
&nbsp;&nbsp;- `{"cuisine": "Japanese", "location": "station"}` -> R01 Sakura Ramen ($18)  
**Mention order in the chat:** `{"cuisine": ["Korean", "Japanese"], "location": ["mall", "station"]}`  
**Should ask:** YES - cuisine@t7, location@t7  
**Questions needed:** 2  
**Successful recommendations:** R28 Kimchi Pot ($22)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-TWOQ-05  (ambiguous_reference, family BB-TWOQ-05, variant single)

*Contrast:* Two things unclear. Chinese+mall -> R35 Noodle Bar 88 ($16); Chinese+station -> R32 Dumpling King ($13); Korean+mall -> R27 Bibim Bowl ($15); Korean+station -> R28 Kimchi Pot ($22). Knowing only the cuisine still leaves station vs mall with no shared restaurant; knowing only the area still leaves two cuisines -> exactly 2 questions needed.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | My friend is choosing where we get lunch. | user: friend decides; lunch, no dinner constraint |
| 2 | assistant | Fun! What is she considering? | assistant asks |
| 3 | user | She's deciding between Chinese and Korean, either near the mall or near the station. | user lists two cuisines (Chinese, Korean) and two areas (mall, station); none chosen |
| 4 | assistant | Got it. Any budget? | assistant asks budget |
| 5 | user | Up to $23 each. | user states max_price=23 |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | She just texted me her choice. Can you find a place that matches it? | user: 'her choice' = cuisine AND area unknown (UNRESOLVED x2; hidden: Chinese + mall) |

**Hidden goal:** `{"max_price": 23, "cuisine": "Chinese", "location": "mall"}`  
**Gold active state:** `{"max_price": 23}`  
**Unresolved:** 'her choice' (turn 7, slot cuisine)  
**Unresolved:** 'her choice' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"cuisine": "Chinese", "location": "mall"}` -> R35 Noodle Bar 88 ($16)  
&nbsp;&nbsp;- `{"cuisine": "Chinese", "location": "station"}` -> R32 Dumpling King ($13)  
&nbsp;&nbsp;- `{"cuisine": "Korean", "location": "mall"}` -> R27 Bibim Bowl ($15)  
&nbsp;&nbsp;- `{"cuisine": "Korean", "location": "station"}` -> R28 Kimchi Pot ($22)  
**Mention order in the chat:** `{"cuisine": ["Chinese", "Korean"], "location": ["mall", "station"]}`  
**Should ask:** YES - cuisine@t7, location@t7  
**Questions needed:** 2  
**Successful recommendations:** R35 Noodle Bar 88 ($16)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-TWOQ-06  (ambiguous_reference, family BB-TWOQ-06, variant single)

*Contrast:* Two things unclear. Japanese+station -> R01 Sakura Ramen ($18); Japanese+mall -> R02 Hoshi Sushi Bar ($24); Italian+station -> R06 Trattoria Lucca ($22); Italian+mall -> R07 Nonna's Kitchen ($27). Knowing only the cuisine still leaves station vs mall with no shared restaurant; knowing only the area still leaves two cuisines -> exactly 2 questions needed.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | My friend is choosing where we eat tonight. | user: friend decides; tonight = dinner |
| 2 | assistant | Fun! What is she considering? | assistant asks |
| 3 | user | She's deciding between Japanese and Italian, either near the station or near the mall. | user lists two cuisines (Japanese, Italian) and two areas (station, mall); none chosen |
| 4 | assistant | Got it. Any budget? | assistant asks budget |
| 5 | user | Up to $28 each. | user states max_price=28 |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | She just texted me her choice. Can you find a place that matches it? | user: 'her choice' = cuisine AND area unknown (UNRESOLVED x2; hidden: Italian + station) |

**Hidden goal:** `{"max_price": 28, "dinner": true, "cuisine": "Italian", "location": "station"}`  
**Gold active state:** `{"max_price": 28, "dinner": true}`  
**Unresolved:** 'her choice' (turn 7, slot cuisine)  
**Unresolved:** 'her choice' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"cuisine": "Japanese", "location": "station"}` -> R01 Sakura Ramen ($18)  
&nbsp;&nbsp;- `{"cuisine": "Japanese", "location": "mall"}` -> R02 Hoshi Sushi Bar ($24)  
&nbsp;&nbsp;- `{"cuisine": "Italian", "location": "station"}` -> R06 Trattoria Lucca ($22)  
&nbsp;&nbsp;- `{"cuisine": "Italian", "location": "mall"}` -> R07 Nonna's Kitchen ($27)  
**Mention order in the chat:** `{"cuisine": ["Japanese", "Italian"], "location": ["station", "mall"]}`  
**Should ask:** YES - cuisine@t7, location@t7  
**Questions needed:** 2  
**Successful recommendations:** R06 Trattoria Lucca ($22)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-TWOQ-07  (ambiguous_reference, family BB-TWOQ-07, variant single)

*Contrast:* Two things unclear. Japanese+mall -> R02 Hoshi Sushi Bar ($24); Japanese+station -> R01 Sakura Ramen ($18); Korean+mall -> R29 Hanok Table ($27); Korean+station -> R28 Kimchi Pot ($22). Knowing only the cuisine still leaves station vs mall with no shared restaurant; knowing only the area still leaves two cuisines -> exactly 2 questions needed.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | My friend is choosing where we eat tonight. | user: friend decides; tonight = dinner |
| 2 | assistant | Fun! What is she considering? | assistant asks |
| 3 | user | She's deciding between Japanese and Korean, either near the mall or near the station. | user lists two cuisines (Japanese, Korean) and two areas (mall, station); none chosen |
| 4 | assistant | Got it. Any budget? | assistant asks budget |
| 5 | user | Up to $28 each. | user states max_price=28 |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | She just texted me her choice. Can you find a place that matches it? | user: 'her choice' = cuisine AND area unknown (UNRESOLVED x2; hidden: Korean + station) |

**Hidden goal:** `{"max_price": 28, "dinner": true, "cuisine": "Korean", "location": "station"}`  
**Gold active state:** `{"max_price": 28, "dinner": true}`  
**Unresolved:** 'her choice' (turn 7, slot cuisine)  
**Unresolved:** 'her choice' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"cuisine": "Japanese", "location": "mall"}` -> R02 Hoshi Sushi Bar ($24)  
&nbsp;&nbsp;- `{"cuisine": "Japanese", "location": "station"}` -> R01 Sakura Ramen ($18)  
&nbsp;&nbsp;- `{"cuisine": "Korean", "location": "mall"}` -> R29 Hanok Table ($27)  
&nbsp;&nbsp;- `{"cuisine": "Korean", "location": "station"}` -> R28 Kimchi Pot ($22)  
**Mention order in the chat:** `{"cuisine": ["Japanese", "Korean"], "location": ["mall", "station"]}`  
**Should ask:** YES - cuisine@t7, location@t7  
**Questions needed:** 2  
**Successful recommendations:** R28 Kimchi Pot ($22)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-TWOQ-08  (ambiguous_reference, family BB-TWOQ-08, variant single)

*Contrast:* Two things unclear. Korean+station -> R28 Kimchi Pot ($22); Korean+mall -> R27 Bibim Bowl ($15), R29 Hanok Table ($27); Japanese+station -> R01 Sakura Ramen ($18); Japanese+mall -> R02 Hoshi Sushi Bar ($24). Knowing only the cuisine still leaves station vs mall with no shared restaurant; knowing only the area still leaves two cuisines -> exactly 2 questions needed.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | My friend is choosing where we get lunch. | user: friend decides; lunch, no dinner constraint |
| 2 | assistant | Fun! What is she considering? | assistant asks |
| 3 | user | She's deciding between Korean and Japanese, either near the station or near the mall. | user lists two cuisines (Korean, Japanese) and two areas (station, mall); none chosen |
| 4 | assistant | Got it. Any budget? | assistant asks budget |
| 5 | user | Up to $27 each. | user states max_price=27 |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | She just texted me her choice. Can you find a place that matches it? | user: 'her choice' = cuisine AND area unknown (UNRESOLVED x2; hidden: Korean + mall) |

**Hidden goal:** `{"max_price": 27, "cuisine": "Korean", "location": "mall"}`  
**Gold active state:** `{"max_price": 27}`  
**Unresolved:** 'her choice' (turn 7, slot cuisine)  
**Unresolved:** 'her choice' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"cuisine": "Korean", "location": "station"}` -> R28 Kimchi Pot ($22)  
&nbsp;&nbsp;- `{"cuisine": "Korean", "location": "mall"}` -> R27 Bibim Bowl ($15), R29 Hanok Table ($27)  
&nbsp;&nbsp;- `{"cuisine": "Japanese", "location": "station"}` -> R01 Sakura Ramen ($18)  
&nbsp;&nbsp;- `{"cuisine": "Japanese", "location": "mall"}` -> R02 Hoshi Sushi Bar ($24)  
**Mention order in the chat:** `{"cuisine": ["Korean", "Japanese"], "location": ["station", "mall"]}`  
**Should ask:** YES - cuisine@t7, location@t7  
**Questions needed:** 2  
**Successful recommendations:** R27 Bibim Bowl ($15), R29 Hanok Table ($27)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

# 4d: Suggestion traps (with accepted controls)

---

## BB-SUG-01A  (suggestion_acceptance, family BB-SUG-01, variant A)

*Contrast:* A: suggestion not accepted -> cuisine=Chinese: R32 Dumpling King ($13). Treating the suggestion as accepted picks R21 Masala House ($20), which is WRONG. B (control): explicit acceptance -> R21 Masala House ($20) correct.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'd like Chinese food near the station. | user states cuisine=Chinese |
| 2 | assistant | Sounds good! Any budget? | assistant asks budget |
| 3 | user | No more than $20 per person. | user states max_price=20 |
| 4 | assistant | There are also some nice Indian places near the station. Would Indian work instead? | assistant PROPOSES cuisine=Indian |
| 5 | user | Hmm, I'll think about it. | user does NOT accept (hedges); cuisine stays Chinese |
| 6 | assistant | Okay! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"max_price": 20, "location": "station", "cuisine": "Chinese"}`  
**Gold active state:** `{"max_price": 20, "location": "station", "cuisine": "Chinese"}`  
**Proposed, not accepted:** `[{"slot": "cuisine", "value": "Indian", "turn": 4, "status": "not accepted"}]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R32 Dumpling King ($13)  
**Safe without asking:** R32 Dumpling King ($13)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-SUG-01B  (suggestion_acceptance, family BB-SUG-01, variant B)

*Contrast:* A: suggestion not accepted -> cuisine=Chinese: R32 Dumpling King ($13). Treating the suggestion as accepted picks R21 Masala House ($20), which is WRONG. B (control): explicit acceptance -> R21 Masala House ($20) correct.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'd like Chinese food near the station. | user states cuisine=Chinese |
| 2 | assistant | Sounds good! Any budget? | assistant asks budget |
| 3 | user | No more than $20 per person. | user states max_price=20 |
| 4 | assistant | There are also some nice Indian places near the station. Would Indian work instead? | assistant PROPOSES cuisine=Indian |
| 5 | user | Sure, let's do Indian instead. | user ACCEPTS proposal; cuisine=Indian |
| 6 | assistant | Okay! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"max_price": 20, "location": "station", "cuisine": "Indian"}`  
**Gold active state:** `{"max_price": 20, "location": "station", "cuisine": "Indian"}`  
**Superseded:** `[{"slot": "cuisine", "value": "Chinese", "turn": 1}]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R21 Masala House ($20)  
**Safe without asking:** R21 Masala House ($20)  
**Relations:** t5 confirm t4 (cuisine); t5 revise t1 (cuisine)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-SUG-02A  (suggestion_acceptance, family BB-SUG-02, variant A)

*Contrast:* A: suggestion not accepted -> cuisine=Indian: R21 Masala House ($20). Treating the suggestion as accepted picks R08 Forno Pizza ($16), which is WRONG. B (control): explicit acceptance -> R08 Forno Pizza ($16) correct.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'd like Indian food near the station. | user states cuisine=Indian |
| 2 | assistant | Sounds good! Any budget? | assistant asks budget |
| 3 | user | No more than $20 per person. | user states max_price=20 |
| 4 | assistant | There are also some nice Italian places near the station. Would Italian work instead? | assistant PROPOSES cuisine=Italian |
| 5 | user | Maybe, I'm not sure yet. | user does NOT accept (hedges); cuisine stays Indian |
| 6 | assistant | Okay! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"max_price": 20, "location": "station", "cuisine": "Indian"}`  
**Gold active state:** `{"max_price": 20, "location": "station", "cuisine": "Indian"}`  
**Proposed, not accepted:** `[{"slot": "cuisine", "value": "Italian", "turn": 4, "status": "not accepted"}]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R21 Masala House ($20)  
**Safe without asking:** R21 Masala House ($20)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-SUG-02B  (suggestion_acceptance, family BB-SUG-02, variant B)

*Contrast:* A: suggestion not accepted -> cuisine=Indian: R21 Masala House ($20). Treating the suggestion as accepted picks R08 Forno Pizza ($16), which is WRONG. B (control): explicit acceptance -> R08 Forno Pizza ($16) correct.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'd like Indian food near the station. | user states cuisine=Indian |
| 2 | assistant | Sounds good! Any budget? | assistant asks budget |
| 3 | user | No more than $20 per person. | user states max_price=20 |
| 4 | assistant | There are also some nice Italian places near the station. Would Italian work instead? | assistant PROPOSES cuisine=Italian |
| 5 | user | Sure, let's do Italian instead. | user ACCEPTS proposal; cuisine=Italian |
| 6 | assistant | Okay! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"max_price": 20, "location": "station", "cuisine": "Italian"}`  
**Gold active state:** `{"max_price": 20, "location": "station", "cuisine": "Italian"}`  
**Superseded:** `[{"slot": "cuisine", "value": "Indian", "turn": 1}]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R08 Forno Pizza ($16)  
**Safe without asking:** R08 Forno Pizza ($16)  
**Relations:** t5 confirm t4 (cuisine); t5 revise t1 (cuisine)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-SUG-03A  (suggestion_acceptance, family BB-SUG-03, variant A)

*Contrast:* A: suggestion not accepted -> cuisine=Mediterranean: R39 Falafel Stop ($11). Treating the suggestion as accepted picks R11 Taco Loco ($12), which is WRONG. B (control): explicit acceptance -> R11 Taco Loco ($12) correct.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'd like Mediterranean food near the station. | user states cuisine=Mediterranean |
| 2 | assistant | Sounds good! Any budget? | assistant asks budget |
| 3 | user | No more than $12 per person. | user states max_price=12 |
| 4 | assistant | There are also some nice Mexican places near the station. Would Mexican work instead? | assistant PROPOSES cuisine=Mexican |
| 5 | user | I don't know, possibly. | user does NOT accept (hedges); cuisine stays Mediterranean |
| 6 | assistant | Okay! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"max_price": 12, "location": "station", "cuisine": "Mediterranean"}`  
**Gold active state:** `{"max_price": 12, "location": "station", "cuisine": "Mediterranean"}`  
**Proposed, not accepted:** `[{"slot": "cuisine", "value": "Mexican", "turn": 4, "status": "not accepted"}]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R39 Falafel Stop ($11)  
**Safe without asking:** R39 Falafel Stop ($11)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-SUG-03B  (suggestion_acceptance, family BB-SUG-03, variant B)

*Contrast:* A: suggestion not accepted -> cuisine=Mediterranean: R39 Falafel Stop ($11). Treating the suggestion as accepted picks R11 Taco Loco ($12), which is WRONG. B (control): explicit acceptance -> R11 Taco Loco ($12) correct.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'd like Mediterranean food near the station. | user states cuisine=Mediterranean |
| 2 | assistant | Sounds good! Any budget? | assistant asks budget |
| 3 | user | No more than $12 per person. | user states max_price=12 |
| 4 | assistant | There are also some nice Mexican places near the station. Would Mexican work instead? | assistant PROPOSES cuisine=Mexican |
| 5 | user | Sure, let's do Mexican instead. | user ACCEPTS proposal; cuisine=Mexican |
| 6 | assistant | Okay! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"max_price": 12, "location": "station", "cuisine": "Mexican"}`  
**Gold active state:** `{"max_price": 12, "location": "station", "cuisine": "Mexican"}`  
**Superseded:** `[{"slot": "cuisine", "value": "Mediterranean", "turn": 1}]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R11 Taco Loco ($12)  
**Safe without asking:** R11 Taco Loco ($12)  
**Relations:** t5 confirm t4 (cuisine); t5 revise t1 (cuisine)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-SUG-04A  (suggestion_acceptance, family BB-SUG-04, variant A)

*Contrast:* A: suggestion not accepted -> cuisine=Italian: R08 Forno Pizza ($16). Treating the suggestion as accepted picks R27 Bibim Bowl ($15), which is WRONG. B (control): explicit acceptance -> R27 Bibim Bowl ($15) correct.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'd like Italian food near the mall. | user states cuisine=Italian |
| 2 | assistant | Sounds good! Any budget? | assistant asks budget |
| 3 | user | No more than $16 per person. | user states max_price=16 |
| 4 | assistant | There are also some nice Korean places near the mall. Would Korean work instead? | assistant PROPOSES cuisine=Korean |
| 5 | user | Let me think about that one. | user does NOT accept (hedges); cuisine stays Italian |
| 6 | assistant | Okay! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"max_price": 16, "location": "mall", "cuisine": "Italian"}`  
**Gold active state:** `{"max_price": 16, "location": "mall", "cuisine": "Italian"}`  
**Proposed, not accepted:** `[{"slot": "cuisine", "value": "Korean", "turn": 4, "status": "not accepted"}]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R08 Forno Pizza ($16)  
**Safe without asking:** R08 Forno Pizza ($16)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-SUG-04B  (suggestion_acceptance, family BB-SUG-04, variant B)

*Contrast:* A: suggestion not accepted -> cuisine=Italian: R08 Forno Pizza ($16). Treating the suggestion as accepted picks R27 Bibim Bowl ($15), which is WRONG. B (control): explicit acceptance -> R27 Bibim Bowl ($15) correct.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'd like Italian food near the mall. | user states cuisine=Italian |
| 2 | assistant | Sounds good! Any budget? | assistant asks budget |
| 3 | user | No more than $16 per person. | user states max_price=16 |
| 4 | assistant | There are also some nice Korean places near the mall. Would Korean work instead? | assistant PROPOSES cuisine=Korean |
| 5 | user | Sure, let's do Korean instead. | user ACCEPTS proposal; cuisine=Korean |
| 6 | assistant | Okay! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"max_price": 16, "location": "mall", "cuisine": "Korean"}`  
**Gold active state:** `{"max_price": 16, "location": "mall", "cuisine": "Korean"}`  
**Superseded:** `[{"slot": "cuisine", "value": "Italian", "turn": 1}]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R27 Bibim Bowl ($15)  
**Safe without asking:** R27 Bibim Bowl ($15)  
**Relations:** t5 confirm t4 (cuisine); t5 revise t1 (cuisine)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-SUG-05A  (suggestion_acceptance, family BB-SUG-05, variant A)

*Contrast:* A: suggestion not accepted -> location=station: R32 Dumpling King ($13). Treating the suggestion as accepted picks R35 Noodle Bar 88 ($16), which is WRONG. B (control): explicit acceptance -> R35 Noodle Bar 88 ($16) correct.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm looking for Chinese food near the station. | user states location=station, cuisine=Chinese |
| 2 | assistant | Sounds good! Any budget? | assistant asks budget |
| 3 | user | No more than $20 per person. | user states max_price=20 |
| 4 | assistant | The mall area also has Chinese food in that range. Want me to look there instead? | assistant PROPOSES location=mall |
| 5 | user | I'm not sure about that yet. | user does NOT accept (hedges); location stays station |
| 6 | assistant | Okay! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Chinese", "max_price": 20, "location": "station"}`  
**Gold active state:** `{"cuisine": "Chinese", "max_price": 20, "location": "station"}`  
**Proposed, not accepted:** `[{"slot": "location", "value": "mall", "turn": 4, "status": "not accepted"}]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R32 Dumpling King ($13)  
**Safe without asking:** R32 Dumpling King ($13)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-SUG-05B  (suggestion_acceptance, family BB-SUG-05, variant B)

*Contrast:* A: suggestion not accepted -> location=station: R32 Dumpling King ($13). Treating the suggestion as accepted picks R35 Noodle Bar 88 ($16), which is WRONG. B (control): explicit acceptance -> R35 Noodle Bar 88 ($16) correct.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm looking for Chinese food near the station. | user states location=station, cuisine=Chinese |
| 2 | assistant | Sounds good! Any budget? | assistant asks budget |
| 3 | user | No more than $20 per person. | user states max_price=20 |
| 4 | assistant | The mall area also has Chinese food in that range. Want me to look there instead? | assistant PROPOSES location=mall |
| 5 | user | Yes, let's look near the mall instead. | user ACCEPTS proposal; location=mall |
| 6 | assistant | Okay! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Chinese", "max_price": 20, "location": "mall"}`  
**Gold active state:** `{"cuisine": "Chinese", "max_price": 20, "location": "mall"}`  
**Superseded:** `[{"slot": "location", "value": "station", "turn": 1}]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R35 Noodle Bar 88 ($16)  
**Safe without asking:** R35 Noodle Bar 88 ($16)  
**Relations:** t5 confirm t4 (location); t5 revise t1 (location)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-SUG-06A  (suggestion_acceptance, family BB-SUG-06, variant A)

*Contrast:* A: suggestion not accepted -> location=mall: R07 Nonna's Kitchen ($27). Treating the suggestion as accepted picks R06 Trattoria Lucca ($22), which is WRONG. B (control): explicit acceptance -> R06 Trattoria Lucca ($22) correct.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm looking for Italian food near the mall. | user states location=mall, cuisine=Italian |
| 2 | assistant | Sounds good! Any budget? | assistant asks budget |
| 3 | user | No more than $30 per person. It's for dinner. | user states max_price=30, dinner=true |
| 4 | assistant | The station area also has Italian food in that range. Want me to look there instead? | assistant PROPOSES location=station |
| 5 | user | Hmm, maybe another time. | user does NOT accept (hedges); location stays mall |
| 6 | assistant | Okay! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Italian", "max_price": 30, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": "Italian", "max_price": 30, "dinner": true, "location": "mall"}`  
**Proposed, not accepted:** `[{"slot": "location", "value": "station", "turn": 4, "status": "not accepted"}]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R07 Nonna's Kitchen ($27)  
**Safe without asking:** R07 Nonna's Kitchen ($27)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-SUG-06B  (suggestion_acceptance, family BB-SUG-06, variant B)

*Contrast:* A: suggestion not accepted -> location=mall: R07 Nonna's Kitchen ($27). Treating the suggestion as accepted picks R06 Trattoria Lucca ($22), which is WRONG. B (control): explicit acceptance -> R06 Trattoria Lucca ($22) correct.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm looking for Italian food near the mall. | user states location=mall, cuisine=Italian |
| 2 | assistant | Sounds good! Any budget? | assistant asks budget |
| 3 | user | No more than $30 per person. It's for dinner. | user states max_price=30, dinner=true |
| 4 | assistant | The station area also has Italian food in that range. Want me to look there instead? | assistant PROPOSES location=station |
| 5 | user | Yes, let's look near the station instead. | user ACCEPTS proposal; location=station |
| 6 | assistant | Okay! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Italian", "max_price": 30, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": "Italian", "max_price": 30, "dinner": true, "location": "station"}`  
**Superseded:** `[{"slot": "location", "value": "mall", "turn": 1}]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R06 Trattoria Lucca ($22)  
**Safe without asking:** R06 Trattoria Lucca ($22)  
**Relations:** t5 confirm t4 (location); t5 revise t1 (location)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-SUG-07A  (suggestion_acceptance, family BB-SUG-07, variant A)

*Contrast:* A: suggestion not accepted -> location=station: R06 Trattoria Lucca ($22). Treating the suggestion as accepted picks R07 Nonna's Kitchen ($27), R09 Osteria Verde ($34), which is WRONG. B (control): explicit acceptance -> R07 Nonna's Kitchen ($27), R09 Osteria Verde ($34) correct.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm looking for Italian food near the station. | user states location=station, cuisine=Italian |
| 2 | assistant | Sounds good! Any budget? | assistant asks budget |
| 3 | user | No more than $35 per person. It's for dinner. | user states max_price=35, dinner=true |
| 4 | assistant | The mall area also has Italian food in that range. Want me to look there instead? | assistant PROPOSES location=mall |
| 5 | user | Possibly, we'll see. | user does NOT accept (hedges); location stays station |
| 6 | assistant | Okay! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Italian", "max_price": 35, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": "Italian", "max_price": 35, "dinner": true, "location": "station"}`  
**Proposed, not accepted:** `[{"slot": "location", "value": "mall", "turn": 4, "status": "not accepted"}]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R06 Trattoria Lucca ($22)  
**Safe without asking:** R06 Trattoria Lucca ($22)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-SUG-07B  (suggestion_acceptance, family BB-SUG-07, variant B)

*Contrast:* A: suggestion not accepted -> location=station: R06 Trattoria Lucca ($22). Treating the suggestion as accepted picks R07 Nonna's Kitchen ($27), R09 Osteria Verde ($34), which is WRONG. B (control): explicit acceptance -> R07 Nonna's Kitchen ($27), R09 Osteria Verde ($34) correct.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm looking for Italian food near the station. | user states location=station, cuisine=Italian |
| 2 | assistant | Sounds good! Any budget? | assistant asks budget |
| 3 | user | No more than $35 per person. It's for dinner. | user states max_price=35, dinner=true |
| 4 | assistant | The mall area also has Italian food in that range. Want me to look there instead? | assistant PROPOSES location=mall |
| 5 | user | Yes, let's look near the mall instead. | user ACCEPTS proposal; location=mall |
| 6 | assistant | Okay! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Italian", "max_price": 35, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": "Italian", "max_price": 35, "dinner": true, "location": "mall"}`  
**Superseded:** `[{"slot": "location", "value": "station", "turn": 1}]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R07 Nonna's Kitchen ($27), R09 Osteria Verde ($34)  
**Safe without asking:** R07 Nonna's Kitchen ($27), R09 Osteria Verde ($34)  
**Relations:** t5 confirm t4 (location); t5 revise t1 (location)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-SUG-08A  (suggestion_acceptance, family BB-SUG-08, variant A)

*Contrast:* A: suggestion not accepted -> location=mall: R02 Hoshi Sushi Bar ($24). Treating the suggestion as accepted picks R01 Sakura Ramen ($18), which is WRONG. B (control): explicit acceptance -> R01 Sakura Ramen ($18) correct.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm looking for Japanese food near the mall. | user states location=mall, cuisine=Japanese |
| 2 | assistant | Sounds good! Any budget? | assistant asks budget |
| 3 | user | No more than $25 per person. It's for dinner. | user states max_price=25, dinner=true |
| 4 | assistant | The station area also has Japanese food in that range. Want me to look there instead? | assistant PROPOSES location=station |
| 5 | user | Oh, by the way, this is for my dad's birthday. | user does NOT accept (changes the subject); location stays mall |
| 6 | assistant | Okay! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Japanese", "max_price": 25, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": "Japanese", "max_price": 25, "dinner": true, "location": "mall"}`  
**Proposed, not accepted:** `[{"slot": "location", "value": "station", "turn": 4, "status": "not accepted"}]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R02 Hoshi Sushi Bar ($24)  
**Safe without asking:** R02 Hoshi Sushi Bar ($24)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-SUG-08B  (suggestion_acceptance, family BB-SUG-08, variant B)

*Contrast:* A: suggestion not accepted -> location=mall: R02 Hoshi Sushi Bar ($24). Treating the suggestion as accepted picks R01 Sakura Ramen ($18), which is WRONG. B (control): explicit acceptance -> R01 Sakura Ramen ($18) correct.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm looking for Japanese food near the mall. | user states location=mall, cuisine=Japanese |
| 2 | assistant | Sounds good! Any budget? | assistant asks budget |
| 3 | user | No more than $25 per person. It's for dinner. | user states max_price=25, dinner=true |
| 4 | assistant | The station area also has Japanese food in that range. Want me to look there instead? | assistant PROPOSES location=station |
| 5 | user | Yes, let's look near the station instead. | user ACCEPTS proposal; location=station |
| 6 | assistant | Okay! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Japanese", "max_price": 25, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": "Japanese", "max_price": 25, "dinner": true, "location": "station"}`  
**Superseded:** `[{"slot": "location", "value": "mall", "turn": 1}]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R01 Sakura Ramen ($18)  
**Safe without asking:** R01 Sakura Ramen ($18)  
**Relations:** t5 confirm t4 (location); t5 revise t1 (location)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

# 4f: Long conversations

---

## BB-LONG-01  (clear, family BB-LONG-01, variant single)

*Contrast:* Correct: R31 Golden Dragon ($24). Forgetting the turn-2 detail (veg+dinner) would also allow R32 Dumpling King ($13), which is wrong.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | assistant | Hi! What can I help you with today? | assistant greets |
| 2 | user | I need a place that's open for dinner and has vegetarian options. | KEY DETAIL in first user message: veg+dinner |
| 3 | assistant | Sure. Is this for a special occasion? | assistant asks occasion |
| 4 | user | Yes, it's my sister's birthday. She just got a new job too. | user: off-topic detail (no constraint) |
| 5 | assistant | Congratulations to her! What food does she like? | assistant asks cuisine |
| 6 | user | She loves Chinese food. | user states cuisine=Chinese |
| 7 | assistant | Great choice. Any area in mind? | assistant asks area |
| 8 | user | Near the station, and let's keep it under $25 a person. | user states location=station, max_price=25 |
| 9 | assistant | Okay: Chinese, near the station, under $25. | assistant summary that LEAVES OUT the turn-2 detail (not a revision) |
| 10 | user | Perfect. What would you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Chinese", "max_price": 25, "location": "station", "vegetarian": true, "dinner": true}`  
**Gold active state:** `{"cuisine": "Chinese", "max_price": 25, "location": "station", "vegetarian": true, "dinner": true}`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R31 Golden Dragon ($24)  
**Safe without asking:** R31 Golden Dragon ($24)  
**Wrong if the early detail is forgotten:** R32 Dumpling King ($13)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LONG-02  (clear, family BB-LONG-02, variant single)

*Contrast:* Correct: R23 Saffron Leaf ($25). Forgetting the turn-2 detail (veg) would also allow R22 Tandoor Grill ($28), which is wrong.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | assistant | Hi! What can I help you with today? | assistant greets |
| 2 | user | I need somewhere with vegetarian options, my partner doesn't eat meat. | KEY DETAIL in first user message: veg |
| 3 | assistant | Sure. Is this for a special occasion? | assistant asks occasion |
| 4 | user | Yes, it's my sister's birthday. She just got a new job too. | user: off-topic detail (no constraint) |
| 5 | assistant | Congratulations to her! What food does she like? | assistant asks cuisine |
| 6 | user | She loves Indian food. | user states cuisine=Indian |
| 7 | assistant | Great choice. Any area in mind? | assistant asks area |
| 8 | user | Near the mall, and let's keep it under $30 a person. | user states location=mall, max_price=30 |
| 9 | assistant | Okay: Indian, near the mall, under $30. | assistant summary that LEAVES OUT the turn-2 detail (not a revision) |
| 10 | user | Perfect. What would you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Indian", "max_price": 30, "location": "mall", "vegetarian": true}`  
**Gold active state:** `{"cuisine": "Indian", "max_price": 30, "location": "mall", "vegetarian": true}`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R23 Saffron Leaf ($25)  
**Safe without asking:** R23 Saffron Leaf ($25)  
**Wrong if the early detail is forgotten:** R22 Tandoor Grill ($28)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LONG-03  (clear, family BB-LONG-03, variant single)

*Contrast:* Correct: R06 Trattoria Lucca ($22). Forgetting the turn-2 detail (dinner) would also allow R08 Forno Pizza ($16), which is wrong.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | assistant | Hi! What can I help you with today? | assistant greets |
| 2 | user | I need a place that's open for dinner. | KEY DETAIL in first user message: dinner |
| 3 | assistant | Sure. Is this for a special occasion? | assistant asks occasion |
| 4 | user | Yes, it's my sister's birthday. She just got a new job too. | user: off-topic detail (no constraint) |
| 5 | assistant | Congratulations to her! What food does she like? | assistant asks cuisine |
| 6 | user | She loves Italian food. | user states cuisine=Italian |
| 7 | assistant | Great choice. Any area in mind? | assistant asks area |
| 8 | user | Near the station, and let's keep it under $25 a person. | user states location=station, max_price=25 |
| 9 | assistant | Okay: Italian, near the station, under $25. | assistant summary that LEAVES OUT the turn-2 detail (not a revision) |
| 10 | user | Perfect. What would you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Italian", "max_price": 25, "location": "station", "dinner": true}`  
**Gold active state:** `{"cuisine": "Italian", "max_price": 25, "location": "station", "dinner": true}`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R06 Trattoria Lucca ($22)  
**Safe without asking:** R06 Trattoria Lucca ($22)  
**Wrong if the early detail is forgotten:** R08 Forno Pizza ($16)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LONG-04  (clear, family BB-LONG-04, variant single)

*Contrast:* Correct: R01 Sakura Ramen ($18). Forgetting the turn-2 detail (budget) would also allow R03 Kumo Izakaya ($29), R05 Ginza Omakase ($58), which is wrong.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | assistant | Hi! What can I help you with today? | assistant greets |
| 2 | user | I can't spend more than $20 per person. | KEY DETAIL in first user message: budget |
| 3 | assistant | Sure. Is this for a special occasion? | assistant asks occasion |
| 4 | user | Yes, it's my sister's birthday. She just got a new job too. | user: off-topic detail (no constraint) |
| 5 | assistant | Congratulations to her! What food does she like? | assistant asks cuisine |
| 6 | user | She loves Japanese food. | user states cuisine=Japanese |
| 7 | assistant | Great choice. Any area in mind? | assistant asks area |
| 8 | user | Near the station. | user states location=station |
| 9 | assistant | Okay: Japanese, near the station. | assistant summary that LEAVES OUT the turn-2 detail (not a revision) |
| 10 | user | Perfect. What would you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Japanese", "max_price": 20, "location": "station"}`  
**Gold active state:** `{"cuisine": "Japanese", "max_price": 20, "location": "station"}`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R01 Sakura Ramen ($18)  
**Safe without asking:** R01 Sakura Ramen ($18)  
**Wrong if the early detail is forgotten:** R03 Kumo Izakaya ($29), R05 Ginza Omakase ($58)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LONG-05A  (ambiguous_reference, family BB-LONG-05, variant A)

*Contrast:* Reference reaches back to turn 2. A: station -> R16 Bangkok Street ($17); mall -> R35 Noodle Bar 88 ($16) -> ask. B: budget $25 -> R31 Golden Dragon ($24) valid for both -> recommend.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Chinese or Thai food, either is fine. | user states cuisine=['Chinese', 'Thai'] |
| 2 | assistant | There are options near the station and near the mall. | KEY DETAIL: assistant mentions both areas (station first, mall second) |
| 3 | user | Nice. Unrelated, but I'm also trying to pick a birthday gift for my mom. | user: off-topic |
| 4 | assistant | Flowers or a good book are always safe choices! | assistant: off-topic reply |
| 5 | user | Good idea. Anyway, my budget is $20 per person. | user states max_price=20 |
| 6 | assistant | Got it. | assistant acknowledges |
| 7 | user | It's for dinner. | user states meal=dinner |
| 8 | assistant | Okay, noted. | assistant acknowledges |
| 9 | user | Can you find me something in that area you mentioned at the start? | user: 'that area you mentioned at the start' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Chinese", "Thai"], "max_price": 20, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Thai"], "max_price": 20, "dinner": true}`  
**Unresolved:** 'that area you mentioned at the start' (turn 9, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R35 Noodle Bar 88 ($16)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t9  
**Questions needed:** 1  
**Successful recommendations:** R16 Bangkok Street ($17)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LONG-05B  (ambiguous_reference, family BB-LONG-05, variant B)

*Contrast:* Reference reaches back to turn 2. A: station -> R16 Bangkok Street ($17); mall -> R35 Noodle Bar 88 ($16) -> ask. B: budget $25 -> R31 Golden Dragon ($24) valid for both -> recommend.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Chinese or Thai food, either is fine. | user states cuisine=['Chinese', 'Thai'] |
| 2 | assistant | There are options near the station and near the mall. | KEY DETAIL: assistant mentions both areas (station first, mall second) |
| 3 | user | Nice. Unrelated, but I'm also trying to pick a birthday gift for my mom. | user: off-topic |
| 4 | assistant | Flowers or a good book are always safe choices! | assistant: off-topic reply |
| 5 | user | Good idea. Anyway, my budget is $25 per person. | user states max_price=25 |
| 6 | assistant | Got it. | assistant acknowledges |
| 7 | user | It's for dinner. | user states meal=dinner |
| 8 | assistant | Okay, noted. | assistant acknowledges |
| 9 | user | Can you find me something in that area you mentioned at the start? | user: 'that area you mentioned at the start' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": ["Chinese", "Thai"], "max_price": 25, "dinner": true, "location": "station"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Thai"], "max_price": 25, "dinner": true}`  
**Unresolved:** 'that area you mentioned at the start' (turn 9, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17), R31 Golden Dragon ($24)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R31 Golden Dragon ($24), R35 Noodle Bar 88 ($16)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R16 Bangkok Street ($17), R31 Golden Dragon ($24)  
**Safe without asking:** R31 Golden Dragon ($24)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LONG-06A  (ambiguous_reference, family BB-LONG-06, variant A)

*Contrast:* Reference reaches back to turn 2. A: station -> R21 Masala House ($20); mall -> R35 Noodle Bar 88 ($16) -> ask. B: budget $25 -> R23 Saffron Leaf ($25), R31 Golden Dragon ($24) valid for both -> recommend.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Chinese or Indian food, either is fine. | user states cuisine=['Chinese', 'Indian'] |
| 2 | assistant | There are options near the station and near the mall. | KEY DETAIL: assistant mentions both areas (station first, mall second) |
| 3 | user | Nice. Unrelated, but I'm also trying to pick a birthday gift for my mom. | user: off-topic |
| 4 | assistant | Flowers or a good book are always safe choices! | assistant: off-topic reply |
| 5 | user | Good idea. Anyway, my budget is $20 per person. | user states max_price=20 |
| 6 | assistant | Got it. | assistant acknowledges |
| 7 | user | It's for dinner. | user states meal=dinner |
| 8 | assistant | Okay, noted. | assistant acknowledges |
| 9 | user | Can you find me something in that area you mentioned at the start? | user: 'that area you mentioned at the start' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Chinese", "Indian"], "max_price": 20, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Indian"], "max_price": 20, "dinner": true}`  
**Unresolved:** 'that area you mentioned at the start' (turn 9, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R21 Masala House ($20)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R35 Noodle Bar 88 ($16)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t9  
**Questions needed:** 1  
**Successful recommendations:** R35 Noodle Bar 88 ($16)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-LONG-06B  (ambiguous_reference, family BB-LONG-06, variant B)

*Contrast:* Reference reaches back to turn 2. A: station -> R21 Masala House ($20); mall -> R35 Noodle Bar 88 ($16) -> ask. B: budget $25 -> R23 Saffron Leaf ($25), R31 Golden Dragon ($24) valid for both -> recommend.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm up for Chinese or Indian food, either is fine. | user states cuisine=['Chinese', 'Indian'] |
| 2 | assistant | There are options near the station and near the mall. | KEY DETAIL: assistant mentions both areas (station first, mall second) |
| 3 | user | Nice. Unrelated, but I'm also trying to pick a birthday gift for my mom. | user: off-topic |
| 4 | assistant | Flowers or a good book are always safe choices! | assistant: off-topic reply |
| 5 | user | Good idea. Anyway, my budget is $25 per person. | user states max_price=25 |
| 6 | assistant | Got it. | assistant acknowledges |
| 7 | user | It's for dinner. | user states meal=dinner |
| 8 | assistant | Okay, noted. | assistant acknowledges |
| 9 | user | Can you find me something in that area you mentioned at the start? | user: 'that area you mentioned at the start' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Chinese", "Indian"], "max_price": 25, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Chinese", "Indian"], "max_price": 25, "dinner": true}`  
**Unresolved:** 'that area you mentioned at the start' (turn 9, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R21 Masala House ($20), R23 Saffron Leaf ($25), R31 Golden Dragon ($24)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R23 Saffron Leaf ($25), R31 Golden Dragon ($24), R35 Noodle Bar 88 ($16)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R23 Saffron Leaf ($25), R31 Golden Dragon ($24), R35 Noodle Bar 88 ($16)  
**Safe without asking:** R23 Saffron Leaf ($25), R31 Golden Dragon ($24)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

# 4g: Fixed versions of guessable originals

---

## BB-FIX-AMB-02A  (ambiguous_reference, family BB-FIX-AMB-02, variant A)

**Fix of:** XX-AMB-02A  
**What was removed:** Removed hint: 'over there' (singular, distal) tends to point at the most recently mentioned area, and the hidden answer (mall) was the last-mentioned area. Turn 7 now says 'near where I'm headed', which is not tied to either mention. Everything else, including the gold labels and restaurants (R28 vs R29, $22 vs $27, comparable), is unchanged.

*Contrast:* Only the cuisine changes. Korean: different restaurants per area -> ask. Japanese: R03 near both -> no need to ask.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Can you help me find a place for dinner tonight? | user states dinner=true |
| 2 | assistant | Sure! I can look near the station or near the mall; both have plenty of options. | assistant mentions two areas |
| 3 | user | I'm craving Korean. | user states cuisine=Korean |
| 4 | assistant | Great. Any budget? | assistant asks budget |
| 5 | user | Up to $30 a person. | user states max_price=30 |
| 6 | assistant | Okay, $30 max per person, open for dinner. | assistant summarises |
| 7 | user | Great, find me something near where I'm headed. | user: 'near where I'm headed' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": "Korean", "max_price": 30, "location": "mall", "dinner": true}`  
**Gold active state:** `{"cuisine": "Korean", "max_price": 30, "dinner": true}`  
**Unresolved:** 'near where I'm headed' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R28 Kimchi Pot ($22)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R29 Hanok Table ($27)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R29 Hanok Table ($27)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-FIX-AMB-02B  (ambiguous_reference, family BB-FIX-AMB-02, variant B)

**Fix of:** XX-AMB-02B  
**What was removed:** Removed hint: 'over there' (singular, distal) tends to point at the most recently mentioned area, and the hidden answer (mall) was the last-mentioned area. Turn 7 now says 'near where I'm headed', which is not tied to either mention. Everything else, including the gold labels and restaurants (R28 vs R29, $22 vs $27, comparable), is unchanged.

*Contrast:* Only the cuisine changes. Korean: different restaurants per area -> ask. Japanese: R03 near both -> no need to ask.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Can you help me find a place for dinner tonight? | user states dinner=true |
| 2 | assistant | Sure! I can look near the station or near the mall; both have plenty of options. | assistant mentions two areas |
| 3 | user | I'm craving Japanese. | user states cuisine=Japanese |
| 4 | assistant | Great. Any budget? | assistant asks budget |
| 5 | user | Up to $30 a person. | user states max_price=30 |
| 6 | assistant | Okay, $30 max per person, open for dinner. | assistant summarises |
| 7 | user | Great, find me something near where I'm headed. | user: 'near where I'm headed' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": "Japanese", "max_price": 30, "location": "mall", "dinner": true}`  
**Gold active state:** `{"cuisine": "Japanese", "max_price": 30, "dinner": true}`  
**Unresolved:** 'near where I'm headed' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R01 Sakura Ramen ($18), R03 Kumo Izakaya ($29)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R02 Hoshi Sushi Bar ($24), R03 Kumo Izakaya ($29)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R02 Hoshi Sushi Bar ($24), R03 Kumo Izakaya ($29)  
**Safe without asking:** R03 Kumo Izakaya ($29)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-FIX-AMB-03A  (ambiguous_reference, family BB-FIX-AMB-03, variant A)

**Fix of:** XX-AMB-03A  
**What was removed:** Removed hints: (1) the hidden cuisine (Mexican) was mentioned last; now it is mentioned first, which balances the original. (2) El Comal (R13) was cheaper, near both areas and open for dinner, so it beat Lotus Thai (R17) on every count. With this database Mexican always has a clearly better option against Thai near the mall, so: constraints are now location=None, max_price=17, vegetarian=True, meal=dinner. Candidates are now Mexican -> R11 Taco Loco ($12), Thai -> R16 Bangkok Street ($17), with neither clearly better. 'The cuisine they mentioned' became "Maya's recommendation" because both cuisines were mentioned by 'they'. Hidden answer stays Mexican.

*Contrast:* A: Mexican -> R11 Taco Loco ($12); Thai -> R16 Bangkok Street ($17); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Mexican, one Thai. | user mentions two cuisines (Mexican first, Thai second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | The area doesn't matter to me. | user: no location constraint |
| 4 | assistant | Okay, anywhere works. | assistant acknowledges |
| 5 | user | No more than $17 a person. It's for dinner. I also need vegetarian options. | user states max_price=17, meal=dinner, vegetarian=true |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Let's go with Maya's recommendation. | user: 'Maya's recommendation' = Mexican or Thai (UNRESOLVED; hidden: Mexican) |

**Hidden goal:** `{"max_price": 17, "vegetarian": true, "dinner": true, "cuisine": "Mexican"}`  
**Gold active state:** `{"max_price": 17, "vegetarian": true, "dinner": true}`  
**Unresolved:** 'Maya's recommendation' (turn 7, slot cuisine)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"cuisine": "Mexican"}` -> R11 Taco Loco ($12)  
&nbsp;&nbsp;- `{"cuisine": "Thai"}` -> R16 Bangkok Street ($17)  
**Mention order in the chat:** `["Mexican", "Thai"]`  
**Should ask:** YES - cuisine@t7  
**Questions needed:** 1  
**Successful recommendations:** R11 Taco Loco ($12)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-FIX-AMB-03B  (ambiguous_reference, family BB-FIX-AMB-03, variant B)

**Fix of:** XX-AMB-03B  
**What was removed:** Removed hints: (1) the hidden cuisine (Mexican) was mentioned last; now it is mentioned first, which balances the original. (2) El Comal (R13) was cheaper, near both areas and open for dinner, so it beat Lotus Thai (R17) on every count. With this database Mexican always has a clearly better option against Thai near the mall, so: constraints are now location=None, max_price=17, vegetarian=True, meal=dinner. Candidates are now Mexican -> R11 Taco Loco ($12), Thai -> R16 Bangkok Street ($17), with neither clearly better. 'The cuisine they mentioned' became "Maya's recommendation" because both cuisines were mentioned by 'they'. Hidden answer stays Mexican.

*Contrast:* A: Mexican -> R11 Taco Loco ($12); Thai -> R16 Bangkok Street ($17); no restaurant serves both -> ask. B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two cuisines, so this is the only one-change way to remove the need to ask).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Two of my friends each recommended a place around here: one Mexican, one Thai. | user mentions two cuisines (Mexican first, Thai second); neither chosen; no link to who said which |
| 2 | assistant | Both sound like good options! Want me to look into them? | assistant offers |
| 3 | user | The area doesn't matter to me. | user: no location constraint |
| 4 | assistant | Okay, anywhere works. | assistant acknowledges |
| 5 | user | No more than $17 a person. It's for dinner. I also need vegetarian options. | user states max_price=17, meal=dinner, vegetarian=true |
| 6 | assistant | Noted. | assistant acknowledges |
| 7 | user | Either of those cuisines is fine with me. | user: cuisine in {Mexican, Thai}; disjunction, not ambiguity |

**Hidden goal:** `{"max_price": 17, "vegetarian": true, "dinner": true, "cuisine": ["Mexican", "Thai"]}`  
**Gold active state:** `{"max_price": 17, "vegetarian": true, "dinner": true, "cuisine": ["Mexican", "Thai"]}`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R11 Taco Loco ($12), R16 Bangkok Street ($17)  
**Safe without asking:** R11 Taco Loco ($12), R16 Bangkok Street ($17)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-FIX-AMB-04A  (ambiguous_reference, family BB-FIX-AMB-04, variant A)

**Fix of:** XX-AMB-04A  
**What was removed:** Removed hints: (1) 'I work by the station but I live by the mall' + 'dinner tonight' lets a model infer 'at home in the evening' = mall; now the user just says they'll be around both areas. (2) Pita Port (R37, $14) was $9-19 cheaper than every station option with the same features. Mediterranean alone always has that gap here, so the cuisine/budget changed to ['Mediterranean', 'Thai'], $20, vegetarian=False: station -> R16 Bangkok Street ($17), mall -> R37 Pita Port ($14). Hidden answer stays mall; the A/B change stays dinner vs lunch.

*Contrast:* A: station -> R16 Bangkok Street ($17); mall -> R37 Pita Port ($14); nothing near both -> ask. B: lunch instead of dinner makes R39 Falafel Stop ($11) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'll be around both the train station and the mall today. I'm up for Mediterranean or Thai food, either is fine. | user states cuisine=['Mediterranean', 'Thai']; user says they will be near BOTH areas (no work/home cue) |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $20 per person. | user states max_price=20 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for dinner. | user states meal=dinner (dinner=true) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Find me something close to where I'll be. | user: 'close to where I'll be' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Mediterranean", "Thai"], "max_price": 20, "dinner": true, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Mediterranean", "Thai"], "max_price": 20, "dinner": true}`  
**Unresolved:** 'Find me something close to where I'll be.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R37 Pita Port ($14)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** YES - location@t7  
**Questions needed:** 1  
**Successful recommendations:** R37 Pita Port ($14)  
**Safe without asking:** (none)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

---

## BB-FIX-AMB-04B  (ambiguous_reference, family BB-FIX-AMB-04, variant B)

**Fix of:** XX-AMB-04B  
**What was removed:** Removed hints: (1) 'I work by the station but I live by the mall' + 'dinner tonight' lets a model infer 'at home in the evening' = mall; now the user just says they'll be around both areas. (2) Pita Port (R37, $14) was $9-19 cheaper than every station option with the same features. Mediterranean alone always has that gap here, so the cuisine/budget changed to ['Mediterranean', 'Thai'], $20, vegetarian=False: station -> R16 Bangkok Street ($17), mall -> R37 Pita Port ($14). Hidden answer stays mall; the A/B change stays dinner vs lunch.

*Contrast:* A: station -> R16 Bangkok Street ($17); mall -> R37 Pita Port ($14); nothing near both -> ask. B: lunch instead of dinner makes R39 Falafel Stop ($11) valid for both -> recommend it.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'll be around both the train station and the mall today. I'm up for Mediterranean or Thai food, either is fine. | user states cuisine=['Mediterranean', 'Thai']; user says they will be near BOTH areas (no work/home cue) |
| 2 | assistant | Sure! There are good options near the station and near the mall. | assistant mentions both areas (station first, mall second); not a user choice |
| 3 | user | My budget is $20 per person. | user states max_price=20 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | It's for lunch. | user states meal=lunch (no dinner constraint) |
| 6 | assistant | Okay, noted. | assistant acknowledges |
| 7 | user | Find me something close to where I'll be. | user: 'close to where I'll be' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": ["Mediterranean", "Thai"], "max_price": 20, "location": "mall"}`  
**Gold active state:** `{"cuisine": ["Mediterranean", "Thai"], "max_price": 20}`  
**Unresolved:** 'Find me something close to where I'll be.' (turn 7, slot location)  
**Candidates per meaning:**  
&nbsp;&nbsp;- `{"location": "station"}` -> R16 Bangkok Street ($17), R39 Falafel Stop ($11)  
&nbsp;&nbsp;- `{"location": "mall"}` -> R37 Pita Port ($14), R39 Falafel Stop ($11)  
**Mention order in the chat:** `["station", "mall"]`  
**Should ask:** no  
**Questions needed:** 0  
**Successful recommendations:** R37 Pita Port ($14), R39 Falafel Stop ($11)  
**Safe without asking:** R39 Falafel Stop ($11)  

- [ ] Answer key correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  - [ ] Natural wording

