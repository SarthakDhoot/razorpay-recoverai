def start_recovery(payment_id):
    """
    Start a recovery attempt for a payment.
    """

    return {
        "payment_id": payment_id,
        "status": "Recovery Attempted"
    }


def mark_recovered(payment_id):
    """
    Mark a payment as successfully recovered.
    """

    return {
        "payment_id": payment_id,
        "status": "Recovered"
    }