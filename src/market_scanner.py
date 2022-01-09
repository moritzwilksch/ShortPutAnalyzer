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


def get_initialized_underlying(ticker: str) -> Underlying:
    underlying = Underlying(ticker)
    underlying.initialize_greeks_and_profitability()
    return underlying


with Status("Lodaing underlyings...", spinner="bouncingBar", console=c) as status:
    underlyings: list[Underlying] = Parallel(n_jobs=2, prefer="threads")(
        delayed(get_initialized_underlying)(ticker) for ticker in watchlist
    )


table = Table(title="Underlyings Profitability")
table.add_column("Ticker", justify="center", style="cyan")
table.add_column("Expiration", justify="center")
table.add_column("Annualized Return", justify="center")

results = []
for underlying in underlyings:
    best_expiration = underlying.get_expiration_closest_to(40)
    profitability = underlying.get_avg_annualized_return(best_expiration)
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
c.print(table)
