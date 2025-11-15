"""Validators - Input-Validierung."""
from typing import Optional


def validate_positive_integer(value: str, default: int = 0, min_value: int = 0, max_value: Optional[int] = None) -> int:
    """
    Validiert einen String als positive Ganzzahl.

    Args:
        value: String-Wert
        default: Default-Wert wenn ungültig
        min_value: Minimaler Wert
        max_value: Maximaler Wert (None = kein Maximum)

    Returns:
        Validierter Integer-Wert
    """
    try:
        int_value = int(value)
        if int_value < min_value:
            return min_value
        if max_value is not None and int_value > max_value:
            return max_value
        return int_value
    except (ValueError, TypeError):
        return default


def validate_interval_component(value: str, component_type: str) -> int:
    """
    Validiert eine Intervall-Komponente (hours, minutes, seconds, milliseconds).

    Args:
        value: String-Wert
        component_type: "hours", "minutes", "seconds" oder "milliseconds"

    Returns:
        Validierter Integer-Wert
    """
    defaults = {
        "hours": 0,
        "minutes": 0,
        "seconds": 0,
        "milliseconds": 0
    }
    
    max_values = {
        "hours": 23,
        "minutes": 59,
        "seconds": 59,
        "milliseconds": 999
    }

    default = defaults.get(component_type, 0)
    max_value = max_values.get(component_type, None)

    return validate_positive_integer(value, default, min_value=0, max_value=max_value)

