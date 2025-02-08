.PHONY: build run clean logs test

# Переменные
IMAGE_NAME = proxy-server
CONTAINER_NAME = proxy-server
PORT = 5000

# Сборка Docker образа
build:
	docker build -t $(IMAGE_NAME) .

# Запуск контейнера
run:
	docker run -d --name $(CONTAINER_NAME) -p $(PORT):$(PORT) $(IMAGE_NAME)

# Остановка и удаление контейнера
clean:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

# Просмотр логов
logs:
	docker logs -f $(CONTAINER_NAME)

# Перезапуск контейнера
restart: clean run

# Сборка и запуск
up: build run

# Проверка статуса контейнера
status:
	docker ps -a | grep $(CONTAINER_NAME)
