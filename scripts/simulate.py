from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.loader import load_config
from engine.math_model import exact_line_rtp
from engine.simulator import simulate_preset


def main() -> None:
    spins = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    config = load_config(Path(__file__).resolve().parents[1] / "config.json")
    for name, preset in config["presets"].items():
        result = simulate_preset(preset, config["lines"], spins=spins)
        print(f"\n{name}")
        print(f"  exact base={exact_line_rtp(preset):.4%}")
        print(f"  sim base={result['base_rtp']:.4%}")
        print(f"  meter contribution={result['feature_contribution']:.4%}")
        print(f"  total RTP={result['total_rtp']:.4%}")
        print(f"  hit rate={result['hit_rate']:.4%}")
        print(f"  SD={result['sd']:.4f}")
        print(f"  max win={result['max_win']:.2f}x")
        print(f"  meter trigger={result['meter_trigger_rate']:.4%}")
        print(f"  avg feature win={result['avg_feature_win']:.4f}x")


if __name__ == "__main__":
    main()
