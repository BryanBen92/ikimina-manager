"""Statements and the group summary.
Owner: Prosper Shimwa
"""

from db import get_connection

from members import get_member, list_members
from benjamin_mugisha.contributions import member_savings, list_fines
from calvin.loans import list_loans, list_overdue_loans


def _scalar(conn, sql, params=()):
    """Run a query that returns one number and give back 0 when it is NULL."""
    row = conn.execute(sql, params).fetchone()
    return row[0] if row and row[0] is not None else 0


def member_statement(member_id):
    """Return a dict: savings, loans taken, amount still owed, fines total."""
    member = get_member(member_id)
    if member is None:
        raise ValueError("Member does not exist.")

    conn = get_connection()
    try:
        savings = _scalar(
            conn,
            "SELECT COALESCE(SUM(amount), 0) FROM contributions WHERE member_id = ?",
            (member_id,),
        )
        loans_taken = _scalar(
            conn,
            "SELECT COALESCE(SUM(amount), 0) FROM loans WHERE member_id = ?",
            (member_id,),
        )
        repaid = _scalar(
            conn,
            """SELECT COALESCE(SUM(r.amount), 0)
               FROM repayments r JOIN loans l ON r.loan_id = l.loan_id
               WHERE l.member_id = ?""",
            (member_id,),
        )
        fines_total = _scalar(
            conn,
            "SELECT COALESCE(SUM(amount), 0) FROM fines WHERE member_id = ?",
            (member_id,),
        )
    finally:
        conn.close()

    loans = list_loans(member_id)
    amount_owed = sum(
        float(loan["total_due"]) - float(loan["amount_paid"])
        for loan in loans
        if loan["status"] == "active"
    )
    if not amount_owed:
        amount_owed = loans_taken - repaid

    return {
        "member_id": member_id,
        "full_name": member.full_name,
        "savings": savings,
        "loans_taken": loans_taken,
        "amount_owed": amount_owed,
        "fines_total": fines_total,
    }


def print_member_statement(member_id):
    """Print the statement as a neat block of text."""
    statement = member_statement(member_id)
    loans = list_loans(member_id)
    fines = list_fines(member_id)

    print("\n===== MEMBER STATEMENT =====")
    print(f"Member ID:   {statement['member_id']}")
    print(f"Name:        {statement['full_name']}")
    print(f"Savings:     {statement['savings']}")
    print(f"Loans taken: {statement['loans_taken']}")
    print(f"Amount owed: {statement['amount_owed']}")
    print(f"Fines total: {statement['fines_total']}")

    if loans:
        print("\nLoans:")
        for loan in loans:
            print(
                f"  Loan {loan['loan_id']}: principal {loan['amount']}, "
                f"total due {loan['total_due']}, paid {loan['amount_paid']}, "
                f"due {loan['due_date']}, status {loan['status']}"
            )

    if fines:
        print("\nFines:")
        for fine in fines:
            print(f"  Fine {fine['fine_id']}: {fine['reason']} - {fine['amount']} ({fine['fine_date']})")
    print("===========================\n")


def group_summary():
    """Return a dict: number of members, total savings, money lent out,
    amount still owed, number of overdue loans, total fines."""
    members = list_members()
    num_members = len(members)
    total_savings = sum(member_savings(m.member_id) for m in members)

    conn = get_connection()
    try:
        money_lent = _scalar(conn, "SELECT COALESCE(SUM(amount), 0) FROM loans")
        amount_owed = _scalar(
            conn,
            "SELECT COALESCE(SUM(total_due - amount_paid), 0) FROM loans WHERE status = 'active'",
        )
        total_fines = _scalar(conn, "SELECT COALESCE(SUM(amount), 0) FROM fines")
    finally:
        conn.close()

    num_overdue = len(list_overdue_loans())

    return {
        "num_members": num_members,
        "total_savings": total_savings,
        "money_lent": money_lent,
        "amount_owed": amount_owed,
        "num_overdue": num_overdue,
        "total_fines": total_fines,
    }


def print_group_summary():
    """Print the summary as a neat block of text."""
    summary = group_summary()
    print("\n===== GROUP SUMMARY =====")
    print(f"Number of members:    {summary['num_members']}")
    print(f"Total savings:        {summary['total_savings']}")
    print(f"Money lent out:       {summary['money_lent']}")
    print(f"Amount still owed:    {summary['amount_owed']}")
    print(f"Number of overdue:    {summary['num_overdue']}")
    print(f"Total fines:          {summary['total_fines']}")
    print("========================\n")
