from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.loader import load_config
from engine.math_model import exact_line_rtp


def main() -> None:
    config = load_config(Path(__file__).resolve().parents[1] / "config.json")
    for name, preset in config["presets"].items():
        print(f"{name}: exact base RTP={exact_line_rtp(preset):.4%}")


if __name__ == "__main__":
    main()
