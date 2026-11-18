# Scenario review sheet

Tick each box after reading the dialogue against its plan.


---

## XX-AMB-01A  (ambiguous_reference, variant A)

*Contrast:* Same 'near there'. At $25 no Japanese place is near both -> ask. At $30 Kumo Izakaya (R03) is near both -> recommend it without asking.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm in the mood for Japanese food. | user states cuisine=Japanese |
| 2 | assistant | Nice! There are Japanese places near the station and near the mall. | assistant mentions two areas (not accepted by user) |
| 3 | user | Good to know. My budget is $25 per person. | user states max_price=25 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | Oh, and it's for lunch, not dinner. | user: lunch -> no dinner constraint |
| 6 | assistant | Okay, lunch it is. | assistant acknowledges |
| 7 | user | Can you find me something near there? | user: 'there' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": "Japanese", "max_price": 25, "location": "station"}`  
**Gold active state:** `{"cuisine": "Japanese", "max_price": 25}`  
**Unresolved:** 'near there' (turn 7)  
&nbsp;&nbsp;- {"location": "station"} -> R01 Sakura Ramen  
&nbsp;&nbsp;- {"location": "mall"} -> R02 Hoshi Sushi Bar  
**Should ask:** YES - location@t7  
**Successful recommendations:** R01 Sakura Ramen  
**Safe without asking:** (none)  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-AMB-01B  (ambiguous_reference, variant B)

*Contrast:* Same 'near there'. At $25 no Japanese place is near both -> ask. At $30 Kumo Izakaya (R03) is near both -> recommend it without asking.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm in the mood for Japanese food. | user states cuisine=Japanese |
| 2 | assistant | Nice! There are Japanese places near the station and near the mall. | assistant mentions two areas (not accepted by user) |
| 3 | user | Good to know. My budget is $30 per person. | user states max_price=30 |
| 4 | assistant | Got it, I'll keep the budget in mind. | assistant acknowledges |
| 5 | user | Oh, and it's for lunch, not dinner. | user: lunch -> no dinner constraint |
| 6 | assistant | Okay, lunch it is. | assistant acknowledges |
| 7 | user | Can you find me something near there? | user: 'there' = station or mall (UNRESOLVED; hidden: station) |

**Hidden goal:** `{"cuisine": "Japanese", "max_price": 30, "location": "station"}`  
**Gold active state:** `{"cuisine": "Japanese", "max_price": 30}`  
**Unresolved:** 'near there' (turn 7)  
&nbsp;&nbsp;- {"location": "station"} -> R01 Sakura Ramen, R03 Kumo Izakaya  
&nbsp;&nbsp;- {"location": "mall"} -> R02 Hoshi Sushi Bar, R03 Kumo Izakaya  
**Should ask:** no  
**Successful recommendations:** R01 Sakura Ramen, R03 Kumo Izakaya  
**Safe without asking:** R03 Kumo Izakaya  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-AMB-02A  (ambiguous_reference, variant A)

*Contrast:* Only the cuisine changes. Korean: different restaurants per area -> ask. Japanese: R03 near both -> no need to ask.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Can you help me find a place for dinner tonight? | user states dinner=true |
| 2 | assistant | Sure! I can look near the station or near the mall; both have plenty of options. | assistant mentions two areas |
| 3 | user | I'm craving Korean. | user states cuisine=Korean |
| 4 | assistant | Great. Any budget? | assistant asks budget |
| 5 | user | Up to $30 a person. | user states max_price=30 |
| 6 | assistant | Okay, $30 max per person, open for dinner. | assistant summarises |
| 7 | user | Great, find me something over there. | user: 'over there' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": "Korean", "max_price": 30, "location": "mall", "dinner": true}`  
**Gold active state:** `{"cuisine": "Korean", "max_price": 30, "dinner": true}`  
**Unresolved:** 'over there' (turn 7)  
&nbsp;&nbsp;- {"location": "station"} -> R28 Kimchi Pot  
&nbsp;&nbsp;- {"location": "mall"} -> R29 Hanok Table  
**Should ask:** YES - location@t7  
**Successful recommendations:** R29 Hanok Table  
**Safe without asking:** (none)  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-AMB-02B  (ambiguous_reference, variant B)

