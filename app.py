from __future__ import annotations

from pathlib import Path

import streamlit as st

from engine.lines import evaluate_lines
from engine.loader import load_config
from engine.math_model import exact_line_rtp
from engine.reels import draw_grid
from engine.simulator import meter_points


START_BALANCE = 1000.0

st.set_page_config(page_title="20 Lines Social", page_icon="🎰", layout="wide")


def ready_result(preset: dict, lines: list[list[int]], bet: float) -> dict:
    return {
        "base_grid": draw_grid(preset),
        "base_wins": [],
        "fs_grid": None,
        "fs_wins": [],
        "win": 0.0,
        "points": 0,
        "triggered": False,
        "message": "按 Spin 开始。",
    }


def do_spin(preset: dict, lines: list[list[int]], bet: float) -> None:
    if st.session_state.balance < bet:
        return

    st.session_state.balance -= bet
    grid = draw_grid(preset)
    wins = evaluate_lines(grid, preset, bet, lines)
    base_win = sum(item["win"] for item in wins)
    points = meter_points(wins, preset)
    meter_value = st.session_state.meter + points
    fs_grid = None
    fs_wins: list[dict] = []
    fs_win = 0.0
    triggered = meter_value >= preset["meter"]["threshold"]

    if triggered:
        for _ in range(preset["meter"]["free_spins"]):
            fs_grid = draw_grid(preset)
            fs_wins = evaluate_lines(fs_grid, preset, bet, lines)
            fs_win += (
                sum(item["win"] for item in fs_wins)
                * preset["meter"]["free_spin_multiplier"]
            )
        st.session_state.meter = 0
        message = (
            f"蓄水池触发：本次 {points} 分，获得 "
            f"{preset['meter']['free_spins']} 次 Free Spin。"
        )
    else:
        st.session_state.meter = meter_value
        message = "本次没有中奖。" if base_win == 0 else f"本次中奖 {base_win:.2f}。"

    total_win = min(base_win + fs_win, preset["max_win"] * bet)
    st.session_state.balance += total_win
    for item in fs_wins:
        item["win"] *= preset["meter"]["free_spin_multiplier"]

    st.session_state.result = {
        "base_grid": grid,
        "base_wins": wins,
        "fs_grid": fs_grid,
        "fs_wins": fs_wins,
        "win": total_win,
        "points": points,
        "triggered": triggered,
        "message": message,
    }


def render_grid(grid: list[list[str]], winning_symbols: set[str]) -> None:
    cells = ["<table style='border-collapse:separate;border-spacing:8px;margin:0 auto;'>"]
    for row in range(len(grid[0])):
        cells.append("<tr>")
        for reel in grid:
            symbol = reel[row]
            border = "3px solid #16a34a" if symbol in winning_symbols else "1px solid #cbd5e1"
            cells.append(
                "<td style='width:74px;height:74px;text-align:center;"
                "vertical-align:middle;font-size:24px;font-weight:700;"
                "background:#e5e7eb;color:#111827;"
                f"border:{border};border-radius:12px;'>{symbol}</td>"
            )
        cells.append("</tr>")
    cells.append("</table>")
    st.markdown("".join(cells), unsafe_allow_html=True)


def wins_table(wins: list[dict]) -> None:
    if not wins:
        st.caption("无中奖线。")
        return
    st.dataframe(
        [
            {
                "线": item["line"],
                "符号": item["symbol"],
                "连数": item["match"],
                "赔率": item["pay"],
                "赢": item["win"],
            }
            for item in wins
        ],
        use_container_width=True,
        hide_index=True,
    )


config_path = Path(__file__).with_name("config.json")
try:
    config = load_config(config_path)
except Exception as exc:
    st.error(f"配置读取失败：{exc}")
    st.stop()

preset_names = list(config["presets"].keys())
preset_name = st.sidebar.selectbox(
    "场次",
    preset_names,
    index=preset_names.index(config["default_preset"]),
    format_func=lambda name: "Beginner" if name == "beginner" else "Advanced",
)
preset = config["presets"][preset_name]

