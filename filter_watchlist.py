#%%
import polars as pl
import json

with open("watchlist.json", "r") as f:
    records = json.load(f)


def fix_dtypes(data) -> pl.DataFrame:
    return data.with_columns(
        [
            pl.col("no").cast(pl.Int16),
            pl.col("sector").cast(pl.Categorical),
            pl.col("industry").cast(pl.Categorical),
            pl.col("country").cast(pl.Categorical),
            pl.col("pe").cast(pl.Float32),
            pl.col("price").cast(pl.Float32),
        ]
    )


df: pl.DataFrame = pl.from_records(records).pipe(fix_dtypes)

#%%
filtered_tickers = df.filter((pl.col("country") == "USA") & (pl.col("price") <= 100)).select(
    "ticker"
).to_series()

#%%
len(filtered_tickers)

#%%
with open("filtered_watchlist.txt", "w") as f:
    for ticker in filtered_tickers:
        f.write(f"{ticker}\n")
