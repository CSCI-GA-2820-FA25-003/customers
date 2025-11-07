# ===================================================
# Build configuration
# ===================================================
PROJECT      ?= customers
IMAGE_NAME   ?= $(PROJECT)-service
TAG          ?= latest

# ===================================================
# Docker build/run/push
# ===================================================
build:
	docker build -t $(IMAGE_NAME):$(TAG) -f service/Dockerfile .

run:
	docker run --rm -p 8080:8080 $(IMAGE_NAME):$(TAG)

push:
	docker push $(IMAGE_NAME):$(TAG)
