"""Contributions and fines.
Owner: Benjamin Mugisha Ntege
"""

from datetime import date

from fadhiri.db import get_connection


def record_contribution(member_id, amount):
    """Save a contribution dated today and return the member's new total savings.

    Raise ValueError if the amount is not positive or the member does not exist.
    """
    if amount is None or amount <= 0:
        raise ValueError("Contribution amount must be positive.")

    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT member_id FROM members WHERE member_id = ?",
            (member_id,),
        ).fetchone()
        if row is None:
            raise ValueError("Member does not exist.")

        today = date.today().isoformat()
        conn.execute(
            """
            INSERT INTO contributions (member_id, amount, contribution_date)
            VALUES (?, ?, ?)
            """,
            (member_id, amount, today),
        )

        total_row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM contributions WHERE member_id = ?",
            (member_id,),
        ).fetchone()
        new_total = total_row["total"]

        conn.commit()
        return new_total
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def list_contributions(member_id):
    """Return all contributions of one member, newest first."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT contribution_id, member_id, amount, contribution_date
            FROM contributions
            WHERE member_id = ?
            ORDER BY contribution_date DESC, contribution_id DESC
            """,
            (member_id,),
        ).fetchall()

        return [
            {
                "contribution_id": row["contribution_id"],
                "member_id": row["member_id"],
                "amount": row["amount"],
                "contribution_date": row["contribution_date"],
            }
            for row in rows
        ]
    finally:
        conn.close()


def member_savings(member_id):
    """Return the total contributed by one member (0 if none)."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM contributions WHERE member_id = ?",
            (member_id,),
        ).fetchone()
        if row is None:
            return 0
        return row["total"]
    finally:
        conn.close()


def record_fine(member_id, reason, amount):
    """Save a fine dated today, raising ValueError for a bad amount or unknown member."""
    # TODO
    raise NotImplementedError


def list_fines(member_id):
    """Return all fines of one member."""
    # TODO
    raise NotImplementedError