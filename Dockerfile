FROM python:slim-buster
WORKDIR /app

RUN apt-get update -y \
  && apt-get -y install \
    xvfb \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

RUN pip install playwright && playwright install
COPY requirements.txt /app/requirements.txt
RUN python3 -m pip install -r /app/requirements.txt

COPY fetch_watchlist_tickers.py /app/fetch_watchlist_tickers.py

CMD xvfb-run python /app/fetch_watchlist_tickers.py