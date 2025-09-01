.PHONY: build run test

build:
	docker build --push -t ghcr.io/enso-labs/interpreter:latest .

docker_run:
	docker run -d --name interpreter ghcr.io/enso-labs/interpreter:latest

test:
	python -m unittest discover