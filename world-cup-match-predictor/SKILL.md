---
name: world-cup-match-predictor
description: 世界杯足球赛前胜平负、比分、进球数和盘口风险预测 skill。Use when the user asks for World Cup, FIFA World Cup, international football, soccer match prediction, score prediction, win-draw-loss probabilities, Poisson/Elo/xG modeling, odds-calibrated analysis, Asian handicap, over-under, match report generation, or post-match prediction calibration.
---

# World Cup Match Predictor

Use this skill to produce a risk-aware World Cup football prediction report that combines:

- User-provided match facts, injuries, odds, xG, Elo, form, and tactical context.
- Optional live web verification when the user allows browsing and current information matters.
- A deterministic Python model for Elo, Poisson score distribution, xG, odds-implied probabilities, over/under, BTTS, and confidence.
- Expert calibration for tactics, lineup uncertainty, schedule, weather, motivation, and market risk.

Never present the prediction as certain. Treat all outputs as research and analysis, not betting advice.

## Workflow

1. Clarify the match list if the user did not name exact fixtures.
2. Verify the date and time basis before predicting: user timezone, local venue timezone, and source display time.
3. Collect inputs from the user first. If the user allows browsing, verify current schedule, injuries, expected lineups, odds, weather, and venue details with sources.
4. Normalize the data into the JSON shape in `references/input-schema.md`.
5. Run the model script:

```bash
python3 world-cup-match-predictor/scripts/predict_match.py match.json --pretty
```

6. Use the model output as a quantitative baseline, then adjust the narrative using `references/methodology.md`.
7. Write the final deep report using `references/report-template.md`.
8. If this is a recurring/daily prediction task and prior predictions are available, start with a short post-match calibration table before new predictions.

## Data Rules

- Prefer user-provided data when it is explicit and timestamped.
- When browsing is available, use it for current facts that can change: squads, injuries, suspensions, expected lineups, odds, venue, weather, and match schedule.
- If sources disagree, list the conflict and lower confidence.
- If browsing is unavailable or not allowed, state that current information may be stale and base the report on provided inputs plus model assumptions.
- Do not invent missing live data such as confirmed lineups, odds movement, or injuries.

## Model Use

Run `scripts/predict_match.py` when the user asks for:

- Win/draw/loss probabilities.
- Exact score prediction.
- Over/under or total-goal ranges.
- BTTS (both teams to score).
- A model-backed deep report.
- Comparison between model probability and market odds.

The script has no third-party dependencies. It accepts a JSON file or stdin and emits JSON.

Minimum useful input:

```json
{
  "home_team": "France",
  "away_team": "Senegal",
  "neutral_site": true,
  "home_elo": 2050,
  "away_elo": 1800,
  "home_xg_for": 2.0,
  "home_xg_against": 0.9,
  "away_xg_for": 1.3,
  "away_xg_against": 1.1,
  "odds": {"home": 1.55, "draw": 4.10, "away": 6.20}
}
```

If xG or Elo is unavailable, still run the script with available fields; it will warn about assumptions.

## Prediction Principles

- Separate ordinary win/draw/loss from Asian handicap, Chinese sports lottery handicap, and over/under.
- Distinguish a team winning from a team covering the handicap.
- Do not overrate favorites only because their market odds are short.
- Do not underrate disciplined Asian, African, CONCACAF, or underdog national teams in tournament settings.
- Do not underrate elite individual match-winners against low blocks.
- Downgrade confidence for missing lineups, core injuries, conflicting odds, extreme weather, early tournament uncertainty, or tactical mismatch.
- Include at least one reverse scenario explaining how the main prediction fails.

## Required Output

Write the report in Chinese unless the user requests another language.

Include these sections:

1. Data basis and freshness.
2. Model baseline: expected goals, win/draw/loss probabilities, top scores, total-goal tendency.
3. Team profile: form, tactical style, attack/defense data, injuries, schedule, physical condition.
4. Key matchups and tactical details.
5. Market and handicap analysis when odds or handicap data are provided.
6. Final prediction: win/draw/loss, confidence, primary score, two backup scores, over/under, BTTS, handicap view.
7. Reverse scenario and biggest uncertainty.
8. Disclaimer.

End with this summary table:

| Item | Prediction |
| --- | --- |
| Win/draw/loss |  |
| Confidence | High / Medium / Low |
| Primary score |  |
| Backup scores |  |
| Expected goals |  |
| Over/under |  |
| BTTS |  |
| Handicap view |  |
| Key reasons |  |
| Biggest uncertainty |  |
| Reverse scenario |  |
| Disclaimer | Research only, not betting advice |

## Resources

- Read `references/input-schema.md` when preparing model input or explaining required fields.
- Read `references/methodology.md` when interpreting model outputs and calibrating with tactical or market context.
- Read `references/report-template.md` when writing the final report.
- Use `scripts/predict_match.py` for deterministic probability and score calculations.
