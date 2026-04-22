# Priority Policy — Dynamic Questioning System (Vehicle Insurance)

## 1. Objective

This document defines the **decision-making policy** used to select the next best question in a vehicle insurance claim intake system.

The goal is to:

* Maximize **information gain per question**
* Ensure **logical and domain-consistent questioning**
* Avoid **redundancy and irrelevant questions**
* Maintain **auditability and determinism**

---

## 2. Core Principles

### 2.1 Deterministic Decision Making

The system must produce the **same next question** for the same input state.

### 2.2 State-Driven Behavior

All decisions depend solely on:

* Current `claim_state`
* Question metadata (triggers, targets, priority)

### 2.3 No Redundancy

A question must **never be asked** if:

* Its target field is already filled
* It has already been asked

### 2.4 Progressive Information Gathering

Questions must follow a logical flow:

1. Understand incident
2. Validate eligibility
3. Assess damage
4. Collect supporting data

---

## 3. Priority Levels

Each question is assigned a priority (1–5):

| Priority | Meaning                                                         |
| -------- | --------------------------------------------------------------- |
| 1        | Critical blockers (legal, eligibility, incident classification) |
| 2        | Core incident understanding                                     |
| 3        | Damage and impact assessment                                    |
| 4        | Documentation and enrichment                                    |
| 5        | Optional or low-value questions                                 |

Lower number = higher priority.

---

## 4. Decision Rules (Ordered)

The system follows these rules in order.

---

### Rule 1 — Incident Classification First

**Fields:**

* `incident_type`
* `sub_incident_type`

**Policy:**

* Must be identified before any downstream questioning

**Reasoning:**

* Drives all trigger logic
* Prevents irrelevant question branches

---

### Rule 2 — Temporal & Location Context

**Fields:**

* `loss_datetime`
* `loss_location.city`
* `loss_location.road_type`

**Policy:**

* Must be collected early (Priority 1–2)

**Reasoning:**

* Required for validation
* Used in trigger conditions
* Supports fraud detection

---

### Rule 3 — Third-Party Involvement Gate

**Field:**

* `third_party.involved`

**Policy:**

* Must be resolved early

**Branching:**

* If `true` → enable third-party questions
* If `false` → suppress all third-party questions

**Reasoning:**

* Major branching condition
* Avoids irrelevant questioning

---

### Rule 4 — Legal & Compliance Requirements

**Fields:**

* `legal_reporting.police_report_filed`
* `legal_reporting.report_number`

**Policy:**

* Ask early if applicable

**Reasoning:**

* Required for claim processing
* Legal dependency

---

### Rule 5 — Policy & Eligibility Gates

**Fields:**

* `policy.policy_active`
* `policy.driver_is_owner`
* `policy.usage_type`

**Policy:**

* Must be resolved before deep questioning

**Reasoning:**

* Determines claim validity
* Prevents unnecessary data collection

---

### Rule 6 — Incident Dynamics

**Fields:**

* `incident_details.moving_or_parked`
* `incident_details.speed_estimate`
* `incident_details.impact_direction`
* `incident_details.weather_conditions`

**Policy:**

* Ask after basic classification

**Reasoning:**

* Provides context for damage assessment
* Supports consistency checks

---

### Rule 7 — Damage Assessment

**Fields:**

* `damage_assessment.damage_areas`
* `damage_assessment.damage_severity`
* `damage_assessment.airbags_deployed`

**Policy:**

* Ask after incident context is known

**Reasoning:**

* Dependent on incident type
* High importance for claim estimation

---

### Rule 8 — Third-Party Details (Conditional)

**Condition:**

* `third_party.involved == true`

**Fields:**

* `third_party.vehicle_id`
* `third_party.driver_details`
* `third_party.insurance_known`

**Policy:**

* Only ask if applicable

**Reasoning:**

* Avoid irrelevant questions
* Required for liability determination

---

### Rule 9 — Documentation & Evidence

**Fields:**

* `documentation.photos_available`
* `documentation.videos_available`
* `documentation.repair_estimate_available`

**Policy:**

* Lower priority (after core info)

**Reasoning:**

* Supports claim processing but not foundational

---

### Rule 10 — Repair & Settlement Preferences

**Fields:**

* `repair_preferences.preferred_workshop`
* `repair_preferences.cashless`
* `repair_preferences.towing_required`

**Policy:**

* Ask toward the end

**Reasoning:**

* Only relevant after damage is known

---

### Rule 11 — Fraud & Consistency Checks

**Fields:**

* `fraud_signals.*`

**Policy:**

* Trigger early if anomalies detected

**Examples:**

* Timeline inconsistencies
* Missing critical fields with high detail elsewhere

**Reasoning:**

* High business importance
* Must not be delayed

---

### Rule 12 — Suppression Rule (Strict)

A question must NOT be asked if:

* Target field is already filled
* Question ID exists in `answered_question_ids`
* Category exists in `already_extracted_categories`

---

### Rule 13 — Dependency Enforcement

A question requiring certain fields must not be asked unless:

```python
required_fields_present ⊆ known_fields
```

---

### Rule 14 — Gap Maximization

Prefer questions that:

* Fill **maximum missing critical fields**
* Reduce uncertainty in state

---

## 5. Scoring Interpretation

Final question selection is based on:

* Priority (from this policy)
* Trigger relevance
* Gap-filling potential

Higher-ranked questions:

* Address critical missing fields
* Match current state strongly
* Follow logical progression

---

## 6. Conflict Resolution

If multiple questions are eligible:

1. Select highest priority
2. If tie → select highest relevance
3. If tie → select highest gap coverage
4. If tie → deterministic ordering (e.g., question_id)

---

## 7. Termination Alignment

Questioning should stop when:

* All critical fields are filled OR
* No high-priority questions remain OR
* Additional questions provide minimal value

---

## 8. Summary

This policy ensures:

* Structured and logical questioning
* Full determinism and auditability
* Efficient information collection
* Domain-aligned decision making

---
