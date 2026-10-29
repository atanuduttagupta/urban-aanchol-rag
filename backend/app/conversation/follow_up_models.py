from dataclasses import dataclass
from enum import StrEnum


class FollowUpIntentType(StrEnum):
    REFERENCE = "reference"
    MORE_RESULTS = "more_results"
    CHANGE_LIMIT = "change_limit"
    REFINE_PRICE = "refine_price"
    REFINE_ATTRIBUTE = "refine_attribute"
    SIMILAR_TO = "similar_to"


@dataclass(frozen=True)
class FollowUpIntent:
    intent_type: FollowUpIntentType
    requested_limit: int | None = None
    reference_position: int | None = None
    semantic_query: str | None = None