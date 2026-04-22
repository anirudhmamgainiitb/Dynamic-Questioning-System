import json
from collections import defaultdict
import numpy as np
from sentence_transformers import SentenceTransformer

RAW_PATH = "data/raw/question_bank_raw.jsonl"
VALID_PATH = "data/processed/question_bank_validated.jsonl"
REJECT_PATH = "data/processed/rejected_questions.jsonl"

SIMILARITY_THRESHOLD = 0.9  # cosine similarity

# -----------------------------
# Load embedding model (global)
# -----------------------------
model = SentenceTransformer('all-MiniLM-L6-v2')


# -----------------------------
# 1. Load JSONL
# -----------------------------
def load_jsonl(path):
    data = []
    with open(path, "r") as f:
        for line in f:
            data.append(json.loads(line))
    return data


# -----------------------------
# 2. Text Normalization
# -----------------------------
def normalize(text):
    return " ".join(text.lower().strip().split())


# -----------------------------
# 3. Schema Validation
# -----------------------------
REQUIRED_KEYS = ["id", "text", "question_field", "priority", "triggers", "targets"]

def validate_schema(q):
    for key in REQUIRED_KEYS:
        if key not in q:
            return False, f"Missing key: {key}"

    if not isinstance(q["priority"], int) or not (1 <= q["priority"] <= 5):
        return False, "Invalid priority"

    if not isinstance(q["triggers"], dict):
        return False, "Triggers must be dict"

    if "fill_fields" not in q["targets"]:
        return False, "Missing targets.fill_fields"

    return True, None


# -----------------------------
# 4. Logical Validation
# -----------------------------
def validate_logic(q):
    field = q["question_field"]
    targets = q["targets"]["fill_fields"]
    triggers = q["triggers"]
    text = q["text"]

    # Field-target alignment
    if field not in targets:
        return False, "Field-target mismatch"

    # Trigger format
    if "incident_type" in triggers:
        if not isinstance(triggers["incident_type"], list):
            return False, "incident_type must be list"

    # Text quality
    if len(text.strip()) < 10:
        return False, "Text too short"

    # Basic sanity
    if "??" in text or text.count("?") > 2:
        return False, "Malformed question"

    return True, None


# -----------------------------
# 5. Semantic Deduplication
# -----------------------------
def deduplicate(questions):
    unique = []
    rejected = []

    # Normalize texts
    texts = [normalize(q["text"]) for q in questions]

    # Compute embeddings
    embeddings = model.encode(texts, convert_to_numpy=True)

    used = set()

    for i in range(len(questions)):
        if i in used:
            continue

        q1 = questions[i]
        emb1 = embeddings[i]

        unique.append(q1)

        for j in range(i + 1, len(questions)):
            if j in used:
                continue

            q2 = questions[j]

            # Only compare same field
            if q1["question_field"] != q2["question_field"]:
                continue

            emb2 = embeddings[j]

            # Cosine similarity
            sim = np.dot(emb1, emb2) / (
                np.linalg.norm(emb1) * np.linalg.norm(emb2)
            )

            if sim >= SIMILARITY_THRESHOLD:
                used.add(j)

                rejected.append({
                    **q2,
                    "reason": "Semantic duplicate",
                    "similarity_score": float(sim)
                })

    return unique, rejected


# -----------------------------
# 6. Coverage Check
# -----------------------------
def coverage_check(questions):
    category_counts = defaultdict(int)

    for q in questions:
        category = q["question_field"].split(".")[0]
        category_counts[category] += 1

    return dict(category_counts)


# -----------------------------
# 7. Validation Pipeline
# -----------------------------
def validate_questions(raw_questions):
    valid = []
    rejected = []

    for q in raw_questions:

        # Schema
        ok, reason = validate_schema(q)
        if not ok:
            rejected.append({**q, "reason": reason})
            continue

        # Logic
        ok, reason = validate_logic(q)
        if not ok:
            rejected.append({**q, "reason": reason})
            continue

        valid.append(q)

    return valid, rejected


# -----------------------------
# 8. Save JSONL
# -----------------------------
def save_jsonl(data, path):
    with open(path, "w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")


# -----------------------------
# 9. Run Pipeline
# -----------------------------
if __name__ == "__main__":

    raw_questions = load_jsonl(RAW_PATH)
    print(f"Loaded {len(raw_questions)} raw questions")

    # Step 1: Schema + Logic
    valid, rejected = validate_questions(raw_questions)
    print(f"After validation: {len(valid)} valid, {len(rejected)} rejected")

    # Step 2: Semantic Deduplication
    valid, duplicate_rejected = deduplicate(valid)

    print(f"After deduplication: {len(valid)}")
    print(f"Semantic duplicates removed: {len(duplicate_rejected)}")

    rejected.extend(duplicate_rejected)

    # Step 3: Coverage
    coverage = coverage_check(valid)
    print("Coverage:", coverage)

    # Step 4: Save outputs
    save_jsonl(valid, VALID_PATH)
    save_jsonl(rejected, REJECT_PATH)

    print("✅ Validation complete")