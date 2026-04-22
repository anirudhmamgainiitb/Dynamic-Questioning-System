import json
from src.retriever.retriever import get_next_question

def run_tests():

    with open("data/test_cases/test_cases.json") as f:
        test_cases = json.load(f)

    with open("data/processed/question_bank_validated.jsonl") as f:
        question_bank = [json.loads(line) for line in f]

    for case in test_cases:

        print(f"\nRunning {case['case_id']}")

        state = case["claim_state"]

        result = get_next_question(state, question_bank)

        # Check expected next question
        if case.get("expected_next_question"):
            expected_field = case["expected_next_question"]["question_field"]

            assert result["question_field"] == expected_field, \
                f"Expected {expected_field}, got {result['question_field']}"

        # Check forbidden questions
        if "expected_non_questions" in case:
            forbidden = case["expected_non_questions"]

            assert result["question_field"] not in forbidden, \
                f"Forbidden question asked: {result['question_field']}"

        print("✅ Passed")

if __name__ == "__main__":
    run_tests()