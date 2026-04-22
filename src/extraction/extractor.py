import re
from datetime import datetime, timedelta


# -----------------------------
# GENERIC YES/NO
# -----------------------------
def extract_yes_no(text):
    text = text.lower()

    if any(x in text for x in ["yes", "yeah", "yep"]):
        return True

    if any(x in text for x in ["no", "not", "none"]):
        return False

    return None


# -----------------------------
# DATETIME
# -----------------------------
def extract_datetime(text):
    text = text.lower()

    if "today" in text:
        return datetime.today().strftime("%Y-%m-%d")

    if "yesterday" in text:
        return (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    return None


# -----------------------------
# LOCATION
# -----------------------------
def extract_location(text):
    cities = ["pune", "mumbai", "delhi", "bangalore"]

    for city in cities:
        if city in text.lower():
            return {"city": city.capitalize()}

    return None


# -----------------------------
# INCIDENT TYPE
# -----------------------------
def extract_incident_type(text):
    text = text.lower()

    if "accident" in text or "collision" in text:
        return "collision"

    if "fire" in text:
        return "fire"

    if "theft" in text:
        return "theft"

    return None


# -----------------------------
# THIRD PARTY
# -----------------------------
def extract_third_party(text):
    text = text.lower()

    if "no other vehicle" in text or "hit a wall" in text:
        return False

    if "bike" in text or "car" in text or "truck" in text:
        return True

    return None


# -----------------------------
# REGISTRATION
# -----------------------------
def extract_registration(text):
    match = re.search(r"[A-Z]{2}\d{2}[A-Z]{2}\d{4}", text.upper())
    if match:
        return match.group()
    return None


# -----------------------------
# POLICE
# -----------------------------
def extract_police(text):
    text = text.lower()

    if "no police" in text:
        return False

    if "police report" in text or "fir" in text:
        return True

    return None


# -----------------------------
# SPEED (FIX FOR YOUR BUG)
# -----------------------------
def extract_speed(text):
    text = text.lower()

    match = re.search(r"\b(\d{1,3})\b", text)

    if match:
        speed = int(match.group())

        if speed <= 20:
            return "0-20"
        elif speed <= 40:
            return "20-40"
        elif speed <= 60:
            return "40-60"
        else:
            return "60+"

    return None