import unittest

from campusflow.queue import unresolved_queue
from campusflow.reports import ticket_report
from campusflow.tickets import create_ticket


class QueueAndReportTests(unittest.TestCase):
    def setUp(self):
        self.tickets = []
        create_ticket(self.tickets, "low later", "Other", "low", 1)      # T001 low
        create_ticket(self.tickets, "high", "Network", "high", 2)        # T002 high
        create_ticket(self.tickets, "critical", "Network", "high", 10)  # T003 critical
        create_ticket(self.tickets, "medium", "Hardware", "medium", 1)  # T004 medium
        create_ticket(self.tickets, "low earlier", "Software", "low", 1) # T005 low
        self.tickets[1]["status"] = "resolved"

    def test_queue_sorts_by_priority_then_numeric_id(self):
        queued = unresolved_queue(self.tickets)
        self.assertEqual([t["id"] for t in queued], ["T003", "T004", "T001", "T005"])

    def test_queue_does_not_mutate_original_list(self):
        original_ids = [ticket["id"] for ticket in self.tickets]
        unresolved_queue(self.tickets)
        self.assertEqual([ticket["id"] for ticket in self.tickets], original_ids)

    def test_report_totals_and_breakdowns(self):
        report = ticket_report(self.tickets)
        self.assertEqual(report["total"], 5)
        self.assertEqual(report["by_priority"]["critical"], 1)
        self.assertEqual(report["by_priority"]["low"], 2)
        self.assertEqual(report["by_status"]["resolved"], 1)
        self.assertEqual(report["by_status"]["open"], 4)
        self.assertEqual(report["by_category"]["Network"], 2)


if __name__ == "__main__":
    unittest.main()
