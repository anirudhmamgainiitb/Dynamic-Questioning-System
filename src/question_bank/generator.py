import json
import itertools
import random
from uuid import uuid4
from collections import defaultdict

OUTPUT_PATH = "data/raw/question_bank_raw.jsonl"
DOMAIN_PATH = "/Users/anirudhmamgain/Documents/BIO/o-health/insurance-question-engine/schemas/domain_vocabularies.json"

random.seed(42)
STYLES = [
    "direct",
    "confirmation",
    "investigative",
    "conditional"
]

def apply_style(text, style):
    if style == "direct":
        return text
    elif style == "confirmation":
        return f"Can you confirm: {text}"
    elif style == "investigative":
        return f"Can you clarify whether {text.lower()}"
    elif style == "conditional":
        return f"If applicable, {text.lower()}"
    return text


CONTEXTS = [
    "",
    " during inspection",
    " at the accident site",
    " in the claim report"
]
# -----------------------------
# LOAD DOMAIN
# -----------------------------
with open(DOMAIN_PATH, "r") as f:
    DOMAIN = json.load(f)

# -----------------------------
# FIELD → DOMAIN MAP
# -----------------------------
FIELD_TO_DOMAIN = {
    "incident_details.weather_conditions": "weather_conditions",
    "incident_details.visibility": "visibility",
    "incident_details.speed_estimate": "speed_estimate",
    "damage_assessment.damage_areas": "damage_areas",
    "damage_assessment.damage_severity": "damage_severity",
    "policy.policy_type": "policy_types",
    "policy.usage_type": "usage_type",
    "loss_location.road_type": "road_types"
}

# -----------------------------
# CATEGORY DISTRIBUTION (~2000)
# -----------------------------
CATEGORY_DISTRIBUTION = {
    "third_party": 300,
    "damage": 350,
    "incident": 350,
    "legal": 250,
    "documentation": 250,
    "policy": 250,
    "repair": 200,
    "fraud": 200
}

# -----------------------------
# ENTITY DEFINITIONS
# -----------------------------
CATEGORY_ENTITIES = {
    "incident": [
        ("weather conditions", "incident_details.weather_conditions"),
        ("visibility", "incident_details.visibility"),
        ("speed at impact", "incident_details.speed_estimate"),
        ("road type", "loss_location.road_type"),
    ],
    "damage": [
        ("damage area", "damage_assessment.damage_areas"),
        ("damage severity", "damage_assessment.damage_severity"),
    ],
    "policy": [
        ("policy type", "policy.policy_type"),
        ("vehicle usage", "policy.usage_type"),
    ],
    "third_party": [
        ("third party involvement", "third_party.involved"),
        ("hit and run status", "third_party.hit_and_run")
    ],
    "legal": [
        ("police report", "legal_reporting.police_report_filed"),
        ("witness availability", "legal_reporting.witness_available")
    ],
    "documentation": [
        ("photos", "documentation.photos_available"),
        ("videos", "documentation.videos_available")
    ],
    "repair": [
        ("repair preference", "repair_preferences.cashless"),
    ],
    "fraud": [
        ("timeline consistency", "fraud_signals.inconsistent_timeline")
    ]
}

