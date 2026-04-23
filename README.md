# hipstarr-streaming-decay-analysis

**Afrobeats vs Latin Pop — Global Asset Retention & Identity Density Index**

A six-month comparative Spotify streaming analysis across 26 tracks (13 Afrobeats, 13 Latin Pop) from 2019 to 2024. Exponential decay modelling, city-level audience geography, and Spotify-only catalogue valuation.

**By Ekene Ahuche · Hipstarr Music Research · Lagos, 2026**
**[@ekenemike_](https://x.com/ekenemike_) · [ekenemike.substack.com](https://ekenemike.substack.com)**

---

## Problem

The dominant narrative around Afrobeats streaming is one of global breakthrough. But a closer look at the data raises a harder question: is Afrobeats building genuine multi-market catalogue assets, or is diaspora-concentrated consumption on Spotify being misread as mainstream crossover?

Two specific problems motivated this research:

**The measurement problem.** Standard 6-month retention calculations apply a single methodology to genres with structurally different rollout patterns. Afrobeats tracks often flatline in their initial viral market before building momentum in secondary markets. Applying a Latin Pop measurement framework to an Afrobeats track produces misleading numbers — not because the music performs differently, but because the lifecycle is different.

**The valuation problem.** The Spotify catalogue valuation gap between Afrobeats and Latin Pop is visible and large. But nobody had examined what is actually driving it. Is it audience loyalty? Royalty rates? Geography? Or something else?

---

## Approach

Latin Pop was chosen as the structural comparator because it achieved genuine verified multi-market Spotify scale during the same period (2019 to 2024), operates from a similarly concentrated home-language audience, and has a comparable number of globally recognised artists. It is the most defensible like-for-like comparison available.

The analysis rejects aggregate streaming volume as a primary metric. Instead it focuses on three questions that matter for catalogue value:

1. How long does a Spotify audience stay after the peak? (retention and half-life)
2. How fast does the audience decline mathematically? (lambda decay rate)
3. Where are the listeners, and how concentrated is that geography? (city-level identity density)

A custom correction framework — the **Data-Lifecycle Mismatch Framework** — was developed to neutralise three systematic errors found in standard streaming retention analysis before any genre comparison was made.

The Python analysis uses `scipy.optimize.curve_fit` to fit exponential decay models to the post-peak weekly stream trajectory of each track. This produces a lambda coefficient (λ) — the mathematically precise decay rate — independent of peak size or absolute stream count.

---

## Steps

### Step 1 — Track selection and inclusion criteria

Tracks must have charted in a minimum of 2 markets outside their home country on Spotify's published weekly Top 200. This threshold is not arbitrary — it directly tests the multi-market penetration question at the centre of the research.

This criterion excluded several culturally prominent Afrobeats tracks (the Asake catalogue, Buga by Kizz Daniel, Free Mind by Tems) because they did not meet the multi-market Spotify chart threshold at time of measurement. That exclusion is itself a finding.

**Final sample:** 13 Afrobeats tracks, 13 Latin Pop tracks, 26 total.

### Step 2 — Data collection

Weekly Spotify chart data was collected from Kworb.net for all 26 tracks. Audience demographics, city-level streaming data, and editorial playlist metadata were collected from Chartmetric Professional.

### Step 3 — Data-Lifecycle Mismatch correction

Three corrections were applied before any retention calculation:

**Active Market Rule:** if the primary market flatlines before the 6-month mark, the calculation pivots to the next active market — applying the same market to both numerator and denominator.

**Primary Market Anchor:** for slow-burn tracks where the local peak lagged the global viral moment, the 6-month clock is anchored to the local market peak rather than the global chart debut.

**Cross-Platform Validation:** where Kworb data is absent or sparse, Chartmetric and TurnTable Charts are used to validate whether a track was genuinely inactive or simply below chart threshold.

### Step 4 — Python analysis (Scripts 01 to 04)

Four Python scripts process the corrected data:

- **01_decay_halflife.py** — loads each Kworb CSV, identifies the peak week, counts forward to find the half-life (weeks to 50% of peak), fits the exponential decay curve to calculate lambda
- **02_decay_curves.py** — normalises all 26 post-peak trajectories to 100% of peak and plots them together, then draws the lambda ranking and the half-life vs retention scatter
- **03_identity_density_index.py** — calculates the IDI composite score: retention (50% weight) + editorial reach (25%) + audience geographic dispersion (25%)
- **04_catalogue_valuation.py** — estimates Spotify-only catalogue value using blended per-stream rates weighted by audience geography, retention-adjusted annual revenue, and industry-standard catalogue multiples (10x to 20x)

### Step 5 — Dashboard build

The research dashboard was built as a self-contained HTML file rather than using Tableau, Power BI, or Looker Studio. The reasoning is documented in the section below.

---

## Why a Custom HTML Dashboard — Not Tableau or Power BI

This is a deliberate choice, not a workaround. There are four reasons.

**Portability.** A single HTML file opens in any browser with no login, no subscription, no installed software, and no expired trial. It works offline. It can be emailed, hosted on GitHub Pages, shared as a link, or opened directly. A Tableau workbook requires Tableau. A Power BI report requires a Power BI account. This dashboard requires nothing.

**Embedding the Python charts directly.** The five Python charts produced by the analysis are embedded as base64 images inside the HTML. This means the dashboard and the charts are the same file — the analytical output and the presentation layer are inseparable. Rebuilding the charts in Tableau would require re-entering the data and losing the mathematical precision of the scipy decay models.

**Ownership of the visual language.** Tableau and Power BI produce output that looks like Tableau and Power BI — which is to say it looks like every other Tableau and Power BI dashboard. For a research project with a specific aesthetic position (dark theme, monospace typography, Hipstarr brand system), a custom build is the only way to own the output completely.

**Portfolio signal.** Building a production-grade interactive dashboard in raw HTML, CSS, and JavaScript — with four working Chart.js visualisations, a 26-row data table, nine navigable tabs, and five embedded Python charts — demonstrates a different skill set from dragging fields into a BI tool. It shows you can build, not just configure.

Looker Studio was used separately for the `hipstarr_looker_master.csv` dataset (32 columns, 26 rows) as a data verification and quick-exploration layer. That is the appropriate use case for a BI tool in this workflow — not the final deliverable.

---

## Assumptions

**Retention methodology.** The 6-month retention window is measured from the primary market peak, not the global chart debut. For tracks where the primary market and the viral market are different (example: Calm Down Remix peaked globally but its primary audience market by Spotify geography is the US), the calculation uses the US market for both numerator and denominator.

**Spotify royalty rates (Script 04).** Per-stream rate assumptions are industry averages and are used for modelling only. Actual rates vary by subscription tier, territory licensing agreements, and time period. Rates used: US/UK/FR/DE/AU/CA at $0.004 per stream, LATAM at $0.0022, Nigeria at $0.0004, other markets at $0.0020.

**Spotify-only scope.** All stream counts, retention calculations, and valuation estimates are Spotify only. They exclude Apple Music, YouTube Music, Tidal, Amazon Music, and all other DSPs. Total cross-platform values would be higher for all tracks.

**Catalogue multiples.** Industry multiples of 10x to 20x annual revenue are applied based on retention tier. These are reference points from observed catalogue transactions, not guaranteed valuations. Tracks with retention above 40% qualify for 20x; 25 to 40% for 16x; below 25% for 10x.

**Inclusion bias.** The sample skews toward tracks with sufficient multi-market Spotify chart data. Tracks with strong streaming numbers concentrated in a single market were excluded. This means the Afrobeats sample is more representative of crossover-adjacent tracks than of the genre's median commercial output.

---

## Result

| Metric | Afrobeats | Latin Pop |
|--------|-----------|-----------|
| Tracks in sample | 13 | 13 |
| Avg 6-month Spotify retention | 30.7% | 33.0% |
| Statistical gap | 2.3 percentage points — near parity | |
| Avg Spotify stream half-life | 13.7 weeks | 11.1 weeks |
| Avg lambda (decay rate) | 0.0784 | 0.0481 |
| Slowest decay | Soso — λ 0.0033, 29w half-life | |
| Fastest decay | Bzrp Vol. 52 — λ 0.1284, 5w half-life | |
| Lagos as #1 Spotify city | 100% of Afrobeats tracks | — |
| Nigerian city concentration | 47 to 65% per track | — |
| Spotify-only catalogue value | $28.9M (13 tracks) | $87.4M (13 tracks) |
| Valuation gap | 3.0x — driven by stream volume, not royalty rates | |

**The headline finding:** After applying the Data-Lifecycle Mismatch correction, Afrobeats and Latin Pop are in near-statistical parity on 6-month Spotify retention. On the more precise half-life measure, Afrobeats audiences actually last longer (13.7w vs 11.1w). The 3x Spotify valuation gap is explained entirely by stream volume — Latin Pop tracks accumulate 6 to 10 times more total Spotify streams per track. Both genres earn comparably per stream in high-yield markets.

**The structural finding:** Afrobeats is not failing at durability. It is succeeding at community penetration — and that community routes through Western Spotify servers at Western royalty rates. The ceiling is a demographic scale gap, not a quality gap.

---

## Track Data

### Afrobeats (13 tracks)

| Track | Artist | Half-Life | Lambda | Spotify Retention |
|-------|--------|-----------|--------|-------------------|
| Soso | Omah Lay | 29w | 0.0033 | 58.8% |
| Calm Down Remix | Rema ft. Selena Gomez | 25w | 0.0478 | 48.2% |
| Peru Remix | Fireboy DML ft. Ed Sheeran | 24w | 0.0372 | 39.9% |
| Soundgasm | Rema | 16w | 0.0695 | 44.1% |
| Essence | Wizkid ft. Tems | 15w | 0.0747 | 39.0% |
| Last Last | Burna Boy | 17w | 0.0323 | 36.6% |
| Love Nwantiti | CKay | 21w | 0.0675 | 32.7% |
| Ku Lo Sa | Oxlade | 11w | 0.0435 | 29.7% |
| Rush | Ayra Starr | 10w | 0.0688 | 29.6% |
| It's Plenty | Burna Boy | 2w | 0.0110 | 27.9% |
| Unavailable | Davido ft. Musa Keys | 2w | 0.0609 | 12.2% |
| Attention | Omah Lay ft. Justin Bieber | 3w | 0.0275 | 0.0% |
| Peru Original | Fireboy DML | 3w | 0.4755 | 0.0% |

### Latin Pop (13 tracks)

| Track | Artist | Half-Life | Lambda | Spotify Retention |
|-------|--------|-----------|--------|-------------------|
| Neverita | Bad Bunny | 7w | 0.0200 | 71.7% |
| Tití Me Preguntó | Bad Bunny | 20w | 0.0365 | 53.2% |
| Provenza | Karol G | 28w | 0.0142 | 52.3% |
| Me Porto Bonito | Bad Bunny ft. Chencho Corleone | 22w | 0.0246 | 46.5% |
| Yonaguni | Bad Bunny | 10w | 0.0320 | 44.8% |
| Bzrp Vol. 52 | Quevedo ft. Bizarrap | 5w | 0.1284 | 26.1% |
| Moscow Mule | Bad Bunny | 3w | 0.0420 | 28.7% |
| Telepatía | Kali Uchis | 14w | 0.0354 | 28.6% |
| Todo De Ti | Rauw Alejandro | 8w | 0.0293 | 25.3% |
| Bichota | Karol G | 15w | 0.0442 | 23.0% |
| TQG | Karol G ft. Shakira | 5w | 0.0518 | 18.5% |
| Bzrp Vol. 53 | Shakira ft. Bizarrap | 4w | 0.0860 | 10.9% |
| El Apagón | Bad Bunny | 3w | 0.0815 | 0.0% |

---

## Repository Structure

```
hipstarr-streaming-decay-analysis/
│
├── index.html                          ← Interactive 9-tab research dashboard
├── README.md
│
├── data/
│   ├── halflife_26tracks.csv           ← Python-calculated half-life + lambda + floor
│   ├── valuation_26tracks.csv          ← Spotify-only catalogue value estimates
│   └── hipstarr_looker_master.csv      ← 26 rows × 32 columns, Looker Studio-ready
│
├── scripts/
│   ├── 01_decay_halflife.py            ← Stream half-life and lambda calculator
│   ├── 02_decay_curves.py              ← Decay curves, lambda ranking, scatter charts
│   ├── 03_identity_density_index.py    ← IDI composite score
│   ├── 04_catalogue_valuation.py       ← Spotify-only catalogue valuation model
│   └── requirements.txt
│
└── outputs/
    ├── halflife_final.png
    ├── decay_curves_final.png
    ├── lambda_ranked.png
    ├── hl_vs_retention.png
    └── catalogue_valuation.png
```

---

## Running the Analysis

```bash
# Install dependencies
pip install pandas numpy matplotlib scipy

# Place Kworb weekly CSVs in kworb_weekly/ folder
# See PYTHON_GUIDE.md for exact file naming

# Run in sequence
python3 scripts/01_decay_halflife.py
python3 scripts/02_decay_curves.py
python3 scripts/03_identity_density_index.py
python3 scripts/04_catalogue_valuation.py
```

Scripts 01 and 02 require the Kworb weekly CSV files.
Scripts 03 and 04 are standalone and run independently.

---

## Data Sources

| Source | What it provided |
|--------|-----------------|
| [Kworb.net](https://kworb.net) | Spotify weekly chart history — primary analytical data |
| [Chartmetric Professional](https://chartmetric.com) | Audience demographics, city-level data, editorial playlist metadata |

Raw Kworb weekly CSV files are not included in this repository (Kworb's intellectual property). Available on request.

---

## Disclaimer

Spotify-only estimates throughout. Revenue calculations use industry-average Spotify streaming rates and standard catalogue multiples for modelling purposes. They do not represent confirmed earnings, distribution deal specifics, or rights holder splits. Not financial or investment advice.

---

## License and Attribution

Original research by Ekene Ahuche / Hipstarr Music Research. Data sourced from Kworb.net and Chartmetric Professional.

If you use or cite this work: Ekene Ahuche, "Afrobeats vs Latin Pop — Global Asset Retention & Identity Density Index," Hipstarr Music Research, Lagos, 2026.

**Contact:** [@ekenemike_](https://x.com/ekenemike_) on X · [ekenemike.substack.com](https://ekenemike.substack.com)

© 2026 Hipstarr Music Research
