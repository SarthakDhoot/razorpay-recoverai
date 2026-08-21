import os
from dotenv import load_dotenv
from openai import OpenAI


# ============================================
# LOAD ENVIRONMENT VARIABLES
# ============================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")


# ============================================
# HELPER: CREATE OPENAI CLIENT
# ============================================

def get_client():
    if not api_key:
        return None

    return OpenAI(api_key=api_key)


# ============================================
# AI RECOVERY STRATEGY
# ============================================

def generate_ai_strategy(
    customer_name,
    amount,
    failure_reason,
    payment_method,
    recovery_probability,
    priority
):
    """
    Generate an AI-powered payment recovery strategy.
    """

    client = get_client()

    # Fallback if API key is missing
    if client is None:
        return {
            "strategy": (
                "Retry payment using an alternative payment method."
            ),
            "message": (
                f"Hi {customer_name}, your payment of "
                f"₹{amount:,.0f} could not be completed. "
                f"Please try again using another payment method."
            ),
            "reason": (
                "AI API key was not found. "
                "Fallback recovery strategy was used."
            )
        }

    try:

        prompt = f"""
You are RecoverAI's payment recovery assistant.

Analyze this failed payment:

Customer: {customer_name}
Amount: ₹{amount}
Failure reason: {failure_reason}
Payment method: {payment_method}
Recovery probability: {recovery_probability}%
Priority: {priority}

Create a concise recovery strategy.

Return exactly three sections:

STRATEGY:
The best action to recover this payment.

MESSAGE:
A short and polite customer-facing payment recovery message.

REASON:
Why this strategy is appropriate.

Do not invent customer information.
Do not mention that you are an AI.
"""

        response = client.responses.create(
            model="gpt-5-mini",
            input=prompt
        )

        result = response.output_text

        return {
            "strategy": result,
            "message": result,
            "reason": (
                "Strategy generated using the OpenAI model."
            )
        }

    except Exception as error:

        return {
            "strategy": (
                "Retry the payment using an alternative "
                "payment method."
            ),
            "message": (
                f"Hi {customer_name}, your payment of "
                f"₹{amount:,.0f} could not be completed. "
                f"Please try again using another payment method."
            ),
            "reason": f"AI fallback used: {error}"
        }


# ============================================
# AI DECISION ENGINE
# ============================================

def generate_ai_decision(
    customer_name,
    amount,
    failure_reason,
    payment_method,
    recovery_probability,
    priority,
    potential_recovery
):
    """
    Generate an AI-powered recovery decision.
    """

    client = get_client()

    # Fallback if API key is missing
    if client is None:
        return {
            "decision": "Retry payment",
            "why": (
                "The payment has recovery potential "
                "and should be retried."
            ),
            "action": (
                "Retry using an alternative payment method."
            ),
            "timing": "Within 24 hours"
        }

    try:

        prompt = f"""
You are RecoverAI's AI Revenue Recovery Decision Engine.

Your job is to decide the best action for a failed payment.

Payment information:

Customer: {customer_name}
Amount: ₹{amount}
Failure Reason: {failure_reason}
Payment Method: {payment_method}
Recovery Probability: {recovery_probability}%
Priority: {priority}
Potential Recovery: ₹{potential_recovery}

Choose the best recovery action.

Possible actions:

- Retry payment
- Request alternative payment method
- Send payment reminder
- Contact customer
- Wait and retry later

Return exactly these four sections:

DECISION:
Give ONE recommended action.

WHY:
Give 2-3 short reasons based only on the provided payment data.

ACTION:
Give a clear operational action for the business.

TIMING:
Recommend when the action should happen.

Do not invent customer information.
Do not mention that you are an AI.
"""

        response = client.responses.create(
            model="gpt-5-mini",
            input=prompt
        )

        result = response.output_text

        return {
            "decision": result,
            "why": (
                "Decision generated from payment risk, "
                "failure reason, recovery probability, "
                "and potential recovery."
            ),
            "action": (
                "Follow the recommended recovery action."
            ),
            "timing": (
                "Based on the AI recommendation."
            )
        }

    except Exception as error:

        return {
            "decision": "Retry payment",
            "why": (
                "The payment has recovery potential "
                "and should be retried."
            ),
            "action": (
                "Retry the payment using an alternative "
                "payment method."
            ),
            "timing": "Within 24 hours"
        }