# -----------------------------
# CATEGORY-SPECIFIC TEMPLATES (IMPORTANT)
# -----------------------------
CATEGORY_TEMPLATES = {

    "damage": [
        "Was the {value} damaged?",
        "Did the {value} sustain impact?",
        "Is there visible damage on the {value}?",
        "Was the {value} affected in the incident?"
    ],

    "incident": [
        "Were the {entity} {value} during the incident?",
        "Did the incident occur under {value} {entity}?",
        "Were {value} conditions observed in {entity}?"
    ],

    "policy": [
        "Is the {entity} categorized as {value}?",
        "Does the policy fall under {value}?",
        "Is the {entity} set to {value}?"
    ],

    "third_party": [
        "Was there {value} in {entity}?",
        "Did the case involve {value} for {entity}?",
        "Is {entity} marked as {value}?"
    ],

    "legal": [
        "Was a {entity} filed?",
        "Is there a record of {entity}?",
        "Was the {entity} completed?"
    ],

    "documentation": [
        "Are {entity} available?",
        "Were {entity} captured during the incident?",
        "Do you have {entity} recorded?"
    ],

    "repair": [
        "Is {entity} set to {value}?",
        "Was {entity} requested?",
        "Does the repair include {entity}?"
    ],

    "fraud": [
        "Is there any indication of {entity}?",
        "Was {entity} detected in this claim?",
        "Does the claim show {entity}?"
    ]
}

# -----------------------------
# PRIORITY
# -----------------------------
CATEGORY_PRIORITY = {
    "legal": 1,
    "policy": 1,
    "incident": 2,
    "third_party": 2,
    "fraud": 2,
    "damage": 3,
    "documentation": 4,
    "repair": 5
}

# -----------------------------
# TRIGGERS
# -----------------------------
def build_triggers(category):
    if category == "third_party":
        return {"incident_type": ["collision"], "third_party_involved": True}
    elif category == "damage":
        return {"incident_type": ["collision", "fire", "flood"]}
    elif category == "incident":
        return {"incident_type": ["collision"]}
    elif category == "legal":
        return {"incident_type": ["collision", "theft"]}
    elif category == "repair":
        return {"incident_type": ["collision"]}
    return {}

# -----------------------------
# CREATE QUESTION
# -----------------------------
def create_question(text, field, category):
    return {
        "id": f"Q{str(uuid4())[:8]}",
        "text": text.strip(),
        "question_field": field,
        "priority": CATEGORY_PRIORITY[category],
        "triggers": build_triggers(category),
        "targets": {"fill_fields": [field]}
    }

# -----------------------------
# GENERATOR CORE (FIXED)
# -----------------------------
def generate_category_questions(category, target_count):
    questions = []
    entities = CATEGORY_ENTITIES[category]
    templates = CATEGORY_TEMPLATES.get(category, [])

    STYLES = ["direct", "confirmation", "investigative", "conditional"]
    CONTEXTS = ["", " during inspection", " at the accident site", " in the claim report"]

    all_combinations = []

    for entity, field in entities:

        # domain values
        if field in FIELD_TO_DOMAIN:
            domain_key = FIELD_TO_DOMAIN[field]
            values = [v for v in DOMAIN[domain_key] if v != "unknown"]
        else:
            values = ["yes", "no"]

        for value in values:
            for template in templates:
                for style in STYLES:
                    for context in CONTEXTS:
                        all_combinations.append((entity, field, value, template, style, context))

    import random
    random.shuffle(all_combinations)

    for entity, field, value, template, style, context in all_combinations:

        value_clean = value.replace("_", " ")

        try:
            base = template.format(entity=entity, value=value_clean)
        except:
            base = f"Can you provide details about {entity}?"

        text = apply_style(base, style) + context

        questions.append(create_question(text, field, category))

        if len(questions) >= target_count:
            break

    return questions

# -----------------------------
# MAIN
# -----------------------------
def generate_all_questions():
    all_questions = []

    for category, count in CATEGORY_DISTRIBUTION.items():
        q = generate_category_questions(category, count)
        all_questions.extend(q)

    return all_questions

# -----------------------------
# SAVE
# -----------------------------
def save_jsonl(questions):
    with open(OUTPUT_PATH, "w") as f:
        for q in questions:
            f.write(json.dumps(q) + "\n")

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    questions = generate_all_questions()
    save_jsonl(questions)

    print(f" Generated {len(questions)} questions")

    counts = defaultdict(int)
    for q in questions:
        counts[q["question_field"].split('.')[0]] += 1

    print(" Distribution:", dict(counts))