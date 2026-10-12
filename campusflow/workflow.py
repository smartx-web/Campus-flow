"""Assignment and lifecycle operations for CampusFlow tickets."""

VALID_STATUSES = ("open", "in_progress", "resolved")


def find_ticket(tickets, ticket_id):
    """Return a ticket by ID, or raise ValueError when it does not exist."""
    if not isinstance(ticket_id, str) or not ticket_id.strip():
        raise ValueError("Ticket ID must be non-empty text.")
    wanted = ticket_id.strip().upper()
    for ticket in tickets:
        if ticket.get("id") == wanted:
            return ticket
    raise ValueError(f"Ticket {wanted!r} was not found.")


def assign_ticket(tickets, ticket_id, fellow):
    """Assign an unresolved ticket to a fellow and return the updated ticket."""
    ticket = find_ticket(tickets, ticket_id)
    if ticket.get("status") == "resolved":
        raise ValueError("A resolved ticket must be reopened before it can be modified.")
    if not isinstance(fellow, str) or not fellow.strip():
        raise ValueError("Assignee must be a non-empty fellow name.")
    ticket["assigned_to"] = fellow.strip()
    return ticket


def change_status(tickets, ticket_id, new_status):
    """Apply an allowed lifecycle transition and return the updated ticket.

    Allowed transitions are open -> in_progress (when assigned),
    in_progress -> resolved, and resolved -> open (explicit reopen).
    """
    ticket = find_ticket(tickets, ticket_id)
    if not isinstance(new_status, str):
        raise ValueError("Status must be open, in_progress, or resolved.")
    new_status = new_status.strip().casefold()
    if new_status not in VALID_STATUSES:
        raise ValueError("Status must be open, in_progress, or resolved.")

    current = ticket.get("status")
    if current == "resolved":
        if new_status != "open":
            raise ValueError("A resolved ticket can only be reopened to open.")
    elif current == "open":
        if new_status != "in_progress":
            raise ValueError("An open ticket can only move to in_progress.")
        if not ticket.get("assigned_to"):
            raise ValueError("Assign the ticket before moving it to in_progress.")
    elif current == "in_progress":
        if new_status != "resolved":
            raise ValueError("A ticket in progress can only move to resolved.")
    else:
        raise ValueError(f"Ticket has an invalid current status: {current!r}.")

    ticket["status"] = new_status
    return ticket
