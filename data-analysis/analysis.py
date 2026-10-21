"""SAMPLE data analysis: India's CO2 emissions in global context (1990-2024).
Data: Our World in Data CO2 dataset (CC BY 4.0) https://github.com/owid/co2-data
Outputs: stats/*.csv, charts/*.png (300 dpi), summary.pdf (1 page).
Run:  python analysis.py   (downloads the CSV if missing)"""
import os, urllib.request
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mt

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data", "owid-co2-data.csv")
URL = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
os.makedirs(os.path.join(HERE, "charts"), exist_ok=True)
os.makedirs(os.path.join(HERE, "stats"), exist_ok=True)
if not os.path.exists(RAW):
    urllib.request.urlretrieve(URL, RAW)

ENT = ["India", "China", "United States", "European Union (27)", "World"]
COLS = ["country", "year", "population", "gdp", "co2", "co2_per_capita", "coal_co2", "oil_co2", "gas_co2", "cement_co2", "co2_growth_prct"]
df = pd.read_csv(RAW, usecols=COLS)
df = df[df.country.isin(ENT) & df.year.between(1990, 2024)].copy()
df.to_csv(os.path.join(HERE, "data", "co2_subset_1990_2024.csv"), index=False)
LAST = int(df.year.max())

# ---------- descriptive statistics ----------
desc = (df[df.country != "World"].groupby("country")[["co2", "co2_per_capita", "co2_growth_prct"]]
        .describe().round(2))
desc.to_csv(os.path.join(HERE, "stats", "descriptive_stats_by_country.csv"))

def cagr(s, y0, y1):
    a, b = s.loc[y0], s.loc[y1]
    return (b / a) ** (1 / (y1 - y0)) - 1

rows = []
for c in ENT:
    s = df[df.country == c].set_index("year")
    rows.append({
        "country": c,
        f"co2_{LAST}_mt": round(s.co2.loc[LAST], 1),
        f"co2_per_capita_{LAST}_t": round(s.co2_per_capita.loc[LAST], 2),
        "co2_1990_mt": round(s.co2.loc[1990], 1),
        "cagr_1990_2024_pct": round(100 * cagr(s.co2, 1990, LAST), 2),
        "cagr_2014_2024_pct": round(100 * cagr(s.co2, 2014, LAST), 2),
        "median_yoy_growth_pct": round(s.co2_growth_prct.loc[1991:].median(), 2),
        "std_yoy_growth_pct": round(s.co2_growth_prct.loc[1991:].std(), 2),
    })
key = pd.DataFrame(rows)
world = df[(df.country == "World") & (df.year == LAST)].co2.iloc[0]
key[f"share_of_world_{LAST}_pct"] = (100 * key[f"co2_{LAST}_mt"] / world).round(1)
key.to_csv(os.path.join(HERE, "stats", "key_metrics.csv"), index=False)
ind = df[df.country == "India"].set_index("year")
mix = ind.loc[LAST, ["coal_co2", "oil_co2", "gas_co2", "cement_co2"]]
mix_share = (100 * mix / ind.loc[LAST, "co2"]).round(1)

# ---------- charts ----------
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.alpha": .25, "axes.titleweight": "bold"})
COL = {"India": "#FF7A00", "China": "#C62828", "United States": "#1565C0", "European Union (27)": "#2E7D32", "World": "#555555"}
SRC = "Source: Our World in Data CO2 dataset (CC BY 4.0) | Sample analysis by Ayush Kumar"

fig, ax = plt.subplots(figsize=(10, 5.6))
for c in ENT[:-1]:
    s = df[df.country == c]
    ax.plot(s.year, s.co2, lw=2.6 if c == "India" else 1.8, color=COL[c], label=c)
    ax.annotate(c.replace(" (27)", ""), (s.year.iloc[-1], s.co2.iloc[-1]), xytext=(6, 0), textcoords="offset points", va="center", color=COL[c], fontsize=10)
ax.set_title(f"Annual CO\u2082 emissions, 1990\u2013{LAST}")
ax.set_ylabel("Million tonnes CO\u2082"); ax.yaxis.set_major_formatter(mt.StrMethodFormatter("{x:,.0f}"))
ax.set_xlim(1990, LAST + 6); ax.set_xticks(range(1990, LAST + 1, 5))
fig.text(0.01, 0.01, SRC, fontsize=8, color="#777"); fig.tight_layout(rect=(0, .03, 1, 1))
fig.savefig(os.path.join(HERE, "charts", "01_total_co2_trend.png"), dpi=300); plt.close(fig)

latest = df[df.year == LAST].set_index("country").co2_per_capita.reindex(ENT[:-1]).sort_values()
fig, ax = plt.subplots(figsize=(10, 5.6))
bars = ax.barh([c.replace(" (27)", "") for c in latest.index], latest.values, color=[COL[c] for c in latest.index])
wpc = df[(df.country == "World") & (df.year == LAST)].co2_per_capita.iloc[0]
ax.axvline(wpc, color="#555", ls="--", lw=1.4); ax.text(wpc + .15, -0.45, f"World avg {wpc:.1f} t", color="#555", fontsize=10)
for b, v in zip(bars, latest.values):
    ax.text(v + .2, b.get_y() + b.get_height() / 2, f"{v:.1f} t", va="center", fontsize=10)
