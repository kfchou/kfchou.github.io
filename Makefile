## ------------------------------------------------------------------------
## This is a header for the makefile
## All lines with ## is discoverable by the help command.
## The @ symbol at the beginning of a command in a Makefile suppresses the command echo.
## Long commands can be broken up with \
## Separate commands are denoted by &&
## ------------------------------------------------------------------------

# Include the .env file
-include .env

# set the interpreter to bash shell
SHELL := /bin/bash

# Set default variable values
my_makevar ?= default_value

# make TARGET_STAGE variable visible to all subprocesses
export TARGET_STAGE

help: ## Print this help message
	@echo "Available commands:"
	@egrep -h '##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?##"}; {printf "\033[36m %-15s\033[0m %s\n", $$1, $$2}'

build: ## Build the docker image. Options are based on your Dockerfile
	@echo "build"
	@$(SHELL) -c "\
	docker build \
	--build-arg X=$(X) \
	--target $(TARGET_STAGE) \
	--platform linux/amd64 \
	-t $(IMAGE_NAME) ."

start: ## Launch the container. Alternatively, you can call your docker-compose file.
	@echo "Running container..."
	@$(SHELL) -c "\
	docker run -d \
	--name $(CONTAINER_NAME) \
	--runtime_variable $(RUNTIME_VARIABLE) \
	-p $(PORT):$(PORT) \
	-v $(host_path1):$(docker_path1):rw \
	-v $(host_path2):$(docker_path2):ro \
	-v ~/.ssh:/home/user/.ssh:ro \
	-e runtime_env_variable=$(runtime_env_variable) \
	$(IMAGE_NAME)"

logs: ## Tail the container logs
    @echo "Tailing Docker container logs..."
    docker logs -f $(CONTAINER_NAME)

shell: ## Enter the container shell
	@echo "Entering Docker container shell..."
	@$(SHELL) -c "\
	docker exec -it $(CONTAINER_NAME) /bin/sh
	"
test: ## Run tests
	@echo $(my_makevar)
	@$(SHELL) -c "\
	docker exec -it $(CONTAINER_NAME) pytest -pytest_options
	"

stop: ## Stop the container
	@echo "Stopping container..."
	@$(SHELL) -c "\
	docker stop $(CONTAINER_NAME)
	"

rm: ## Remove the container
	@echo "Removing container..."	
	@$(SHELL) -c "\
	docker rm $(CONTAINER_NAME)
	"

clean: rm ## Clean up all Docker artifacts (include image)
	@echo "Cleaning up Docker artifacts..."
	docker rmi $(IMAGE_NAME)

redeploy: clean build run ## Rebuild and run the container

# Phony targets
.PHONY: help build logs start shell test stop rm clean redeploy