*Contrast:* Only the cuisine changes. Korean: different restaurants per area -> ask. Japanese: R03 near both -> no need to ask.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Can you help me find a place for dinner tonight? | user states dinner=true |
| 2 | assistant | Sure! I can look near the station or near the mall; both have plenty of options. | assistant mentions two areas |
| 3 | user | I'm craving Japanese. | user states cuisine=Japanese |
| 4 | assistant | Great. Any budget? | assistant asks budget |
| 5 | user | Up to $30 a person. | user states max_price=30 |
| 6 | assistant | Okay, $30 max per person, open for dinner. | assistant summarises |
| 7 | user | Great, find me something over there. | user: 'over there' = station or mall (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": "Japanese", "max_price": 30, "location": "mall", "dinner": true}`  
**Gold active state:** `{"cuisine": "Japanese", "max_price": 30, "dinner": true}`  
**Unresolved:** 'over there' (turn 7)  
&nbsp;&nbsp;- {"location": "station"} -> R01 Sakura Ramen, R03 Kumo Izakaya  
&nbsp;&nbsp;- {"location": "mall"} -> R02 Hoshi Sushi Bar, R03 Kumo Izakaya  
**Should ask:** no  
**Successful recommendations:** R02 Hoshi Sushi Bar, R03 Kumo Izakaya  
**Safe without asking:** R03 Kumo Izakaya  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-AMB-03A  (ambiguous_reference, variant A)

*Contrast:* A: a singular reference to one of two cuisines (no restaurant serves both) -> ask. B: user accepts either -> no question needed.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | My coworkers keep recommending a Thai place and a Mexican place around here. | user mentions two cuisines (neither chosen yet) |
| 2 | assistant | Both are popular cuisines nearby! Would you like me to look into one of them? | assistant offers |
| 3 | user | I want somewhere near the mall with vegetarian options. | user states location=mall, vegetarian=true |
| 4 | assistant | Got it: near the mall, with vegetarian options. | assistant summarises |
| 5 | user | And no more than $30 a person. | user states max_price=30 |
| 6 | assistant | Noted, $30 max. | assistant acknowledges |
| 7 | user | Let's do the cuisine they mentioned. | user: singular 'the cuisine' = Thai or Mexican (UNRESOLVED; hidden: Mexican) |

**Hidden goal:** `{"cuisine": "Mexican", "max_price": 30, "location": "mall", "vegetarian": true}`  
**Gold active state:** `{"max_price": 30, "location": "mall", "vegetarian": true}`  
**Unresolved:** 'the cuisine they mentioned' (turn 7)  
&nbsp;&nbsp;- {"cuisine": "Thai"} -> R17 Lotus Thai  
&nbsp;&nbsp;- {"cuisine": "Mexican"} -> R13 El Comal  
**Should ask:** YES - cuisine@t7  
**Successful recommendations:** R13 El Comal  
**Safe without asking:** (none)  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-AMB-03B  (ambiguous_reference, variant B)

*Contrast:* A: a singular reference to one of two cuisines (no restaurant serves both) -> ask. B: user accepts either -> no question needed.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | My coworkers keep recommending a Thai place and a Mexican place around here. | user mentions two cuisines (neither chosen yet) |
| 2 | assistant | Both are popular cuisines nearby! Would you like me to look into one of them? | assistant offers |
| 3 | user | I want somewhere near the mall with vegetarian options. | user states location=mall, vegetarian=true |
| 4 | assistant | Got it: near the mall, with vegetarian options. | assistant summarises |
| 5 | user | And no more than $30 a person. | user states max_price=30 |
| 6 | assistant | Noted, $30 max. | assistant acknowledges |
| 7 | user | Either of those cuisines is fine with me. | user: cuisine in {Thai, Mexican}; disjunction, not ambiguity |

**Hidden goal:** `{"cuisine": ["Thai", "Mexican"], "max_price": 30, "location": "mall", "vegetarian": true}`  
**Gold active state:** `{"cuisine": ["Thai", "Mexican"], "max_price": 30, "location": "mall", "vegetarian": true}`  
**Should ask:** no  
**Successful recommendations:** R13 El Comal, R17 Lotus Thai  
**Safe without asking:** R13 El Comal, R17 Lotus Thai  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-AMB-04A  (ambiguous_reference, variant A)

*Contrast:* Dinner vs lunch. At dinner nothing is near both areas -> ask. At lunch Falafel Stop (R39) is near both -> recommend directly.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I work by the train station but I live by the mall. | user mentions two areas |
| 2 | assistant | Handy! How can I help? | assistant asks |
| 3 | user | I want Mediterranean food with vegetarian options. | user states cuisine=Mediterranean, vegetarian=true |
| 4 | assistant | Sounds good. What's your budget? | assistant asks budget |
| 5 | user | Up to $35. It's for dinner tonight. | user states max_price=35, dinner=true |
| 6 | assistant | Okay. | assistant acknowledges |
| 7 | user | Find something close to where I'll be. | user: work (station) or home (mall)? (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": "Mediterranean", "max_price": 35, "location": "mall", "vegetarian": true, "dinner": true}`  
**Gold active state:** `{"cuisine": "Mediterranean", "max_price": 35, "vegetarian": true, "dinner": true}`  
**Unresolved:** 'close to where I'll be' (turn 7)  
&nbsp;&nbsp;- {"location": "station"} -> R36 Olive & Thyme, R38 Aegean Table  
&nbsp;&nbsp;- {"location": "mall"} -> R37 Pita Port  
**Should ask:** YES - location@t7  
**Successful recommendations:** R37 Pita Port  
**Safe without asking:** (none)  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-AMB-04B  (ambiguous_reference, variant B)

*Contrast:* Dinner vs lunch. At dinner nothing is near both areas -> ask. At lunch Falafel Stop (R39) is near both -> recommend directly.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I work by the train station but I live by the mall. | user mentions two areas |
| 2 | assistant | Handy! How can I help? | assistant asks |
| 3 | user | I want Mediterranean food with vegetarian options. | user states cuisine=Mediterranean, vegetarian=true |
| 4 | assistant | Sounds good. What's your budget? | assistant asks budget |
| 5 | user | Up to $35. It's for lunch tomorrow. | user states max_price=35; lunch -> no dinner constraint |
| 6 | assistant | Okay. | assistant acknowledges |
| 7 | user | Find something close to where I'll be. | user: work (station) or home (mall)? (UNRESOLVED; hidden: mall) |

**Hidden goal:** `{"cuisine": "Mediterranean", "max_price": 35, "location": "mall", "vegetarian": true}`  
**Gold active state:** `{"cuisine": "Mediterranean", "max_price": 35, "vegetarian": true}`  
**Unresolved:** 'close to where I'll be' (turn 7)  
&nbsp;&nbsp;- {"location": "station"} -> R36 Olive & Thyme, R38 Aegean Table, R39 Falafel Stop  
&nbsp;&nbsp;- {"location": "mall"} -> R37 Pita Port, R39 Falafel Stop  
**Should ask:** no  
**Successful recommendations:** R37 Pita Port, R39 Falafel Stop  
**Safe without asking:** R39 Falafel Stop  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-AMB-05  (ambiguous_reference, variant single)

*Contrast:* Price ambiguity where a $20 option (El Comal, R13) satisfies both readings -> no question needed.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm getting dinner with my friend near the mall tonight. | user states location=mall, dinner=true |
| 2 | assistant | Fun! What kind of food? | assistant asks cuisine |
| 3 | user | Mexican. I usually spend about $20 max, but he's fine going up to $30. | user states cuisine=Mexican; mentions two budgets (neither chosen) |
| 4 | assistant | Okay, thanks for the details. | assistant acknowledges |
| 5 | user | And it has to be open for dinner, obviously. | user restates dinner=true |
| 6 | assistant | Of course. | assistant acknowledges |
| 7 | user | Let's just go with that budget. What do you suggest? | user: 'that budget' = $20 or $30 (UNRESOLVED; hidden: $30) |

**Hidden goal:** `{"cuisine": "Mexican", "max_price": 30, "location": "mall", "dinner": true}`  
**Gold active state:** `{"cuisine": "Mexican", "location": "mall", "dinner": true}`  
**Unresolved:** 'that budget' (turn 7)  
&nbsp;&nbsp;- {"max_price": 20} -> R13 El Comal  
&nbsp;&nbsp;- {"max_price": 30} -> R12 Casa Azul, R13 El Comal  
**Should ask:** no  
**Successful recommendations:** R12 Casa Azul, R13 El Comal  
**Safe without asking:** R13 El Comal  

> FLAG: Recency could make 'that budget' read as $30 (last mentioned). Team should agree whether this counts as genuinely ambiguous. The gold decision (don't ask, recommend R13) holds either way.

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-CLR-01A  (clear, variant A)

*Contrast:* B adds a pseudo-ambiguous 'near there' with only one possible referent. Gold is identical; tests whether the system asks just because it sees 'there' (H3).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Hi, can you help me pick a place to eat tonight? | user opens request; 'tonight' = dinner |
| 2 | assistant | Of course! What kind of food are you in the mood for? | assistant asks cuisine |
| 3 | user | Thai, please. I'll be near the train station. | user states cuisine=Thai, location=station |
| 4 | assistant | Got it, Thai near the station. Do you have a budget in mind? | assistant acknowledges, asks budget |
| 5 | user | Nothing over $25 a person, and it has to be open for dinner. | user states max_price=25, dinner=true |
| 6 | user | What would you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Thai", "max_price": 25, "location": "station", "dinner": true}`  
**Gold active state:** `{"cuisine": "Thai", "max_price": 25, "location": "station", "dinner": true}`  
**Should ask:** no  
**Successful recommendations:** R16 Bangkok Street  
**Safe without asking:** R16 Bangkok Street  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-CLR-01B  (clear, variant B)

*Contrast:* B adds a pseudo-ambiguous 'near there' with only one possible referent. Gold is identical; tests whether the system asks just because it sees 'there' (H3).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Hi, can you help me pick a place to eat tonight? | user opens request; 'tonight' = dinner |
| 2 | assistant | Of course! What kind of food are you in the mood for? | assistant asks cuisine |
| 3 | user | Thai, please. I'll be near the train station. | user states cuisine=Thai, location=station |
| 4 | assistant | Got it, Thai near the station. Do you have a budget in mind? | assistant acknowledges, asks budget |
| 5 | user | Nothing over $25 a person, and it has to be open for dinner. | user states max_price=25, dinner=true |
| 6 | user | Anything near there works. What would you recommend? | user requests recommendation; 'there' can only mean the station (only location mentioned) |

**Hidden goal:** `{"cuisine": "Thai", "max_price": 25, "location": "station", "dinner": true}`  
**Gold active state:** `{"cuisine": "Thai", "max_price": 25, "location": "station", "dinner": true}`  
**Should ask:** no  
**Successful recommendations:** R16 Bangkok Street  
**Safe without asking:** R16 Bangkok Street  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-CLR-02A  (clear, variant A)

*Contrast:* Budget 30 vs 35: one valid restaurant vs two. B checks the system just picks one of several valid options instead of asking the user to choose.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm meeting a friend at the mall for dinner. Can you suggest an Italian place? | user states location=mall, dinner=true, cuisine=Italian |
| 2 | assistant | Sure. Any budget or dietary needs I should know about? | assistant asks budget/diet |
| 3 | user | My friend is vegetarian, so we need vegetarian options. | user states vegetarian=true |
| 4 | assistant | Noted: vegetarian-friendly Italian near the mall. | assistant summarises |
| 5 | user | And let's keep it to $30 per person at most. | user states max_price=30 |
| 6 | user | Which one should we go to? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Italian", "max_price": 30, "location": "mall", "vegetarian": true, "dinner": true}`  
**Gold active state:** `{"cuisine": "Italian", "max_price": 30, "location": "mall", "vegetarian": true, "dinner": true}`  
**Should ask:** no  
**Successful recommendations:** R07 Nonna's Kitchen  
**Safe without asking:** R07 Nonna's Kitchen  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-CLR-02B  (clear, variant B)

*Contrast:* Budget 30 vs 35: one valid restaurant vs two. B checks the system just picks one of several valid options instead of asking the user to choose.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm meeting a friend at the mall for dinner. Can you suggest an Italian place? | user states location=mall, dinner=true, cuisine=Italian |
| 2 | assistant | Sure. Any budget or dietary needs I should know about? | assistant asks budget/diet |
| 3 | user | My friend is vegetarian, so we need vegetarian options. | user states vegetarian=true |
| 4 | assistant | Noted: vegetarian-friendly Italian near the mall. | assistant summarises |
| 5 | user | And let's keep it to $35 per person at most. | user states max_price=35 |
| 6 | user | Which one should we go to? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Italian", "max_price": 35, "location": "mall", "vegetarian": true, "dinner": true}`  
**Gold active state:** `{"cuisine": "Italian", "max_price": 35, "location": "mall", "vegetarian": true, "dinner": true}`  
**Should ask:** no  
**Successful recommendations:** R07 Nonna's Kitchen, R09 Osteria Verde  
**Safe without asking:** R07 Nonna's Kitchen, R09 Osteria Verde  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-CLR-03A  (clear, variant A)

*Contrast:* Lunch vs dinner in turn 1. Dumpling King (R32) is valid only for lunch; tests that an early constraint is still applied six turns later.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I want to grab lunch near the station today. | user states location=station; lunch -> no dinner constraint |
| 2 | assistant | Happy to help! Any cuisine in mind? | assistant asks cuisine |
| 3 | user | Chinese sounds good. | user states cuisine=Chinese |
| 4 | assistant | Great. What's your budget per person? | assistant asks budget |
| 5 | user | Up to $25. | user states max_price=25 |
| 6 | assistant | Okay: Chinese near the station, $25 or less. | assistant summarises |
| 7 | user | Perfect, what's your pick? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Chinese", "max_price": 25, "location": "station"}`  
**Gold active state:** `{"cuisine": "Chinese", "max_price": 25, "location": "station"}`  
**Should ask:** no  
**Successful recommendations:** R31 Golden Dragon, R32 Dumpling King  
**Safe without asking:** R31 Golden Dragon, R32 Dumpling King  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-CLR-03B  (clear, variant B)

*Contrast:* Lunch vs dinner in turn 1. Dumpling King (R32) is valid only for lunch; tests that an early constraint is still applied six turns later.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I want to grab dinner near the station tonight. | user states location=station, dinner=true |
| 2 | assistant | Happy to help! Any cuisine in mind? | assistant asks cuisine |
| 3 | user | Chinese sounds good. | user states cuisine=Chinese |
| 4 | assistant | Great. What's your budget per person? | assistant asks budget |
| 5 | user | Up to $25. | user states max_price=25 |
| 6 | assistant | Okay: Chinese near the station, $25 or less. | assistant summarises |
| 7 | user | Perfect, what's your pick? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Chinese", "max_price": 25, "location": "station", "dinner": true}`  
**Gold active state:** `{"cuisine": "Chinese", "max_price": 25, "location": "station", "dinner": true}`  
**Should ask:** no  
**Successful recommendations:** R31 Golden Dragon  
**Safe without asking:** R31 Golden Dragon  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-CLR-04A  (clear, variant A)

*Contrast:* Budget 20 vs 30 changes the valid set; both fully specified, so no question is needed.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm looking for a Korean lunch spot by the mall. | user states cuisine=Korean, location=mall; lunch |
| 2 | assistant | Sounds good! Any dietary restrictions? | assistant asks diet |
| 3 | user | I'm vegetarian. | user states vegetarian=true |
| 4 | assistant | Got it. And your budget? | assistant asks budget |
| 5 | user | $20 max per person. | user states max_price=20 |
| 6 | user | What do you suggest? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Korean", "max_price": 20, "location": "mall", "vegetarian": true}`  
**Gold active state:** `{"cuisine": "Korean", "max_price": 20, "location": "mall", "vegetarian": true}`  
**Should ask:** no  
**Successful recommendations:** R27 Bibim Bowl  
**Safe without asking:** R27 Bibim Bowl  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-CLR-04B  (clear, variant B)

*Contrast:* Budget 20 vs 30 changes the valid set; both fully specified, so no question is needed.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm looking for a Korean lunch spot by the mall. | user states cuisine=Korean, location=mall; lunch |
| 2 | assistant | Sounds good! Any dietary restrictions? | assistant asks diet |
| 3 | user | I'm vegetarian. | user states vegetarian=true |
| 4 | assistant | Got it. And your budget? | assistant asks budget |
| 5 | user | $30 max per person. | user states max_price=30 |
| 6 | user | What do you suggest? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Korean", "max_price": 30, "location": "mall", "vegetarian": true}`  
**Gold active state:** `{"cuisine": "Korean", "max_price": 30, "location": "mall", "vegetarian": true}`  
**Should ask:** no  
**Successful recommendations:** R27 Bibim Bowl, R29 Hanok Table  
**Safe without asking:** R27 Bibim Bowl, R29 Hanok Table  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-CLR-05  (clear, variant single)

*Contrast:* Everything already confirmed by the user; any further question is redundant.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Hey, I need a dinner spot for tonight. | user states dinner=true |
| 2 | assistant | Sure! What cuisine? | assistant asks cuisine |
| 3 | user | Mediterranean. Somewhere near the station. | user states cuisine=Mediterranean, location=station |
| 4 | user | I'm vegetarian, and I'd like to stay under $25. | user states vegetarian=true, max_price=25 |
| 5 | assistant | So: Mediterranean, near the station, vegetarian options, under $25, open for dinner. Is that right? | assistant summarises and checks |
| 6 | user | Yes, exactly. | user confirms the summary |
| 7 | user | What's the best match? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Mediterranean", "max_price": 25, "location": "station", "vegetarian": true, "dinner": true}`  
**Gold active state:** `{"cuisine": "Mediterranean", "max_price": 25, "location": "station", "vegetarian": true, "dinner": true}`  
**Should ask:** no  
**Successful recommendations:** R36 Olive & Thyme  
**Safe without asking:** R36 Olive & Thyme  
**Relations:** t6 confirm t5 (all)  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-REV-01A  (revision, variant A)

*Contrast:* 'Instead' replaces Italian (Trattoria Lucca R06 becomes wrong); 'too' keeps it valid. One word flips whether the old requirement is outdated.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Find me an Italian place for dinner, under $30 a person. | user states cuisine=Italian, dinner=true, max_price=30 |
| 2 | assistant | Sure! Any area preference? | assistant asks location |
| 3 | user | Near the station, please. | user states location=station |
| 4 | assistant | Got it: Italian, near the station, under $30. | assistant summarises |
| 5 | user | Actually, make it Japanese instead. | user REVISES cuisine Italian -> Japanese |
| 6 | assistant | No problem. | assistant acknowledges |
| 7 | user | What's your recommendation? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Japanese", "max_price": 30, "location": "station", "dinner": true}`  
**Gold active state:** `{"cuisine": "Japanese", "max_price": 30, "location": "station", "dinner": true}`  
**Superseded:** `[{"slot": "cuisine", "value": "Italian", "turn": 1}]`  
**Should ask:** no  
**Successful recommendations:** R01 Sakura Ramen, R03 Kumo Izakaya  
**Safe without asking:** R01 Sakura Ramen, R03 Kumo Izakaya  
**Relations:** t5 revise t1 (cuisine)  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-REV-01B  (revision, variant B)

*Contrast:* 'Instead' replaces Italian (Trattoria Lucca R06 becomes wrong); 'too' keeps it valid. One word flips whether the old requirement is outdated.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Find me an Italian place for dinner, under $30 a person. | user states cuisine=Italian, dinner=true, max_price=30 |
| 2 | assistant | Sure! Any area preference? | assistant asks location |
| 3 | user | Near the station, please. | user states location=station |
| 4 | assistant | Got it: Italian, near the station, under $30. | assistant summarises |
| 5 | user | Actually, Japanese would be fine too. | user WIDENS cuisine to {Italian, Japanese}; Italian stays |
| 6 | assistant | No problem. | assistant acknowledges |
| 7 | user | What's your recommendation? | user requests recommendation |

**Hidden goal:** `{"cuisine": ["Italian", "Japanese"], "max_price": 30, "location": "station", "dinner": true}`  
**Gold active state:** `{"cuisine": ["Italian", "Japanese"], "max_price": 30, "location": "station", "dinner": true}`  
**Should ask:** no  
**Successful recommendations:** R01 Sakura Ramen, R03 Kumo Izakaya, R06 Trattoria Lucca  
**Safe without asking:** R01 Sakura Ramen, R03 Kumo Izakaya, R06 Trattoria Lucca  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-REV-02A  (revision, variant A)

*Contrast:* Real revision vs a mentioned-but-rejected number. Siam Garden (R18, $31) is wrong in A, valid in B.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I want Thai food near the mall. | user states cuisine=Thai, location=mall |
| 2 | assistant | Great choice! Any dietary needs? | assistant asks diet |
| 3 | user | Vegetarian options, please. And I can spend up to $35. | user states vegetarian=true, max_price=35 |
| 4 | assistant | Okay: Thai, near the mall, vegetarian-friendly, $35 max. | assistant summarises |
| 5 | user | Actually, let's lower it to $25. | user REVISES max_price 35 -> 25 |
| 6 | assistant | Got it. | assistant acknowledges |
| 7 | user | Which place do you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Thai", "max_price": 25, "location": "mall", "vegetarian": true}`  
**Gold active state:** `{"cuisine": "Thai", "max_price": 25, "location": "mall", "vegetarian": true}`  
**Superseded:** `[{"slot": "max_price", "value": 35, "turn": 3}]`  
**Should ask:** no  
**Successful recommendations:** R17 Lotus Thai  
**Safe without asking:** R17 Lotus Thai  
**Relations:** t5 revise t3 (max_price)  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-REV-02B  (revision, variant B)

*Contrast:* Real revision vs a mentioned-but-rejected number. Siam Garden (R18, $31) is wrong in A, valid in B.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I want Thai food near the mall. | user states cuisine=Thai, location=mall |
| 2 | assistant | Great choice! Any dietary needs? | assistant asks diet |
| 3 | user | Vegetarian options, please. And I can spend up to $35. | user states vegetarian=true, max_price=35 |
| 4 | assistant | Okay: Thai, near the mall, vegetarian-friendly, $35 max. | assistant summarises |
| 5 | user | My friend usually keeps it under $25, but $35 is fine this time. | user mentions $25 but does NOT revise; max_price stays 35 |
| 6 | assistant | Got it. | assistant acknowledges |
| 7 | user | Which place do you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Thai", "max_price": 35, "location": "mall", "vegetarian": true}`  
**Gold active state:** `{"cuisine": "Thai", "max_price": 35, "location": "mall", "vegetarian": true}`  
**Should ask:** no  
**Successful recommendations:** R17 Lotus Thai, R18 Siam Garden  
**Safe without asking:** R17 Lotus Thai, R18 Siam Garden  
**Relations:** t5 confirm t3 (max_price)  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-REV-03A  (revision, variant A)

*Contrast:* Same position, different slot revised. Tests that a revision updates only its own slot and leaves the others intact.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'd like Indian food for dinner tonight. | user states cuisine=Indian, dinner=true |
| 2 | assistant | Lovely. Where will you be? | assistant asks location |
| 3 | user | Near the station. I need vegetarian options too. | user states location=station, vegetarian=true |
| 4 | assistant | Got it. Budget? | assistant asks budget |
| 5 | user | Up to $30. | user states max_price=30 |
| 6 | user | Actually, change that to near the mall. | user REVISES location station -> mall |
| 7 | assistant | Updated! | assistant acknowledges |
| 8 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Indian", "max_price": 30, "location": "mall", "vegetarian": true, "dinner": true}`  
**Gold active state:** `{"cuisine": "Indian", "max_price": 30, "location": "mall", "vegetarian": true, "dinner": true}`  
**Superseded:** `[{"slot": "location", "value": "station", "turn": 3}]`  
**Should ask:** no  
**Successful recommendations:** R23 Saffron Leaf  
**Safe without asking:** R23 Saffron Leaf  
**Relations:** t6 revise t3 (location)  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-REV-03B  (revision, variant B)

*Contrast:* Same position, different slot revised. Tests that a revision updates only its own slot and leaves the others intact.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'd like Indian food for dinner tonight. | user states cuisine=Indian, dinner=true |
| 2 | assistant | Lovely. Where will you be? | assistant asks location |
| 3 | user | Near the station. I need vegetarian options too. | user states location=station, vegetarian=true |
| 4 | assistant | Got it. Budget? | assistant asks budget |
| 5 | user | Up to $30. | user states max_price=30 |
| 6 | user | Actually, let's cap it at $25. | user REVISES max_price 30 -> 25; location stays station |
| 7 | assistant | Updated! | assistant acknowledges |
| 8 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Indian", "max_price": 25, "location": "station", "vegetarian": true, "dinner": true}`  
**Gold active state:** `{"cuisine": "Indian", "max_price": 25, "location": "station", "vegetarian": true, "dinner": true}`  
**Superseded:** `[{"slot": "max_price", "value": 30, "turn": 5}]`  
**Should ask:** no  
**Successful recommendations:** R21 Masala House, R23 Saffron Leaf  
**Safe without asking:** R21 Masala House, R23 Saffron Leaf  
**Relations:** t6 revise t5 (max_price)  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-REV-04A  (revision, variant A)

*Contrast:* Constraint-changing revision vs constraint-irrelevant revision. Falafel Stop (R39, no dinner) is wrong in A, valid in B.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Looking for a Mediterranean lunch spot near the station today. | user states cuisine=Mediterranean, location=station; lunch |
| 2 | assistant | Sure! Anything else I should know? | assistant asks |
| 3 | user | I'm vegetarian, and I want to keep it under $25. | user states vegetarian=true, max_price=25 |
| 4 | assistant | Got it: Mediterranean, near the station, vegetarian, under $25. | assistant summarises |
| 5 | user | Oh wait, it's actually dinner, not lunch. | user REVISES meal lunch -> dinner (adds dinner=true) |
| 6 | assistant | Thanks for letting me know. | assistant acknowledges |
| 7 | user | So which place? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Mediterranean", "max_price": 25, "location": "station", "vegetarian": true, "dinner": true}`  
**Gold active state:** `{"cuisine": "Mediterranean", "max_price": 25, "location": "station", "vegetarian": true, "dinner": true}`  
**Superseded:** `[{"slot": "meal", "value": "lunch", "turn": 1}]`  
**Should ask:** no  
**Successful recommendations:** R36 Olive & Thyme  
**Safe without asking:** R36 Olive & Thyme  
**Relations:** t5 revise t1 (dinner)  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-REV-04B  (revision, variant B)

*Contrast:* Constraint-changing revision vs constraint-irrelevant revision. Falafel Stop (R39, no dinner) is wrong in A, valid in B.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Looking for a Mediterranean lunch spot near the station today. | user states cuisine=Mediterranean, location=station; lunch |
| 2 | assistant | Sure! Anything else I should know? | assistant asks |
| 3 | user | I'm vegetarian, and I want to keep it under $25. | user states vegetarian=true, max_price=25 |
| 4 | assistant | Got it: Mediterranean, near the station, vegetarian, under $25. | assistant summarises |
| 5 | user | Oh wait, it's actually lunch tomorrow, not today. | user revises the DATE only; no tracked constraint changes |
| 6 | assistant | Thanks for letting me know. | assistant acknowledges |
| 7 | user | So which place? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Mediterranean", "max_price": 25, "location": "station", "vegetarian": true}`  
**Gold active state:** `{"cuisine": "Mediterranean", "max_price": 25, "location": "station", "vegetarian": true}`  
**Should ask:** no  
**Successful recommendations:** R36 Olive & Thyme, R39 Falafel Stop  
**Safe without asking:** R36 Olive & Thyme, R39 Falafel Stop  
**Relations:** t5 revise t1 (date (untracked))  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-REV-05  (revision, variant single)

*Contrast:* Revision chain: the latest revision wins; Hoshi Sushi Bar (R02) would be the outdated pick.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I want Italian for dinner near the mall. | user states cuisine=Italian, dinner=true, location=mall |
| 2 | assistant | Sounds good! Budget? | assistant asks budget |
| 3 | user | Up to $30. Vegetarian options too, please. | user states max_price=30, vegetarian=true |
| 4 | user | Actually, make it Japanese. | user REVISES cuisine Italian -> Japanese |
| 5 | assistant | Switched to Japanese. | assistant acknowledges |
| 6 | user | Hmm, no, let's go back to Italian after all. | user REVISES cuisine Japanese -> Italian |
| 7 | assistant | Okay, back to Italian. | assistant acknowledges |
| 8 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Italian", "max_price": 30, "location": "mall", "vegetarian": true, "dinner": true}`  
**Gold active state:** `{"cuisine": "Italian", "max_price": 30, "location": "mall", "vegetarian": true, "dinner": true}`  
**Superseded:** `[{"slot": "cuisine", "value": "Italian", "turn": 1}, {"slot": "cuisine", "value": "Japanese", "turn": 4}]`  
**Should ask:** no  
**Successful recommendations:** R07 Nonna's Kitchen  
**Safe without asking:** R07 Nonna's Kitchen  
**Relations:** t4 revise t1 (cuisine); t6 revise t4 (cuisine)  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-SUG-01A  (suggestion_acceptance, variant A)

*Contrast:* Non-acceptance vs explicit acceptance (positive control). Osteria Verde (R09, $34) is wrong in A, valid in B.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm looking for an Italian dinner near the mall. | user states cuisine=Italian, dinner=true, location=mall |
| 2 | assistant | Great! Any budget or dietary needs? | assistant asks |
| 3 | user | Vegetarian options, and I'd like to stay under $30. | user states vegetarian=true, max_price=30 |
| 4 | assistant | If you could go up to $35, there would be a few more options. | assistant PROPOSES max_price=35 |
| 5 | user | Hmm, I'll think about it. | user does NOT accept; max_price stays 30 |
| 6 | assistant | Okay! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Italian", "max_price": 30, "location": "mall", "vegetarian": true, "dinner": true}`  
**Gold active state:** `{"cuisine": "Italian", "max_price": 30, "location": "mall", "vegetarian": true, "dinner": true}`  
**Proposed, not accepted:** `[{"slot": "max_price", "value": 35, "turn": 4, "status": "not accepted"}]`  
**Should ask:** no  
**Successful recommendations:** R07 Nonna's Kitchen  
**Safe without asking:** R07 Nonna's Kitchen  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-SUG-01B  (suggestion_acceptance, variant B)

*Contrast:* Non-acceptance vs explicit acceptance (positive control). Osteria Verde (R09, $34) is wrong in A, valid in B.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'm looking for an Italian dinner near the mall. | user states cuisine=Italian, dinner=true, location=mall |
| 2 | assistant | Great! Any budget or dietary needs? | assistant asks |
| 3 | user | Vegetarian options, and I'd like to stay under $30. | user states vegetarian=true, max_price=30 |
| 4 | assistant | If you could go up to $35, there would be a few more options. | assistant PROPOSES max_price=35 |
| 5 | user | Sure, $35 is fine. | user ACCEPTS proposal; max_price=35 |
| 6 | assistant | Okay! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Italian", "max_price": 35, "location": "mall", "vegetarian": true, "dinner": true}`  
**Gold active state:** `{"cuisine": "Italian", "max_price": 35, "location": "mall", "vegetarian": true, "dinner": true}`  
**Superseded:** `[{"slot": "max_price", "value": 30, "turn": 3}]`  
**Should ask:** no  
**Successful recommendations:** R07 Nonna's Kitchen, R09 Osteria Verde  
**Safe without asking:** R07 Nonna's Kitchen, R09 Osteria Verde  
**Relations:** t5 confirm t4 (max_price); t5 revise t3 (max_price)  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-SUG-02A  (suggestion_acceptance, variant A)

*Contrast:* Rejected vs accepted proposal. The correct restaurant is completely different (R31 vs R28).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I need a dinner spot near the station tonight. | user states location=station, dinner=true |
| 2 | assistant | Happy to help. What's your budget? | assistant asks budget |
| 3 | user | $25 per person at most. | user states max_price=25 |
| 4 | assistant | Korean is a popular choice around the station. Would that work? | assistant PROPOSES cuisine=Korean |
| 5 | user | Not Korean, I had it yesterday. Let's do Chinese. | user REJECTS proposal; states cuisine=Chinese |
| 6 | assistant | Got it. | assistant acknowledges |
| 7 | user | Which restaurant should I go to? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Chinese", "max_price": 25, "location": "station", "dinner": true}`  
**Gold active state:** `{"cuisine": "Chinese", "max_price": 25, "location": "station", "dinner": true}`  
**Proposed, not accepted:** `[{"slot": "cuisine", "value": "Korean", "turn": 4, "status": "rejected"}]`  
**Should ask:** no  
**Successful recommendations:** R31 Golden Dragon  
**Safe without asking:** R31 Golden Dragon  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-SUG-02B  (suggestion_acceptance, variant B)

*Contrast:* Rejected vs accepted proposal. The correct restaurant is completely different (R31 vs R28).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I need a dinner spot near the station tonight. | user states location=station, dinner=true |
| 2 | assistant | Happy to help. What's your budget? | assistant asks budget |
| 3 | user | $25 per person at most. | user states max_price=25 |
| 4 | assistant | Korean is a popular choice around the station. Would that work? | assistant PROPOSES cuisine=Korean |
| 5 | user | Korean sounds great. | user ACCEPTS proposal; cuisine=Korean |
| 6 | assistant | Got it. | assistant acknowledges |
| 7 | user | Which restaurant should I go to? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Korean", "max_price": 25, "location": "station", "dinner": true}`  
**Gold active state:** `{"cuisine": "Korean", "max_price": 25, "location": "station", "dinner": true}`  
**Should ask:** no  
**Successful recommendations:** R28 Kimchi Pot  
**Safe without asking:** R28 Kimchi Pot  
**Relations:** t5 confirm t4 (cuisine)  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-SUG-03A  (suggestion_acceptance, variant A)

*Contrast:* Hedged vs explicit acceptance. A must not treat 'maybe' as acceptance in its state (H1), but does not need to ask because a mall option is safe under both readings.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I want Japanese food for dinner. | user states cuisine=Japanese, dinner=true |
| 2 | assistant | Great! Any budget? | assistant asks budget |
| 3 | user | Under $25 per person. | user states max_price=25 |
| 4 | assistant | The area around the mall has some nice options. Want me to look there? | assistant PROPOSES location=mall |
| 5 | user | Maybe, I'm not sure yet. | user neither accepts nor rejects (UNRESOLVED acceptance; hidden: no preference) |
| 6 | assistant | Okay. | assistant acknowledges |
| 7 | user | What do you suggest? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Japanese", "max_price": 25, "dinner": true}`  
**Gold active state:** `{"cuisine": "Japanese", "max_price": 25, "dinner": true}`  
**Proposed, not accepted:** `[{"slot": "location", "value": "mall", "turn": 4, "status": "unresolved"}]`  
**Unresolved:** 'Maybe, I'm not sure yet.' (turn 5)  
&nbsp;&nbsp;- {"location": null} -> R01 Sakura Ramen, R02 Hoshi Sushi Bar  
&nbsp;&nbsp;- {"location": "mall"} -> R02 Hoshi Sushi Bar  
**Should ask:** no  
**Successful recommendations:** R01 Sakura Ramen, R02 Hoshi Sushi Bar  
**Safe without asking:** R02 Hoshi Sushi Bar  

> FLAG: Is a hedge ('Maybe, I'm not sure yet') non-acceptance or unresolved? I labelled it unresolved. Either way the gold action is the same: Hoshi Sushi Bar (R02) satisfies both readings, so no question is needed. Needs a team decision for the guidelines.

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-SUG-03B  (suggestion_acceptance, variant B)

*Contrast:* Hedged vs explicit acceptance. A must not treat 'maybe' as acceptance in its state (H1), but does not need to ask because a mall option is safe under both readings.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I want Japanese food for dinner. | user states cuisine=Japanese, dinner=true |
| 2 | assistant | Great! Any budget? | assistant asks budget |
| 3 | user | Under $25 per person. | user states max_price=25 |
| 4 | assistant | The area around the mall has some nice options. Want me to look there? | assistant PROPOSES location=mall |
| 5 | user | Yes, the mall works. | user ACCEPTS proposal; location=mall |
| 6 | assistant | Okay. | assistant acknowledges |
| 7 | user | What do you suggest? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Japanese", "max_price": 25, "location": "mall", "dinner": true}`  
**Gold active state:** `{"cuisine": "Japanese", "max_price": 25, "location": "mall", "dinner": true}`  
**Should ask:** no  
**Successful recommendations:** R02 Hoshi Sushi Bar  
**Safe without asking:** R02 Hoshi Sushi Bar  
**Relations:** t5 confirm t4 (location)  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-SUG-04A  (suggestion_acceptance, variant A)

*Contrast:* 'Heard' vs 'accepted'. In B the state must contain no location constraint (H1, state metric).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'd like Mexican food for lunch. | user states cuisine=Mexican; lunch |
| 2 | assistant | Sure! There are Mexican places near the station and near the mall. | assistant PROPOSES two areas |
| 3 | user | The station's easier for me. | user ACCEPTS one proposal: location=station |
| 4 | assistant | Got it. Anything else, like budget or dietary needs? | assistant asks |
| 5 | user | Vegetarian options, and no more than $20. | user states vegetarian=true, max_price=20 |
| 6 | assistant | Thanks! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Mexican", "max_price": 20, "location": "station", "vegetarian": true}`  
**Gold active state:** `{"cuisine": "Mexican", "max_price": 20, "location": "station", "vegetarian": true}`  
**Proposed, not accepted:** `[{"slot": "location", "value": "mall", "turn": 2, "status": "not accepted"}]`  
**Should ask:** no  
**Successful recommendations:** R11 Taco Loco, R13 El Comal  
**Safe without asking:** R11 Taco Loco, R13 El Comal  
**Relations:** t3 confirm t2 (location)  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-SUG-04B  (suggestion_acceptance, variant B)

*Contrast:* 'Heard' vs 'accepted'. In B the state must contain no location constraint (H1, state metric).

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | I'd like Mexican food for lunch. | user states cuisine=Mexican; lunch |
| 2 | assistant | Sure! There are Mexican places near the station and near the mall. | assistant PROPOSES two areas |
| 3 | user | Okay. | user ACKNOWLEDGES only; neither area accepted |
| 4 | assistant | Got it. Anything else, like budget or dietary needs? | assistant asks |
| 5 | user | Vegetarian options, and no more than $20. | user states vegetarian=true, max_price=20 |
| 6 | assistant | Thanks! | assistant acknowledges |
| 7 | user | What do you recommend? | user requests recommendation |

**Hidden goal:** `{"cuisine": "Mexican", "max_price": 20, "vegetarian": true}`  
**Gold active state:** `{"cuisine": "Mexican", "max_price": 20, "vegetarian": true}`  
**Proposed, not accepted:** `[{"slot": "location", "value": "station", "turn": 2, "status": "acknowledged only"}, {"slot": "location", "value": "mall", "turn": 2, "status": "acknowledged only"}]`  
**Should ask:** no  
**Successful recommendations:** R11 Taco Loco, R13 El Comal, R15 Burrito Express  
**Safe without asking:** R11 Taco Loco, R13 El Comal, R15 Burrito Express  

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing

---

## XX-SUG-05  (suggestion_acceptance, variant single)

*Contrast:* Partial acceptance of a two-part suggestion. Saffron Leaf (R23, Indian) is the trap.

| # | Speaker | Text | Planned act |
|---|---|---|---|
| 1 | user | Can you find me somewhere for dinner? I'm not picky about cuisine. | user states dinner=true; no cuisine pref |
| 2 | assistant | Sure! What's your budget? | assistant asks budget |
| 3 | user | Up to $25 a person. | user states max_price=25 |
| 4 | assistant | How about Indian near the mall? There are good options there. | assistant PROPOSES cuisine=Indian AND location=mall |
| 5 | user | The mall works, but not Indian. | user ACCEPTS location=mall, REJECTS Indian |
| 6 | assistant | Got it. | assistant acknowledges |
| 7 | user | What would you pick? | user requests recommendation |

**Hidden goal:** `{"exclude_cuisine": ["Indian"], "max_price": 25, "location": "mall", "dinner": true}`  
**Gold active state:** `{"exclude_cuisine": ["Indian"], "max_price": 25, "location": "mall", "dinner": true}`  
**Proposed, not accepted:** `[{"slot": "cuisine", "value": "Indian", "turn": 4, "status": "rejected"}]`  
**Should ask:** no  
**Successful recommendations:** R02 Hoshi Sushi Bar, R13 El Comal, R31 Golden Dragon, R35 Noodle Bar 88, R37 Pita Port  
**Safe without asking:** R02 Hoshi Sushi Bar, R13 El Comal, R31 Golden Dragon, R35 Noodle Bar 88, R37 Pita Port  
**Relations:** t5 confirm t4 (location)  

> FLAG: Uses exclude_cuisine (a negative constraint). Check the team schema allows it; if not, replace turn 5 with an explicit cuisine.

- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing