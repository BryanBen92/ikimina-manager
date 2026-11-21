"""Ikimina Manager: entry point and menus.
Owner: Benjamin Bryan Inema
"""
from db import create_tables
from prosper.validators import get_int


def show_role_menu():
    """Print: 1 Treasurer, 2 Member, 0 Exit. Return the user's choice."""
    print("\n===== IKIMINA MANAGER =====")
    print("1 Treasurer")
    print("2 Member")
    print("0 Exit")
    return get_int("Choice: ")


def main():
    create_tables()
    while True:
        choice = show_role_menu()
        if choice == 0:
            print("Goodbye.")
            break
        else:
            print("Not implemented yet.")


if __name__ == "__main__":
    main()
