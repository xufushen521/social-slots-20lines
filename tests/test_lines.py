from pathlib import Path
import unittest

from engine.lines import evaluate_lines
from engine.loader import load_config


class LinesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_config(Path(__file__).resolve().parents[1] / "config.json")
        cls.preset = cls.config["presets"]["beginner"]

    def test_all_k_wins_all_twenty_lines(self) -> None:
        grid = [["K", "K", "K"] for _ in range(5)]
        wins = evaluate_lines(grid, self.preset, 1.0, self.config["lines"])
        self.assertEqual(len(wins), 20)
        k5 = self.preset["symbols"]["K"]["pays"]["5"]
        self.assertTrue(all(item["match"] == 5 for item in wins))
        self.assertTrue(all(item["win"] == k5 for item in wins))


if __name__ == "__main__":
    unittest.main()
