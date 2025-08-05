import statistics as stats
from datetime import datetime
from typing import Dict, List, Any, Tuple
import json
from pathlib import Path
# --------------------------------------------------------------------------
# 1)  ――――  low-level helpers
# --------------------------------------------------------------------------

MetricArray = List[float]


def delta_calc(*, baseline_avg: float, comparison_avg: float) -> float:
    """
    Return percentage change: +0.12 → +12 %, –0.05 → –5 %.
    """
    if baseline_avg == 0:                       # avoid /0
        return 0.0
    return (comparison_avg - baseline_avg) / baseline_avg


def baseline_variance(*, values: MetricArray) -> float:
    """
    Sample stdev (n-1).  Returns 0 for |values| < 2.
    """
    # print(values)
    return stats.stdev(values) if len(values) > 1 else 0.0


def significance_flag(*, delta: float, stdev: float,
                      sigma: float = 3.0) -> bool:
    """
    Heuristic significance test:  |delta|  >  sigma * stdev.
    Default ≈ 95 % confidence if data are normal.
    """
    # print(delta, sigma, stdev, 'test')
    return abs(delta) > sigma * stdev


# --------------------------------------------------------------------------
# 2)  ――――  mid-level helpers
# --------------------------------------------------------------------------

METRIC_CODES = [
    "bounce_rate",
    "conversion_rate",
    "revenue",
    "search_conversion_rate",
    "unique_visitors",
]


def _pivot(rows: List[Dict[str, Any]]) -> Dict[str, MetricArray]:
    """Turn list-of-dict rows into {metric: [values…]} for METRIC_CODES."""
    return {
        m: [row[m] for row in rows if m in row]   # tolerate sparse rows
        for m in METRIC_CODES
    }


def _mean(values: MetricArray) -> float:
    return stats.mean(values) if values else 0.0


# --------------------------------------------------------------------------
# 3)  ――――  top-level processing
# --------------------------------------------------------------------------

def process_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point.
    Returns the nested report structure described in the prompt.
    """
    # ---------- basic prep ---------- #
    start = datetime.fromisoformat(payload["start_date"])
    end   = datetime.fromisoformat(payload["end_date"])

    ref   = _pivot(payload["reference_metrics"])
    curr  = _pivot(payload["current_metrics"])

    initiatives = [
        i for i in payload.get("initiatives", [])
        if start <= datetime.fromisoformat(i["launch_timestamp"]) <= end
    ]

    output: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # 3-A) OVERALL layer (reference vs current, no initiative split)
    # ------------------------------------------------------------------
    overall = {}
    for m in METRIC_CODES:
        ref_arr, cur_arr = ref[m], curr[m]
        ref_avg, cur_avg = _mean(ref_arr), _mean(cur_arr)
        delta   = delta_calc(baseline_avg=ref_avg, comparison_avg=cur_avg)
        stdev   = baseline_variance(values=ref_arr)/ref_avg
        sig     = significance_flag(delta=delta, stdev=stdev)

        overall[m] = {
            "current_avg": round(cur_avg, 4),
            "change": f"{delta:+.2%}",
            "overall_sig": sig,
        }

    # ------------------------------------------------------------------
    # 3-B) INITIATIVE layer
    # ------------------------------------------------------------------
    if not initiatives:        # -------- NO_INITIATIVE fallback -------- #
        init_id = "NO_INITIATIVE"
        output[init_id] = {
            "overall": {"metrics": _enrich(overall, init_id, True)}
        }
    else:                      # -------------- per-initiative --------- #
        for init in initiatives:
            init_id   = init["initiative_id"]
            init_name = init["initiative_name"]
            launch_ts = datetime.fromisoformat(init["launch_timestamp"])

            init_metrics: Dict[str, Any] = {}

            for m in METRIC_CODES:
                # split current window at launch
                pre  = [row[m] for row in payload["current_metrics"]
                        if datetime.fromisoformat(row["date"]) < launch_ts]
                post = [row[m] for row in payload["current_metrics"]
                        if datetime.fromisoformat(row["date"]) >= launch_ts]

                if not pre or not post:          # nothing to compare
                    continue

                pre_avg, post_avg = _mean(pre), _mean(post)
                delta = delta_calc(baseline_avg=pre_avg,
                                   comparison_avg=post_avg)
                stdev = baseline_variance(values=pre)
                sig   = significance_flag(delta=delta, stdev=stdev)

                init_metrics[m] = {
                    "current_avg": round(post_avg, 4),
                    "change": f"{delta:+.2%}",
                    "initiative_sig": sig,
                    "overall_sig": overall[m]["overall_sig"],
                }

            if init_metrics:
                output[init_id] = {
                    "initiative_name": init_name,
                    "overall": {"metrics":
                                _enrich(init_metrics, init_id, False)}
                }

    return output


# --------------------------------------------------------------------------
# 4)  ――――  explanation helper
# --------------------------------------------------------------------------

def _enrich(metrics_dict: Dict[str, Any],
            init_id: str,
            is_no_initiative: bool) -> Dict[str, Any]:
    """
    Add natural-language explanations in-place and return the dict.

    If initiative_sig TRUE →  
      "Post-launch *[m]* changed {initiative_delta_%} vs. pre-launch,  
        indicating impact from **{init.initiative_name}**."  
    • Else-if overall_sig TRUE →  
      "Change significant but not clearly tied to the **{init.initiative_name}**."  
    • Else →  
      "The change is very small and falls within the usual range, so it's not meaningful."        
    """
    for m, rec in metrics_dict.items():
        # sig_field = "overall_sig" if is_no_initiative else "initiative_sig"
        print(rec)
        significant_init = rec.get("initiative_sig", False)
        significant_overall = rec["overall_sig"]

        if is_no_initiative:
            if significant_overall:
                rec["explanation"] = (
                    "Change may be due to ongoing impact from earlier "
                    "initiatives or external factors. Consider expanding "
                    "the date window."
                )
            else:
                rec["explanation"] = (
                    "The change is very small and falls within the usual range, so it is not meaningful."
                )
        else:
            if significant_init:
                rec["explanation"] = (
                    f"Post-launch [metric_codes] changed [initiative_delta] vs. pre-launch, indicating impact from [initiative_name]"
                )
            elif significant_overall:
                rec["explanation"] = (
                    f"Change significant but not clearly tied to the [initiative_name]"
                )
            else:
                rec["explanation"] = (
                    "The change is very small (statistically) and falls within the usual range, so it is not meaningful."
                )
    return metrics_dict





if __name__ == "__main__":
    fixture_path = Path(__file__).parent / "data" / "test_data1.json"
    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture not found: {fixture_path}")  

    payload = json.loads(fixture_path.read_text())


    report = process_payload(payload)
    print(json.dumps(report, indent=2))