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
