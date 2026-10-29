# Day 12 — Conversational Follow-ups

## Objective

Establish a deterministic foundation for understanding customer follow-up messages and resolving product references using trusted conversation context.

The implementation must preserve the separation between follow-up detection, reference resolution, retrieval orchestration, and recommendation logic.

## Day 12 Architecture

```text
Customer Follow-up
        ↓
Follow-up Intent Detection
        ↓
Retrieval Safety
        ↓
Context-aware Reference Resolution
        ↓
Resolution Status
        ↓
Future Retrieval / Recommendation Continuation
```

Day 12 establishes the conversation-resolution foundation. It does not yet implement complete pagination, duplicate-free retrieval, or LLM-generated responses.

---

## 12A — Architecture Review

Reviewed the existing conversation and retrieval architecture.

Design decisions:

- Keep conversation logic separate from retrieval and recommendation.
- Reuse trusted `ConversationContext`.
- Do not invent product IDs.
- Preserve ambiguity when a request cannot be resolved deterministically.
- Avoid expanding the conversation context model without a demonstrated requirement.

---

## 12B — Follow-up Intent Model

Created:

```text
backend/app/conversation/follow_up_models.py
```

Introduced `FollowUpIntentType` and the immutable `FollowUpIntent` model.

Supported intent categories:

- `REFERENCE`
- `MORE_RESULTS`
- `CHANGE_LIMIT`
- `REFINE_PRICE`
- `REFINE_ATTRIBUTE`
- `SIMILAR_TO`

The model can carry a requested result limit, reference position, and semantic query.

Tests:

```text
backend/tests/test_follow_up_models.py
```

---

## 12C — Deterministic Follow-up Detector

Created:

```text
backend/app/conversation/follow_up_detector.py
```

The detector recognizes a baseline set of follow-up patterns, including:

- References to the first, second, or third result
- Requests for more results
- Requests to change the result limit
- Price refinement
- Attribute refinement
- Similar-product requests

Unsupported or unrecognized patterns return `None` rather than being assigned an arbitrary intent.

Combined requests such as “Something cheaper than the second one” are deliberately not simplified into a reference-only intent.

Tests:

```text
backend/tests/test_follow_up_detector.py
```

The detector is a deterministic baseline. It is not a general-purpose natural-language intent parser.

---

## 12D — Context-aware Reference Resolution

Integrated follow-up detection into:

```text
backend/app/conversation/resolution.py
```

The existing reference resolver remains in:

```text
backend/app/conversation/resolver.py
```

It resolves supported positional references using `ConversationContext.last_result_ids` and selected-product references using trusted context.

The resolution layer retains the existing `RESOLVED`, `AMBIGUOUS`, and `UNRESOLVED` outcomes.

### Safety behaviour

- Resolve a positional reference only when the requested result exists in the prior result list.
- Do not invent product IDs.
- Keep unresolved references ambiguous when retrieval-critical signals exist.
- Do not treat a combined price-comparison and positional-reference request as resolved merely because its product reference can be identified.
- Preserve the existing deterministic resolver as a fallback for supported references that the new detector does not recognize, except when the combined-comparison safety rule applies.

### Regression test

Added integration cases to:

```text
backend/tests/test_resolution.py
```

The tests cover second-result resolution, a missing third result, and a combined price-comparison/reference request.

During testing, the combined-request case exposed a fallback issue: the existing resolver could resolve the positional reference even though the full request remained ambiguous. The fallback was constrained to preserve the ambiguity.

---

## Verification

### Focused tests

The following conversation-related test files were checked:

```text
backend/tests/test_resolution.py
backend/tests/test_reference_resolver.py
backend/tests/test_follow_up_models.py
backend/tests/test_follow_up_detector.py
backend/tests/test_conversation_context.py
```

Result:

```text
39 passed
```

### Full test suite

Result:

```text
234 passed
```

### Ruff

The conversation application code passed:

```powershell
python -m ruff check backend/app/conversation
```

The broader command:

```powershell
python -m ruff check backend/app/conversation backend/tests
```

reported 23 findings in several existing test files. These include import-order issues, duplicate imports, unused imports, and other lint findings. They were not all part of Day 12 and were deliberately left untouched.

### Whitespace verification

```powershell
git diff --check
```

Passed after removing the extra blank lines at the ends of two modified files.

---

## Architecture Decisions

### 1. Follow-up detection and reference resolution are separate

The detector identifies a supported follow-up pattern. The resolver verifies whether a product reference can be mapped to trusted conversation context.

### 2. Retrieval safety remains authoritative

A detected follow-up does not automatically make the complete query safe. Additional retrieval-critical ambiguity must still be handled.

### 3. Do not claim unimplemented continuation behaviour

Although the model recognizes `MORE_RESULTS`, complete pagination and duplicate exclusion remain future work. Recognition alone does not retrieve additional products.

### 4. Preserve provider independence

The deterministic conversation layer does not require an LLM provider. Future LLM interpretation must not bypass deterministic safety checks.

---

## Day 12 Outcome

Urban Aanchol now has a baseline follow-up intent model, deterministic follow-up detector, and an integrated context-aware reference-resolution path.

The next step is to implement duplicate-free continuation when a customer asks for more sarees, using previously shown product IDs.

## Completion Checklist

- [x] Existing conversation architecture reviewed
- [x] Follow-up intent model created
- [x] Deterministic follow-up detector created
- [x] Reference resolution integrated with follow-up detection
- [x] Combined comparison/reference safety regression added
- [x] Focused conversation tests passed
- [x] Full test suite passed: 234 tests
- [x] Conversation application Ruff check passed
- [x] `git diff --check` passed
- [ ] Journey documentation committed
- [ ] Changes pushed to GitHub

Day 12 is ready for final review, documentation integration, and commit.
