# Engineer A integration proposal

These contracts are proposed by Engineer A. Engineer B must review and agree;
this document does not claim a discussion or agreement that has not occurred.

- Store tickets in a `list[dict]`. Pass the collection explicitly; no globals.
- `create_ticket(tickets, title, category, urgency, affected_users)` validates all
  inputs, appends exactly one dictionary, and returns that same dictionary.
- Required fields: id, title, category, urgency, affected_users, priority, status,
  assigned_to. New tickets are `open` and unassigned (`None`).
- Business logic raises `ValueError` with useful messages. The future CLI catches
  it and displays the message. Business logic does not call `input()` or `print()`.
- Titles are trimmed; categories use canonical title case; urgency uses lowercase.
  Surrounding whitespace is accepted. Counts accept positive Python integers or
  ASCII digit strings from CLI input. Booleans, floats and decimal strings fail.
- IDs use `T` plus a minimum of three digits. Generate max numeric ID + 1 from
  the current collection, not len(collection) + 1. Reject malformed/duplicate
  stored IDs instead of attempting an unsafe repair. Deletion is outside scope;
  if later supported, persistence must track a high-water mark to prevent reuse
  after deleting the largest ID.
- Priority follows the four specified rules in order; it is deterministic Python.
- Engineer B owns assignment, lifecycle, queue, reports and their tests. Resolved
  tickets must not be changed until explicit reopen; creation never edits a ticket.
- JSON persistence and the repeating CLI menu remain shared integration work.
  Proposed `load_tickets(path) -> list[dict]` and `save_tickets(path, tickets)` live
  in `campusflow/storage.py`. Missing files return an empty list; malformed JSON
  raises a clear error. Save atomically and do not overwrite invalid existing data.
- Caller saves after a successful operation. A failed save must be surfaced and
  handled during integration; Engineer A's module alone guarantees only validation
  failures leave the collection unchanged.
- Unit tests exercise business functions directly. A JSON round-trip test checks
  ID generation after reload, not the unimplemented filesystem storage feature.
