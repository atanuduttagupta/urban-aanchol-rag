import re

from backend.app.conversation.follow_up_models import (
    FollowUpIntent,
    FollowUpIntentType,
)


def detect_follow_up_intent(
    query: str,
) -> FollowUpIntent | None:
    normalized = re.sub(r"\s+", " ", query.strip().casefold())

    if not normalized:
        return None


    # Do not silently simplify queries containing multiple intents.
    if (
        re.search(r"\bcheaper\s+than\b", normalized)
        and re.search(
            r"\b(?:first|second|third|1st|2nd|3rd)\s+one\b",
            normalized,
        )
    ):
        return None


    reference_patterns = (
        (r"\b(?:the )?second one\b", 2),
        (r"\b(?:the )?first one\b", 1),
        (r"\b(?:the )?third one\b", 3),
    )

    for pattern, position in reference_patterns:
        if re.search(pattern, normalized):
            return FollowUpIntent(
                intent_type=FollowUpIntentType.REFERENCE,
                reference_position=position,
                semantic_query=query,
            )

    more_match = re.search(
        r"\b(?:show me|give me|find me|show)\s+(\d+)\s+more\b",
        normalized,
    )
    if more_match:
        count = int(more_match.group(1))
        if count > 0:
            return FollowUpIntent(
                intent_type=FollowUpIntentType.MORE_RESULTS,
                requested_limit=count,
                semantic_query=query,
            )
        return None

    limit_match = re.search(
        r"\b(?:show me|give me|show)\s+(\d+)\s+instead\b",
        normalized,
    )
    if limit_match:
        count = int(limit_match.group(1))
        if count > 0:
            return FollowUpIntent(
                intent_type=FollowUpIntentType.CHANGE_LIMIT,
                requested_limit=count,
                semantic_query=query,
            )
        return None

    if re.search(
        r"\b(?:something|anything|sarees?)\s+cheaper\b",
        normalized,
    ):
        return FollowUpIntent(
            intent_type=FollowUpIntentType.REFINE_PRICE,
            semantic_query=query,
        )

    if re.search(
        r"\bsame style\b|\bin (?:red|blue|green|black|white|pink)\b",
        normalized,
    ):
        return FollowUpIntent(
            intent_type=FollowUpIntentType.REFINE_ATTRIBUTE,
            semantic_query=query,
        )

    if re.search(
        r"\bsimilar\b|\bsomething like (?:this|that)\b",
        normalized,
    ):
        return FollowUpIntent(
            intent_type=FollowUpIntentType.SIMILAR_TO,
            semantic_query=query,
        )

    return None
