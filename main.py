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


def manage_members():
    while True:
        print("\n--- Manage Members ---")
        print("1 List members")
        print("2 Search members")
        print("3 Update member")
        print("4 Delete member")
        print("0 Back")
        choice = get_int("Choice: ")
        try:
            if choice == 1:
                for m in list_members():
                    print(m)
            elif choice == 2:
                text = get_text("Search text: ")
                for m in search_members(text):
                    print(m)
            elif choice == 3:
                mid = get_int("Member ID: ")
                name = get_text("New full name: ")
                phone = get_text("New phone: ")
                if update_member(mid, name, phone):
                    print("Member updated.")
                else:
                    print("Member not found.")
            elif choice == 4:
                mid = get_int("Member ID: ")
                if delete_member(mid):
                    print("Member deleted.")
                else:
                    print("Could not delete member (may have records).")
            elif choice == 0:
                break
            else:
                print("Invalid option.")
        except Exception as exc:
            print(f"Error: {exc}")


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
            if choice == 1:
                name = get_text("Full name: ")
                phone = get_text("Phone: ")
                mid = add_member(name, phone)
                print(f"Member added with ID {mid}.")
            elif choice == 2:
                mid = get_int("Member ID: ")
                amount = get_amount("Amount: ")
                from benjamin_mugisha.contributions import record_contribution
                total = record_contribution(mid, amount)
                print(f"Contribution recorded. New total savings: {total}")
            elif choice == 3:
                mid = get_int("Member ID: ")
                amount = get_amount("Loan amount: ")
                limit = max_loan_allowed(mid)
                print(f"Max loan allowed: {limit}")
                loan_id, total_due, due_date = issue_loan(mid, amount)
                print(f"Loan {loan_id} issued. Total due: {total_due}, due {due_date}.")
            elif choice == 4:
                loan_id = get_int("Loan ID: ")
                amount = get_amount("Repayment amount: ")
                remaining = record_repayment(loan_id, amount)
                print(f"Repayment recorded. Remaining balance: {remaining}")
            elif choice == 5:
                mid = get_int("Member ID: ")
                reason = get_text("Reason: ")
                amount = get_amount("Fine amount: ")
                record_fine(mid, reason, amount)
                print("Fine recorded.")
            elif choice == 6:
                mid = get_int("Member ID: ")
                print_member_statement(mid)
            elif choice == 7:
                loans = list_overdue_loans()
                if not loans:
                    print("No overdue loans.")
                for loan in loans:
                    print(loan)
            elif choice == 8:
                print_group_summary()
            elif choice == 9:
                manage_members()
            elif choice == 0:
                break
            else:
                print("Invalid option.")
        except Exception as exc:
            print(f"Error: {exc}")


def member_menu():
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
