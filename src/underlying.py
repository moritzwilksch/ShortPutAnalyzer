import yfinance as yf
import datetime
import pandas as pd


class Underlying:
    """ Represents an underlying by ticker symbol """

    def __init__(
        self, ticker: str = None, dte_considered: tuple[int, int] = None
    ) -> None:
        """ Initialize underlying """
        if dte_considered is None:
            self.dte_considered = (25, 50)

        self.ticker: str = ticker
        self.today: str = datetime.datetime.today()
        self.yfticker: yf.Ticker = yf.Ticker(ticker)
        self.last_close = self.yfticker.history("1d")["Close"].tolist()[0]

        self._load_expirations()
        self._load_put_options()

    # --------------------- Private Methods ---------------------
    def _load_expirations(self):
        """ Loads available & considered expirations from YF """
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
        self.put_options: dict = dict()
        for expiration_date, dte in self.considered_expirations.items():
            self.put_options[expiration_date] = self._extract_from_yf_option_chain(
                self.yfticker.option_chain(expiration_date).puts
            )
            # self.put_options[expiration_date].append({"dte": dte})

    def _extract_from_yf_option_chain(self, option_chain: pd.DataFrame):
        """ Extracts data from YF option chain """
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

    # --------------------- Public Methods ---------------------
    # TBD


if __name__ == "__main__":
    apple = Underlying("AAPL")
    print(apple.available_expirations)
