# Hipstarr Music Research
## Python Scripts — Complete Setup and Filing Guide

Everything you need to run the analysis from scratch, understand what each
script does, and file the project correctly on GitHub.

---

## What the 4 scripts produce

| Script | What it does | Output |
|--------|-------------|--------|
| 01_decay_halflife.py | Calculates how many weeks before each track loses half its Spotify audience | halflife_26tracks.csv + halflife_final.png |
| 02_decay_curves.py | Draws the full week-by-week audience decline for all 26 tracks + lambda ranking + scatter | decay_curves_final.png + lambda_ranked.png + hl_vs_retention.png |
| 03_identity_density_index.py | Scores each track on a composite catalogue quality index (retention + editorial + audience spread) | idi_scores.csv + idi_chart.png |
| 04_catalogue_valuation.py | Estimates Spotify-only catalogue value using audience geography, retention, and industry multiples | valuation_26tracks.csv + catalogue_valuation.png |

Scripts 01 and 02 read the raw Kworb weekly CSV files.
Scripts 03 and 04 use hardcoded data and run standalone with no CSV files needed.

---

## Step 1: Install the required libraries

Run this once before anything else. Open your terminal and paste:

```bash
pip install pandas numpy matplotlib scipy
```

If you are on a Mac or Linux system and get a permissions error, use:

```bash
pip install pandas numpy matplotlib scipy --break-system-packages
```

This installs:
- **pandas** — reads and organises the CSV data
- **numpy** — does the maths
- **matplotlib** — draws all the charts
- **scipy** — fits the exponential decay curves

---

## Step 2: Set up your folder structure

Create a folder on your computer called `hipstarr-analysis` (or any name you like).
Inside it, create these exact folders and files:

```
hipstarr-analysis/
│
├── kworb_weekly/              ← PUT ALL YOUR KWORB CSV FILES HERE
│   ├── attention.csv
│   ├── calm_down_remix.csv
│   ├── essence.csv
│   ├── its_plenty.csv
│   ├── ku_lo_sa.csv
│   ├── last_last.csv
│   ├── love_nwantiti.csv
│   ├── peru_original.csv
│   ├── peru_remix.csv
│   ├── rush.csv
│   ├── soso.csv
│   ├── soundgasm.csv
│   ├── unavailable.csv
│   ├── bichota.csv
│   ├── bzrp_vol_52.csv
│   ├── bzrp_vol_53.csv
│   ├── el_apagon.csv
│   ├── me_porto_bonito.csv
│   ├── moscow_mule.csv
│   ├── neverita.csv
│   ├── provenza.csv
│   ├── telepatia.csv
│   ├── titi_me_pregunto.csv
│   ├── todo_de_ti.csv
│   ├── tqg.csv
│   └── yonaguni.csv
│
├── outputs/                   ← Scripts write all results here (created automatically)
│
├── 01_decay_halflife.py
├── 02_decay_curves.py
├── 03_identity_density_index.py
└── 04_catalogue_valuation.py
```

**Important:** The `outputs/` folder is created automatically when you run
the first script. You do not need to create it yourself.

---

## Step 3: File naming — critical

The scripts look for files by exact name inside the `kworb_weekly/` folder.
The filenames must match exactly including underscores and no capital letters.

### Afrobeats files (13 tracks)

| Track | Save your Kworb export as |
|-------|--------------------------|
| Attention (Omah Lay ft. Justin Bieber) | `attention.csv` |
| Calm Down Remix (Rema ft. Selena Gomez) | `calm_down_remix.csv` |
| Essence (Wizkid ft. Tems) | `essence.csv` |
| It's Plenty (Burna Boy) | `its_plenty.csv` |
| Ku Lo Sa (Oxlade) | `ku_lo_sa.csv` |
| Last Last (Burna Boy) | `last_last.csv` |
| Love Nwantiti (CKay) | `love_nwantiti.csv` |
| Peru Original (Fireboy DML) | `peru_original.csv` |
| Peru Remix (Fireboy DML ft. Ed Sheeran) | `peru_remix.csv` |
| Rush (Ayra Starr) | `rush.csv` |
| Soso (Omah Lay) | `soso.csv` |
| Soundgasm (Rema) | `soundgasm.csv` |
| Unavailable (Davido ft. Musa Keys) | `unavailable.csv` |

### Latin Pop files (13 tracks)

