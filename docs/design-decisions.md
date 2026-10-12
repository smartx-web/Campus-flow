# CampusFlow design decisions

This document records the implementation choices made for the current integrated
starter. Both fellows should review and discuss these choices; this file alone is
not evidence that a team discussion or approval has occurred.

## Data model

- Tickets are dictionaries collected in a list. The collection is passed to
  functions explicitly; business logic does not depend on module-level ticket state.
- Each ticket contains `id`, `title`, `category`, `urgency`, `affected_users`,
  `priority`, `status`, and `assigned_to`.
- A new ticket begins with status `open` and `assigned_to=None`.
- Creation validates every input before appending, so invalid input does not
  partially mutate the collection.

## Priority and IDs

- Priority rules are evaluated from most specific to least specific so the
  critical condition cannot be hidden by the broader high-priority condition.
- IDs use a `T` prefix and at least three digits. The next ID is one greater than
  the largest existing numeric ID rather than the list length. Invalid or duplicate
  stored IDs are rejected instead of silently repaired.
- Ticket deletion is not currently supported. If deletion is introduced, ID
  allocation must preserve a high-water mark so removed IDs are never reused.

## Workflow

- Valid lifecycle transitions are `open` → `in_progress` → `resolved`.
- Moving an open ticket to `in_progress` requires an assignee.
- A resolved ticket may only transition to `open`; this is the explicit reopen step.
  Assignment of a resolved ticket is rejected until it has been reopened.
- Business functions raise `ValueError`; the CLI catches these errors and displays
  a useful message. Business logic does not call `input()` or `print()`.

## Queue and reports

- The unresolved queue excludes tickets whose status is `resolved`.
- Queue ordering is critical, high, medium, low, then ascending numeric ticket ID.
- Reports return totals and breakdowns by priority, status, and category. They are
  computed from the current collection and are not stored as duplicated data.

## JSON persistence

- `load_tickets(path)` returns an empty list if the file does not exist.
- Malformed JSON, duplicate IDs, invalid IDs, missing required fields, and invalid
  stored status/priority values produce a clear error.
- `save_tickets(path, tickets)` validates the collection and writes to a temporary
  file before replacing the destination, reducing the chance of a partial write.
- The caller saves after successful mutations. Runtime data is stored in
  `data/tickets.json` and is excluded from version control.

## Limitations and future improvements

- This is a local single-user CLI, not a concurrent multi-user service. Two processes
  writing the same JSON file at the same time could overwrite each other's changes.
- JSON is appropriate for the assessment's small dataset but would not be ideal for
  many simultaneous users; a database with transactions would be a stronger next step.
- Assignee names are free text; the application does not maintain a fellow directory.
- There is no delete operation, authentication, audit history, or concurrent-write
  locking. These are outside the current scope.
