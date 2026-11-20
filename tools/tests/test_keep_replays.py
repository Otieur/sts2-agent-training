"""Offline tests for tools/keep_replays.py (a temporary save folder; the real one is never touched)."""
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import keep_replays as kr  # noqa: E402


def recording(version="v0.111.1", commit="cc1f9462", body=b"fight"):
    v, c = version.encode(), commit.encode()
    return struct.pack("<i", len(v)) + v + struct.pack("<i", len(c)) + c + body * 20


class TestKeepReplays(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.saves = root / "steam"
        self.dest = root / "kept"
        self.index = self.dest / "player-index.json"
        for prof in ("76561190000000000/profile1", "76561190000000000/modded/profile1", "76561190000000000/modded/profile2"):
            d = self.saves / prof / "replays"
            d.mkdir(parents=True)
            (d / "latest.mcr").write_bytes(recording(body=prof.encode()))

    def tearDown(self):
        self.tmp.cleanup()

    def test_header(self):
        self.assertEqual(kr.read_header(recording()), ("v0.111.1", "cc1f9462"))
        self.assertIsNone(kr.read_header(b"\x00" * 10))

    def test_sources_skip_the_agent_and_hide_the_id(self):
        labels = [label for label, _ in kr.sources(self.saves)]
        self.assertEqual(sorted(labels), ["modded-profile1", "profile1"])
        self.assertFalse(any("7656119" in label for label in labels))

    def test_copies_once_and_leaves_the_source_alone(self):
        label, f = next(s for s in kr.sources(self.saves) if s[0] == "profile1")
        before = (f.read_bytes(), f.stat().st_mtime_ns)
        kept = kr.keep_if_new(label, f, self.dest, self.index, settle=0)
        self.assertIsNotNone(kept)
        self.assertEqual(kept.read_bytes(), before[0])
        self.assertNotIn("7656119", str(kept))
        self.assertIsNone(kr.keep_if_new(label, f, self.dest, self.index, settle=0))   # same content: not kept twice
        self.assertEqual((f.read_bytes(), f.stat().st_mtime_ns), before)                # source unchanged
        f.write_bytes(recording(body=b"next fight"))                                      # the game's next fight
        self.assertIsNotNone(kr.keep_if_new(label, f, self.dest, self.index, settle=0))
        self.assertEqual(len(kr.load_index(self.index)), 2)

    def test_incomplete_file_is_not_kept(self):
        label, f = next(s for s in kr.sources(self.saves) if s[0] == "profile1")
        f.write_bytes(b"\x08\x00")
        self.assertIsNone(kr.keep_if_new(label, f, self.dest, self.index, settle=0))


if __name__ == "__main__":
    unittest.main()
