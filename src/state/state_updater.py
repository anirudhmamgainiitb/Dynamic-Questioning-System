from src.utils.state_utils import set_nested
from src.extraction.extractor import (
    extract_datetime,
    extract_location,
    extract_incident_type,
    extract_third_party,
    extract_registration,
    extract_police,
    extract_speed,
    extract_yes_no
)


# -----------------------------
# MAIN STATE UPDATE
# -----------------------------
def update_state(state, user_input, last_question=None):
    updates = {}

    # -------------------------
    # Extract signals
    # -------------------------
    dt = extract_datetime(user_input)
    loc = extract_location(user_input)
    tp = extract_third_party(user_input)
    reg = extract_registration(user_input)
    police = extract_police(user_input)
    incident = extract_incident_type(user_input)
    speed = extract_speed(user_input)
    yes_no = extract_yes_no(user_input)

    # -------------------------
    # Assign extracted values
    # -------------------------
    if dt:
        updates["loss_datetime"] = dt

    if loc:
        updates["loss_location"] = loc

    if tp is not None:
        updates["third_party.involved"] = tp

    if reg:
        updates["third_party.vehicle_id"] = reg

    if police is not None:
        updates["legal_reporting.police_report_filed"] = police

    if incident:
        updates["incident_type"] = incident

    if speed:
        updates["incident_details.speed_estimate"] = speed

    # -------------------------
    # YES/NO fallback (SAFE)
    # -------------------------
    if yes_no is not None and last_question:
        field = last_question["question_field"]

        # apply only if field not already extracted
        if field not in updates:
            updates[field] = yes_no

    # -------------------------
    # Apply updates
    # -------------------------
    for field, value in updates.items():
        set_nested(state, field, value)

    # -------------------------
    # TRACK FIELDS
    # -------------------------
    if last_question:
        field = last_question["question_field"]

        state.setdefault("asked_fields", set()).add(field)
        state.setdefault("answered_fields", set()).add(field)

    # -------------------------
    # Track categories
    # -------------------------
    state.setdefault("meta", {})
    state["meta"].setdefault("already_extracted_categories", [])

    for field in updates:
        category = field.split(".")[0]

        if category not in state["meta"]["already_extracted_categories"]:
            state["meta"]["already_extracted_categories"].append(category)

    return state