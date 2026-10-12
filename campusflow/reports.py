"""Simple ticket summary reports."""

PRIORITIES = ("critical", "high", "medium", "low")
STATUSES = ("open", "in_progress", "resolved")


def ticket_report(tickets):
    """Return totals and breakdowns by priority, status, and category."""
    by_priority = {priority: 0 for priority in PRIORITIES}
    by_status = {status: 0 for status in STATUSES}
    by_category = {}

    for ticket in tickets:
        priority = ticket.get("priority")
        status = ticket.get("status")
        category = ticket.get("category", "Unknown")
        if priority in by_priority:
            by_priority[priority] += 1
        if status in by_status:
            by_status[status] += 1
        by_category[category] = by_category.get(category, 0) + 1

    return {
        "total": len(tickets),
        "by_priority": by_priority,
        "by_status": by_status,
        "by_category": dict(sorted(by_category.items())),
    }
