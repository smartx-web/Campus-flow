"""Ticket creation and validation, without interactive input or file I/O."""

import re

CATEGORIES = ("Network", "Hardware", "Software", "Other")
URGENCY_LEVELS = ("low", "medium", "high")
_TICKET_ID = re.compile(r"T([0-9]{3,})\Z")


def normalize_title(title):
    """Return a trimmed, non-blank title or raise ValueError."""
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Title must be non-empty text.")
    return title.strip()


def normalize_category(category):
    """Accept whitespace and case variations of the four categories."""
    if isinstance(category, str):
        for allowed in CATEGORIES:
            if category.strip().casefold() == allowed.casefold():
                return allowed
    raise ValueError("Category must be Network, Hardware, Software, or Other.")


def normalize_urgency(urgency):
    """Return low, medium or high in lowercase."""
    if isinstance(urgency, str):
        normalized = urgency.strip().casefold()
        if normalized in URGENCY_LEVELS:
            return normalized
    raise ValueError("Urgency must be low, medium, or high.")


def normalize_affected_users(affected_users):
    """Accept a positive int or an ASCII digit string from the CLI.

    Reject bool (despite being an int subclass), floats and decimal strings.
    """
    if type(affected_users) is int:
        value = affected_users
    elif isinstance(affected_users, str) and re.fullmatch(
        r"[0-9]+", affected_users.strip()
    ):
        try:
            value = int(affected_users.strip())
        except ValueError:
            raise ValueError("Affected users must be a positive integer.") from None
    else:
        raise ValueError("Affected users must be a positive integer.")
    if value <= 0:
        raise ValueError("Affected users must be a positive integer.")
    return value


def calculate_priority(urgency, affected_users):
    """Validate inputs, then apply the mission's first-match priority rules."""
    urgency = normalize_urgency(urgency)
    affected_users = normalize_affected_users(affected_users)
    if urgency == "high" and affected_users >= 10:
        return "critical"
    if urgency == "high" or affected_users >= 10:
        return "high"
    if urgency == "medium" or affected_users >= 3:
        return "medium"
    return "low"


def next_ticket_id(tickets):
    """Generate an ID above the largest numeric ID, including after reload.

    The collection must be a list of dictionaries with unique positive IDs
    formatted as T001, T002, etc. Invalid stored IDs cause a clear error.
    """
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be a list of ticket dictionaries.")
    seen = set()
    largest = 0
    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise ValueError("Stored tickets must be dictionaries.")
        ticket_id = ticket.get("id")
        match = _TICKET_ID.fullmatch(ticket_id) if isinstance(ticket_id, str) else None
        if match is None:
            raise ValueError("Stored ticket has an invalid ID; expected T001 format.")
        try:
            number = int(match.group(1))
        except ValueError:
            raise ValueError("Stored ticket has an invalid numeric ID.") from None
        if number <= 0 or ticket_id != f"T{number:03d}":
            raise ValueError("Stored ticket has an invalid ID; expected T001 format.")
        if number in seen:
            raise ValueError("Stored tickets contain duplicate IDs.")
        seen.add(number)
        largest = max(largest, number)
    return f"T{largest + 1:03d}"


def create_ticket(tickets, title, category, urgency, affected_users):
    """Validate, append one ticket, and return that dictionary.

    All validation happens before mutation. The caller owns persistence and
    should save the collection after success. Invalid input raises ValueError.
    """
    title = normalize_title(title)
    category = normalize_category(category)
    urgency = normalize_urgency(urgency)
    affected_users = normalize_affected_users(affected_users)
    ticket_id = next_ticket_id(tickets)
    ticket = {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": calculate_priority(urgency, affected_users),
        "status": "open",
        "assigned_to": None,
    }
    tickets.append(ticket)
    return ticket
