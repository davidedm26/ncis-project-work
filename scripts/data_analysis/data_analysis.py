import csv
from pathlib import Path

import matplotlib.pyplot as plt


def _set_plot_style() -> None:
    for style in ("seaborn-v0_8-darkgrid", "seaborn-v0_8-whitegrid", "ggplot"):
        try:
            plt.style.use(style)
            return
        except OSError:
            continue


def _read_iperf2_udp_csv(path: Path):
    time_s = []
    throughput_mbps = []

    with path.open(newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) < 12:
                continue

            interval = row[6].strip()
            if "-" not in interval:
                continue

            try:
                total_datagrams = int(row[11])
            except ValueError:
                total_datagrams = 0
            if total_datagrams < 0:
                continue

            try:
                t_end = float(interval.split("-", 1)[1])
                bandwidth_bps = float(row[8])
            except ValueError:
                continue

            time_s.append(t_end)
            throughput_mbps.append(bandwidth_bps / 1e6)

    return time_s, throughput_mbps


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    up_csv = script_dir / "up.csv"
    down_csv = script_dir / "down.csv"

    _set_plot_style()

    time_up, throughput_up = _read_iperf2_udp_csv(up_csv)
    time_down, throughput_down = _read_iperf2_udp_csv(down_csv)

    if not time_up or not time_down:
        raise SystemExit(
            "No samples parsed from CSV files. Verify paths and iPerf2 UDP CSV format: "
            f"up={up_csv} down={down_csv}"
        )

    fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
    ax.plot(
        time_up,
        throughput_up,
        label="Video Streaming",
        linewidth=2.6,
        color="tab:red",
    )
    ax.plot(
        time_down,
        throughput_down,
        label="Other Traffic",
        linewidth=2.6,
        color="tab:blue",
    )
    ax.set_title("Throughput comparison")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Throughput (Mbps)")
    ax.legend()
    ax.grid(True, which="major", alpha=0.25)
    fig.savefig(script_dir / "throughput_compared.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()

