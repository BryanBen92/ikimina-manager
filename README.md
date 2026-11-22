# Ikimina Manager

A menu-driven Python terminal app (SQLite) that helps a savings group treasurer record
contributions, loans, repayments, and fines, and print statements. PLP-2, Group 9.

Run: `python main.py` (Python 3, nothing to install).

## Menu (treasurer)
```
1 Add a member
2 Record a contribution
3 Issue a loan
4 Record a repayment
5 Record a fine
6 Member statement
7 Overdue loans
8 Group summary
9 Manage members
0 Exit
```
(Member role: view own statement only.)

## Who writes what
| Person | File | You write |
|---|---|---|
| Fadhiri Faisal Ndegeya Ihirwe | database/db.py | connection, tables, settings |
| David Ngoga | members/members.py | Member class + add/get/list/search/update/delete |
| Benjamin Mugisha Ntege | contributions/contributions.py | contributions + fines |
| Calvin Ngabo Ruvugabigwi | loans/loans.py | loan limit, issue loan, repayments, overdue |
| Benjamin Bryan Inema | main.py | role menu, treasurer menu, member menu |
| Prosper Shimwa | reports/reports.py, utils/validators.py | statements, group summary, safe input |

Each function has a docstring saying what it must do.

## Tables
- members: member_id, full_name, phone, date_joined
- contributions: contribution_id, member_id, amount, contribution_date
- loans: loan_id, member_id, amount, interest, total_due, amount_paid, issue_date, due_date, status
- repayments: repayment_id, loan_id, amount, repayment_date
- fines: fine_id, member_id, reason, amount, fine_date
- settings: key, value (loan_limit_multiplier, interest_rate_percent, loan_days). Confirm real values with a treasurer.

## Git (work on main, your files only)
```
git pull
# write your code and run it
git add <your file>
git commit -m "Add member CRUD functions"
git pull --rebase && git push
```
Commit small and often, with messages that say what you did. Every member needs more than 4 commits on main.

