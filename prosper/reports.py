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
