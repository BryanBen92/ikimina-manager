"""Ikimina Manager: entry point and menus.
Owner: Benjamin Bryan Inema
"""
from db import create_tables

from members import add_member, list_members, search_members, update_member, delete_member
from benjamin_mugisha.contributions import record_contribution, record_fine
from calvin.loans import max_loan_allowed, issue_loan, record_repayment, list_overdue_loans
from prosper.reports import print_member_statement, print_group_summary
from prosper.validators import get_int, get_amount, get_text

TREASURER_PIN = "1234"


def show_role_menu():
    print("\n===== IKIMINA MANAGER =====")
    print("1 Treasurer")
    print("2 Member")
    print("0 Exit")
    return get_int("Choice: ")


def treasurer_menu():
    pin = get_text("Treasurer PIN: ")
    if pin != TREASURER_PIN:
        print("Wrong PIN.")
        return
    while True:
        print("\n===== TREASURER MENU =====")
        print("1 Add a member")
        print("2 Record a contribution")
        print("3 Issue a loan")
        print("4 Record a repayment")
        print("5 Record a fine")
        print("6 Member statement")
        print("7 Overdue loans")
        print("8 Group summary")
        print("9 Manage members")
        print("0 Exit")
        choice = get_int("Choice: ")
        try:
            if choice == 0:
                break
            else:
                print("Option not wired yet.")
        except Exception as exc:
            print(f"Error: {exc}")


def member_menu():
    """Ask for a member ID and print that member's statement (read only)."""
    mid = get_int("Member ID: ")
    try:
        print_member_statement(mid)
    except Exception as exc:
        print(f"Error: {exc}")


def main():
    create_tables()
    while True:
        choice = show_role_menu()
        if choice == 1:
            treasurer_menu()
        elif choice == 2:
            member_menu()
        elif choice == 0:
            print("Goodbye.")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
