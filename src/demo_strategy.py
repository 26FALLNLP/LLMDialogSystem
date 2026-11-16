"""Rule-based strategy for the station/mall contrast in the sample dialogues."""

from __future__ import annotations

import re

from .dialogue_types import Ask, Decision, DialogueContext, Question, Recommend


_CUISINE = re.compile(r"\bin the mood for (.+?) food\b", re.IGNORECASE)
_BUDGET = re.compile(r"\bbudget is \$(\d+)\b", re.IGNORECASE)
_NEAR_THERE = re.compile(r"\bnear there\b", re.IGNORECASE)
_NEAR_LOCATION = re.compile(r"\bnear (?:the )?(station|mall)\b", re.IGNORECASE)


class DemoStrategy:
    """Use the public text and catalog to exercise both pipeline branches."""

    system_id = "demo-shared-candidate"

    def decide(self, context: DialogueContext) -> Decision:
        cuisine = None
        max_price = None
        offered_locations: tuple[str, ...] = ()
        locations: tuple[str, ...] = ()
        unresolved_turn = None

        for turn in context.turns:
            mentioned = tuple(dict.fromkeys(
                match.casefold() for match in _NEAR_LOCATION.findall(turn.text)
            ))
            if turn.role == "assistant":
                if len(mentioned) > 1:
                    offered_locations = mentioned
                continue

            if match := _CUISINE.search(turn.text):
                cuisine = match[1].casefold()
            if match := _BUDGET.search(turn.text):
                max_price = int(match[1])
            if _NEAR_THERE.search(turn.text) and offered_locations:
                locations = offered_locations
                unresolved_turn = turn.turn_id
            elif len(mentioned) == 1:
                locations = mentioned
                unresolved_turn = None

        if cuisine is None or max_price is None or not locations:
            return Decision(None, error="Demo strategy needs a cuisine, budget, and location options.")

        candidate_sets = {
            location: {
                str(restaurant["restaurant_id"])
                for restaurant in context.restaurant_database
                if str(restaurant["cuisine"]).casefold() == cuisine
                and int(restaurant["price_per_person"]) <= max_price
                and restaurant[f"near_{location}"]
            }
            for location in locations
        }
        shared = set.intersection(*candidate_sets.values())
        snapshot = {
            "cuisine": cuisine,
            "max_price": max_price,
            "unresolved_turn": unresolved_turn,
            "candidate_sets": {
                location: sorted(candidates) for location, candidates in candidate_sets.items()
            },
            "shared_candidates": sorted(shared),
        }

        if shared:
            return Decision(Recommend(min(shared)), state_snapshot=snapshot)
        possible = set.union(*candidate_sets.values())
        if not possible:
            return Decision(None, state_snapshot=snapshot, error="No matching restaurant.")
        if unresolved_turn is not None and "ASK" in context.allowed_actions:
            question = Question(
                text="Do you mean near the station or near the mall?",
                slot="location",
                reference_turn_id=unresolved_turn,
            )
            return Decision(Ask((question,)), state_snapshot=snapshot)
        return Decision(Recommend(min(possible)), state_snapshot=snapshot)
