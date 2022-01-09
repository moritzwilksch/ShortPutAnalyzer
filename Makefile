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