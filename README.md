# CampusFlow

A Python command-line campus helpdesk project. **Engineer A's contribution is
implemented; the complete CLI product is not integrated yet.** Standard library only.

## Engineer A: implemented

- Validated ticket creation with all eight required fields.
- Exact first-match priority calculation.
- Consistent title, category, urgency and affected-user normalization.
- Unique numeric IDs derived from existing records, including after JSON reload.
- Automated tests for boundaries, invalid input, mutation safety and ID handling.

Run tests from the repository root with Python 3:

```bash
python -m unittest discover -s tests -v
```

Use the creation contract from the future CLI:

```python
from campusflow.tickets import create_ticket

tickets = []  # Replace with load_tickets(path) after storage is implemented.
ticket = create_ticket(tickets, "Campus Wi-Fi is down", "Network", "high", "15")
print(ticket)  # T001, critical, open, assigned_to=None
```

Business functions raise `ValueError`; catch it at the CLI boundary and display the
message. No third-party packages, framework, database, AI SDK or API key are needed.

## Integration still required

Engineer B contributes assignment, workflow, work queue, reports and matching tests.
Both engineers agree the contracts, integrate JSON file storage and the repeating
CLI menu, run the full suite on main, and demonstrate the complete application.
See `docs/design-decisions.md` and `docs/ai-learning-log.md`.

Each fellow must contribute real code and tests on their own branch, author a PR,
review the partner's PR and receive genuine partner approval before merging. This
AI-assisted contribution and its notes do not replace those learning/review duties.
Runtime data belongs in ignored `data/tickets.json`; do not commit personal data.
