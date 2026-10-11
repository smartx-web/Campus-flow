# AI-assisted implementation notes — Engineer A

These are AI-authored implementation/verification notes, not evidence that either
fellow independently learned, wrote code, or reviewed a partner's PR. Each fellow
must add their own genuine interactions, explanations and verification evidence.

## 1. First-match priority rules
Learning question: Why must critical be checked before high?
AI explanation: A high-urgency ticket affecting 10 people satisfies both conditions;
returning high first would make critical unreachable.
Verification: `PriorityTests` explicitly covers high/9 -> high, high/10 -> critical,
medium/10 -> high, and low/2 -> low versus low/3 -> medium.

## 2. Suggestion rejected: len(tickets) + 1 for IDs
Candidate shortcut: Use the list length to generate the next ID.
Correction: IDs may be unsorted or contain gaps after reload. Scan numeric IDs and
use max + 1; validate duplicates and malformed IDs first.
Verification: `test_unsorted_ids_and_gaps_use_numeric_max` uses T010, T002, T009 and
expects T011. Tests cover JSON round-trip and rollover from T999 to T1000.
This is an AI-generated critique, not a fellow's independent correction.

## 3. Integer validation trap
Learning question: Is isinstance(value, int) enough for affected_users?
AI explanation: Python bool is an int subclass. Accepting True would store one user
from invalid input. `int(1.5)` also truncates invalid decimal input.
Decision: Require exact int type or positive ASCII digit text; do not coerce floats.
Verification: Tests reject True, False, 1.0, 2.5, decimal strings, zero and negatives.

## Fellow completion required
For each of at least three real interactions, record your question, AI response,
your own understanding, the check you ran and what you changed or rejected. Add
actual dates and outputs. Explain one independent correction in your own words.
Do not relabel the notes above as personal learning evidence.
