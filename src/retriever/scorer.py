from src.utils.state_utils import get_nested


# -----------------------------
# 1. PRIORITY SCORE
# -----------------------------
def compute_priority_score(priority):
    return (6 - priority) / 5  # 1 → 1.0, 5 → 0.2


# -----------------------------
# 2. GAP SCORE (unchanged)
# -----------------------------
def compute_gap_score(question, state):
    missing = 0

    for field in question["targets"]["fill_fields"]:
        if get_nested(state, field) is None:
            missing += 1

    return missing / len(question["targets"]["fill_fields"])


# -----------------------------
# 3. RELEVANCE SCORE (unchanged)
# -----------------------------
def compute_relevance(question, state):
    score = 0
    triggers = question.get("triggers", {})

    if "incident_type" in triggers:
        if state.get("incident_type") in triggers["incident_type"]:
            score += 1

    if "third_party_involved" in triggers:
        if state.get("third_party", {}).get("involved") == triggers["third_party_involved"]:
            score += 1

    return score / (len(triggers) + 1e-5)


# -----------------------------
# 4. REPETITION PENALTY (NEW)
# -----------------------------
def compute_repetition_penalty(question, state):
    field = question["question_field"]

    asked = state.get("asked_fields", set())
    answered = state.get("answered_fields", set())

    if field in answered:
        return -1.0   # very strong penalty

    if field in asked:
        return -0.6   # strong penalty

    return 0.0


# -----------------------------
# 5. INFORMATION GAIN (NEW)
# -----------------------------
def compute_information_gain(question, state):
    field = question["question_field"]
    category = field.split(".")[0]

    extracted = state.get("meta", {}).get("already_extracted_categories", [])

    if category not in extracted:
        return 1.0   # new category → strong boost

    return 0.0


# -----------------------------
# 6. FINAL SCORER
# -----------------------------
def score_question(question, state):

    p = compute_priority_score(question["priority"])
    g = compute_gap_score(question, state)
    r = compute_relevance(question, state)

    rep = compute_repetition_penalty(question, state)
    info = compute_information_gain(question, state)

    final_score = (
        0.3 * p +
        0.25 * r +
        0.25 * g +
        0.15 * info +
        0.3 * rep   # penalty (negative)
    )

    return {
        "priority": p,
        "relevance": r,
        "gap": g,
        "info_gain": info,
        "repetition_penalty": rep,
        "final": final_score
    }