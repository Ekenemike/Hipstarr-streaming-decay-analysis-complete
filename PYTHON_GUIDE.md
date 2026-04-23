"""
Hipstarr Music Research
Script 02 — Decay Curves, Lambda Ranking, and Half-Life vs Retention
======================================================================

WHAT THIS SCRIPT DOES (plain English):
  While Script 01 gives you ONE number per track (how many weeks to half),
  this script draws the FULL PICTURE — a line for each track showing how
  Spotify streams moved week by week after the peak, for all 26 tracks
  at once.

  It also draws two additional charts:
  - Lambda ranked: which tracks decay fastest and slowest, as a single bar
  - Half-life vs retention scatter: two durability measures plotted together

HOW TO RUN:   python3 02_decay_curves.py
NEEDS:        kworb_weekly/ folder  AND  outputs/halflife_26tracks.csv (from Script 01)
PRODUCES:     outputs/decay_curves_final.png
              outputs/lambda_ranked.png
              outputs/hl_vs_retention.png
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')   # non-interactive backend — no screen required
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patheffects import withStroke

warnings.filterwarnings('ignore')
os.makedirs('outputs', exist_ok=True)

# ── TRACK CONFIGURATION ───────────────────────────────────────────────────────
# Same as Script 01 — maps CSV stem to (name, genre, primary market, fallback)
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

# ── 6-MONTH SPOTIFY RETENTION (from master tracker) ──────────────────────────
# Used for the half-life vs retention scatter (Chart C)
RETENTION = {
    "Attention":       0.0,   "Calm Down Remix": 48.17, "Essence":      39.0,
    "It's Plenty":    27.92,  "Ku Lo Sa":        29.73, "Last Last":    36.58,
    "Love Nwantiti":  32.71,  "Peru Original":    0.0,  "Peru Remix":   39.94,
    "Rush":           29.6,   "Soso":            58.80, "Soundgasm":    44.12,
    "Unavailable":    12.21,  "Bichota":         22.96, "Bzrp Vol. 52": 26.11,
    "Bzrp Vol. 53":   10.88,  "El Apagón":        0.0,  "Me Porto Bonito": 46.53,
    "Moscow Mule":    28.71,  "Neverita":        71.74, "Provenza":     52.32,
    "Telepatía":      28.58,  "Tití Me Preguntó":53.23, "Todo De Ti":   25.26,
    "TQG":            18.53,  "Yonaguni":        44.79,
}

# ── COLOUR PALETTE ────────────────────────────────────────────────────────────
AFRO  = "#FF6B35"   # orange  — Afrobeats
LATIN = "#4ECDC4"   # teal    — Latin Pop
GOLD  = "#D4AF37"   # gold    — brand accent / titles
BG    = "#080808"   # near-black background
W     = "#F0EEF8"   # off-white text

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor":   BG,
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
    Load a Kworb weekly CSV. Handles blank header rows, comma-formatted
    numbers, and '--' missing values. Returns a clean DataFrame or None.
    """
    for skip in [0, 1]:
        try:
            df = pd.read_csv(path, dtype=str, skip_blank_lines=True, skiprows=skip)
            df.columns = df.columns.str.strip()
            df = df[[c for c in df.columns if c.strip() != '']]
            dc = [c for c in df.columns if c.lower() == 'date']
            if not dc:
                continue
            dc = dc[0]
            # remove Kworb summary rows
            df = df[~df[dc].isin(['Total', 'Peak', 'total', 'peak', ''])].copy()
            df = df.dropna(subset=[dc])
            df[dc] = pd.to_datetime(df[dc].astype(str).str.strip(), errors='coerce')
            df = df.dropna(subset=[dc]).sort_values(dc).reset_index(drop=True)
            df = df.rename(columns={dc: 'Date'})
            for col in df.columns:
                if col == 'Date':
                    continue
                # strip commas and convert to numbers
                df[col] = df[col].astype(str).str.replace(',', '', regex=False)
                df[col] = df[col].replace({'--': np.nan, '': np.nan})
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            if len(df) > 3:
                return df
        except Exception:
            continue
    return None


def get_series(df, primary_market, fallback_market):
    """
    Get the weekly stream series for the primary market, with fallback.
    Returns (series, market_code_used).
    """
    for market in [primary_market, fallback_market, 'Global']:
        if market and market in df.columns and (df[market] > 0).sum() >= 4:
            return df[market].copy(), market
    # last resort: use whichever column has the most non-zero weeks
    numeric_cols = [c for c in df.columns if c != 'Date']
    best = max(numeric_cols, key=lambda c: (df[c] > 0).sum())
    return df[best].copy(), best


def add_branding(fig):
    """Add Hipstarr brand name and handles to the bottom of any chart."""
    outline = [withStroke(linewidth=4, foreground="black")]
    fig.text(0.015, 0.012, "HIPSTARR MUSIC RESEARCH",
             ha='left', va='bottom', fontsize=11, color=GOLD,
             fontweight='bold', fontfamily='monospace', path_effects=outline)
    fig.text(0.985, 0.012, "@ekenemike_   ekenemike.substack.com   tiktok @ekenemike_",
             ha='right', va='bottom', fontsize=9.5, color="#999",
             fontfamily='monospace', path_effects=outline)


