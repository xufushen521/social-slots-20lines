from pathlib import Path
import unittest

from engine.loader import load_config


class ConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_config(Path(__file__).resolve().parents[1] / "config.json")

    def test_twenty_unique_lines(self) -> None:
        self.assertEqual(len(self.config["lines"]), 20)
        self.assertEqual(len({tuple(line) for line in self.config["lines"]}), 20)

    def test_two_modes(self) -> None:
        self.assertEqual(set(self.config["presets"]), {"beginner", "advanced"})
        for preset in self.config["presets"].values():
            self.assertEqual(preset["grid"]["reels"], 5)
            self.assertEqual(preset["grid"]["rows"], 3)
            self.assertEqual(preset["meter"]["threshold"], 100)


if __name__ == "__main__":
    unittest.main()
