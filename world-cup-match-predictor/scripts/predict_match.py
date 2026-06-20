#!/usr/bin/env python3
"""World Cup football match probability and scoreline model.

Input: JSON file path or stdin.
Output: JSON with expected goals, WDL probabilities, scorelines, totals, BTTS,
confidence, and warnings.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


ResultProbs = Dict[str, float]


def as_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def normalize(probs: Mapping[str, float]) -> ResultProbs:
    total = sum(max(0.0, float(v)) for v in probs.values())
    if total <= 0:
        keys = list(probs.keys())
        return {key: 1.0 / len(keys) for key in keys}
    return {key: max(0.0, float(value)) / total for key, value in probs.items()}


def decimal_odds_to_probs(odds: Mapping[str, Any]) -> Optional[ResultProbs]:
    raw: ResultProbs = {}
    for key in ("home", "draw", "away"):
        value = as_float(odds.get(key))
        if value is None or value <= 1.0:
            return None
        raw[key] = 1.0 / value
    return normalize(raw)


def elo_probs(
    home_elo: Optional[float],
    away_elo: Optional[float],
    neutral_site: bool,
    home_advantage: float,
) -> Tuple[ResultProbs, List[str]]:
    warnings: List[str] = []
    if home_elo is None or away_elo is None:
        warnings.append("Elo missing; using neutral 1X2 prior.")
        return {"home": 0.365, "draw": 0.270, "away": 0.365}, warnings

    adjusted_diff = home_elo - away_elo
    if not neutral_site:
        adjusted_diff += home_advantage

    home_no_draw = 1.0 / (1.0 + 10.0 ** (-adjusted_diff / 400.0))
    draw = clamp(0.275 - abs(home_no_draw - 0.5) * 0.12, 0.205, 0.285)
    non_draw = 1.0 - draw
    return normalize(
        {
            "home": non_draw * home_no_draw,
            "draw": draw,
            "away": non_draw * (1.0 - home_no_draw),
        }
    ), warnings


def estimate_expected_goals(data: Mapping[str, Any]) -> Tuple[float, float, List[str]]:
    warnings: List[str] = []
    neutral_site = bool(data.get("neutral_site", True))
    home_elo = as_float(data.get("home_elo"))
    away_elo = as_float(data.get("away_elo"))

    h_for = as_float(data.get("home_xg_for"))
    h_against = as_float(data.get("home_xg_against"))
    a_for = as_float(data.get("away_xg_for"))
    a_against = as_float(data.get("away_xg_against"))

    if None not in (h_for, h_against, a_for, a_against):
        home_goals = math.sqrt(max(0.05, h_for) * max(0.05, a_against))
        away_goals = math.sqrt(max(0.05, a_for) * max(0.05, h_against))
    else:
        warnings.append("xG/xGA incomplete; expected goals estimated from Elo and tournament defaults.")
        elo_diff = 0.0
        if home_elo is not None and away_elo is not None:
            elo_diff = clamp(home_elo - away_elo, -450.0, 450.0)
        home_goals = 1.27 + elo_diff / 900.0
        away_goals = 1.17 - elo_diff / 1050.0

    if not neutral_site:
        home_goals += 0.12
        away_goals -= 0.04

    adjustments = data.get("adjustments") or {}
    if not isinstance(adjustments, Mapping):
        adjustments = {}

    home_attack = as_float(adjustments.get("home_attack"), 0.0) or 0.0
    away_attack = as_float(adjustments.get("away_attack"), 0.0) or 0.0
    home_defense = as_float(adjustments.get("home_defense"), 0.0) or 0.0
    away_defense = as_float(adjustments.get("away_defense"), 0.0) or 0.0
    home_delta = as_float(adjustments.get("home_goal_delta"), 0.0) or 0.0
    away_delta = as_float(adjustments.get("away_goal_delta"), 0.0) or 0.0

    home_goals = home_goals * (1.0 + home_attack + away_defense) + home_delta
    away_goals = away_goals * (1.0 + away_attack + home_defense) + away_delta

    return clamp(home_goals, 0.15, 4.5), clamp(away_goals, 0.15, 4.5), warnings


def poisson_pmf(lam: float, max_goals: int) -> List[float]:
    probs = []
    for goals in range(max_goals + 1):
        probs.append(math.exp(-lam) * (lam ** goals) / math.factorial(goals))
    return probs


def score_matrix(home_goals: float, away_goals: float, max_goals: int) -> List[Dict[str, Any]]:
    home_pmf = poisson_pmf(home_goals, max_goals)
    away_pmf = poisson_pmf(away_goals, max_goals)
    rows: List[Dict[str, Any]] = []
    total = 0.0
    for h, hp in enumerate(home_pmf):
        for a, ap in enumerate(away_pmf):
            prob = hp * ap
            total += prob
            rows.append(
                {
                    "home_goals": h,
                    "away_goals": a,
                    "score": f"{h}-{a}",
                    "probability": prob,
                    "result": "home" if h > a else "away" if a > h else "draw",
                    "total_goals": h + a,
                    "btts": h > 0 and a > 0,
                }
            )
    for row in rows:
        row["probability"] = row["probability"] / total if total else 0.0
    return rows


def wdl_from_scores(rows: Iterable[Mapping[str, Any]]) -> ResultProbs:
    probs = {"home": 0.0, "draw": 0.0, "away": 0.0}
    for row in rows:
        probs[str(row["result"])] += float(row["probability"])
    return normalize(probs)


def totals_from_scores(rows: Iterable[Mapping[str, Any]], line: float) -> Dict[str, float]:
    under = push = over = btts_yes = 0.0
    for row in rows:
        prob = float(row["probability"])
        total_goals = float(row["total_goals"])
        if total_goals > line:
            over += prob
        elif total_goals < line:
            under += prob
        else:
            push += prob
        if row["btts"]:
            btts_yes += prob
    return {
        "line": line,
        "over": over,
        "push": push,
        "under": under,
        "btts_yes": btts_yes,
        "btts_no": 1.0 - btts_yes,
    }


def blend_probs(poisson: ResultProbs, elo: ResultProbs, market: Optional[ResultProbs]) -> Tuple[ResultProbs, Dict[str, float]]:
    if market:
        weights = {"poisson": 0.50, "elo": 0.25, "market": 0.25}
    else:
        weights = {"poisson": 0.65, "elo": 0.35, "market": 0.0}
    blended = {
        key: poisson[key] * weights["poisson"]
        + elo[key] * weights["elo"]
        + ((market or {}).get(key, 0.0) * weights["market"])
        for key in ("home", "draw", "away")
    }
    return normalize(blended), weights


def confidence_label(blended: ResultProbs, warnings: List[str], market: Optional[ResultProbs]) -> Dict[str, Any]:
    ordered = sorted(blended.items(), key=lambda item: item[1], reverse=True)
    top_key, top_prob = ordered[0]
    gap = top_prob - ordered[1][1]
    level = "low"
    if top_prob >= 0.54 and gap >= 0.18 and len(warnings) <= 1:
        level = "high"
    elif top_prob >= 0.43 and gap >= 0.08 and len(warnings) <= 3:
        level = "medium"

    reasons = [f"Top result is {top_key} at {top_prob:.1%}; gap to second is {gap:.1%}."]
    if warnings:
        reasons.append("Data warnings lower confidence.")
    if market is None:
        reasons.append("No market odds were supplied.")
    return {"level": level, "top_result": top_key, "top_probability": top_prob, "gap": gap, "reasons": reasons}


def pct(value: float) -> float:
    return round(value * 100.0, 2)


def rounded_probs(probs: Mapping[str, float]) -> Dict[str, float]:
    return {key: pct(value) for key, value in probs.items()}


def predict(data: Mapping[str, Any], max_goals: int = 8) -> Dict[str, Any]:
    warnings: List[str] = []
    home_team = str(data.get("home_team") or "Home")
    away_team = str(data.get("away_team") or "Away")
    neutral_site = bool(data.get("neutral_site", True))
    home_advantage = as_float(data.get("home_advantage_elo"), 60.0) or 60.0

    if home_team == "Home" or away_team == "Away":
        warnings.append("Team names missing or incomplete.")

    expected_home, expected_away, eg_warnings = estimate_expected_goals(data)
    warnings.extend(eg_warnings)

    scores = score_matrix(expected_home, expected_away, max_goals)
    poisson_probs = wdl_from_scores(scores)

    elo, elo_warnings = elo_probs(
        as_float(data.get("home_elo")),
        as_float(data.get("away_elo")),
        neutral_site,
        home_advantage,
    )
    warnings.extend(elo_warnings)

    odds = data.get("odds")
    market = decimal_odds_to_probs(odds) if isinstance(odds, Mapping) else None
    if odds and market is None:
        warnings.append("Odds supplied but invalid; market probabilities ignored.")

    blended, weights = blend_probs(poisson_probs, elo, market)
    top_scores = sorted(scores, key=lambda row: row["probability"], reverse=True)[:8]

    line = as_float(data.get("over_under_line"), 2.5)
    totals = totals_from_scores(scores, line if line is not None else 2.5)
    confidence = confidence_label(blended, warnings, market)

    return {
        "match": {
            "home_team": home_team,
            "away_team": away_team,
            "competition": data.get("competition"),
            "match_time": data.get("match_time"),
            "venue": data.get("venue"),
            "neutral_site": neutral_site,
        },
        "expected_goals": {
            "home": round(expected_home, 3),
            "away": round(expected_away, 3),
            "total": round(expected_home + expected_away, 3),
        },
        "probabilities_percent": {
            "poisson": rounded_probs(poisson_probs),
            "elo": rounded_probs(elo),
            "market_no_vig": rounded_probs(market) if market else None,
            "blended": rounded_probs(blended),
            "blend_weights": weights,
        },
        "top_scorelines": [
            {
                "score": row["score"],
                "probability_percent": pct(float(row["probability"])),
                "result": row["result"],
            }
            for row in top_scores
        ],
        "totals_percent": {
            key: round(value, 2) if key == "line" else pct(value) if isinstance(value, float) else value
            for key, value in totals.items()
        },
        "confidence": confidence,
        "warnings": warnings,
        "analyst_notes": [
            "Use blended probabilities as the baseline, then calibrate with lineup, tactical, schedule, weather, and market context.",
            "If confirmed lineups or odds movement contradict this output, lower confidence or rerun with updated adjustments.",
            "Predictions are probabilistic research and not betting advice.",
        ],
    }


def read_input(path: Optional[str]) -> Dict[str, Any]:
    if path:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return json.load(sys.stdin)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Predict football match WDL and score probabilities.")
    parser.add_argument("input", nargs="?", help="Path to input JSON. Reads stdin when omitted.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--max-goals", type=int, default=8, help="Maximum goals per team in score matrix.")
    args = parser.parse_args(argv)

    try:
        data = read_input(args.input)
        output = predict(data, max_goals=max(5, min(args.max_goals, 12)))
    except Exception as exc:  # noqa: BLE001 - CLI should return readable JSON errors.
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1

    print(json.dumps(output, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
