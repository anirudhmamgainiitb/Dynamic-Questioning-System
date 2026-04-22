from src.utils.state_utils import get_nested


CRITICAL_FIELDS = [
    "incident_type",
    "loss_datetime",
    "loss_location.city",
    "third_party.involved",
]


# -----------------------------
# COVERAGE
# -----------------------------
def compute_coverage(state):
    filled = 0

    for field in CRITICAL_FIELDS:
        if get_nested(state, field) is not None:
            filled += 1

    return filled / len(CRITICAL_FIELDS)


# -----------------------------
# TERMINATION POLICY
# -----------------------------
def should_terminate(state, next_question, turn_count, score=None):

    # -----------------------------
    # Rule 1: No valid questions
    # -----------------------------
    if next_question is None:
        return True, "No valid questions remaining"

    # -----------------------------
    # Rule 2: Critical coverage
    # -----------------------------
    coverage = compute_coverage(state)

    if coverage >= 0.75:   # 🔥 relaxed threshold
        return True, "Critical information collected"

    # -----------------------------
    # Rule 3: Low priority questions only
    # -----------------------------
    priority = next_question.get("priority", 3)  # 🔥 safe access

    if priority >= 4:
        return True, "Only low-priority questions remaining"

    # -----------------------------
    # Rule 4: Low information gain
    # -----------------------------
    if score is not None and score < 0.3:
        return True, "Low information gain"

    # -----------------------------
    # Rule 5: Max turns
    # -----------------------------
    if turn_count >= 15:
        return True, "Max turns reached"

    return False, None