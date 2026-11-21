"""Statements and the group summary.
Owner: Prosper Shimwa

Called from main.py (Bryan) through print_member_statement and
print_group_summary. Data comes from the tables created in fadhiri/db.py.
"""
from fadhiri.db import get_connection


def _scalar(conn, sql, params=()):
    """Run a query that returns one number and give back 0 when it is NULL."""
    row = conn.execute(sql, params).fetchone()
    return row[0] if row and row[0] is not None else 0


def member_statement(member_id):
    """Return a dict: savings, loans taken, amount still owed, fines total."""
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
               FROM repayments r JOIN loans l ON r.loan_id = l.id
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

    return {
        "savings": savings,
        "loans_taken": loans_taken,
        "amount_owed": loans_taken - repaid,
        "fines_total": fines_total,
    }


def print_member_statement(member_id):
    """Print the statement as a neat block of text."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT name FROM members WHERE id = ?", (member_id,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        print(f"No member found with ID {member_id}.")
        return

    s = member_statement(member_id)
    print("=" * 36)
    print(f" MEMBER STATEMENT: {row[0]} (ID {member_id})")
    print("=" * 36)
    print(f" Total savings      : {s['savings']:>12,.0f}")
    print(f" Loans taken        : {s['loans_taken']:>12,.0f}")
    print(f" Amount still owed  : {s['amount_owed']:>12,.0f}")
    print(f" Fines total        : {s['fines_total']:>12,.0f}")
    print("=" * 36)


def group_summary():
    """Return a dict: number of members, total savings, money lent out,
    amount still owed, number of overdue loans, total fines."""
    conn = get_connection()
    try:
        num_members = _scalar(conn, "SELECT COUNT(*) FROM members")
        total_savings = _scalar(
            conn, "SELECT COALESCE(SUM(amount), 0) FROM contributions"
        )
        money_lent = _scalar(conn, "SELECT COALESCE(SUM(amount), 0) FROM loans")
        repaid = _scalar(conn, "SELECT COALESCE(SUM(amount), 0) FROM repayments")
        total_fines = _scalar(conn, "SELECT COALESCE(SUM(amount), 0) FROM fines")
        # A loan is overdue when its due date has passed and it is not fully repaid.
        num_overdue = _scalar(
            conn,
            """SELECT COUNT(*) FROM loans l
               WHERE l.due_date < date('now')
                 AND l.amount > (SELECT COALESCE(SUM(r.amount), 0)
                                 FROM repayments r WHERE r.loan_id = l.id)""",
        )
    finally:
        conn.close()

    return {
        "num_members": num_members,
        "total_savings": total_savings,
        "money_lent": money_lent,
        "amount_owed": money_lent - repaid,
        "num_overdue": num_overdue,
        "total_fines": total_fines,
    }


def print_group_summary():
    """Print the summary as a neat block of text."""
    g = group_summary()
    print("=" * 36)
    print(" GROUP SUMMARY")
    print("=" * 36)
    print(f" Number of members  : {g['num_members']:>12}")
    print(f" Total savings      : {g['total_savings']:>12,.0f}")
    print(f" Money lent out     : {g['money_lent']:>12,.0f}")
    print(f" Amount still owed  : {g['amount_owed']:>12,.0f}")
    print(f" Overdue loans      : {g['num_overdue']:>12}")
    print(f" Total fines        : {g['total_fines']:>12,.0f}")
    print("=" * 36)
