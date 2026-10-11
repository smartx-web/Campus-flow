import copy
import unittest

from campusflow.tickets import (
    calculate_priority,
    create_ticket,
    next_ticket_id,
    normalize_affected_users,
    normalize_category,
    normalize_title,
    normalize_urgency,
)


class PriorityTests(unittest.TestCase):
    def test_all_rules_and_boundaries(self):
        # Expected values are explicit requirements, not copied control flow.
        cases = [
            ("high", 1, "high"), ("high", 9, "high"),
            ("high", 10, "critical"), ("high", 15, "critical"),
            ("medium", 1, "medium"), ("medium", 9, "medium"),
            ("medium", 10, "high"), ("low", 1, "low"),
            ("low", 2, "low"), ("low", 3, "medium"),
            ("low", 9, "medium"), ("low", 10, "high"),
        ]
        for urgency, count, expected in cases:
            with self.subTest(urgency=urgency, count=count):
                self.assertEqual(calculate_priority(urgency, count), expected)

    def test_critical_rule_takes_precedence_over_high(self):
        self.assertEqual(calculate_priority("high", 10), "critical")

    def test_high_count_takes_precedence_over_medium_urgency(self):
        self.assertEqual(calculate_priority("medium", 10), "high")

    def test_priority_normalizes_cli_input(self):
        self.assertEqual(calculate_priority(" HIGH ", " 15 "), "critical")

    def test_priority_rejects_invalid_urgency(self):
        with self.assertRaisesRegex(ValueError, "Urgency"):
            calculate_priority("urgent", 10)

    def test_priority_rejects_invalid_count(self):
        with self.assertRaisesRegex(ValueError, "positive integer"):
            calculate_priority("low", 0)


class ValidationTests(unittest.TestCase):
    def test_title_is_trimmed_without_changing_inner_text(self):
        self.assertEqual(normalize_title("  Wi-Fi is down  "), "Wi-Fi is down")

    def test_blank_and_non_text_titles_are_rejected(self):
        for value in ("", " \t\n", None, 42, True):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Title"):
                    normalize_title(value)

    def test_every_category_accepts_case_variations(self):
        for value in ("Network", "Hardware", "Software", "Other"):
            with self.subTest(value=value):
                self.assertEqual(normalize_category(" " + value.swapcase() + " "), value)

    def test_invalid_categories_are_rejected(self):
        for value in ("", "Networking", "Laptop", None, 7):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Category"):
                    normalize_category(value)

    def test_every_urgency_accepts_case_variations(self):
        for value in ("low", "medium", "high"):
            self.assertEqual(normalize_urgency(" " + value.upper() + " "), value)

    def test_invalid_urgencies_are_rejected(self):
        for value in ("", "critical", "urgent", None, 7):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Urgency"):
                    normalize_urgency(value)

    def test_positive_integer_and_cli_digit_strings(self):
        for value, expected in ((1, 1), (15, 15), ("3", 3), (" 10 ", 10), ("001", 1)):
            with self.subTest(value=value):
                self.assertEqual(normalize_affected_users(value), expected)
                self.assertIs(type(normalize_affected_users(value)), int)

    def test_invalid_counts_including_bool_and_float_are_rejected(self):
        for value in (0, -1, 1.0, 2.5, True, False, "0", "-2", "1.0", "3.5",
                      "three", "", " ", None, [], "1e2", "+2", "３"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "positive integer"):
                    normalize_affected_users(value)


class CreationTests(unittest.TestCase):
    def test_required_example_and_exact_fields(self):
        tickets = []
        ticket = create_ticket(tickets, "Campus Wi-Fi is down", "Network", "high", 15)
        self.assertEqual(ticket, {
            "id": "T001", "title": "Campus Wi-Fi is down", "category": "Network",
            "urgency": "high", "affected_users": 15, "priority": "critical",
            "status": "open", "assigned_to": None,
        })
        self.assertEqual(tickets, [ticket])
        self.assertIs(tickets[0], ticket)

    def test_creation_normalizes_values(self):
        ticket = create_ticket([], "  Broken editor  ", "sOfTwArE", " LOW ", " 3 ")
        self.assertEqual((ticket["title"], ticket["category"], ticket["urgency"],
                          ticket["affected_users"], ticket["priority"]),
                         ("Broken editor", "Software", "low", 3, "medium"))

    def test_successive_ids_are_unique(self):
        tickets = []
        for _ in range(3):
            create_ticket(tickets, "Issue", "Other", "low", 1)
        self.assertEqual([t["id"] for t in tickets], ["T001", "T002", "T003"])

    def test_each_invalid_field_leaves_collection_unchanged(self):
        tickets = []
        create_ticket(tickets, "Existing", "Network", "high", 10)
        cases = [(" ", "Other", "low", 1), ("Issue", "Invalid", "low", 1),
                 ("Issue", "Other", "Invalid", 1), ("Issue", "Other", "low", 0)]
        for args in cases:
            before = copy.deepcopy(tickets)
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    create_ticket(tickets, *args)
                self.assertEqual(tickets, before)

    def test_failed_creation_does_not_consume_id(self):
        tickets = []
        with self.assertRaises(ValueError):
            create_ticket(tickets, "Issue", "Other", "low", -1)
        self.assertEqual(create_ticket(tickets, "Issue", "Other", "low", 1)["id"], "T001")

    def test_bad_stored_ids_prevent_mutation(self):
        tickets = [{"id": "bad", "title": "Keep me"}]
        before = copy.deepcopy(tickets)
        with self.assertRaisesRegex(ValueError, "invalid ID"):
            create_ticket(tickets, "Issue", "Other", "low", 1)
        self.assertEqual(tickets, before)

    def test_creation_rejects_non_list_collection(self):
        with self.assertRaisesRegex(ValueError, "list"):
            create_ticket({}, "Issue", "Other", "low", 1)


class IdTests(unittest.TestCase):
    def test_empty_collection_starts_at_one(self):
        self.assertEqual(next_ticket_id([]), "T001")

    def test_unsorted_ids_and_gaps_use_numeric_max(self):
        self.assertEqual(next_ticket_id([{"id": "T010"}, {"id": "T002"},
                                         {"id": "T009"}]), "T011")

    def test_reload_preserves_id_sequence(self):
        import json
        original = []
        create_ticket(original, "First", "Other", "low", 1)
        reloaded = json.loads(json.dumps(original))
        self.assertEqual(create_ticket(reloaded, "Next", "Other", "low", 1)["id"], "T002")

    def test_id_width_expands_beyond_999(self):
        self.assertEqual(next_ticket_id([{"id": "T999"}]), "T1000")
        self.assertEqual(next_ticket_id([{"id": "T1000"}]), "T1001")

    def test_invalid_stored_ids_are_rejected(self):
        for value in ("T000", "T01", "T0001", "t001", "T-01", "T001x", None, 1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    next_ticket_id([{"id": value}])

    def test_duplicate_ids_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            next_ticket_id([{"id": "T001"}, {"id": "T001"}])

    def test_missing_id_and_invalid_records_are_rejected(self):
        for tickets in ([{}], ["T001"], [None]):
            with self.subTest(tickets=tickets):
                with self.assertRaises(ValueError):
                    next_ticket_id(tickets)


if __name__ == "__main__":
    unittest.main()
