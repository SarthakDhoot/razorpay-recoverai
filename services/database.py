import os

from dotenv import load_dotenv
from supabase import create_client


# Load .env
load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL is missing from .env")

if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY is missing from .env")


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


def save_recovery_action(
    payment_id,
    action,
    status="attempted"
):
    """Save a recovery action to Supabase."""

    response = supabase.table(
        "recovery_actions"
    ).insert({
        "payment_id": str(payment_id),
        "action": action,
        "status": status
    }).execute()

    return response


def get_recovery_actions():
    """Get all recovery actions from Supabase."""

    response = supabase.table(
        "recovery_actions"
    ).select("*").order(
        "created_at",
        desc=True
    ).execute()

    return response.data


def mark_payment_recovered(payment_id):
    """Mark a payment as recovered."""

    response = supabase.table(
        "recovery_actions"
    ).insert({
        "payment_id": str(payment_id),
        "action": "Payment recovered",
        "status": "recovered"
    }).execute()

    return response