import unittest
from collections import deque

from termmy.termiohub.input_parser import State, parse


def make_test_dfa() -> State:
    # root
    root = State({}, False)

    # ESC is final and also a prefix
    esc = State({}, True)
    root.link(0x1B, esc)

    # ESC [ A
    bracket = State({}, False)
    esc.link(ord("["), bracket)
    up = State({}, True)
    bracket.link(ord("A"), up)

    # Simple one-byte token
    x = State({}, True)
    root.link(ord("X"), x)

    return root


class TestParse(unittest.TestCase):
    def setUp(self) -> None:
        self.dfa = make_test_dfa()
        self.timeout = 0.05

    def test_empty_queue_returns_none(self):
        q = deque()
        out = parse(q, self.dfa, self.timeout, latency_timeout=0.1, current_time=1.0)
        self.assertIsNone(out)
        self.assertEqual(len(q), 0)

    def test_unknown_byte_returns_single_char_and_consumes(self):
        q = deque([(b"Z", 1.0)])
        out = parse(q, self.dfa, self.timeout, latency_timeout=0.1, current_time=1.1)
        self.assertEqual(out, (b"Z", 1.0))
        self.assertEqual(len(q), 0)

    def test_final_non_prefix_returns_immediately(self):
        q = deque([(b"X", 1.0)])
        out = parse(q, self.dfa, self.timeout, latency_timeout=0.1, current_time=1.01)
        self.assertEqual(out, (b"X", 1.0))
        self.assertEqual(len(q), 0)

    def test_esc_within_timeout_waits_and_does_not_consume(self):
        q = deque([(b"\x1b", 1.0)])
        out = parse(q, self.dfa, self.timeout, latency_timeout=0.1, current_time=1.02)
        self.assertIsNone(out)
        self.assertEqual(list(q), [(b"\x1b", 1.0)])

    def test_esc_after_timeout_returns_esc_and_consumes(self):
        q = deque([(b"\x1b", 1.0)])
        out = parse(q, self.dfa, self.timeout, latency_timeout=0.1, current_time=1.2)
        self.assertEqual(out, (b"\x1b", 1.0))
        self.assertEqual(len(q), 0)

    def test_full_escape_sequence_returns_longest_match(self):
        q = deque([(b"\x1b", 1.0), (b"[", 1.01), (b"A", 1.02)])
        out = parse(q, self.dfa, self.timeout, latency_timeout=0.1, current_time=1.03)
        self.assertEqual(out, (b"\x1b[A", 1.0))
        self.assertEqual(len(q), 0)

    def test_unknown_continuation_returns_longest_prefix_and_pushes_back_unused(self):
        q = deque([(b"\x1b", 1.0), (b"[", 1.01), (b"B", 1.02)])
        out = parse(q, self.dfa, self.timeout, latency_timeout=0.1, current_time=1.06)
        self.assertEqual(out, (b"\x1b", 1.0))
        self.assertEqual(list(q), [(b"[", 1.01), (b"B", 1.02)])

    def test_timeout_mid_sequence_returns_longest_prefix_and_pushes_back_tail(self):
        q = deque([(b"\x1b", 1.0), (b"[", 1.01), (b"A", 1.20)])
        out = parse(q, self.dfa, self.timeout, latency_timeout=0.1, current_time=1.21)
        self.assertEqual(out, (b"\x1b", 1.0))
        self.assertEqual(list(q), [(b"[", 1.01), (b"A", 1.20)])


if __name__ == "__main__":
    unittest.main()
