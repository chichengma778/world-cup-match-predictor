# World Cup Match Predictor Skill

一个用于 Codex 的世界杯足球赛前预测 skill，支持深度赛前分析和可执行 Python 概率模型。

## 能做什么

- 胜平负概率预测
- 精确比分分布
- 期望进球、大小球、双方进球
- Elo / Poisson / xG / 赔率混合校准
- 伤停、战术、赛程、盘口和反向剧本分析
- 中文深度报告模板

## 快速试跑

```bash
python3 world-cup-match-predictor/scripts/predict_match.py examples/sample-match.json --pretty
```

也可以通过 stdin 传入 JSON：

```bash
python3 world-cup-match-predictor/scripts/predict_match.py --pretty < examples/sample-match.json
```

最小输入示例：

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
  "odds": {"home": 1.55, "draw": 4.10, "away": 6.20},
  "over_under_line": 2.5
}
```

## 目录

```text
world-cup-match-predictor/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── input-schema.md
│   ├── methodology.md
│   └── report-template.md
└── scripts/predict_match.py
```

## 免责声明

本项目仅用于足球赛事研究、概率建模和数据讨论，不构成投注建议或确定性结论。
