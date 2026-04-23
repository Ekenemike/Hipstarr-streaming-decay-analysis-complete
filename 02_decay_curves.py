"""
Hipstarr Music Research
Script 01 — Stream Half-Life Calculator
========================================

WHAT THIS SCRIPT DOES (plain English):
  Imagine a song peaks at 1 million Spotify streams in a week. The "half-life"
  is simply: how many weeks later did it fall to 500,000 streams?

  A long half-life (Soso: 29 weeks) means the audience stuck around.
  A short half-life (Bzrp Vol. 52: 5 weeks) means people moved on fast.

  This script reads the raw Kworb weekly Spotify chart data for all 26 tracks,
  finds each track's peak week, counts how many weeks it took to drop to 50%
  of that peak, and calculates a mathematical decay rate called lambda (λ).

HOW TO RUN:   python3 01_decay_halflife.py
NEEDS:        kworb_weekly/ folder with 26 CSV files (see PYTHON_GUIDE.md)
PRODUCES:     outputs/halflife_26tracks.csv
              outputs/halflife_final.png
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')   # use non-interactive backend — no screen required
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patheffects import withStroke
from scipy.optimize import curve_fit   # for fitting the exponential decay curve

warnings.filterwarnings('ignore')
os.makedirs('outputs', exist_ok=True)   # create outputs/ folder if it doesn't exist

# ── TRACK CONFIGURATION ───────────────────────────────────────────────────────
# Maps each CSV filename stem to: (display name, genre, primary market, fallback market)
# Primary market = the market used to calculate retention and half-life
# Fallback market = used if the primary market has too few data points
TRACK_CFG = {
    "attention":        ("Attention",           "Afrobeats", "NG",  None),
    "calm_down_remix":  ("Calm Down Remix",     "Afrobeats", "US",  "GB"),
    "essence":          ("Essence",             "Afrobeats", "ZA",  "NG"),
    "its_plenty":       ("It's Plenty",         "Afrobeats", "NG",  None),
    "ku_lo_sa":         ("Ku Lo Sa",            "Afrobeats", "NL",  "FR"),
    "last_last":        ("Last Last",           "Afrobeats", "GB",  "NL"),
    "love_nwantiti":    ("Love Nwantiti",       "Afrobeats", "US",  "GB"),
    "peru_original":    ("Peru Original",       "Afrobeats", "GB",  "NG"),
    "peru_remix":       ("Peru Remix",          "Afrobeats", "GB",  "NL"),
    "rush":             ("Rush",                "Afrobeats", "FR",  "NL"),
    "soso":             ("Soso",                "Afrobeats", "NG",  None),
    "soundgasm":        ("Soundgasm",           "Afrobeats", "NL",  "NG"),
    "unavailable":      ("Unavailable",         "Afrobeats", "NG",  None),
    "bichota":          ("Bichota",             "Latin Pop", "MX",  None),
    "bzrp_vol_52":      ("Bzrp Vol. 52",        "Latin Pop", "MX",  "AR"),
    "bzrp_vol_53":      ("Bzrp Vol. 53",        "Latin Pop", "MX",  "AR"),
    "el_apagon":        ("El Apagón",           "Latin Pop", "MX",  None),
    "me_porto_bonito":  ("Me Porto Bonito",     "Latin Pop", "MX",  None),
    "moscow_mule":      ("Moscow Mule",         "Latin Pop", "MX",  None),
    "neverita":         ("Neverita",            "Latin Pop", "MX",  "US"),
    "provenza":         ("Provenza",            "Latin Pop", "MX",  None),
    "telepatia":        ("Telepatía",           "Latin Pop", "US",  "MX"),
    "titi_me_pregunto": ("Tití Me Preguntó",    "Latin Pop", "MX",  None),
    "todo_de_ti":       ("Todo De Ti",          "Latin Pop", "MX",  None),
    "tqg":              ("TQG",                 "Latin Pop", "MX",  None),
    "yonaguni":         ("Yonaguni",            "Latin Pop", "MX",  None),
}

# ── COLOUR PALETTE ────────────────────────────────────────────────────────────
AFRO  = "#FF6B35"   # orange  — Afrobeats
LATIN = "#4ECDC4"   # teal    — Latin Pop
GOLD  = "#D4AF37"   # gold    — brand accent / titles
BG    = "#080808"   # near-black background
W     = "#F0EEF8"   # off-white text

# Apply dark theme to all charts produced by this script
plt.rcParams.update({
    "figure.facecolor": BG,    # chart background
    "axes.facecolor":   BG,    # plot area background
    "axes.edgecolor":   "#2a2a2a",
    "axes.labelcolor":  "#aaa",
    "xtick.color":      "#888",
    "ytick.color":      W,
    "text.color":       W,
    "grid.color":       "#181818",
    "font.family":      "monospace",
    "font.size":        10,
})


def load_csv(path):
    """
    Load a Kworb weekly CSV file and return a clean DataFrame.

    Kworb files have two quirks this function handles:
      1. Some files have a blank first row — we try skipping 0 or 1 rows
      2. Stream numbers use commas as thousands separators (1,234,567)
      3. Missing weeks are shown as '--' — we treat these as zero

    Returns a DataFrame with a 'Date' column plus one column per country code,
    or None if the file cannot be read.
    """
    for skip in [0, 1]:   # try both — some files have a blank header row
        try:
            df = pd.read_csv(path, dtype=str, skip_blank_lines=True, skiprows=skip)
            df.columns = df.columns.str.strip()
            # drop any completely empty columns
            df = df[[c for c in df.columns if c.strip() != '']]

            # find the date column (case-insensitive)
            date_cols = [c for c in df.columns if c.lower() == 'date']
            if not date_cols:
                continue
            dc = date_cols[0]

            # remove summary rows kworb adds at the bottom ('Total', 'Peak')
            df = df[~df[dc].isin(['Total', 'Peak', 'total', 'peak', ''])].copy()
            df = df.dropna(subset=[dc])

            # parse dates and sort chronologically
            df[dc] = pd.to_datetime(df[dc].astype(str).str.strip(), errors='coerce')
            df = df.dropna(subset=[dc]).sort_values(dc).reset_index(drop=True)
            df = df.rename(columns={dc: 'Date'})

            # clean all stream columns: remove commas, convert to numbers
            for col in df.columns:
                if col == 'Date':
                    continue
                df[col] = df[col].astype(str).str.replace(',', '', regex=False)
                df[col] = df[col].replace({'--': np.nan, '': np.nan})
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            if len(df) > 3:   # need at least 4 rows to be usable
                return df
        except Exception:
            continue
    return None   # return None if both attempts fail


def get_series(df, primary_market, fallback_market):
    """
    Extract the weekly stream count series for the relevant market.

    Uses the primary market if it has at least 4 non-zero weeks.
    Falls back to the fallback market, then 'Global', then whichever
    column has the most non-zero values.

    This implements the Active Market Rule from the Data-Lifecycle
    Mismatch Framework — we always compare the same market to itself
    when calculating retention, never mixing global and local numbers.
    """
    for market in [primary_market, fallback_market, 'Global']:
        if market and market in df.columns and (df[market] > 0).sum() >= 4:
            return df[market].copy(), market

    # last resort: pick the country column with the most streaming weeks
    numeric_cols = [c for c in df.columns if c != 'Date']
    best = max(numeric_cols, key=lambda c: (df[c] > 0).sum())
    return df[best].copy(), best


def exp_decay(t, S0, lam):
    """
    Standard exponential decay formula.

    S0  = starting level (the peak stream count)
    lam = lambda, the decay rate (how fast it falls)
    t   = time in weeks after the peak

    A higher lambda means the track loses listeners faster.
    Soso: lambda 0.0033 (very slow). Bzrp Vol 52: lambda 0.1284 (very fast).
    """
    return S0 * np.exp(-lam * t)


def analyse_track(series):
    """
    Calculate half-life, lambda, peak details, and floor percentage
    from a weekly stream count series.

    Returns:
      half_life  — weeks until streams dropped to 50% of peak (None if never)
      peak_val   — stream count at the peak week
      peak_idx   — row index of the peak week
      lam        — exponential decay rate coefficient (None if fit failed)
      floor_pct  — last 4 weeks average as % of peak (how much remains)
    """
    if series.max() == 0:
        return None, 0, 0, None, 0

    # identify the peak week
    peak_idx = int(series.idxmax())
    peak_val = float(series.iloc[peak_idx])

    # isolate the post-peak portion — this is what we analyse
    post_peak = series.iloc[peak_idx:].reset_index(drop=True)

    # half-life: first week where streams fell to 50% of peak or below
    below_half = post_peak[post_peak <= peak_val * 0.5]
    half_life = int(below_half.index[0]) if not below_half.empty else None

    # lambda: fit an exponential decay curve to post-peak data using scipy
    lam = None
    if len(post_peak) >= 5:   # need at least 5 data points for a meaningful fit
        try:
            t = np.arange(len(post_peak), dtype=float)
            popt, _ = curve_fit(
                exp_decay,
                t,
                post_peak.values.astype(float),
                p0=[peak_val, 0.05],                      # initial guess
                bounds=([0, 0.0001], [peak_val * 5, 2.0]),  # sensible limits
                maxfev=8000                               # max iterations
            )
            lam = round(float(popt[1]), 5)   # extract and round lambda
        except Exception:
            pass   # curve_fit can fail on noisy data — leave as None

    # floor: average of the last 4 weeks as % of peak
    # this shows whether the track settled at a stable baseline
    floor_pct = float(post_peak.iloc[-4:].mean() / peak_val * 100) if len(post_peak) >= 4 else 0

    return half_life, peak_val, peak_idx, lam, floor_pct


def add_branding(fig):
    """
    Add the Hipstarr brand mark and social handles to the bottom of a chart.
    Uses path effects (text outline) so it reads on both light and dark areas.
    """
    outline = [withStroke(linewidth=4, foreground="black")]
    fig.text(0.015, 0.012, "HIPSTARR MUSIC RESEARCH",
             ha='left', va='bottom', fontsize=11, color=GOLD,
             fontweight='bold', fontfamily='monospace', path_effects=outline)
    fig.text(0.985, 0.012, "@ekenemike_   ekenemike.substack.com   tiktok @ekenemike_",
             ha='right', va='bottom', fontsize=9.5, color="#999",
             fontfamily='monospace', path_effects=outline)


def main():
    print("=== Script 01: Stream Half-Life Calculator ===\n")

    results = []   # will hold one dict per track

    for stem, (name, genre, primary_mkt, fallback_mkt) in TRACK_CFG.items():
        path = os.path.join('kworb_weekly', f'{stem}.csv')

        # check file exists before attempting to load
        if not os.path.exists(path):
            print(f"  MISSING: {path}")
            continue

        df = load_csv(path)
        if df is None:
            print(f"  COULD NOT READ: {path}")
            continue

        # extract the relevant market's stream series
        series, market_used = get_series(df, primary_mkt, fallback_mkt)

        # run the analysis
        half_life, peak_val, peak_idx, lam, floor_pct = analyse_track(series)
        peak_date = df.loc[peak_idx, 'Date']

        results.append({
            "Track":         name,
            "Genre":         genre,
            "Market":        market_used,
            "Peak_Streams":  int(peak_val),
            "Peak_Date":     peak_date.strftime('%Y-%m-%d'),
            "HalfLife_Wks":  half_life,
            "Lambda":        lam,
            "Floor_Pct":     round(floor_pct, 1),
            "Rows":          len(df),
        })

        # print progress to terminal
        hl_str  = f"{half_life}w" if half_life else "never reached 50%"
        lam_str = str(round(lam, 4)) if lam else "N/A"
        print(f"  {name:<22} {market_used:<5} peak={peak_val:>11,.0f}  "
              f"half-life={hl_str:<14} lambda={lam_str}")

    # save results to CSV
    df_out = pd.DataFrame(results)
    df_out.to_csv('outputs/halflife_26tracks.csv', index=False)
    print(f"\nSaved: outputs/halflife_26tracks.csv ({len(results)} tracks)")

    # print genre-level summary
    for genre in ["Afrobeats", "Latin Pop"]:
        gdf  = df_out[df_out.Genre == genre]
        calc = gdf.dropna(subset=["HalfLife_Wks"])   # exclude tracks where half-life wasn't reached
        print(f"\n{genre} ({len(gdf)} tracks):")
        print(f"  Avg half-life:  {calc['HalfLife_Wks'].mean():.1f}w")
        print(f"  Avg lambda:     {gdf['Lambda'].dropna().mean():.4f}")
        print(f"  Avg floor:      {gdf['Floor_Pct'].mean():.1f}%")

    # ── BUILD THE CHART ───────────────────────────────────────────────────────
    # Sort tracks by half-life (shortest first) for ranked bar chart
    calc_df  = df_out.dropna(subset=['HalfLife_Wks']).sort_values('HalfLife_Wks')
    # colour each bar by genre
    colors   = [AFRO if g == "Afrobeats" else LATIN for g in calc_df.Genre]
    # calculate genre averages for the dotted reference lines
    afro_avg  = calc_df[calc_df.Genre == "Afrobeats"]['HalfLife_Wks'].mean()
    latin_avg = calc_df[calc_df.Genre == "Latin Pop"]['HalfLife_Wks'].mean()

    fig, ax = plt.subplots(figsize=(16, 12))

    # draw the horizontal bars
    bars = ax.barh(range(len(calc_df)), calc_df.HalfLife_Wks,
                   color=colors, height=0.72, alpha=0.88)

    # label each bar with its value
    for i, (bar, (_, row)) in enumerate(zip(bars, calc_df.iterrows())):
        w = bar.get_width()
        if w > 7:
            # label inside the bar if bar is wide enough
            ax.text(w - .4, i, f"{int(w)}w", va='center', ha='right',
                    fontsize=10, color=BG, fontweight='bold')
        else:
            # label outside if bar is too narrow
            ax.text(w + .3, i, f"{int(w)}w", va='center', ha='left',
                    fontsize=10, color="#bbb")

    ax.set_yticks(range(len(calc_df)))
    ax.set_yticklabels(calc_df.Track, fontsize=12, color=W)

    # vertical reference lines
    ax.axvline(26, color='#3a3a3a', lw=1.5, ls='--', alpha=0.9)   # 6-month mark
    ax.axvline(afro_avg,  color=AFRO,  lw=1.2, ls=':', alpha=0.7)  # Afrobeats average
    ax.axvline(latin_avg, color=LATIN, lw=1.2, ls=':', alpha=0.7)  # Latin Pop average

    # labels for reference lines
    ax.text(26.4, len(calc_df) - .5, "6 months", fontsize=10, color="#555", va='top')
    ax.text(afro_avg  + .2, -1.1, f"Afro avg {afro_avg:.0f}w",  fontsize=9, color=AFRO,  va='top')
    ax.text(latin_avg + .2, -1.1, f"Latin avg {latin_avg:.0f}w", fontsize=9, color=LATIN, va='top')

    ax.set_xlabel("Weeks before Spotify streams drop to half of peak",
                  fontsize=11, color="#aaa", labelpad=10)
    ax.set_title(
        "HOW LONG DO HITS LAST?  Stream Half-Life\n"
        "26 Tracks: Afrobeats vs Latin Pop  2019 to 2024",
        color=GOLD, fontsize=15, fontweight='bold', loc='left', pad=16)

    ax.spines[["top", "right", "bottom"]].set_visible(False)
    ax.grid(axis='x', alpha=.12)
    ax.tick_params(labelsize=11, colors=W)

    # legend showing both genres and their averages
    ax.legend(
        handles=[
            mpatches.Patch(color=AFRO,  label=f"Afrobeats  avg {afro_avg:.0f}w"),
            mpatches.Patch(color=LATIN, label=f"Latin Pop  avg {latin_avg:.0f}w"),
        ],
        framealpha=0, labelcolor=W, fontsize=11, loc='lower right')

    add_branding(fig)
    plt.tight_layout(rect=[0, .055, 1, 1])   # leave space at bottom for branding
    plt.savefig('outputs/halflife_final.png', dpi=200, bbox_inches='tight', facecolor=BG)
    plt.close()
    print("Saved: outputs/halflife_final.png")


if __name__ == "__main__":
    main()
