# -----------------------------
# FILTER MODULE
# -----------------------------

def check_triggers(question, state):
    """
    Check if a question satisfies trigger conditions.
    """

    triggers = question.get("triggers", {})

    for key, value in triggers.items():

        # If state doesn't have the key → cannot satisfy trigger
        if key not in state:
            return False

        state_value = state[key]

        # If trigger expects list (e.g., incident_type)
        if isinstance(value, list):
            if state_value not in value:
                return False

        # If trigger expects exact match
        else:
            if state_value != value:
                return False

    return True


# -----------------------------
# MAIN FILTER FUNCTION
# -----------------------------

def filter_questions(questions, state):
    """
    Filters questions based on:
    1. Trigger conditions
    2. Already answered fields
    3. Already asked fields
    """

    filtered = []

    asked_fields = state.get("asked_fields", set())
    answered_fields = state.get("answered_fields", set())

    for q in questions:

        field = q.get("question_field")

        # -----------------------------
        # 1. Skip already answered
        # -----------------------------
        if field in answered_fields:
            continue

        # -----------------------------
        # 2. Skip already asked
        # -----------------------------
        if field in asked_fields:
            continue

        # -----------------------------
        # 3. Check triggers
        # -----------------------------
        if not check_triggers(q, state):
            continue

        # -----------------------------
        # 4. Basic sanity check
        # -----------------------------
        if not q.get("text") or len(q["text"].strip()) < 5:
            continue

        filtered.append(q)

    return filtered