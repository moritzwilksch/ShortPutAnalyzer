import yfinance as yf
import datetime
import pandas as pd
from py_vollib.black_scholes.greeks.numerical import delta
from treasury_api import TreasuryAPI
from rich.console import Console
import numpy as np
from pymongo import MongoClient
import os

c = Console()


class Underlying:
    """Represents an underlying by ticker symbol"""

    def __init__(
        self, ticker: str = None, dte_considered: tuple[int, int] = None
    ) -> None:
        """Initialize underlying"""
        if dte_considered is None:
            self.dte_considered = (25, 50)

        self.ticker: str = ticker
        self.today = datetime.datetime.today()
        self.yfticker: yf.Ticker = yf.Ticker(ticker)
        self.last_close = self.yfticker.history("1d")["Close"].tolist()[0]

        self._load_expirations()
        self._load_put_options()
        self._load_return_std()
        self._load_riskfree_rate()

    # ------------------------------- Private Methods -------------------------------
    def _load_expirations(self):
        """Loads available & considered expirations from YF"""
        # maps YYYY-MM-DD expiration dates -> number of days until then
        self.available_expirations: dict[str, int] = {
            expdate: (datetime.datetime.strptime(expdate, "%Y-%m-%d") - self.today).days
            for expdate in self.yfticker.options
        }

        # set of expirations that have DTE in range of dte_considered
        self.considered_expirations = {
            k: v
            for k, v in self.available_expirations.items()
            if v >= self.dte_considered[0] and v <= self.dte_considered[1]
        }

    def _load_put_options(self):
        """Loads put options from YF as dict: expiration_date -> list of options"""
        self.put_options: dict = dict()
        for expiration_date in self.considered_expirations:
            self.put_options[expiration_date] = self._extract_from_yf_option_chain(
                self.yfticker.option_chain(expiration_date).puts
            )

    def _extract_from_yf_option_chain(self, option_chain: pd.DataFrame):
        """Extracts data from YF option chain"""
        results = []
        for record in option_chain.to_records():
            results.append(
                {
                    "strike": record["strike"],
                    "lastPrice": record["lastPrice"],
                    "inTheMoney": record["inTheMoney"],
                }
            )

        return results

    def _load_return_std(self):
        """Loads the return standard deviation of the underlying"""
        self.return_std = self.yfticker.history(period="2y")["Close"].pct_change().std()

    def _load_riskfree_rate(self):
        api = TreasuryAPI()
        self.riskfree_rate = api.pull_tbill_rate()

    def _add_delta_to_put_options(self) -> None:
        """Adds delta to each put option"""
        for expiration_date, dte in self.considered_expirations.items():
            for option in self.put_options[expiration_date]:

                option_delta = delta(
                    flag="p",
                    S=self.last_close,
                    K=option["strike"],
                    t=dte / 365,
                    r=self.riskfree_rate,
                    sigma=self.return_std * (365) ** 0.5,
                )
                option["delta"] = abs(option_delta)

    def _add_annualized_return_to_put_options(self) -> None:
        """Adds annualized return to each put option"""
        for expiration_date, dte in self.considered_expirations.items():
            for option in self.put_options[expiration_date]:
                option["annualized_return"] = (
                    (option["lastPrice"] / option["strike"])
                    * (1 - option["delta"])
                    / dte
                    * 365
                )

    # ------------------------------- Public Methods -------------------------------
    def get_avg_annualized_return(
        self, expiration: str = None, delta_range: tuple[float, float] = None
    ) -> float:
        """
        Returns the average annualized return of the underlying.
        Defined as: average annualized return of all put options with delta in `delta_range` (default: [0.1, 0.3])
        """
        if expiration is None:
            raise ValueError("Expiration date must be specified")

        if delta_range is None:
            delta_range = (0.1, 0.3)

        return np.mean(
            [
                option["annualized_return"]
                for option in self.put_options[expiration]
                if delta_range[0] <= option["delta"] <= delta_range[1]
            ]
        )

    def initialize_greeks_and_profitability(self) -> None:
        self._add_delta_to_put_options()
        self._add_annualized_return_to_put_options()

    def get_expiration_closest_to(self, dte:int) -> str:
        """ Returns expiration date closest to dte """
        return min({k: abs(v - dte) for k, v in self.available_expirations.items()}.items(), key=lambda x: x[1])[0]

    def persist_to_db(self) -> None:
        user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
        passwd = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
        dbname = os.getenv("MONGO_INITDB_DATABASE")

        # client = MongoClient(f"mongodb://{user}:{passwd}@localhost:27017/{dbname}?authSource=admin")
        # client = MongoClient(host="localhost", port=27017, username=user, password=passwd, authSource="admin")
        client = MongoClient(f"mongodb://{user}:{passwd}@localhost:27017/{dbname}", authSource="admin")
        db = client.get_database(dbname)
        coll = db.get_collection("underlyings")

        for x in coll.find():
            print(x)

        print("works")

        datalist = []
        for expiration, data in self.put_options.items():
            for elem in data:
                elem["inTheMoney"] = bool(elem["inTheMoney"])
            datalist.append({expiration: data})

        coll.insert_many(datalist)

        client.close()



if __name__ == "__main__":
    apple = Underlying("AAPL")
    apple.initialize_greeks_and_profitability()
    apple.persist_to_db()
    c.print(apple.put_options)
    print(apple.available_expirations)
