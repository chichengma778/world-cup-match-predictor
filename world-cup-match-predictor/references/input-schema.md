# Input Schema

Use JSON for `scripts/predict_match.py`. Fields are optional unless marked required.

## Required

```json
{
  "home_team": "France",
  "away_team": "Senegal"
}
```

For a neutral World Cup venue, use the listed first team as `home_team` only as a display side.

## Recommended Fields

```json
{
  "competition": "2026 FIFA World Cup",
  "match_time": "2026-06-17 03:00 Asia/Shanghai",
  "venue": "MetLife Stadium",
  "neutral_site": true,
  "home_elo": 2050,
  "away_elo": 1800,
  "home_xg_for": 2.0,
  "home_xg_against": 0.9,
  "away_xg_for": 1.3,
  "away_xg_against": 1.1,
  "odds": {"home": 1.55, "draw": 4.10, "away": 6.20},
  "opening_odds": {"home": 1.62, "draw": 3.95, "away": 5.80},
  "over_under_line": 2.5,
  "asian_handicap": {"team": "home", "line": -1.25, "price": 1.95},
  "adjustments": {
    "home_attack": 0.00,
    "away_attack": 0.00,
    "home_defense": 0.00,
    "away_defense": 0.00,
    "home_goal_delta": 0.00,
    "away_goal_delta": 0.00
  },
  "notes": ["Neutral venue", "Home side has one attacking injury doubt"]
}
```

## Field Meaning

| Field | Meaning |
| --- | --- |
| `neutral_site` | `true` for most World Cup matches unless there is a material host advantage. |
| `home_elo`, `away_elo` | Team ratings. Any consistent Elo scale is acceptable. |
| `home_xg_for`, `away_xg_for` | Recent or tournament-adjusted expected goals for. |
| `home_xg_against`, `away_xg_against` | Recent or tournament-adjusted expected goals against. |
| `odds` | Decimal 1X2 odds. Used to calculate no-vig market probability. |
| `opening_odds` | Decimal 1X2 opening odds, used by the analyst for movement commentary. |
| `over_under_line` | Main total-goals line, usually 2.0, 2.25, 2.5, 2.75, or 3.0. |
| `asian_handicap` | Optional Asian handicap context; the script records it but the final report must interpret it. |
| `adjustments.*_attack` | Multiplicative attack adjustment. Example: `-0.10` means reduce that team's attack expectation by 10%. |
| `adjustments.*_defense` | Defensive weakness adjustment applied to the opponent's attack. Example: `home_defense: -0.08` lowers away goals; `home_defense: 0.10` raises away goals. |
| `adjustments.*_goal_delta` | Direct goal expectation delta after percentage adjustments. |

## Interpreting Missing Data

- Missing odds: rely on Elo and Poisson/xG only; say market calibration is unavailable.
- Missing xG: the script estimates expected goals from Elo and tournament defaults; lower confidence.
- Missing Elo: the script uses xG and market data; lower confidence.
- Missing lineups or injuries: do not claim lineups are confirmed; flag this as a live-data risk.
