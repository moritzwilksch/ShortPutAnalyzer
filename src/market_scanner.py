from underlying import Underlying
from rich.progress import track
from rich.table import Table
from rich.console import Console
from rich.status import Status
from joblib import Parallel, delayed

c = Console()

watchlist = [
    "OHI",
    "MPW",
    "IRM",
    "ABBV",
    "KR",
    "MAIN",
    "ARCC",
    "T",
    "PLTR",
    "SPHD",
    "SBUX",
]

with open("manual_filtered_watchlist.txt", "r") as f:
    watchlist = [ticker.strip() for ticker in f.readlines()]


def get_initialized_underlying(ticker: str) -> Underlying:
    try:
        underlying = Underlying(ticker)
        underlying.initialize_greeks_and_profitability()
    except:
        c.print(f"[yellow][WARN][/] Error initializing {ticker}")
        return None
    c.print(f"[green][INFO][/] Got {underlying.ticker}")
    return underlying


with Status("Loading underlyings...", spinner="bouncingBar", console=c) as status:
    underlyings: list[Underlying] = Parallel(n_jobs=2, prefer="threads")(
        delayed(get_initialized_underlying)(ticker) for ticker in watchlist
    )


table = Table(title="Underlyings Profitability")
table.add_column("Ticker", justify="center", style="cyan")
table.add_column("Expiration", justify="center")
table.add_column("Annualized Return", justify="center")

results = []
for underlying in underlyings:
    if underlying is None:
        continue

    best_expiration = underlying.get_expiration_closest_to(40)
    try:
        profitability = underlying.get_avg_annualized_return(best_expiration)
    except:
        c.print(f"[yellow][WARN][/] {underlying.ticker} has no options")
        continue

    if profitability > 0:
        results.append(
            {
                "ticker": underlying.ticker,
                "expiration": best_expiration,
                "return": profitability,
            }
        )


results.sort(key=lambda x: x["return"], reverse=True)
for result in results:
    table.add_row(result["ticker"], result["expiration"], f'{result["return"]:.2%}')
c.clear()
c.print(table)
