def assign_priority(
    recovery_probability,
    potential_recovery
):
    """
    Assign a priority level based on
    recovery probability and potential revenue.
    """

    if (
        recovery_probability >= 75
        and potential_recovery >= 5000
    ):
        return "HIGH"

    elif (
        recovery_probability >= 60
        or potential_recovery >= 3000
    ):
        return "MEDIUM"

    else:
        return "LOW"


def priority_score(
    recovery_probability,
    potential_recovery
):
    """
    Calculate a combined score for
    ranking failed payments.
    """

    score = (
        recovery_probability * 0.6
        + min(potential_recovery / 100, 100) * 0.4
    )

    return round(score, 2)