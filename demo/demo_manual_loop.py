import json
from datetime import datetime

from src.termination.termination_policy import should_terminate
from src.state.state_updater import update_state
from src.retriever.retriever import get_next_question


# -----------------------------
# Load question bank
# -----------------------------
def load_questions(path):
    questions = []
    with open(path, "r") as f:
        for line in f:
            questions.append(json.loads(line))
    return questions


# -----------------------------
# Initialize state
# -----------------------------
def init_state():
    return {
        "incident_type": None,
        "loss_datetime": None,
        "loss_location": {"city": None, "road_type": None},
        "third_party": {"involved": None, "vehicle_id": None},
        "legal_reporting": {"police_report_filed": None},

        # 🔥 REQUIRED for retriever
        "asked_fields": set(),
        "answered_fields": set(),
        "recent_fields": [],

        "meta": {
            "answered_question_ids": [],
            "already_extracted_categories": []
        }
    }


# -----------------------------
# Safe JSON serialization
# -----------------------------
def serialize_state(state):
    serialized = {}

    for k, v in state.items():
        if isinstance(v, set):
            serialized[k] = list(v)
        elif isinstance(v, dict):
            serialized[k] = serialize_state(v)
        else:
            serialized[k] = v

    return serialized


# -----------------------------
# Logging
# -----------------------------
def log_turn(turn_id, state, question):
    log = {
        "turn": turn_id,
        "state": serialize_state(state),  # 🔥 fix
        "question": question,
        "timestamp": str(datetime.now())
    }

    with open(f"logs/sample_runs/turn_{turn_id}.json", "w") as f:
        json.dump(log, f, indent=2)


# -----------------------------
# Main Loop
# -----------------------------
def run_demo():

    question_bank = load_questions("data/processed/question_bank_validated.jsonl")

    state = init_state()

    print("\n🚗 Insurance Claim Assistant\n")

    turn = 1
    last_question = None  # 🔥 important

    while True:

        user_input = input("\n👤 You: ")

        # -----------------------------
        # Step 1: Update state
        # -----------------------------
        state = update_state(state, user_input, last_question)

        # -----------------------------
        # Step 2: Retrieve next question
        # -----------------------------
        question = get_next_question(state, question_bank)

        # -----------------------------
        # Step 3: Termination check
        # -----------------------------
        stop, reason = should_terminate(state, question,turn)
        if stop:
            print(f"\n✅ Conversation ended: {reason}")
            break

        # -----------------------------
        # Step 4: Show question
        # -----------------------------
        print(f"\n🤖 Next Question: {question['question_text']}")

        # -----------------------------
        # Step 5: Track answered question
        # -----------------------------
        state["meta"]["answered_question_ids"].append(question["question_id"])

        # -----------------------------
        # Step 6: Log turn
        # -----------------------------
        log_turn(turn, state, question)

        # -----------------------------
        # Step 7: Update last question
        # -----------------------------
        last_question = question

        turn += 1


if __name__ == "__main__":
    run_demo()