ax.set_title(f"CO\u2082 per person, {LAST}"); ax.set_xlabel("Tonnes CO\u2082 per person"); ax.grid(axis="y", visible=False)
fig.text(0.01, 0.01, SRC, fontsize=8, color="#777"); fig.tight_layout(rect=(0, .03, 1, 1))
fig.savefig(os.path.join(HERE, "charts", "02_per_capita_comparison.png"), dpi=300); plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 5.6))
parts = ["coal_co2", "oil_co2", "gas_co2", "cement_co2"]
ax.stackplot(ind.index, [ind[p].fillna(0) for p in parts], labels=["Coal", "Oil", "Gas", "Cement"],
             colors=["#3E2723", "#FF7A00", "#42A5F5", "#9E9E9E"], alpha=.9)
ax.set_title(f"India: CO\u2082 by source, 1990\u2013{LAST}"); ax.set_ylabel("Million tonnes CO\u2082")
ax.yaxis.set_major_formatter(mt.StrMethodFormatter("{x:,.0f}")); ax.legend(loc="upper left", frameon=False)
ax.annotate("COVID-19 dip (2020)", (2020, ind.co2.loc[2020]), xytext=(2005, ind.co2.loc[2020] * 1.02),
            arrowprops=dict(arrowstyle="->", color="#333"), fontsize=10)
fig.text(0.01, 0.01, SRC, fontsize=8, color="#777"); fig.tight_layout(rect=(0, .03, 1, 1))
fig.savefig(os.path.join(HERE, "charts", "03_india_co2_by_source.png"), dpi=300); plt.close(fig)

# ---------- 1-page PDF summary ----------
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
st = getSampleStyleSheet(); small = ParagraphStyle("s", parent=st["BodyText"], fontSize=8.6, leading=11.2)
k = key.set_index("country")
i_ = k.loc["India"]; c_ = k.loc["China"]; u_ = k.loc["United States"]
doc = SimpleDocTemplate(os.path.join(HERE, "summary.pdf"), pagesize=A4, leftMargin=14*mm, rightMargin=14*mm, topMargin=11*mm, bottomMargin=9*mm)
story = [Paragraph(f"India's CO<sub>2</sub> Emissions in Context, 1990\u2013{LAST}", st["Title"]),
         Paragraph("<i>Sample / demo analysis for portfolio purposes. Public data: Our World in Data (CC BY 4.0).</i>", small), Spacer(1, 4)]
bul = [
    f"<b>Scale:</b> India emitted {i_[f'co2_{LAST}_mt']:,.0f} Mt CO<sub>2</sub> in {LAST} ({i_[f'share_of_world_{LAST}_pct']}% of the world), up from {i_['co2_1990_mt']:,.0f} Mt in 1990 \u2013 a {i_['cagr_1990_2024_pct']}% compound annual growth rate, the fastest of the four economies compared.",
    f"<b>Per person it is still low:</b> {i_[f'co2_per_capita_{LAST}_t']} t per person vs a world average of {k.loc['World', f'co2_per_capita_{LAST}_t']} t, China {c_[f'co2_per_capita_{LAST}_t']} t and the US {u_[f'co2_per_capita_{LAST}_t']} t.",
    f"<b>Momentum:</b> over the last decade (2014\u2013{LAST}) India grew {i_['cagr_2014_2024_pct']}%/yr, China {c_['cagr_2014_2024_pct']}%/yr, while the US ({u_['cagr_2014_2024_pct']}%/yr) and EU ({k.loc['European Union (27)','cagr_2014_2024_pct']}%/yr) declined.",
    f"<b>Volatility:</b> India's median year-on-year growth is {i_['median_yoy_growth_pct']}% (std. dev. {i_['std_yoy_growth_pct']} pts); the sharpest drop was 2020 (COVID-19), fully recovered by 2021.",
    f"<b>Energy mix:</b> coal is {mix_share['coal_co2']}% of India's {LAST} fossil+cement CO<sub>2</sub>, oil {mix_share['oil_co2']}%, cement {mix_share['cement_co2']}%, gas {mix_share['gas_co2']}% \u2013 the trend is driven by coal power.",
]
story += [Paragraph("\u2022 " + b, small) for b in bul] + [Spacer(1, 5)]
tbl = [["Economy", f"CO2 {LAST} (Mt)", "Per capita (t)", "World share", "CAGR 1990\u20132024", "CAGR 2014\u20132024"]]
for c in ENT:
    r = k.loc[c]
    tbl.append([c, f"{r[f'co2_{LAST}_mt']:,.0f}", f"{r[f'co2_per_capita_{LAST}_t']:.2f}", f"{r[f'share_of_world_{LAST}_pct']:.1f}%", f"{r['cagr_1990_2024_pct']:.2f}%", f"{r['cagr_2014_2024_pct']:.2f}%"])
t = Table(tbl, hAlign="LEFT")
t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2937")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                       ("FONTSIZE", (0, 0), (-1, -1), 8), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
                       ("ALIGN", (1, 1), (-1, -1), "RIGHT"), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5), ("TOPPADDING", (0, 0), (-1, -1), 2.5)]))
story += [t, Spacer(1, 5)]
w = 89*mm; h = w * 5.6 / 10
img = lambda f, ww=w: Image(os.path.join(HERE, "charts", f), width=ww, height=ww * 5.6 / 10)
g = Table([[img("01_total_co2_trend.png"), img("02_per_capita_comparison.png")]], colWidths=[w + 2*mm] * 2)
story += [g, img("03_india_co2_by_source.png", 120*mm),
          Paragraph("Method: Python (pandas, matplotlib). Descriptive stats per country in stats/descriptive_stats_by_country.csv; key metrics in stats/key_metrics.csv. Reproduce with <i>python analysis.py</i>.", small)]
doc.build(story)
print(key.to_string(index=False)); print("mix", mix_share.to_dict())
