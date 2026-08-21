def calculate_recovery_score(payment):
    """
    Calculate a recovery probability for a failed payment.
    """

    score = 50

    failure_reason = str(
        payment.get("failure_reason", "")
    ).lower()

    payment_method = str(
        payment.get("payment_method", "")
    ).lower()

    recovery_status = str(
        payment.get("recovery_status", "")
    ).lower()

    # Failure reason analysis
    if "timeout" in failure_reason:
        score += 15

    elif "insufficient" in failure_reason:
        score += 10

    elif "declined" in failure_reason:
        score += 5

    elif "expired" in failure_reason:
        score += 8

    # Payment method analysis
    if payment_method == "upi":
        score += 10

    elif payment_method == "credit card":
        score += 5

    # Recovery status
    if recovery_status == "contacted":
        score += 5

    elif recovery_status == "recovered":
        score = 95

    # Keep score between 0 and 100
    score = max(0, min(score, 100))

    return score


def get_priority(score):
    """
    Convert recovery score into a priority level.
    """

    if score >= 75:
        return "HIGH"

    elif score >= 50:
        return "MEDIUM"

    else:
        return "LOW"


def get_recommended_action(payment, score):
    """
    Recommend the best recovery action.
    """

    failure_reason = str(
        payment.get("failure_reason", "")
    ).lower()

    if "insufficient" in failure_reason:
        return "Ask customer to retry with another payment method."

    if "declined" in failure_reason:
        return "Ask customer to retry using another card."

    if "expired" in failure_reason:
        return "Ask customer to update their card details."

    if "timeout" in failure_reason:
        return "Ask customer to retry the payment."

    return "Send a payment recovery reminder."


def generate_recovery_message(payment):
    """
    Generate a personalized recovery message.
    """

    customer = payment.get(
        "customer_name",
        "Customer"
    )

    amount = payment.get(
        "amount",
        0
    )

    return (
        f"Hi {customer}, your recent payment of "
        f"₹{amount:,.0f} could not be completed. "
        f"Please try the payment again using another "
        f"payment method. If you need any help, "
        f"we're here to assist you."
    )