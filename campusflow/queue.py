"""Priority-ordered unresolved ticket queue."""

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _numeric_ticket_id(ticket):
    ticket_id = ticket.get("id", "")
    if not isinstance(ticket_id, str) or not ticket_id.startswith("T"):
        raise ValueError("Ticket has an invalid ID; expected T001 format.")
    number_text = ticket_id[1:]
    if not number_text.isascii() or not number_text.isdigit() or int(number_text) <= 0:
        raise ValueError("Ticket has an invalid ID; expected T001 format.")
    return int(number_text)


def unresolved_queue(tickets):
    """Return unresolved tickets sorted by priority, then numeric ticket ID.

    The original list is not mutated. Any status other than 'resolved' is
    considered unresolved so invalid status values are not silently hidden.
    """
    for ticket in tickets:
        if ticket.get("priority") not in PRIORITY_ORDER:
            raise ValueError(f"Ticket {ticket.get('id', '?')} has an invalid priority.")
    return sorted(
        (ticket for ticket in tickets if ticket.get("status") != "resolved"),
        key=lambda ticket: (PRIORITY_ORDER[ticket["priority"]], _numeric_ticket_id(ticket)),
    )
