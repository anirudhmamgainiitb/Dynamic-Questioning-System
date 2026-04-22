from src.retriever.filter import filter_questions
from src.retriever.scorer import score_question


# -----------------------------
# MAIN RETRIEVER
# -----------------------------
def get_next_question(state, question_bank):
    """
    Returns the next best question based on:
    - filtering
    - scoring
    - anti-repetition constraints
    """

    # -----------------------------
    # 0. INIT STATE MEMORY
    # -----------------------------
    state.setdefault("asked_fields", set())
    state.setdefault("answered_fields", set())
    state.setdefault("recent_fields", [])

    # -----------------------------
    # 1. FILTER
    # -----------------------------
    candidates = filter_questions(question_bank, state)

    if not candidates:
        return None

    # -----------------------------
    # 2. SCORE ALL
    # -----------------------------
    scored = []

    for q in candidates:
        scores = score_question(q, state)
        scored.append((q, scores))

    # -----------------------------
    # 3. SORT BY SCORE
    # -----------------------------
    scored.sort(key=lambda x: x[1]["final"], reverse=True)

    # -----------------------------
    # 4. SELECT (ANTI-REPETITION LOGIC)
    # -----------------------------
    asked = state.get("asked_fields", set())
    answered = state.get("answered_fields", set())
    recent = state.get("recent_fields", [])

    selected_q = None
    selected_scores = None

    for q, scores in scored:
        field = q["question_field"]

        # ❌ HARD BLOCK 1: already answered
        if field in answered:
            continue

        # ❌ HARD BLOCK 2: already asked
        if field in asked:
            continue

        # ❌ HARD BLOCK 3: recently asked (prevents loops)
        if field in recent:
            continue

        selected_q = q
        selected_scores = scores
        break

    # -----------------------------
    # 5. FALLBACK (if everything blocked)
    # -----------------------------
    if not selected_q:
        for q, scores in scored:
            field = q["question_field"]

            # allow less strict fallback (ignore recent)
            if field not in answered:
                selected_q = q
                selected_scores = scores
                break

    # absolute fallback
    if not selected_q:
        selected_q, selected_scores = scored[0]

    # -----------------------------
    # 6. UPDATE STATE MEMORY
    # -----------------------------
    field = selected_q["question_field"]

    state["recent_fields"].append(field)
    state["recent_fields"] = state["recent_fields"][-3:]  # keep last 3

    state["asked_fields"].add(field)

    # -----------------------------
    # 7. RETURN RESPONSE
    # -----------------------------
    return {
    "question_id": selected_q["id"],
    "question_text": selected_q["text"],
    "question_field": selected_q["question_field"],
    "priority": selected_q["priority"],   
    "score_breakdown": selected_scores,
    "why_asked": build_reason(selected_q, state)
}


# -----------------------------
# REASON BUILDER
# -----------------------------
def build_reason(question, state):
    """
    Explains WHY the question was selected
    """

    reasons = []

    triggers = question.get("triggers", {})

    # Trigger reasoning
    for key in triggers:
        if key in state:
            reasons.append(f"{key} condition satisfied")

    # Missing field reasoning
    for field in question["targets"]["fill_fields"]:
        reasons.append(f"{field} not yet collected")

    # Category exploration
    category = question["question_field"].split(".")[0]
    extracted = state.get("meta", {}).get("already_extracted_categories", [])

    if category not in extracted:
        reasons.append("new category exploration")

    return reasons