"""JSON persistence for CampusFlow tickets."""

import json
import os
import tempfile
from pathlib import Path

from campusflow.tickets import next_ticket_id

REQUIRED_FIELDS = {
    "id", "title", "category", "urgency", "affected_users",
    "priority", "status", "assigned_to",
}


def _validate_loaded_tickets(data):
    if not isinstance(data, list):
        raise ValueError("Ticket data must be a JSON list.")
    # Reuse ID validation to prevent duplicates and unsafe future ID generation.
    next_ticket_id(data)
    for index, ticket in enumerate(data, start=1):
        missing = REQUIRED_FIELDS - ticket.keys()
        if missing:
            raise ValueError(
                f"Ticket record {index} is missing required field(s): "
                + ", ".join(sorted(missing))
                + "."
            )
        if not isinstance(ticket["title"], str) or not ticket["title"].strip():
            raise ValueError(f"Ticket record {index} has an invalid title.")
        if ticket["status"] not in ("open", "in_progress", "resolved"):
            raise ValueError(f"Ticket record {index} has an invalid status.")
        if ticket["priority"] not in ("critical", "high", "medium", "low"):
            raise ValueError(f"Ticket record {index} has an invalid priority.")
    return data


def load_tickets(path="data/tickets.json"):
    """Load tickets from JSON; a missing file represents a fresh installation."""
    file_path = Path(path)
    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Could not read ticket data from {file_path}: invalid JSON "
            f"at line {exc.lineno}, column {exc.colno}."
        ) from exc
    except OSError as exc:
        raise ValueError(f"Could not read ticket data from {file_path}: {exc}.") from exc
    return _validate_loaded_tickets(data)


def save_tickets(path, tickets):
    """Atomically save tickets as JSON, preserving the old file on write failure."""
    _validate_loaded_tickets(tickets)
    file_path = Path(path)
    parent = file_path.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{file_path.name}.", suffix=".tmp", dir=str(parent)
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                json.dump(tickets, file, indent=2, ensure_ascii=False)
                file.write("\n")
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary_name, file_path)
        except Exception:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise
    except (OSError, TypeError, ValueError) as exc:
        if isinstance(exc, ValueError) and str(exc).startswith("Ticket"):
            raise
        raise ValueError(f"Could not save ticket data to {file_path}: {exc}.") from exc
