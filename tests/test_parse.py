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

class TestState(unittest.TestCase):
    def test_from_bytes_builds_linear_chain_and_final(self):
        root = State.from_bytes(b"ABC", is_final=True)

        s1 = root.single_transit(ord("A"))
        self.assertIsNotNone(s1); assert s1 is not None # For type checker
        self.assertFalse(root.is_final)
        
        s2 = s1.single_transit(ord("B"))
        self.assertIsNotNone(s2); assert s2 is not None # For type checker
        self.assertFalse(s1.is_final)

        s3 = s2.single_transit(ord("C"))
        self.assertIsNotNone(s3); assert s3 is not None # For type checker
        self.assertTrue(s3.is_final)
        self.assertEqual(s3.transition, {})

    def test_numbers_self_loop(self):
        state = State.numbers(is_final=True)
        self.assertTrue(state.is_final)
        for i in range(10):
            self.assertIs(state.single_transit(ord(str(i))), state)
        self.assertIsNone(state.single_transit(ord("A")))

    def test_link_duplicate_key_raises(self):
        root = State({}, False)
        root.link(ord("X"), State({}, True))
        with self.assertRaises(ValueError):
            root.link(ord("X"), State({}, False))

    def test_from_constructor_list_mixed_bytes_and_callable(self):
        dfa = State.from_constructor_list(
            [
                b"\x1b[<35;",
                State.numbers,
                b";",
                State.numbers,
                b"M",
            ],
            is_final=True,
        )
        final_state = dfa
        for b in b"\x1b[<35;55;21M":
            final_state = final_state.single_transit(b)
            self.assertIsNotNone(final_state)
            assert final_state is not None # For type checker
        self.assertIsNotNone(final_state)
        self.assertTrue(final_state.is_final)

    def test_from_constructor_list_invalid_item_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            State.from_constructor_list([b"A", 123])  # type: ignore[list-item]

    def test_from_constructor_list_missing_linkage_before_callable_raises(self):
        with self.assertRaises(ValueError):
            State.from_constructor_list([State.numbers, State.numbers])

class TestMergeStates(unittest.TestCase):
    def assert_accepts(self, dfa: State, seq: bytes) -> None:
        state = dfa.multi_transit(seq)
        self.assertIsNotNone(state)
        assert state is not None  # For type checker
        self.assertTrue(state.is_final)

    def assert_rejects(self, dfa: State, seq: bytes) -> None:
        state = dfa.multi_transit(seq)
        self.assertTrue(state is None or not state.is_final)
    
    # Base cases
    
    def test_merge_0_states(self):
        out = State.merge(*[])
        self.assertFalse(out.is_final)
        self.assertEqual(out.transition, {})
    
    def test_merge_1_non_finalstate(self):
        out = State.merge(*[State({}, False)])
        self.assertFalse(out.is_final)
        self.assertEqual(out.transition, {})

    def test_merge_1_final_state(self):
        out = State.merge(*[State({}, True)])
        self.assertTrue(out.is_final)
        self.assertEqual(out.transition, {})
    
    def test_merge_2_small_states(self):
        s1 = State({ord("A"): State({}, True)}, False)
        s2 = State({ord("B"): State({}, False)}, False)
        out = State.merge(*[s1, s2])
        self.assertFalse(out.is_final)
        self.assertIn(ord("A"), out.transition)
        self.assertIn(ord("B"), out.transition)
        trans_a = out.single_transit(ord("A"))
        trans_b = out.single_transit(ord("B"))
        self.assertIsNotNone(trans_a); assert trans_a is not None # For type checker
        self.assertIsNotNone(trans_b); assert trans_b is not None # For type checker
        self.assertTrue(trans_a.is_final)
        self.assertFalse(trans_b.is_final)

    def test_merge_shared_prefix_combines_finality(self):
        s1 = State.from_bytes(b"AB", is_final=True)
        s2 = State.from_bytes(b"AB", is_final=False)
        out = State.merge(s1, s2)
        self.assert_accepts(out, b"AB")

    def test_merge_disjoint_sequences(self):
        s1 = State.from_bytes(b"ab", is_final=True)
        s2 = State.from_bytes(b"xy", is_final=True)
        out = State.merge(s1, s2)
        self.assert_accepts(out, b"ab")
        self.assert_accepts(out, b"xy")
        self.assert_rejects(out, b"a")
        self.assert_rejects(out, b"x")
        self.assert_rejects(out, b"zz")

    def test_merge_revisited_neighbor_links_all_symbols(self):
        loop_digits = State.numbers(is_final=False)
        literal_a = State.from_bytes(b"A", is_final=True)
        out = State.merge(loop_digits, literal_a)
        
        for d in b"0123456789":
            self.assertIsNotNone(out.single_transit(d), f"{d}")

        self.assert_accepts(out, b"A")

    def test_merge_root_is_final_if_any_input_root_is_final(self):
        non_final = State({}, False)
        final = State({}, True)
        out = State.merge(non_final, final)
        self.assertTrue(out.is_final)
        self.assertEqual(out.transition, {})

    def test_merge_two_loops_and_literal(self):
        digits = State.numbers(is_final=False)
        letters = State({}, False)
        letters.link(ord("a"), letters)
        letters.link(ord("b"), letters)
        letters.link(ord("!"), State({}, True))

        out = State.merge(digits, letters)

        self.assert_accepts(out, b"ab!")
        self.assert_rejects(out, b"ab")

        for d in b"0123456789":
            self.assertIsNotNone(out.single_transit(d))

    def test_merge_overlapping_prefixes_distinct_terminals(self):
        left = State.from_bytes(b"car", is_final=True)
        right = State.from_bytes(b"cat", is_final=True)
        out = State.merge(left, right)

        self.assert_accepts(out, b"car")
        self.assert_accepts(out, b"cat")
        self.assert_rejects(out, b"ca")
        self.assert_rejects(out, b"cap")

    def test_merge_order_invariance_for_language(self):
        s1 = State.from_bytes(b"hi", is_final=True)
        s2 = State.from_bytes(b"ho", is_final=True)
        s3 = State.from_bytes(b"hey", is_final=True)

        merged_a = State.merge(s1, s2, s3)
        merged_b = State.merge(s3, s1, s2)

        accepted = [b"hi", b"ho", b"hey"]
        rejected = [b"h", b"ha", b"hez", b"hello"]

        for seq in accepted:
            self.assert_accepts(merged_a, seq)
            self.assert_accepts(merged_b, seq)

        for seq in rejected:
            self.assert_rejects(merged_a, seq)
            self.assert_rejects(merged_b, seq)
    
    
        