| Track | Save your Kworb export as |
|-------|--------------------------|
| Bichota (Karol G) | `bichota.csv` |
| Bzrp Vol. 52 (Quevedo ft. Bizarrap) | `bzrp_vol_52.csv` |
| Bzrp Vol. 53 (Shakira ft. Bizarrap) | `bzrp_vol_53.csv` |
| El Apagón (Bad Bunny) | `el_apagon.csv` |
| Me Porto Bonito (Bad Bunny ft. Chencho) | `me_porto_bonito.csv` |
| Moscow Mule (Bad Bunny) | `moscow_mule.csv` |
| Neverita (Bad Bunny) | `neverita.csv` |
| Provenza (Karol G) | `provenza.csv` |
| Telepatía (Kali Uchis) | `telepatia.csv` |
| Tití Me Preguntó (Bad Bunny) | `titi_me_pregunto.csv` |
| Todo De Ti (Rauw Alejandro) | `todo_de_ti.csv` |
| TQG (Karol G ft. Shakira) | `tqg.csv` |
| Yonaguni (Bad Bunny) | `yonaguni.csv` |

### What format should the Kworb CSV be in?

When you export from Kworb, the file should look like this
(Date column followed by country code columns with weekly stream numbers):

```
Date,NG,GB,US,NL,FR,...
2022-07-14,83970,12000,45000,,
2022-07-21,95000,14000,52000,,
2022-07-28,112000,16000,61000,,
```

The scripts handle commas in numbers, missing values shown as `--`,
and blank header rows automatically. You do not need to clean the files.

---

## Step 4: Run the scripts in order

Open your terminal, navigate to your `hipstarr-analysis/` folder, then run:

```bash
python3 01_decay_halflife.py
```

Wait for it to finish, then run:

```bash
python3 02_decay_curves.py
```

Then:

```bash
python3 03_identity_density_index.py
```

Then:

```bash
python3 04_catalogue_valuation.py
```

Each script prints its progress to the terminal so you can see what it is doing.

**Run order matters for Scripts 01 and 02.** Script 02 reads the CSV that
Script 01 produces. Scripts 03 and 04 are standalone and can be run
in any order or independently.

---

## Step 5: Check your outputs

After running all four scripts, your `outputs/` folder should contain:

```
outputs/
├── halflife_26tracks.csv       ← Table of all half-life results
├── valuation_26tracks.csv      ← Spotify-only catalogue value estimates
├── idi_scores.csv              ← Identity Density Index scores
├── halflife_final.png          ← Chart: half-life bar chart
├── decay_curves_final.png      ← Chart: post-peak decay curves (26 lines)
├── lambda_ranked.png           ← Chart: decay rate ranked slowest to fastest
├── hl_vs_retention.png         ← Chart: half-life vs retention scatter
├── idi_chart.png               ← Chart: IDI scores ranked
└── catalogue_valuation.png     ← Chart: Spotify-only catalogue value estimates
```

---

## What each script actually does (no jargon)

### Script 01 — Half-Life Calculator

A track's "half-life" is simply the number of weeks before its Spotify streams
dropped to 50% of the peak week. Soso peaked and took 29 weeks to halve.
Bzrp Vol. 52 peaked and halved in 5 weeks.

This script reads each Kworb CSV, finds the peak week, then counts forward
until streams fall below that 50% threshold. It also fits a mathematical
curve to the decline to calculate the "lambda" decay rate — a single number
that captures how fast the audience is leaving.

**A non-technical way to think about lambda:** imagine two candles. One burns
slowly and lasts all night. One burns bright and is out in an hour. Lambda
is the burn rate. Soso is the slow candle (lambda 0.0033). Bzrp Vol. 52 is
the bright one (lambda 0.1284). Soso burns 39 times more slowly.

### Script 02 — Decay Curves and Ranking Charts

While Script 01 gives you one number per track (half-life), this script draws
the full picture: a line showing how streams moved week by week after the peak
for all 26 tracks at once, normalised to 100% so you can compare tracks of
very different sizes on the same chart.

It also draws the lambda ranking (slowest to fastest decay) and a scatter plot
showing where each track sits when you plot half-life against retention together.

### Script 03 — Identity Density Index

Retention alone does not capture the full picture of a track's value. A track
with 60% retention but very few listeners is not worth more than one with 35%
retention and millions of listeners.

The IDI combines three things into one score out of 100:
- How many Spotify listeners stayed after 6 months (50% weight)
- How many editorial playlists backed it and what their reach was (25% weight)
- How spread out the audience is globally rather than concentrated in one city (25% weight)

