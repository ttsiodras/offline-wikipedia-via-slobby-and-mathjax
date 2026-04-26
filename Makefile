# Makefile for MathJax Proxy Docker container
# Combined container: Slobby server + MathJax proxy

IMAGE_NAME = mathjax-proxy
CONTAINER_NAME = mathjax-proxy

# Default target: build if needed, then always run
.PHONY: default
default: build
	@$(MAKE) run

# Build the Docker image (combined Slobby + MathJax proxy)
.PHONY: build
build:
	@echo "Building Docker image..."
	@if ! docker image inspect $(IMAGE_NAME) > /dev/null 2>&1; then \
		docker build -t $(IMAGE_NAME) .; \
	else \
		echo "Image already exists. Use 'make rebuild' to force rebuild."; \
	fi

# Force rebuild the Docker image
.PHONY: rebuild
rebuild:
	@echo "Rebuilding Docker image..."
	docker build -t $(IMAGE_NAME) .

# Run the container (starts both Slobby and MathJax proxy)
.PHONY: run
run:
	@echo "Starting combined container (Slobby + MathJax proxy)..."
	@docker stop $(CONTAINER_NAME) 2>/dev/null || true
	@docker rm $(CONTAINER_NAME) 2>/dev/null || true
	docker run --rm --name $(CONTAINER_NAME) \
		-p 127.0.0.1:8013:8013 \
		-p 127.0.0.1:8014:8014 \
		-v /opt/aard.wikipedia:/opt/aard \
		-e TARGET_HOST=127.0.0.1 \
		-e TARGET_PORT=8013 \
		-e SLOBBY_FILE=/opt/aard/enwiki-20260401.slob \
		$(IMAGE_NAME)
	@echo "Container started."
	@echo "  - Slobby:   http://127.0.0.1:8013"
	@echo "  - Proxy:    http://127.0.0.1:8014"

# Stop the container
.PHONY: stop
stop:
	@echo "Stopping container..."
	@docker stop $(CONTAINER_NAME) 2>/dev/null || true
	@docker rm $(CONTAINER_NAME) 2>/dev/null || true
	@echo "Container stopped."

# View logs
.PHONY: logs
logs:
	docker logs -f $(CONTAINER_NAME)

# Shell into the container
.PHONY: shell
shell:
	docker exec -it $(CONTAINER_NAME) /bin/sh

# Clean up (stop, remove container, and remove image)
.PHONY: clean
clean: stop
	@echo "Removing image..."
	@docker rmi $(IMAGE_NAME) 2>/dev/null || true
	@echo "Clean complete."
