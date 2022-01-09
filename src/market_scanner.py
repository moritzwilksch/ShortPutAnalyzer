from underlying import Underlying
from rich.progress import track
from rich.table import Table
from rich.console import Console

c = Console()

watchlist = ["OHI", "MPW", "PFE"]
underlyings = []

for ticker in track(watchlist, description="Loading underlyings..."):
    underlying = Underlying(ticker)
    underlying.initialize_greeks_and_profitability()
    underlyings.append(underlying)

table = Table(title="Underlyings Profitability")
table.add_column("Ticker", justify="left")
table.add_column("Annualized Return", justify="center")

for underlying in underlyings:
    profitability = underlying.get_avg_annualized_return('2022-02-11')

    table.add_row(
        underlying.ticker,
        f"{profitability:.2%}%",
    )

c.print(table)