class TestParse(unittest.TestCase):
    def setUp(self) -> None:
        self.dfa = make_test_dfa()
        self.timeout = 0.05
        self.latency_timeout = 0.25

    def test_empty_queue_returns_none(self):
        q = deque()
        out = parse(
            q, self.dfa, self.timeout,
            latency_timeout=self.latency_timeout, current_time=1.0
        )
        self.assertIsNone(out)
        self.assertEqual(len(q), 0)

    def test_unknown_byte_returns_single_char_and_consumes(self):
        q = deque([(b"Z", 1.0)])
        out = parse(
            q, self.dfa, self.timeout,
            latency_timeout=self.latency_timeout, current_time=1.1
        )
        self.assertEqual(out, (b"Z", 1.0))
        self.assertEqual(len(q), 0)

    def test_final_non_prefix_returns_immediately(self):
        q = deque([(b"X", 1.0)])
        out = parse(
            q, self.dfa, self.timeout,
            latency_timeout=self.latency_timeout, current_time=1.01
        )
        self.assertEqual(out, (b"X", 1.0))
        self.assertEqual(len(q), 0)

    def test_esc_within_timeout_waits_and_does_not_consume(self):
        q = deque([(b"\x1b", 1.0)])
        out = parse(
            q, self.dfa, self.timeout,
            latency_timeout=self.latency_timeout, current_time=1.02
        )
        self.assertIsNone(out)
        self.assertEqual(list(q), [(b"\x1b", 1.0)])

    def test_esc_after_timeout_returns_esc_and_consumes(self):
        q = deque([(b"\x1b", 1.0)])
        out = parse(
            q, self.dfa, self.timeout,
            latency_timeout=self.latency_timeout, current_time=1.2
        )
        self.assertEqual(out, (b"\x1b", 1.0))
        self.assertEqual(len(q), 0)

    def test_full_escape_sequence_returns_longest_match(self):
        q = deque([(b"\x1b", 1.0), (b"[", 1.01), (b"A", 1.02)])
        out = parse(
            q, self.dfa, self.timeout,
            latency_timeout=self.latency_timeout, current_time=1.03
        )
        self.assertEqual(out, (b"\x1b[A", 1.0))
        self.assertEqual(len(q), 0)

    def test_unknown_continuation_returns_longest_prefix_and_pushes_back_unused(self):
        q = deque([(b"\x1b", 1.0), (b"[", 1.01), (b"B", 1.02)])
        out = parse(
            q, self.dfa, self.timeout,
            latency_timeout=self.latency_timeout, current_time=1.06
        )
        self.assertEqual(out, (b"\x1b", 1.0))
        self.assertEqual(list(q), [(b"[", 1.01), (b"B", 1.02)])

    def test_timeout_mid_sequence_returns_longest_prefix_and_pushes_back_tail(self):
        q = deque([(b"\x1b", 1.0), (b"[", 1.01), (b"A", 1.20)])
        out = parse(
            q, self.dfa, self.timeout,
            latency_timeout=self.latency_timeout, current_time=1.21
        )
        self.assertEqual(out, (b"\x1b", 1.0))
        self.assertEqual(list(q), [(b"[", 1.01), (b"A", 1.20)])


if __name__ == "__main__":
    unittest.main()
