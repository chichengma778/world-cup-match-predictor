# Methodology

Use the script output as a baseline, then calibrate it with football context.

## Quantitative Layers

1. Elo estimates team strength and a first-pass win/draw/loss split.
2. xG and xGA estimate expected goals for each side.
3. Poisson converts expected goals into scoreline probabilities.
4. Odds imply no-vig market probabilities when decimal 1X2 odds are available.
5. The blended probability combines model and market views:
   - With odds: Poisson 50%, Elo 25%, market 25%.
   - Without odds: Poisson 65%, Elo 35%.

The blend is not a guarantee. It is a disciplined baseline for the analyst to challenge.

## Calibration Checklist

Before finalizing, adjust confidence and narrative for:

- Confirmed or likely lineup changes.
- Core-player injury/suspension.
- Tactical mismatch, such as favorite struggling against low blocks.
- Set-piece mismatch.
- Travel, heat, humidity, altitude, pitch, and kickoff time.
- Tournament incentives: group table, goal difference, rotation, knockout risk tolerance.
- Market movement: odds shortening, favorite heat, handicap support, total-goal movement.

## Confidence Rules

Use high confidence only when:

- Model, odds, squad news, tactical profile, and motivation point in the same direction.
- The favorite has multiple scoring routes or the underdog has clear structural problems.
- There is no major lineup, schedule, or source conflict.

Use medium confidence when the preferred side is clear but one or two material variables can change the match.

Use low confidence when:

- Lineups are unknown and core players are doubtful.
- Odds and model disagree sharply.
- The match has strong draw paths.
- The predicted score cluster is wide.
- Weather, rotation, or tournament incentives can reshape the game state.

## Handicap Rules

Always identify the market:

- Ordinary 1X2: home/draw/away.
- Chinese sports lottery handicap: winning by the handicap margin matters.
- Asian handicap: quarter lines create half-win/half-loss outcomes.
- Over/under: depends on the posted total-goal line.

Do not say a favorite is a good handicap side only because it is likely to win.

## Reverse Scenario

Every report must include at least one path where the main call fails:

- Favorite fails to score early and the match turns into a low-tempo draw.
- Underdog scores first from transition or set piece.
- Early card, penalty, or injury breaks the model assumption.
- Favorite wins but slows down, failing to cover.
- Market overreacts to reputation and underrates defensive resilience.

## Disclaimer

State that predictions are probabilistic sports analysis, not financial or betting advice.
