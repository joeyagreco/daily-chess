.PHONY: deps
deps: deps
	@python3 -m pip install -r requirements.format.txt
	@python3 -m pip install -r requirements.txt

.PHONY: fmt
fmt:
	@black --config=pyproject.toml .
	@autoflake --config=pyproject.toml .
	@isort .

.PHONY: up
up:
	@python3 app.py

.PHONY: up-reqs
up-reqs:
	@pipreqs . --force

.PHONY: docker-build
docker-build:
	@docker build -t daily_chess .

.PHONY: docker
docker:
	@docker run daily_chess

.PHONY: docker-push
docker-push:
	@if [ -z "$(username)" ] || [ -z "$(tag)" ]; then \
		echo "Error: Dockerhub username or tag not provided. Please specify as 'make docker-push username=<username> tag=<tag>'"; \
	else \
		docker tag daily_chess $(username)/daily-chess:$(tag); \
		docker push $(username)/daily-chess:$(tag); \
	fi
