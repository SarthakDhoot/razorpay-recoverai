def calculate_recovery_opportunity(
    amount,
    recovery_probability
):
    """
    Calculate estimated revenue
    that could potentially be recovered.
    """

    opportunity = (
        amount * recovery_probability / 100
    )

    return round(opportunity, 2)


def calculate_total_opportunity(payments):
    """
    Calculate total potential recovery
    across failed payments.
    """

    total_opportunity = 0

    for payment in payments:

        opportunity = calculate_recovery_opportunity(
            payment["amount"],
            payment["recovery_probability"]
        )

        total_opportunity += opportunity

    return round(total_opportunity, 2)