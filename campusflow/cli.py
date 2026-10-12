"""Interactive command-line interface for CampusFlow."""

from campusflow.queue import unresolved_queue
from campusflow.reports import ticket_report
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket
from campusflow.workflow import assign_ticket, change_status, find_ticket

DEFAULT_DATA_PATH = "data/tickets.json"


def _show_ticket(ticket):
    print(f"\n{ticket['id']} — {ticket['title']}")
    print(f"  Category: {ticket['category']}")
    print(f"  Urgency: {ticket['urgency']}")
    print(f"  Affected users: {ticket['affected_users']}")
    print(f"  Priority: {ticket['priority']}")
    print(f"  Status: {ticket['status']}")
    print(f"  Assigned to: {ticket['assigned_to'] or 'Unassigned'}")


def _print_tickets(tickets):
    if not tickets:
        print("No tickets found.")
        return
    for ticket in tickets:
        _show_ticket(ticket)


def _print_report(tickets):
    report = ticket_report(tickets)
    print(f"\nTotal tickets: {report['total']}")
    print("By priority:")
    for priority, count in report["by_priority"].items():
        print(f"  {priority.title()}: {count}")
    print("By status:")
    for status, count in report["by_status"].items():
        print(f"  {status.replace('_', ' ').title()}: {count}")
    print("By category:")
    if not report["by_category"]:
        print("  No categories yet.")
    else:
        for category, count in report["by_category"].items():
            print(f"  {category}: {count}")


def _read_choice(prompt, allowed):
    choice = input(prompt).strip()
    if choice not in allowed:
        raise ValueError(f"Choose one of: {', '.join(allowed)}.")
    return choice


def run_cli(data_path=DEFAULT_DATA_PATH):
    """Run the menu until the user chooses to exit."""
    try:
        tickets = load_tickets(data_path)
    except ValueError as exc:
        print(f"Startup error: {exc}")
        return

    print("CampusFlow Helpdesk")
    while True:
        print(
            "\n1. Create ticket\n"
            "2. List all tickets\n"
            "3. View ticket\n"
            "4. Assign ticket\n"
            "5. Change ticket status / reopen\n"
            "6. Show unresolved work queue\n"
            "7. Show reports\n"
            "8. Save now\n"
            "0. Exit"
        )
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                title = input("Ticket title: ")
                category = input("Category (Network/Hardware/Software/Other): ")
                urgency = input("Urgency (low/medium/high): ")
                affected_users = input("Number of affected users: ")
                ticket = create_ticket(tickets, title, category, urgency, affected_users)
                save_tickets(data_path, tickets)
                print(f"Created {ticket['id']} with {ticket['priority']} priority.")
            elif choice == "2":
                _print_tickets(tickets)
            elif choice == "3":
                ticket = find_ticket(tickets, input("Ticket ID: "))
                _show_ticket(ticket)
            elif choice == "4":
                ticket_id = input("Ticket ID: ")
                fellow = input("Assign to fellow: ")
                assign_ticket(tickets, ticket_id, fellow)
                save_tickets(data_path, tickets)
                print(f"Ticket {ticket_id.strip().upper()} assigned successfully.")
            elif choice == "5":
                ticket_id = input("Ticket ID: ")
                print("Statuses: open, in_progress, resolved")
                print("To reopen a resolved ticket, choose open.")
                new_status = input("New status: ")
                change_status(tickets, ticket_id, new_status)
                save_tickets(data_path, tickets)
                print(f"Ticket {ticket_id.strip().upper()} status updated.")
            elif choice == "6":
                _print_tickets(unresolved_queue(tickets))
            elif choice == "7":
                _print_report(tickets)
            elif choice == "8":
                save_tickets(data_path, tickets)
                print(f"Saved {len(tickets)} ticket(s) to {data_path}.")
            elif choice == "0":
                print("Goodbye.")
                return
            else:
                print("Please choose a listed menu option.")
        except ValueError as exc:
            print(f"Error: {exc}")
        except OSError as exc:
            print(f"File error: {exc}")
