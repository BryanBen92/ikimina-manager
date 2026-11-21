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


def issue_loan(member_id, amount):
    """
    Issue a new loan to a member after verifying eligibility.

    This function checks that the member has borrowing capacity and creates
    a new loan record with calculated interest and due date.

    Args:
        member_id: The ID of the member to receive the loan.
        amount: The principal loan amount requested (must be positive).

    Returns:
        tuple: A 3-tuple containing:
            - loan_id: The new loan's primary key.
            - total_due: The total amount due including interest.
            - due_date: The date when repayment is due (ISO string YYYY-MM-DD).

    Raises:
        ValueError: If the loan amount is not positive or exceeds the
                     member's available borrowing limit.
    """
    # Verify requested amount is positive
    if amount <= 0:
        raise ValueError(
            f"Loan amount must be positive, got {amount}. "
            "Please provide a valid positive principal amount."
        )

    # Get interest rate and loan duration from settings
    interest_rate_percent = get_setting("interest_rate_percent")
    loan_days = get_setting("loan_days")

    if interest_rate_percent is None:
        raise ValueError(
            "Interest rate percent is not configured. "
            "Please consult the treasurer to set this value."
        )

    if loan_days is None:
        raise ValueError(
            "Loan duration in days is not configured. "
            "Please consult the treasurer to set this value."
        )

    # Calculate interest and total due
    interest = amount * interest_rate_percent / 100
    total_due = amount + interest

    # Calculate due date (today + loan_days)
    today = date.today()
    due_date = today + timedelta(days=loan_days)
    due_date_str = due_date.isoformat()

    # Check if member is eligible for the requested amount
    available_limit = max_loan_allowed(member_id)
    if amount > available_limit:
        raise ValueError(
            f"Requested loan amount of {amount} exceeds available limit "
            f"of {available_limit:.2f}. "
            "Member may need to increase savings or reduce other outstanding loans."
        )

    # Insert the new loan record
    conn = get_connection()
    query = """
        INSERT INTO loans (member_id, amount, interest, total_due, amount_paid, issue_date, due_date, status)
        VALUES (?, ?, ?, ?, 0, ?, ?)
    """
    today_str = today.isoformat()

    try:
        cursor = conn.execute(
            query,
            (
                member_id,
                amount,
                interest,
                total_due,
                today_str,
                due_date_str,
                "active"
            )
        )
        loan_id = cursor.lastrowid

        # Save changes to database
        conn.commit()

        return (loan_id, total_due, due_date_str)

    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Failed to create loan: {e}")
    finally:
        conn.close()
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
