def get_nested(state, field_path):
    """
    Safely access nested dictionary fields using dot notation.

    Example:
    field_path = "third_party.vehicle_id"
    """

    keys = field_path.split(".")
    value = state

    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None

    return value


def has_nested(state, field_path):
    return get_nested(state, field_path) is not None


def set_nested(state, field_path, value):
    keys = field_path.split(".")
    d = state

    for key in keys[:-1]:
        if key not in d or not isinstance(d[key], dict):
            d[key] = {}
        d = d[key]

    d[keys[-1]] = value