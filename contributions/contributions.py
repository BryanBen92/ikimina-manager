"""Contributions and fines.
Owner: Benjamin Mugisha Ntege
"""

from datetime import date

from database.db import get_connection


def _member_exists(conn, member_id):
    """Return True when the given member exists in the members table."""
    row = conn.execute(
        "SELECT 1 FROM members WHERE member_id = ?",
        (member_id,),
    ).fetchone()
    return row is not None


def record_contribution(member_id, amount):
    """Save a contribution dated today and return the member's new total savings.

    Args:
        member_id: The ID of the contributing member.
        amount: The contribution amount, which must be positive.

    Returns:
        The member's updated total savings, including this contribution.

    Raises:
        ValueError: If ``amount`` is not positive or the member does not exist.
    """
    try:
        if amount is None or amount <= 0:
            raise ValueError("Contribution amount must be positive.")
    except TypeError as exc:
        raise ValueError("Contribution amount must be positive.") from exc

    conn = get_connection()
    try:
        if not _member_exists(conn, member_id):
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
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM contributions
            WHERE member_id = ?
            """,
            (member_id,),
        ).fetchone()
        new_total = total_row["total"] if total_row is not None else 0

        conn.commit()
        return new_total
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def list_contributions(member_id):
    """Return all contributions of one member, newest first.

    Entries sharing a date are ordered by contribution ID descending as a
    stable tie-breaker.

    Args:
        member_id: The ID of the member whose contributions to return.

    Returns:
        A list of contribution dictionaries. An empty list is returned when
        the member has no contributions.
    """
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
    """Return the total contributed by one member (0 if none).

    Args:
        member_id: The ID of the member whose savings to return.

    Returns:
        The member's total contributions, or 0 when there are none.
    """
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM contributions
            WHERE member_id = ?
            """,
            (member_id,),
        ).fetchone()
        if row is None:
            return 0
        return row["total"]
    finally:
        conn.close()


def record_fine(member_id, reason, amount):
    """Save a fine dated today, raising ValueError for a bad amount or unknown member.

    Args:
        member_id: The ID of the fined member.
        reason: The reason for the fine.
        amount: The fine amount, which must be positive.

    Raises:
        ValueError: If ``amount`` is not positive or the member does not exist.
    """
    try:
        if amount is None or amount <= 0:
            raise ValueError("Fine amount must be positive.")
    except TypeError as exc:
        raise ValueError("Fine amount must be positive.") from exc

    conn = get_connection()
    try:
        if not _member_exists(conn, member_id):
            raise ValueError("Member does not exist.")

        today = date.today().isoformat()
        conn.execute(
            """
            INSERT INTO fines (member_id, reason, amount, fine_date)
            VALUES (?, ?, ?, ?)
            """,
            (member_id, reason, amount, today),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def list_fines(member_id):
    """Return all fines for the member.

    Args:
        member_id: The ID of the member whose fines to return.

    Returns:
        A list of fine dictionaries. An empty list is returned when the
        member has no fines.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT fine_id, member_id, reason, amount, fine_date
            FROM fines
            WHERE member_id = ?
            ORDER BY fine_id ASC
            """,
            (member_id,),
        ).fetchall()

        return [
            {
                "fine_id": row["fine_id"],
                "member_id": row["member_id"],
                "reason": row["reason"],
                "amount": row["amount"],
                "fine_date": row["fine_date"],
            }
            for row in rows
        ]
    finally:
        conn.close()