A high IDI means deep loyalty, strong institutional support, and global spread.
Calm Down Remix is the only Afrobeats track in Tier 1.

### Script 04 — Spotify-Only Catalogue Valuation

**Important: These are Spotify-only estimates. They exclude Apple Music,
YouTube Music, Tidal, Amazon Music, and all other platforms.**

This script estimates what each track's Spotify streaming revenue stream
might be worth to a catalogue buyer. Three steps:

1. Work out the blended per-stream rate based on where listeners are.
   A US Spotify subscriber generates roughly $0.004 per stream.
   A Nigerian free-tier listener generates roughly $0.0004 per stream.
   The blended rate is a weighted average based on each track's audience geography.

2. Estimate current annual Spotify earnings. Uses the 6-month retention rate
   to scale the peak-year streams down to a realistic current-year figure.

3. Multiply by the industry catalogue multiple. Buyers typically pay 10x to 20x
   annual income for music catalogues. Tracks with high audience loyalty
   (retention above 40%) qualify for the 20x multiple because the income
   stream is more predictable.

---

## How to file this on GitHub

### Recommended repository structure

```
hipstarr-streaming-decay-analysis/     ← Repository root
│
├── index.html                          ← The dashboard (rename from hipstarr_dashboard_FINAL.html)
├── README.md                           ← Project overview (use README_FINAL.md)
│
├── data/
│   ├── halflife_26tracks.csv
│   ├── valuation_26tracks.csv
│   └── hipstarr_looker_master.csv
│
├── scripts/
│   ├── 01_decay_halflife.py
│   ├── 02_decay_curves.py
│   ├── 03_identity_density_index.py
│   ├── 04_catalogue_valuation.py
│   └── requirements.txt
│
└── outputs/
    ├── halflife_final.png
    ├── decay_curves_final.png
    ├── lambda_ranked.png
    ├── hl_vs_retention.png
    └── catalogue_valuation.png
```

### What to leave out of the repository

**Do not upload the raw Kworb weekly CSVs.** Kworb's chart data is their
intellectual property. Add a note to your README instead:

> Raw weekly Spotify chart data sourced from Kworb.net.
> Available on request.

**Do not upload any Chartmetric exports.** Their data is also proprietary.

### Repository name and description

**Name:** `hipstarr-streaming-decay-analysis`

**Description (the one-line field under the repo name):**
```
Comparative Spotify streaming decay analysis: Afrobeats vs Latin Pop —
retention, half-life, lambda, city geography, and Spotify-only catalogue
valuation across 26 tracks (2019–2024)
```

**Topics to add (GitHub lets you add searchable tags):**
```
music-data  afrobeats  spotify  streaming-analytics  python
data-analysis  music-industry  latin-pop  decay-modeling  catalogue-valuation
```

### Step-by-step GitHub upload

1. Go to github.com and click **New repository**
2. Name it `hipstarr-streaming-decay-analysis`
3. Set it to **Public** (so it shows on your profile)
4. Do not initialise with a README (you have your own)
5. Click **Create repository**
6. Follow the upload instructions GitHub shows you, or use GitHub Desktop
   if you prefer a visual interface

### Enabling GitHub Pages (makes the dashboard live online)

After uploading, you can make the dashboard accessible as a live URL:

1. Go to your repository **Settings**
2. Click **Pages** in the left sidebar
3. Under **Source**, select **main** branch and **/ (root)** folder
4. Click **Save**
5. GitHub will give you a URL like `https://ekenemike.github.io/hipstarr-streaming-decay-analysis/`
6. The `index.html` file (your dashboard) will load at that URL

This gives you a link you can share directly — no downloading required.

---

## Common problems and fixes

**"Module not found" error when running a script**
Run `pip install pandas numpy matplotlib scipy` again.
If that does not work, try `pip3` instead of `pip`.

**"No such file or directory: kworb_weekly/essence.csv"**
Check the file is in the `kworb_weekly/` folder and the name matches exactly.
File names are case-sensitive. `Essence.csv` will not work — it must be `essence.csv`.

**Chart saves but looks blank**
Make sure you are running the script from inside the `hipstarr-analysis/` folder,
not from a different directory. Use `cd hipstarr-analysis` in your terminal first.

**Script 02 crashes saying it cannot find halflife_26tracks.csv**
Run Script 01 first. Script 02 reads the CSV that Script 01 creates.

---

*Hipstarr Music Research · Ekene Ahuche · Lagos 2026*
*@ekenemike_ · ekenemike.substack.com · TikTok @ekenemike_*
