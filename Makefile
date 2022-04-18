install:
	pip install -r requirements.txt

db-up:
	docker run \
		--name shortput-db \
		--restart unless-stopped \
		-d \
		-p 27017:27017 \
		--env-file .env \
		-v `pwd`/db:/data/db \
		mongo

db-down:
	docker stop shortput-db
	docker rm shortput-db

fetch-watchlist:
	xvfb-run python fetch_watchlist_tickers.py

docker/build:
	docker build -t finviz-scrape .

docker/run:
	docker container rm finviz-scrape
	docker run -it --name finviz-scrape finviz-scrape