all: run

run:
	docker-compose up --build --scale e2e=0

test:
	docker-compose up --build e2e

.PHONY: test
