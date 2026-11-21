"""Loans and repayments module for Ikimina Manager.

This module handles:
- Calculating maximum loan limits based on member savings
- Issuing new loans with interest calculations
- Recording repayments and updating loan status
- Listing active and overdue loans
"""

from datetime import date, timedelta

from fadhiri.db import get_connection, get_setting
from benjamin_mugisha.contributions import member_savings


def max_loan_allowed(member_id):
    """
    Calculate the maximum amount a member can borrow.

    The borrowing limit is determined by:
        1. Getting total savings from the member's contributions
        2. Multiplying by loan_limit_multiplier setting
        3. Subtracting any outstanding balance from active loans

    Args:
        member_id: The ID of the member to check.

    Returns:
        float: The remaining amount the member can still borrow.

    Raises:
        ValueError: If loan_limit_multiplier setting is not configured.
        sqlite3.Error: If database operation fails.
    """
    # Get the loan limit multiplier from settings
    loan_limit_multiplier = get_setting("loan_limit_multiplier")
    if loan_limit_multiplier is None:
        raise ValueError(
            "Loan limit multiplier is not configured. "
            "Please consult the treasurer to set this value."
        )

    # Get member's total savings from contributions
    total_savings = member_savings(member_id)

    # Calculate maximum loan based on savings and multiplier
    max_loan = total_savings * loan_limit_multiplier

    # Get outstanding balance from active loans
    conn = get_connection()
    query = """
        SELECT SUM(total_due - amount_paid) as outstanding_balance
        FROM loans
        WHERE member_id = ? AND status = 'active'
    """
    result = conn.execute(query, (member_id,)).fetchone()
    conn.close()

    # Outstanding balance is 0 if no active loans exist
    outstanding_balance = result["outstanding_balance"] if result else 0.0

    # Calculate remaining amount available to borrow
    remaining = max_loan - outstanding_balance

    return float(remaining)
