import numpy as np
import polars as pl
import os

# ---------------------------------------------------------------------------
# CONFIG
# Why here at the top? So you can tweak the shape of your data without
# hunting through the code. Change these and re-run — no logic changes needed.
# ---------------------------------------------------------------------------
SEED       = 42          # fixed seed = reproducible results every time
START_DATE = "2022-01-01"
END_DATE   = "2024-12-31"

BASELINE   = 1_000       # daily revenue on day 0 (your starting floor)
TREND_RATE = 0.5         # revenue added per day — 0.5 = ~$180 more/year
WEEKLY_AMP = 150         # strength of the Mon-Sun wave
YEARLY_AMP = 300         # strength of the Jan-Dec wave (summer peak etc.)
NOISE_STD  = 80          # std dev of random daily noise
N_PROMO_DAYS = 20        # how many random promo/spike days per year
PROMO_BOOST  = (300, 800)# (min, max) revenue added on promo days

OUTPUT_DIR  = "data"
OUTPUT_FILE = "raw_data.csv"


def build_date_series(start: str, end: str) -> pl.Series:
    """
    Why Polars date_range instead of pandas?
    Polars is faster on large DataFrames and has a cleaner API for time series.
    eager=True returns the series immediately instead of a lazy expression.
    """
    return pl.date_range(
        pl.date(*map(int, start.split("-"))),
        pl.date(*map(int, end.split("-"))),
        interval="1d",
        eager=True,
    )


def trend(n: int) -> np.ndarray:
    """
    Why a linear trend?
    It's the simplest assumption: revenue grows steadily over time.
    If you later find it's exponential, you can swap np.arange for np.exp here.
    """
    return BASELINE + np.arange(n) * TREND_RATE


def weekly_seasonality(n: int) -> np.ndarray:
    """
    Why a sine wave with period 7?
    A sine wave is the simplest smooth repeating pattern.
    Period = 7 days means it completes one full cycle per week.
    This captures the Mon-dip / Fri-Sat peak rhythm common in retail.
    """
    return WEEKLY_AMP * np.sin(2 * np.pi * np.arange(n) / 7)


def yearly_seasonality(dates: pl.Series) -> np.ndarray:
    """
    Why day-of-year for yearly seasonality?
    Day-of-year (1–365) lets us build a full annual wave — peaks in summer,
    troughs in winter, or whatever pattern your business follows.
    The sine wave peaks around day 180 (late June) by default.
    """
    day_of_year = dates.dt.ordinal_day().to_numpy()
    return YEARLY_AMP * np.sin(2 * np.pi * day_of_year / 365)


def weekend_boost(dates: pl.Series) -> np.ndarray:
    """
    Why a separate weekend boost on top of the weekly sine wave?
    The sine wave gives a smooth weekly rhythm, but many businesses have a
    sharp discrete jump on weekends — that's hard to model with a smooth curve.
    Combining both gives a more realistic shape.
    Polars weekday(): Monday=0, Sunday=6.
    """
    dow = dates.dt.weekday().to_numpy()
    return np.where(dow >= 5, 200, 0).astype(float)


def noise(n: int, rng: np.random.Generator) -> np.ndarray:
    """
    Why Gaussian noise?
    Real daily revenue fluctuates randomly around its expected value.
    Normal distribution is the standard assumption when you don't know better.
    NOISE_STD controls how "wiggly" the data looks.
    """
    return rng.normal(loc=0, scale=NOISE_STD, size=n)


def promo_spikes(n: int, rng: np.random.Generator) -> np.ndarray:
    """
    Why add spikes?
    Real businesses run promotions, flash sales, and holiday events that
    create sudden jumps in revenue. Without these, a model trained on smooth
    data won't be robust to real-world surprises.
    N_PROMO_DAYS per year scales the count to the dataset length.
    """
    years = n / 365
    n_spikes = int(N_PROMO_DAYS * years)
    spike_days = rng.choice(n, size=n_spikes, replace=False)
    boost = rng.uniform(*PROMO_BOOST, size=n_spikes)

    spikes = np.zeros(n)
    spikes[spike_days] = boost
    return spikes


def generate(start: str = START_DATE, end: str = END_DATE) -> pl.DataFrame:
    rng   = np.random.default_rng(seed=SEED)
    dates = build_date_series(start, end)
    n     = len(dates)

    # Stack each component — this mirrors how real revenue actually forms.
    # Keeping them separate makes it easy to inspect or tune each layer.
    revenue = (
        trend(n)
        + weekly_seasonality(n)
        + yearly_seasonality(dates)
        + weekend_boost(dates)
        + noise(n, rng)
        + promo_spikes(n, rng)
    )

    # Clip at 0: revenue can't be negative (returns/refunds are handled elsewhere)
    revenue = np.clip(revenue, 0, None)

    return pl.DataFrame({"date": dates, "revenue": revenue})


def save(df: pl.DataFrame) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    df.write_csv(path)
    return path


if __name__ == "__main__":
    df   = generate()
    path = save(df)

    print(f"Generated {len(df):,} days of data  ({START_DATE} to {END_DATE})")
    print(f"Revenue  min={df['revenue'].min():.0f}  "
          f"mean={df['revenue'].mean():.0f}  "
          f"max={df['revenue'].max():.0f}")
    print(f"Saved to {path}")
