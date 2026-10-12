import unittest

from campusflow.tickets import create_ticket
from campusflow.workflow import assign_ticket, change_status, find_ticket


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tickets = []
        self.ticket = create_ticket(
            self.tickets, "Campus Wi-Fi", "Network", "high", 12
        )

    def test_find_ticket_returns_matching_record(self):
        self.assertIs(find_ticket(self.tickets, "t001"), self.ticket)

    def test_find_missing_ticket_raises(self):
        with self.assertRaisesRegex(ValueError, "was not found"):
            find_ticket(self.tickets, "T099")

    def test_assign_ticket_trims_fellow_name(self):
        result = assign_ticket(self.tickets, "T001", "  Ada  ")
        self.assertIs(result, self.ticket)
        self.assertEqual(result["assigned_to"], "Ada")

    def test_blank_assignee_rejected_without_mutation(self):
        with self.assertRaisesRegex(ValueError, "non-empty"):
            assign_ticket(self.tickets, "T001", "  ")
        self.assertIsNone(self.ticket["assigned_to"])

    def test_cannot_start_unassigned_ticket(self):
        with self.assertRaisesRegex(ValueError, "Assign the ticket"):
            change_status(self.tickets, "T001", "in_progress")
        self.assertEqual(self.ticket["status"], "open")

    def test_assigned_ticket_can_move_to_in_progress(self):
        assign_ticket(self.tickets, "T001", "Ada")
        change_status(self.tickets, "T001", "in_progress")
        self.assertEqual(self.ticket["status"], "in_progress")

    def test_open_ticket_cannot_be_resolved_directly(self):
        with self.assertRaisesRegex(ValueError, "only move to in_progress"):
            change_status(self.tickets, "T001", "resolved")

    def test_in_progress_ticket_can_be_resolved(self):
        assign_ticket(self.tickets, "T001", "Ada")
        change_status(self.tickets, "T001", "in_progress")
        change_status(self.tickets, "T001", "resolved")
        self.assertEqual(self.ticket["status"], "resolved")

    def test_resolved_ticket_can_only_be_reopened(self):
        assign_ticket(self.tickets, "T001", "Ada")
        change_status(self.tickets, "T001", "in_progress")
        change_status(self.tickets, "T001", "resolved")
        with self.assertRaisesRegex(ValueError, "only be reopened"):
            change_status(self.tickets, "T001", "in_progress")
        change_status(self.tickets, "T001", "open")
        self.assertEqual(self.ticket["status"], "open")

    def test_resolved_ticket_cannot_be_assigned_until_reopened(self):
        assign_ticket(self.tickets, "T001", "Ada")
        change_status(self.tickets, "T001", "in_progress")
        change_status(self.tickets, "T001", "resolved")
        with self.assertRaisesRegex(ValueError, "reopened"):
            assign_ticket(self.tickets, "T001", "Ben")

    def test_unknown_status_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Status must be"):
            change_status(self.tickets, "T001", "waiting")


if __name__ == "__main__":
    unittest.main()
