from pathlib import Path
import unittest

from engine.loader import load_config
from engine.math_model import exact_line_rtp
from engine.simulator import simulate_preset


class SimulatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_config(Path(__file__).resolve().parents[1] / "config.json")

    def test_modes_and_meter(self) -> None:
        for preset in self.config["presets"].values():
            exact = exact_line_rtp(preset)
            result = simulate_preset(
                preset,
                self.config["lines"],
                spins=20_000,
                seed=7,
            )
            self.assertAlmostEqual(result["base_rtp"], exact, delta=0.15)
            self.assertGreater(result["feature_contribution"], 0)
            self.assertGreater(result["meter_trigger_rate"], 0)


if __name__ == "__main__":
    unittest.main()
