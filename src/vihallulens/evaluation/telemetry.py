"""Reading the GPU's temperature and clock, so a timing number can say whether to trust it.

Measured at T08: two runs back to back in one session showed three tiers with identical
workloads getting 10-15 % slower in the second run. The likely cause is the passively cooled
T4 dropping its clock as it heats, but nothing in that run recorded temperature, so it stayed a
guess. Recording it costs one subprocess call and turns "these timings may be off" into
"here is whether they were".

Used by the throughput measurement of T08 and by the encoder fine-tuning of T18, which is the
other place where several configurations are timed one after another.
"""

from __future__ import annotations

import subprocess

# Measured at T08: two runs back to back in one session showed three tiers with identical
# workloads getting 10-15 % slower in the second run. The likely cause is the passively cooled
# T4 dropping its clock as it heats, but nothing in the run recorded temperature, so it stayed
# a guess. Recording it costs one subprocess call per tier and makes the next run self-
# diagnosing instead.
NVIDIA_SMI_FIELDS = ("temperature.gpu", "clocks.current.sm", "clocks.max.sm", "utilization.gpu")

# How far the SM clock may fall over a session, in percentage points of its maximum, before
# the tiers stop being comparable with each other. Two points is roughly the size of the
# effect that would show up as the 10-15 % timing difference measured at T08.
CLOCK_DROP_POINTS = 2.0

# A temperature rise this large across the session is what turns a clock drop from "the driver
# did something" into "the card is shedding heat". Both are reported either way.
HEAT_RISE_C = 5.0


def parse_telemetry(line: str) -> dict | None:
    """Turn one nvidia-smi CSV row into numbers, or None when it is not usable.

    nvidia-smi answers "[N/A]" for fields a card does not expose rather than failing, so the
    row has to be checked field by field instead of trusted because the call succeeded.
    """
    parts = [part.strip() for part in line.split(",")]
    if len(parts) != len(NVIDIA_SMI_FIELDS):
        return None
    try:
        values = [float(part) for part in parts]
    except ValueError:
        return None

    temperature, current_clock, max_clock, utilisation = values
    reading = {
        "temperature_c": temperature,
        "sm_clock_mhz": current_clock,
        "sm_clock_max_mhz": max_clock,
        "utilization_pct": utilisation,
    }
    reading["clock_ratio"] = current_clock / max_clock if max_clock else float("nan")
    return reading


def gpu_telemetry() -> dict | None:
    """Temperature and clock of GPU 0 right now, or None when nvidia-smi cannot answer."""
    try:
        done = subprocess.run(
            ["nvidia-smi", f"--query-gpu={','.join(NVIDIA_SMI_FIELDS)}",
             "--format=csv,noheader,nounits", "--id=0"],
            capture_output=True, text=True, check=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return parse_telemetry(done.stdout.strip().splitlines()[0]) if done.stdout.strip() else None


def throttling_verdict(readings: list[dict]) -> tuple[bool, str]:
    """Did the card slow down over the session enough to make the tiers incomparable?

    The judgement rests on the *trend*, not on any single reading. An absolute rule such as
    "the clock is below 95 % of maximum" looks obvious and is wrong: a card sitting idle
    down-clocks on purpose, and the reading is taken just after a tier ends, so an idle value
    is entirely normal. Measured on a laptop card at rest: 1,500 of 2,100 MHz, 71 %, with
    nothing throttling at all.

    What does mean something is the clock being lower at the end of the session than at the
    start while the temperature climbed. That is the pattern which makes tiers measured late
    look slower than tiers measured early for reasons unrelated to the work being timed.
    """
    # ``value == value`` is False only for nan, which is what a card with no reported maximum
    # clock produces; such a reading carries no information about throttling.
    ratios = [
        item["clock_ratio"] for item in readings if item["clock_ratio"] == item["clock_ratio"]
    ]
    temperatures = [item["temperature_c"] for item in readings]
    if len(ratios) < 2:
        return False, "không đủ số đo xung nhịp để kết luận"

    clock_drop = (ratios[0] - ratios[-1]) * 100
    heat_rise = temperatures[-1] - temperatures[0]
    trend = (
        f"xung SM {ratios[0] * 100:.0f} % → {ratios[-1] * 100:.0f} % mức tối đa, "
        f"nhiệt độ {temperatures[0]:.0f} → {temperatures[-1]:.0f} °C"
    )

    if clock_drop > CLOCK_DROP_POINTS and heat_rise > HEAT_RISE_C:
        return True, f"{trend} — tụt xung kèm nóng lên, đúng dạng hạ xung vì nhiệt"
    if clock_drop > CLOCK_DROP_POINTS:
        return True, f"{trend} — xung tụt {clock_drop:.0f} điểm mà nhiệt không tăng mấy"
    if heat_rise > HEAT_RISE_C:
        return False, f"{trend} — nóng lên nhưng xung chưa tụt, tạm thời chưa ảnh hưởng"
    return False, f"{trend} — ổn định"
