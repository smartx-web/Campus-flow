import json
import tempfile
import unittest
from pathlib import Path

from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.path = Path(self.temp_dir.name) / "tickets.json"

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(load_tickets(self.path), [])

    def test_save_and_reload_preserves_tickets_and_next_id(self):
        tickets = []
        create_ticket(tickets, "Wi-Fi", "Network", "high", 10)
        save_tickets(self.path, tickets)
        loaded = load_tickets(self.path)
        self.assertEqual(loaded, tickets)
        next_ticket = create_ticket(loaded, "Broken mouse", "Hardware", "low", 1)
        self.assertEqual(next_ticket["id"], "T002")

    def test_malformed_json_has_clear_error(self):
        self.path.write_text('{"not valid":', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            load_tickets(self.path)

    def test_non_list_json_is_rejected(self):
        self.path.write_text(json.dumps({"tickets": []}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "JSON list"):
            load_tickets(self.path)

    def test_duplicate_ids_are_rejected(self):
        tickets = []
        create_ticket(tickets, "One", "Other", "low", 1)
        duplicate = dict(tickets[0])
        tickets.append(duplicate)
        with self.assertRaisesRegex(ValueError, "duplicate IDs"):
            save_tickets(self.path, tickets)

    def test_missing_required_field_is_rejected(self):
        ticket = {
            "id": "T001", "title": "Wi-Fi", "category": "Network",
            "urgency": "high", "affected_users": 10, "priority": "critical",
            "status": "open",
        }
        self.path.write_text(json.dumps([ticket]), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "missing required field"):
            load_tickets(self.path)


if __name__ == "__main__":
    unittest.main()
