# Labeling sheet (second annotator)

Please label each conversation **on your own, before any discussion**. Do not open the scenario files, the review sheets or `item_key.csv` - they contain the answers.

For each item fill one row of `labels_template.csv`:

- **should_ask**: `yes` if the assistant should ask a clarification question before recommending (because the user's request can be read in more than one way AND no single restaurant in the table fits every reading); otherwise `no`.
- **cuisine, exclude_cuisine, max_price, location, vegetarian, dinner**: the user's *settled* requirements at the end of the conversation. Leave a field blank if it was never stated, is still unclear, or was only suggested by the assistant and not accepted. `Thai|Mexican` = either is fine. `vegetarian`/`dinner`: `yes` or blank. Lunch = no dinner requirement. `location` is `station` or `mall`.
- **relations**: links between turns, written `source>target:relation:slot` and separated by `;`. Relations: `revise` (replaces an earlier requirement), `confirm` (accepts an assistant suggestion), `clarify`. Example: `5>4:confirm:max_price; 5>3:revise:max_price`. Blank if none.

## Restaurant table

| id | name | cuisine | $/person | near station | near mall | vegetarian | open for dinner |
|---|---|---|---|---|---|---|---|
| R01 | Sakura Ramen | Japanese | 18 | yes |  |  | yes |
| R02 | Hoshi Sushi Bar | Japanese | 24 |  | yes | yes | yes |
| R03 | Kumo Izakaya | Japanese | 29 | yes | yes |  | yes |
| R04 | Tsuki Bento | Japanese | 14 |  |  | yes |  |
| R05 | Ginza Omakase | Japanese | 58 | yes |  |  | yes |
| R06 | Trattoria Lucca | Italian | 22 | yes |  | yes | yes |
| R07 | Nonna's Kitchen | Italian | 27 |  | yes | yes | yes |
| R08 | Forno Pizza | Italian | 16 | yes | yes | yes |  |
| R09 | Osteria Verde | Italian | 34 |  | yes | yes | yes |
| R10 | Il Mulino Nero | Italian | 45 |  |  |  | yes |
| R11 | Taco Loco | Mexican | 12 | yes |  | yes | yes |
| R12 | Casa Azul | Mexican | 26 |  | yes |  | yes |
| R13 | El Comal | Mexican | 19 | yes | yes | yes | yes |
| R14 | Agave Cantina | Mexican | 38 |  | yes |  | yes |
| R15 | Burrito Express | Mexican | 10 |  |  | yes |  |
| R16 | Bangkok Street | Thai | 17 | yes |  | yes | yes |
| R17 | Lotus Thai | Thai | 23 |  | yes | yes |  |
| R18 | Siam Garden | Thai | 31 |  | yes | yes | yes |
| R19 | Chili Basil | Thai | 21 |  |  |  | yes |
| R20 | Royal Orchid | Thai | 48 | yes | yes | yes | yes |
| R21 | Masala House | Indian | 20 | yes |  | yes | yes |
| R22 | Tandoor Grill | Indian | 28 |  | yes |  | yes |
| R23 | Saffron Leaf | Indian | 25 | yes | yes | yes | yes |
| R24 | Dosa Corner | Indian | 13 |  |  | yes |  |
| R25 | Maharaja Palace | Indian | 52 |  | yes | yes | yes |
| R26 | Seoul BBQ | Korean | 36 | yes |  |  | yes |
| R27 | Bibim Bowl | Korean | 15 |  | yes | yes |  |
| R28 | Kimchi Pot | Korean | 22 | yes |  |  | yes |
| R29 | Hanok Table | Korean | 27 |  | yes | yes | yes |
| R30 | Gangnam Grill | Korean | 44 |  |  |  | yes |
| R31 | Golden Dragon | Chinese | 24 | yes | yes | yes | yes |
| R32 | Dumpling King | Chinese | 13 | yes |  | yes |  |
| R33 | Sichuan Spice | Chinese | 26 |  | yes |  | yes |
| R34 | Jade Garden | Chinese | 39 |  |  | yes | yes |
| R35 | Noodle Bar 88 | Chinese | 16 |  | yes |  | yes |
| R36 | Olive & Thyme | Mediterranean | 23 | yes |  | yes | yes |
| R37 | Pita Port | Mediterranean | 14 |  | yes | yes | yes |
| R38 | Aegean Table | Mediterranean | 33 | yes |  | yes | yes |
| R39 | Falafel Stop | Mediterranean | 11 | yes | yes | yes |  |
| R40 | Santorini Grill | Mediterranean | 47 |  | yes |  | yes |

## S01

1. **user**: Can you find me somewhere for dinner? I'm not picky about cuisine.  
2. **assistant**: Sure! What's your budget?  
3. **user**: Up to $25 a person.  
4. **assistant**: How about Indian near the mall? There are good options there.  
5. **user**: The mall works, but not Indian.  
6. **assistant**: Got it.  
7. **user**: What would you pick?  

should_ask: ____  constraints: ____  relations: ____

## S02

1. **user**: I work by the train station but I live by the mall.  
2. **assistant**: Handy! How can I help?  
3. **user**: I want Mediterranean food with vegetarian options.  
4. **assistant**: Sounds good. What's your budget?  
5. **user**: Up to $35. It's for dinner tonight.  
6. **assistant**: Okay.  
7. **user**: Find something close to where I'll be.  

should_ask: ____  constraints: ____  relations: ____

## S03

1. **user**: I'm looking for Italian food near the station.  
2. **assistant**: Sounds good! Any budget?  
3. **user**: No more than $35 per person. It's for dinner.  
4. **assistant**: The mall area also has Italian food in that range. Want me to look there instead?  
5. **user**: Yes, let's look near the mall instead.  
6. **assistant**: Okay!  
7. **user**: What do you recommend?  

should_ask: ____  constraints: ____  relations: ____

## S04

1. **user**: I'm up for Chinese or Indian food, either is fine.  
2. **assistant**: There are options near the station and near the mall.  
3. **user**: Nice. Unrelated, but I'm also trying to pick a birthday gift for my mom.  
4. **assistant**: Flowers or a good book are always safe choices!  
5. **user**: Good idea. Anyway, my budget is $20 per person.  
6. **assistant**: Got it.  
7. **user**: It's for dinner.  
8. **assistant**: Okay, noted.  
9. **user**: Can you find me something in that area you mentioned at the start?  

should_ask: ____  constraints: ____  relations: ____

## S05

1. **user**: I'm in the mood for Japanese food.  
2. **assistant**: Nice! There are Japanese places near the station and near the mall.  
3. **user**: Good to know. My budget is $25 per person.  
4. **assistant**: Got it, I'll keep the budget in mind.  
5. **user**: Oh, and it's for lunch, not dinner.  
6. **assistant**: Okay, lunch it is.  
7. **user**: Can you find me something near there?  

should_ask: ____  constraints: ____  relations: ____

## S06

1. **user**: I work by the train station but I live by the mall.  
2. **assistant**: Handy! How can I help?  
3. **user**: I want Mediterranean food with vegetarian options.  
4. **assistant**: Sounds good. What's your budget?  
5. **user**: Up to $35. It's for lunch tomorrow.  
6. **assistant**: Okay.  
7. **user**: Find something close to where I'll be.  

should_ask: ____  constraints: ____  relations: ____

## S07

1. **user**: I'd like Indian food for dinner tonight.  
2. **assistant**: Lovely. Where will you be?  
3. **user**: Near the station. I need vegetarian options too.  
4. **assistant**: Got it. Budget?  
5. **user**: Up to $30.  
6. **user**: Actually, let's cap it at $25.  
7. **assistant**: Updated!  
8. **user**: What do you recommend?  

should_ask: ____  constraints: ____  relations: ____

## S08

1. **user**: I'm looking for Chinese food near the station.  
2. **assistant**: Sounds good! Any budget?  
3. **user**: No more than $20 per person.  
4. **assistant**: The mall area also has Chinese food in that range. Want me to look there instead?  
5. **user**: Yes, let's look near the mall instead.  
6. **assistant**: Okay!  
7. **user**: What do you recommend?  

should_ask: ____  constraints: ____  relations: ____

## S09

1. **user**: I'm looking for a Korean lunch spot by the mall.  
2. **assistant**: Sounds good! Any dietary restrictions?  
3. **user**: I'm vegetarian.  
4. **assistant**: Got it. And your budget?  
5. **user**: $20 max per person.  
6. **user**: What do you suggest?  

should_ask: ____  constraints: ____  relations: ____

## S10

1. **user**: I'd like Indian food near the station.  
2. **assistant**: Sounds good! Any budget?  
3. **user**: No more than $20 per person.  
4. **assistant**: There are also some nice Italian places near the station. Would Italian work instead?  
5. **user**: Maybe, I'm not sure yet.  
6. **assistant**: Okay!  
7. **user**: What do you recommend?  

should_ask: ____  constraints: ____  relations: ____

## S11

1. **user**: I'm up for Chinese or Korean food, either is fine.  
2. **assistant**: Sure! There are good options near the station and near the mall.  
3. **user**: My budget is $15 per person.  
4. **assistant**: Got it, I'll keep the budget in mind.  
5. **user**: It's for lunch.  
6. **assistant**: Okay, noted.  
7. **user**: Find me a spot over there.  

should_ask: ____  constraints: ____  relations: ____

## S12

1. **user**: I'm up for Indian or Japanese food, either is fine.  
2. **assistant**: Sure! There are good options near the mall and near the station.  
3. **user**: My budget is $24 per person.  
4. **assistant**: Got it, I'll keep the budget in mind.  
5. **user**: It's for dinner. I also need vegetarian options.  
6. **assistant**: Okay, noted.  
7. **user**: Pick something on that side, please.  

should_ask: ____  constraints: ____  relations: ____

## S13

1. **assistant**: Hi! What can I help you with today?  
2. **user**: I need somewhere with vegetarian options, my partner doesn't eat meat.  
3. **assistant**: Sure. Is this for a special occasion?  
4. **user**: Yes, it's my sister's birthday. She just got a new job too.  
5. **assistant**: Congratulations to her! What food does she like?  
6. **user**: She loves Indian food.  
7. **assistant**: Great choice. Any area in mind?  
8. **user**: Near the mall, and let's keep it under $30 a person.  
9. **assistant**: Okay: Indian, near the mall, under $30.  
10. **user**: Perfect. What would you recommend?  

should_ask: ____  constraints: ____  relations: ____

## S14

1. **user**: Two of my friends each recommended a place around here: one Thai, one Italian.  
2. **assistant**: Both sound like good options! Want me to look into them?  
3. **user**: The area doesn't matter to me.  
4. **assistant**: Okay, anywhere works.  
5. **user**: No more than $17 a person. It's for lunch.  
6. **assistant**: Noted.  
7. **user**: Let's go with Sam's recommendation.  

should_ask: ____  constraints: ____  relations: ____

## S15

1. **user**: Hey, I need a dinner spot for tonight.  
2. **assistant**: Sure! What cuisine?  
3. **user**: Mediterranean. Somewhere near the station.  
4. **user**: I'm vegetarian, and I'd like to stay under $25.  
5. **assistant**: So: Mediterranean, near the station, vegetarian options, under $25, open for dinner. Is that right?  
6. **user**: Yes, exactly.  
7. **user**: What's the best match?  

should_ask: ____  constraints: ____  relations: ____

## S16

1. **user**: I'd like Chinese food near the station.  
2. **assistant**: Sounds good! Any budget?  
3. **user**: No more than $20 per person.  
4. **assistant**: There are also some nice Indian places near the station. Would Indian work instead?  
5. **user**: Sure, let's do Indian instead.  
6. **assistant**: Okay!  
7. **user**: What do you recommend?  

should_ask: ____  constraints: ____  relations: ____

## S17

1. **user**: I'm meeting a friend at the mall for dinner. Can you suggest an Italian place?  
2. **assistant**: Sure. Any budget or dietary needs I should know about?  
3. **user**: My friend is vegetarian, so we need vegetarian options.  
4. **assistant**: Noted: vegetarian-friendly Italian near the mall.  
5. **user**: And let's keep it to $35 per person at most.  
6. **user**: Which one should we go to?  

should_ask: ____  constraints: ____  relations: ____

## S18

1. **user**: I'd like Mediterranean food near the station.  
2. **assistant**: Sounds good! Any budget?  
3. **user**: No more than $12 per person.  
4. **assistant**: There are also some nice Mexican places near the station. Would Mexican work instead?  
5. **user**: I don't know, possibly.  
6. **assistant**: Okay!  
7. **user**: What do you recommend?  

should_ask: ____  constraints: ____  relations: ____

## S19

1. **assistant**: Hi! What can I help you with today?  
2. **user**: I need a place that's open for dinner and has vegetarian options.  
3. **assistant**: Sure. Is this for a special occasion?  
4. **user**: Yes, it's my sister's birthday. She just got a new job too.  
5. **assistant**: Congratulations to her! What food does she like?  
6. **user**: She loves Chinese food.  
7. **assistant**: Great choice. Any area in mind?  
8. **user**: Near the station, and let's keep it under $25 a person.  
9. **assistant**: Okay: Chinese, near the station, under $25.  
10. **user**: Perfect. What would you recommend?  

should_ask: ____  constraints: ____  relations: ____

## S20

1. **user**: My friend is choosing where we get lunch.  
2. **assistant**: Fun! What is she considering?  
3. **user**: She's deciding between Korean and Japanese, either near the station or near the mall.  
4. **assistant**: Got it. Any budget?  
5. **user**: Up to $27 each.  
6. **assistant**: Noted.  
7. **user**: She just texted me her choice. Can you find a place that matches it?  

should_ask: ____  constraints: ____  relations: ____

## S21

1. **user**: Can you help me find a place for dinner tonight?  
2. **assistant**: Sure! I can look near the station or near the mall; both have plenty of options.  
3. **user**: I'm craving Korean.  
4. **assistant**: Great. Any budget?  
5. **user**: Up to $30 a person.  
6. **assistant**: Okay, $30 max per person, open for dinner.  
7. **user**: Great, find me something over there.  

should_ask: ____  constraints: ____  relations: ____

## S22

1. **user**: I'm looking for an Italian dinner near the mall.  
2. **assistant**: Great! Any budget or dietary needs?  
3. **user**: Vegetarian options, and I'd like to stay under $30.  
4. **assistant**: If you could go up to $35, there would be a few more options.  
5. **user**: Sure, $35 is fine.  
6. **assistant**: Okay!  
7. **user**: What do you recommend?  

should_ask: ____  constraints: ____  relations: ____

## S23

1. **user**: Find me an Italian place for dinner, under $30 a person.  
2. **assistant**: Sure! Any area preference?  
3. **user**: Near the station, please.  
4. **assistant**: Got it: Italian, near the station, under $30.  
5. **user**: Actually, Japanese would be fine too.  
6. **assistant**: No problem.  
7. **user**: What's your recommendation?  

should_ask: ____  constraints: ____  relations: ____

## S24

1. **assistant**: Hi! What can I help you with today?  
2. **user**: I can't spend more than $20 per person.  
3. **assistant**: Sure. Is this for a special occasion?  
4. **user**: Yes, it's my sister's birthday. She just got a new job too.  
5. **assistant**: Congratulations to her! What food does she like?  
6. **user**: She loves Japanese food.  
7. **assistant**: Great choice. Any area in mind?  
8. **user**: Near the station.  
9. **assistant**: Okay: Japanese, near the station.  
10. **user**: Perfect. What would you recommend?  

should_ask: ____  constraints: ____  relations: ____

## S25

1. **user**: Looking for a Mediterranean lunch spot near the station today.  
2. **assistant**: Sure! Anything else I should know?  
3. **user**: I'm vegetarian, and I want to keep it under $25.  
4. **assistant**: Got it: Mediterranean, near the station, vegetarian, under $25.  
5. **user**: Oh wait, it's actually dinner, not lunch.  
6. **assistant**: Thanks for letting me know.  
7. **user**: So which place?  

should_ask: ____  constraints: ____  relations: ____

## S26

1. **user**: I'm up for Japanese or Korean food, either is fine.  
2. **assistant**: Sure! There are good options near the mall and near the station.  
3. **user**: My budget is $20 per person.  
4. **assistant**: Okay. With that budget, the station side and the mall side both still have choices.  
5. **user**: It's for lunch.  
6. **assistant**: Okay, noted.  
7. **user**: Let's go with the second place you mentioned.  

should_ask: ____  constraints: ____  relations: ____

## S27

1. **user**: I'm looking for a Korean lunch spot by the mall.  
2. **assistant**: Sounds good! Any dietary restrictions?  
3. **user**: I'm vegetarian.  
4. **assistant**: Got it. And your budget?  
5. **user**: $30 max per person.  
6. **user**: What do you suggest?  

should_ask: ____  constraints: ____  relations: ____

## S28

1. **user**: I want Japanese food for dinner.  
2. **assistant**: Great! Any budget?  
3. **user**: Under $25 per person.  
4. **assistant**: The area around the mall has some nice options. Want me to look there?  
5. **user**: Yes, the mall works.  
6. **assistant**: Okay.  
7. **user**: What do you suggest?  

should_ask: ____  constraints: ____  relations: ____

## S29

1. **assistant**: Hi! What can I help you with today?  
2. **user**: I need a place that's open for dinner.  
3. **assistant**: Sure. Is this for a special occasion?  
4. **user**: Yes, it's my sister's birthday. She just got a new job too.  
5. **assistant**: Congratulations to her! What food does she like?  
6. **user**: She loves Italian food.  
7. **assistant**: Great choice. Any area in mind?  
8. **user**: Near the station, and let's keep it under $25 a person.  
9. **assistant**: Okay: Italian, near the station, under $25.  
10. **user**: Perfect. What would you recommend?  

should_ask: ____  constraints: ____  relations: ____

## S30

1. **user**: Find me an Italian place for dinner, under $30 a person.  
2. **assistant**: Sure! Any area preference?  
3. **user**: Near the station, please.  
4. **assistant**: Got it: Italian, near the station, under $30.  
5. **user**: Actually, make it Japanese instead.  
6. **assistant**: No problem.  
7. **user**: What's your recommendation?  

should_ask: ____  constraints: ____  relations: ____
