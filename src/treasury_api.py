from datetime import datetime
import requests
import datetime


class TreasuryAPI:
    def __init__(self) -> None:
        self.URL = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
        self.ENDPOINT = "/v2/accounting/od/avg_interest_rates"

        self.today_datetime = datetime.datetime.today()
        self.params = {
            "filter": f"record_calendar_year:gte:{self.today_datetime.year - 1},security_desc:eq:Treasury Bills"
        }

    def pull_tbill_rate(self) -> float:
        """Pulls the current tbill rate from the treasury api"""
        r = requests.get(f"{self.URL}{self.ENDPOINT}", params=self.params)
        jsondata = r.json()["data"]
        jsondata.sort(key=lambda x: x["record_date"])
        most_current_record = jsondata[-1]
        return float(most_current_record["avg_interest_rate_amt"])/100


if __name__ == "__main__":
    t = TreasuryAPI()
    print(t.pull_tbill_rate())