def main():
    print("=== Script 02: Decay Curves and Lambda Charts ===\n")

    # ── LOAD ALL TRACK SERIES ─────────────────────────────────────────────────
    # We store the post-peak stream series for each track so we can normalise
    # them all to 100% and plot them together on the same axes
    store = {}   # { track_name: { 's': series, 'pi': peak_index, 'genre': genre } }

    for stem, (name, genre, pm, fb) in TRACK_CFG.items():
        path = os.path.join('kworb_weekly', f'{stem}.csv')
        if not os.path.exists(path):
            print(f"  MISSING: {path}")
            continue
        df = load_csv(path)
        if df is None:
            print(f"  COULD NOT READ: {path}")
            continue
        series, market = get_series(df, pm, fb)
        if series.max() > 0:
            store[name] = {
                's':     series,
                'pi':    int(series.idxmax()),   # index of the peak week
                'genre': genre,
            }
            print(f"  Loaded: {name:<22} ({market})")

    print(f"\nLoaded {len(store)}/26 series")

    # separate into genre lists for chart looping
    afro_names  = [n for n, d in store.items() if d['genre'] == "Afrobeats"]
    latin_names = [n for n, d in store.items() if d['genre'] == "Latin Pop"]

    # ── CHART A: POST-PEAK DECAY CURVES ──────────────────────────────────────
    # Each line starts at 100% (peak week) and shows how streams declined.
    # Normalising to 100% lets us compare tracks of very different sizes —
    # Bzrp Vol 53's 20M-peak and Soso's 400k-peak are on the same scale.
    fig, axes = plt.subplots(1, 2, figsize=(22, 10))
    fig.suptitle(
        "STREAM DECAY CURVES  How Fast Do Tracks Lose Their Spotify Audience?\n"
        "100% = peak week   each line = one track   green = healthy   red = rapid loss",
        color=GOLD, fontsize=14, fontweight='bold', x=.5, ha='center', y=1.02)

    for ax, names, color, genre_label in [
        (axes[0], afro_names,  AFRO,  "Afrobeats"),
        (axes[1], latin_names, LATIN, "Latin Pop"),
    ]:
        # coloured background zones to signal retention health
        ax.fill_between([0, 85],  0,  30, color='#3a0000', alpha=.35)   # danger zone < 30%
        ax.fill_between([0, 85], 30,  50, color='#2a2200', alpha=.20)   # caution 30–50%
        ax.fill_between([0, 85], 50, 115, color='#001800', alpha=.12)   # healthy > 50%

        # horizontal reference lines at 50% and 30%
        ax.axhline(50, color='#444', lw=1.5, ls='--')   # half of peak
        ax.axhline(30, color='#2a2a2a', lw=1, ls=':')   # rapid-loss threshold

        # vertical line at 6 months
        ax.axvline(26, color='#2a2a2a', lw=1, alpha=.6)
        ax.text(26.5, 109, "6mo", fontsize=9, color='#444')
        ax.text(1, 52, "50%", fontsize=9, color='#555', va='bottom')
        ax.text(1, 32, "30%", fontsize=9, color='#444', va='bottom')

        for track_name in names:
            d = store.get(track_name)
            if not d:
                continue

            # slice the series from peak onwards and normalise to 100%
            post = d['s'].iloc[d['pi']:].reset_index(drop=True)
            if len(post) < 3 or post.iloc[0] == 0:
                continue
            normed = (post / post.iloc[0] * 100).clip(0, 115)   # cap at 115% for display
            t = np.arange(len(normed))

            ax.plot(t, normed.values, color=color, alpha=.55, lw=2.2)

            # label the track name at the end of its line
            ax.annotate(
                track_name,
                (t[-1], float(normed.iloc[-1])),
                xytext=(4, 0), textcoords='offset points',
                fontsize=9.5, color=W, alpha=.85, va='center', fontweight='bold')

        ax.set_title(genre_label, color=color, fontsize=13,
                     fontweight='bold', loc='left', pad=10)
        ax.set_xlabel("Weeks after Spotify peak", fontsize=11, color="#aaa", labelpad=8)
        ax.set_ylabel("% of peak streams still active", fontsize=11, color="#aaa", labelpad=8)
        ax.set_ylim(-5, 118)
        ax.set_xlim(-1, 82)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis='y', alpha=.10)
        ax.tick_params(labelsize=11, colors=W)

    add_branding(fig)
    plt.tight_layout(rect=[0, .055, 1, 1])
    plt.savefig('outputs/decay_curves_final.png', dpi=200, bbox_inches='tight', facecolor=BG)
    plt.close()
    print("Saved: outputs/decay_curves_final.png")

    # ── CHART B: LAMBDA RANKED ────────────────────────────────────────────────
    # Lambda (λ) is the mathematical rate of decay — one number per track.
    # Sorted slowest to fastest so the most durable assets are at the top.
    # A shorter bar = slower decay = more durable catalogue asset.
    df_hl  = pd.read_csv('outputs/halflife_26tracks.csv')   # output from Script 01
    df_hl['Retention'] = df_hl['Track'].map(RETENTION)      # add retention for Chart C

    df_lam = df_hl.dropna(subset=['Lambda']).sort_values('Lambda')   # sort ascending
    colors = [AFRO if g == "Afrobeats" else LATIN for g in df_lam.Genre]

    fig, ax = plt.subplots(figsize=(15, 10))
    bars = ax.barh(range(len(df_lam)), df_lam.Lambda, color=colors, height=0.70, alpha=.88)

    # label each bar with its lambda value
    for i, (bar, (_, row)) in enumerate(zip(bars, df_lam.iterrows())):
        ax.text(bar.get_width() + .001, i, f"λ={row['Lambda']:.4f}",
                va='center', fontsize=10, color="#bbb")

    ax.set_yticks(range(len(df_lam)))
    ax.set_yticklabels(df_lam.Track, fontsize=12, color=W)

    # reference line at λ=0.05 — informal threshold between durable and volatile
    ax.axvline(.05, color='#444', lw=1.2, ls='--')
    ax.text(.052, len(df_lam) - .5, "durable  to  volatile", fontsize=9, color="#555", va='top')

    ax.set_xlabel("Decay Rate λ — lower = slower decay = more durable Spotify catalogue asset",
                  fontsize=11, color="#aaa", labelpad=10)
    ax.set_title(
        "DECAY RATE (LAMBDA)  Which Tracks Burn Slowest?\n"
        "Lower number = slower audience loss = higher long-term Spotify catalogue value",
        color=GOLD, fontsize=14, fontweight='bold', loc='left', pad=14)
    ax.spines[["top", "right", "bottom"]].set_visible(False)
    ax.grid(axis='x', alpha=.12)
    ax.tick_params(labelsize=11, colors=W)
    ax.legend(
        handles=[mpatches.Patch(color=AFRO, label='Afrobeats'),
                 mpatches.Patch(color=LATIN, label='Latin Pop')],
        framealpha=0, labelcolor=W, fontsize=11)
    add_branding(fig)
    plt.tight_layout(rect=[0, .055, 1, 1])
    plt.savefig('outputs/lambda_ranked.png', dpi=200, bbox_inches='tight', facecolor=BG)
    plt.close()
    print("Saved: outputs/lambda_ranked.png")

    # ── CHART C: HALF-LIFE vs RETENTION SCATTER ───────────────────────────────
    # Two independent measures of durability plotted against each other.
    # X-axis: how many weeks before streams halved (half-life)
    # Y-axis: what % of listeners were still streaming at 6 months (retention)
    # Bubble size: peak weekly Spotify streams — bigger bubble = bigger peak
    # Tracks in the top-right quadrant are the most valuable by both measures.
    fig, ax = plt.subplots(figsize=(15, 9))

    for _, row in df_hl.dropna(subset=['HalfLife_Wks']).iterrows():
        c   = AFRO if row.Genre == "Afrobeats" else LATIN
        ret = RETENTION.get(row.Track, 0)

        # scale bubble size by peak streams — clamp to a visible range
        sz = max(80, min(row.Peak_Streams / 25000, 900))

        ax.scatter(row.HalfLife_Wks, ret,
                   s=sz, color=c, alpha=.75, edgecolors=c, lw=.8, zorder=4)

        # label each bubble with the track name
        ax.annotate(row.Track, (row.HalfLife_Wks, ret),
                    xytext=(6, 3), textcoords='offset points',
                    fontsize=9.5, color=W, alpha=.9)

    ax.set_xlabel("How many weeks before Spotify streams halved (half-life)",
                  fontsize=11, color="#aaa", labelpad=10)
    ax.set_ylabel("What % of Spotify listeners stayed after 6 months (retention)",
                  fontsize=11, color="#aaa", labelpad=10)
    ax.set_title(
        "HALF-LIFE vs RETENTION  Two Ways to Measure Durability\n"
        "bubble size = peak weekly Spotify streams in primary market",
        color=GOLD, fontsize=14, fontweight='bold', loc='left', pad=14)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=.10)
    ax.tick_params(labelsize=11, colors=W)
    ax.legend(
        handles=[mpatches.Patch(color=AFRO, label='Afrobeats'),
                 mpatches.Patch(color=LATIN, label='Latin Pop')],
        framealpha=0, labelcolor=W, fontsize=11)
    add_branding(fig)
    plt.tight_layout(rect=[0, .055, 1, 1])
    plt.savefig('outputs/hl_vs_retention.png', dpi=200, bbox_inches='tight', facecolor=BG)
    plt.close()
    print("Saved: outputs/hl_vs_retention.png")


if __name__ == "__main__":
    main()
