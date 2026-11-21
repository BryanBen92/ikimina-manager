"""Safe keyboard input helpers.
Owner: Prosper Shimwa
Each function keeps asking until the input is valid (while True + try/except).
"""


def get_int(prompt):
    """Ask for a whole number (e.g. a member ID or a menu choice)."""
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Invalid input. Please enter a whole number (e.g. 5).")


def get_amount(prompt):
    """Ask for a positive number (e.g. money). Zero and negatives are rejected."""
    while True:
        try:
            value = float(input(prompt).strip().replace(",", ""))
            if value <= 0:
                print("The amount must be greater than 0.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a number (e.g. 5000).")


def get_text(prompt):
    """Ask for text that is not empty (spaces only do not count)."""
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("This field cannot be empty. Please try again.")
