from datetime import date
from fadhiri.db import get_connection


class Member:
    """A savings group member."""

    def __init__(self, member_id, full_name, phone, date_joined):
        self.member_id = member_id
        self.full_name = full_name
        self.phone = phone
        self.date_joined = date_joined

    def __str__(self):
        return (
            f"Member ID: {self.member_id}, "
            f"Name: {self.full_name}, "
            f"Phone: {self.phone}, "
            f"Date Joined: {self.date_joined}"
        )


def add_member(full_name, phone):
    """Add a new member and return the new member ID."""
    if not full_name or not full_name.strip():
        raise ValueError("Full name is required")

    joined_date = date.today().isoformat()
    conn = get_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO members (full_name, phone, date_joined)
            VALUES (?, ?, ?)
            """,
            (full_name.strip(), phone, joined_date),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_member(member_id):
    """Return a Member by ID, or None if not found."""
    conn = get_connection()

    try:
        row = conn.execute(
            """
            SELECT member_id, full_name, phone, date_joined
            FROM members
            WHERE member_id = ?
            """,
            (member_id,),
        ).fetchone()

        if row is None:
            return None

        return Member(
            row["member_id"],
            row["full_name"],
            row["phone"],
            row["date_joined"],
        )
    finally:
        conn.close()


def list_members():
    """Return all members as Member objects."""
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT member_id, full_name, phone, date_joined
            FROM members
            ORDER BY member_id
            """
        ).fetchall()

        return [
            Member(
                row["member_id"],
                row["full_name"],
                row["phone"],
                row["date_joined"],
            )
            for row in rows
        ]
    finally:
        conn.close()


def search_members(text):
    """Return members whose names contain the search text."""
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT member_id, full_name, phone, date_joined
            FROM members
            WHERE LOWER(full_name) LIKE LOWER(?)
            ORDER BY member_id
            """,
            (f"%{text}%",),
        ).fetchall()

        return [
            Member(
                row["member_id"],
                row["full_name"],
                row["phone"],
                row["date_joined"],
            )
            for row in rows
        ]
    finally:
        conn.close()
