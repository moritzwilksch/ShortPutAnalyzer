FROM mcr.microsoft.com/playwright/python:v1.21.0-focal
WORKDIR /app

RUN apt-get update -y \
  && apt-get -y install \
    xvfb \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*


COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY fetch_watchlist_tickers.py /app/fetch_watchlist_tickers.py

CMD xvfb-run python /app/fetch_watchlist_tickers.py