# CampusFlow

CampusFlow is a standard-library-only Python command-line helpdesk ticket manager.
It creates and validates tickets, assigns fellows, enforces the ticket lifecycle,
orders unresolved work by priority, prints summary reports, and persists tickets to JSON.

## Requirements

- Python 3.9 or newer (no third-party packages required)
- A terminal

## Run the application

From the repository root:

```bash
python -m campusflow
```

The first run starts with an empty collection. Ticket data is stored at
`data/tickets.json`, created automatically after the first successful write. The
`data/` directory is intentionally ignored by Git because it contains runtime data.

The menu supports:

1. Create a ticket
2. List all tickets
3. View one ticket
4. Assign a ticket to a fellow
5. Change status or reopen a resolved ticket
6. Show the unresolved work queue
7. Show reports
8. Save immediately
0. Exit

The app saves after successful create, assignment, and status-change operations.
If the JSON file is missing, the app starts fresh. If it is malformed or has
invalid records, the app displays an error instead of silently overwriting it.

## Ticket rules

- Categories: `Network`, `Hardware`, `Software`, `Other`
- Urgency: `low`, `medium`, `high`
- Affected-user count must be a positive integer.
- Priority rules are checked in this order:
  1. `high` urgency and at least 10 affected users → `critical`
  2. `high` urgency or at least 10 affected users → `high`
  3. `medium` urgency or at least 3 affected users → `medium`
  4. Otherwise → `low`
- IDs use `T001`, `T002`, ... and are generated from the largest numeric ID,
  so gaps and reloads do not create duplicates.
- Lifecycle: `open` → `in_progress` → `resolved`. A ticket must be assigned before
  it can move to `in_progress`. A resolved ticket can only be changed after an
  explicit transition back to `open`.
- The unresolved queue sorts by `critical`, `high`, `medium`, `low`, then by the
  numeric ticket ID in ascending order.

## Run the tests

From the repository root:

```bash
python -m unittest discover -s tests -v
```

The test suite covers creation, validation, priority rules, ID handling, workflow,
queue ordering, reports, JSON persistence, malformed data, and duplicate IDs.

## Project layout

```text
campusflow/
  tickets.py    # creation, validation, priority, ID generation
  workflow.py   # lookup, assignment, status transitions
  queue.py      # unresolved work queue
  reports.py    # ticket totals and breakdowns
  storage.py    # JSON loading and atomic saving
  cli.py        # repeating interactive menu
  __main__.py   # python -m campusflow entry point
tests/          # unittest test suite
docs/           # design decisions and AI learning-log guidance
```

## Team and assessment responsibilities

This implementation is AI-assisted starter work and does not substitute for the
assessment's collaboration evidence. Both fellows should understand the code, run
the tests, make meaningful contributions on their own branches, open pull requests,
review the partner's PR with at least two substantive observations, and obtain the
required partner approval before merging. Each fellow must independently record
three genuine AI-learning interactions, including one AI suggestion they verified
and corrected, improved, or rejected. Do not claim a review, approval, test, or
learning interaction that did not actually happen.