if st.session_state.get("active_preset") != preset_name:
    st.session_state.active_preset = preset_name
    st.session_state.balance = START_BALANCE
    st.session_state.bet = preset["bet"]["default"]
    st.session_state.meter = 0
    st.session_state.result = ready_result(
        preset, config["lines"], preset["bet"]["default"]
    )

bet = st.sidebar.selectbox(
    "总下注",
    preset["bet"]["levels"],
    index=preset["bet"]["levels"].index(st.session_state.bet),
    format_func=lambda value: f"{value:.2f}",
)
st.session_state.bet = bet

if st.sidebar.button("重置余额与蓄水池"):
    st.session_state.balance = START_BALANCE
    st.session_state.meter = 0
    st.session_state.result = ready_result(preset, config["lines"], bet)
    st.rerun()

summary = preset.get("math_summary", {})
st.sidebar.metric("设计 RTP", f"{summary.get('total_rtp', 0):.2%}")
st.sidebar.caption("20 条固定线 · 蓄水池 Feature")

st.title("20 Lines Social")
st.caption(
    f"{'Beginner' if preset_name == 'beginner' else 'Advanced'} · 5×3 · "
    f"20 lines · Max Win {preset['max_win']}x"
)

metrics = st.columns(4)
metrics[0].metric("余额", f"{st.session_state.balance:.2f}")
metrics[1].metric("总下注", f"{bet:.2f}")
metrics[2].metric("本次中奖", f"{st.session_state.result['win']:.2f}")
metrics[3].metric("蓄水池", f"{st.session_state.meter}/{preset['meter']['threshold']}")

st.progress(
    min(1.0, st.session_state.meter / preset["meter"]["threshold"]),
    text=f"蓄水池 {st.session_state.meter} / {preset['meter']['threshold']}",
)

if st.button(f"Spin（{bet:.2f}）", type="primary", use_container_width=True):
    do_spin(preset, config["lines"], bet)
    st.rerun()

result = st.session_state.result
st.subheader("Base 结果")
if result["triggered"]:
    st.success(result["message"])
elif result["win"] > 0:
    st.info(result["message"])
else:
    st.caption(result["message"])

render_grid(result["base_grid"], {item["symbol"] for item in result["base_wins"]})
wins_table(result["base_wins"])

if result["fs_grid"]:
    st.subheader("蓄水池 Free Spin")
    st.caption(
        f"本次蓄水池 +{result['points']} 分 · "
        f"Free Spin x{preset['meter']['free_spin_multiplier']:.1f}"
    )
    render_grid(result["fs_grid"], {item["symbol"] for item in result["fs_wins"]})
    wins_table(result["fs_wins"])

with st.expander("20 条线图"):
    st.dataframe(
        [
            {"Line": index, **{f"R{reel + 1}": row + 1 for reel, row in enumerate(line)}}
            for index, line in enumerate(config["lines"], start=1)
        ],
        use_container_width=True,
        hide_index=True,
    )

with st.expander("RTP 摘要（面试可讲）"):
    st.write(f"精确 Base RTP：{exact_line_rtp(preset):.2%}")
    st.write(f"蓄水池贡献：{summary.get('feature_rtp', 0):.2%}")
    st.write(f"设计总 RTP：{summary.get('total_rtp', 0):.2%}")
    st.write(f"1M 模拟总 RTP：{summary.get('sim_total_rtp', 0):.2%}")
    st.write(f"1M hit rate：{summary.get('hit_rate', 0):.2%}")
    st.write(f"1M SD：{summary.get('sd', 0):.3f}")
    st.write(f"1M 最大观察值：{summary.get('max_win_observed', 0):.2f}x")
    st.write(f"蓄水池触发率：{summary.get('meter_trigger_rate', 0):.3%}")
    st.write("赔率口径：总下注倍数 / 中奖线。")
