"""Loans and repayments module for Ikimina Manager."""

from datetime import date, timedelta

from database.db import get_connection, get_setting
from contributions.contributions import member_savings


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
        SELECT COALESCE(SUM(total_due - amount_paid), 0) as outstanding_balance
        FROM loans
        WHERE member_id = ? AND status = 'active'
    """
    result = conn.execute(query, (member_id,)).fetchone()
    conn.close()

    # Outstanding balance is 0 if no active loans exist
    outstanding_balance = float(result["outstanding_balance"]) if result else 0.0

    # Calculate remaining amount available to borrow
    remaining = max_loan - outstanding_balance

    return float(remaining)


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
        VALUES (?, ?, ?, ?, 0, ?, ?, ?)
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


def record_repayment(loan_id, amount):
    """
    Record a repayment for an existing active loan.

    This function validates the loan exists and is active, checks that
    the repayment amount doesn't exceed the outstanding balance, then
    saves the repayment and updates the loan's amount_paid. If the loan
    becomes fully paid, its status is updated to 'repaid'.

    Args:
        loan_id: The ID of the loan being repaid.
        amount: The repayment amount (must be positive).

    Returns:
        float: The remaining balance on the loan after this repayment.

    Raises:
        ValueError: If repayment amount is not positive or exceeds outstanding.
        sqlite3.Error: If database operation fails.
    """
    # Verify repayment amount is positive
    if amount <= 0:
        raise ValueError(
            f"Repayment amount must be positive, got {amount}. "
            "Please provide a valid positive repayment amount."
        )

    # Retrieve the loan from database
    conn = get_connection()
    query = """
        SELECT loan_id, member_id, total_due, amount_paid, status
        FROM loans
        WHERE loan_id = ?
    """
    result = conn.execute(query, (loan_id,)).fetchone()

    if result is None:
        raise ValueError(
            f"Loan ID {loan_id} not found. Please verify the loan exists."
        )

    loan_id_db, member_id, total_due, amount_paid, status = result

    # Check that loan is still active (not already repaid)
    if status == "repaid":
        raise ValueError(
            f"Loan ID {loan_id} has already been fully repaid. "
            "No further repayments can be recorded."
        )

    # Calculate outstanding balance before repayment
    remaining_balance = total_due - amount_paid

    # Check if repayment exceeds outstanding balance
    if amount > remaining_balance:
        raise ValueError(
            f"Repayment amount of {amount} exceeds outstanding balance "
            f"of {remaining_balance:.2f}. "
            f"The loan has {remaining_balance:.2f} remaining."
        )

    # Save repayment and update loan amount_paid in a transaction
    try:
        # Record the repayment
        conn.execute(
            """
                INSERT INTO repayments (loan_id, amount, repayment_date)
                VALUES (?, ?, ?)
            """,
            (loan_id, amount, date.today().isoformat())
        )

        # Update the loan's amount_paid
        new_amount_paid = amount_paid + amount
        conn.execute(
            "UPDATE loans SET amount_paid = ? WHERE loan_id = ?",
            (new_amount_paid, loan_id)
        )

        # If fully paid, update status to repaid
        if new_amount_paid >= total_due:
            conn.execute(
                "UPDATE loans SET status = 'repaid' WHERE loan_id = ?",
                (loan_id,)
            )

        # Save all changes
        conn.commit()

        return float(remaining_balance - amount)

    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Failed to record repayment: {e}")
    finally:
        conn.close()


def list_overdue_loans():
    """
    Retrieve all active loans that are past their due date.

    This function identifies loans whose due_date is earlier than today's
    date and status is still 'active' (not fully repaid). These are
    considered overdue and may need attention.

    Returns:
        list: A list of dictionaries containing overdue loan information.
               Each dictionary contains:
               - loan_id: The loan's primary key
               - member_id: The member who received the loan
               - amount: The principal loan amount
               - interest: The calculated interest
               - total_due: Total amount due including interest
               - amount_paid: Amount already paid
               - issue_date: When the loan was issued
               - due_date: When repayment is due
               - status: Current loan status

    Example:
        >>> overdue = list_overdue_loans()
        >>> for loan in overdue:
        ...     print(f"Loan {loan['loan_id']} to member {loan['member_id']} "
        ...           f"is overdue by {(date.today() > loan['due_date'])}")
    """
    # Get today's date as ISO string for comparison
    today_str = date.today().isoformat()

    conn = get_connection()
    query = """
        SELECT loan_id, member_id, amount, interest, total_due, 
               amount_paid, issue_date, due_date, status
        FROM loans
        WHERE status = 'active' AND due_date < ?
        ORDER BY due_date ASC
    """

    cursor = conn.execute(query, (today_str,))
    results = cursor.fetchall()
    conn.close()

    # Convert rows to dictionaries for easier use
    loans = []
    for row in results:
        loans.append({
            "loan_id": row["loan_id"],
            "member_id": row["member_id"],
            "amount": float(row["amount"]),
            "interest": float(row["interest"]),
            "total_due": float(row["total_due"]),
            "amount_paid": float(row["amount_paid"]),
            "issue_date": row["issue_date"],
            "due_date": row["due_date"],
            "status": row["status"]
        })

    return loans


def list_loans(member_id):
    """
    Retrieve all loans belonging to a specific member.

    This function returns all loan records for the specified member,
    regardless of their status (active, repaid, or any other). The results
    are returned in a dictionary format for easy access to individual fields.

    Args:
        member_id: The ID of the member whose loans to retrieve.

    Returns:
        list: A list of dictionaries containing loan information.
               Each dictionary contains:
               - loan_id: The loan's primary key
               - member_id: The member who received the loan
               - amount: The principal loan amount
               - interest: The calculated interest
               - total_due: Total amount due including interest
               - amount_paid: Amount already paid
               - issue_date: When the loan was issued (ISO string)
               - due_date: When repayment is due (ISO string)
               - status: Current loan status ('active' or 'repaid')

    Example:
        >>> loans = list_loans(1)
        >>> for loan in loans:
        ...     print(f"Loan ID {loan['loan_id']}: ${loan['amount']} "
        ...           f"(Due: {loan['due_date']}, Paid: {loan['amount_paid']})")

    Note:
        Returns an empty list if the member has no loans.
    """
    conn = get_connection()
    query = """
        SELECT loan_id, member_id, amount, interest, total_due, 
               amount_paid, issue_date, due_date, status
        FROM loans
        WHERE member_id = ?
        ORDER BY issue_date DESC
    """

    cursor = conn.execute(query, (member_id,))
    results = cursor.fetchall()
    conn.close()

    # Convert rows to dictionaries for easier use
    loans = []
    for row in results:
        loans.append({
            "loan_id": row["loan_id"],
            "member_id": row["member_id"],
            "amount": float(row["amount"]),
            "interest": float(row["interest"]),
            "total_due": float(row["total_due"]),
            "amount_paid": float(row["amount_paid"]),
            "issue_date": row["issue_date"],
            "due_date": row["due_date"],
            "status": row["status"]
        })

    return loans
