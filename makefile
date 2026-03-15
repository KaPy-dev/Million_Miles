.PHONY: build run stop logs restart clean 
build:
	docker-compose build

run:
	docker-compose up -d

stop:
	docker-compose down

logs:
	docker-compose logs -f

restart: stop run

clean:
	docker-compose down -v
	docker rmi vavilon-frontend

restart:
	docker compose up --build -d && docker compose logs -f