# Descriptive analysis + trend charts: India's CO₂ emissions in context (1990–2024)

> **Sample / demo analysis** built on public data – Our World in Data CO₂ dataset (CC BY 4.0), <https://github.com/owid/co2-data>.

- Script: [`analysis.py`](analysis.py) (pandas + matplotlib + reportlab). Downloads the dataset if missing, then writes everything below.
- 1-page summary: [`summary.pdf`](summary.pdf)
- Stats: [`stats/descriptive_stats_by_country.csv`](stats/descriptive_stats_by_country.csv) (count, mean, std, min, quartiles, max per country) and [`stats/key_metrics.csv`](stats/key_metrics.csv) (latest totals, per-capita, CAGR, world share, YoY growth median/std)
- Subset used: [`data/co2_subset_1990_2024.csv`](data/co2_subset_1990_2024.csv)

| | |
|---|---|
| ![Total CO2](charts/01_total_co2_trend.png) | ![Per capita](charts/02_per_capita_comparison.png) |

![India by source](charts/03_india_co2_by_source.png)

**Key findings (2024):** India 3,194 Mt CO₂ = 8.3% of world; 5.16%/yr compound growth since 1990 (fastest of India, China, US, EU); but only 2.2 t per person vs 4.7 t world average; coal = 66% of India's CO₂.

```bash
pip install pandas matplotlib reportlab
python analysis.py
```
