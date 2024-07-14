---
layout: post
title:  Makefile Cheatsheet
categories: [Cheatsheet,Software,Makefile,Docker]
---
A template for using Makefiles to orchestrate Docker containers

# Makewhat?
Makefile is a *build tool* that helps us build & test our software, without having to remember potentially long shell commands. It's been around since the 1970s, and was primarily used to build & test C and C++ applications. 

There are plenty of guides and tutorials out there (like [this one by Chase Lambert](https://makefiletutorial.com/) or [this one by the npm founder Isaacs](https://gist.github.com/isaacs/62a2d1825d04437c6f08)), so the goal of this blogpost is to provide a template for using `Make` together with `Docker`.

## General Structure
Makefiles should be simple and intuitive. For example `make build` should build your program. `make test` should test it. Some people like to add `make dev` to create a virtual environment for them.

The basic syntax of the makefile is:
```
target: dependencies
    command
```
Here, the `dependencies` can be a file, or another command. Make assumes the dependency is a file by default.

Unless specified, the `command` is by default read by the `sh` interpreter.

# A word about Makefile variables and Shell variables
* When Make starts, it automatically creates Make variables out of all the environment variables (shell variables) that are already set.
* All variables created inside the Makefile are make_variables
* Shell variables are accessed with `$$shell_var`. Make variables are accessed with `$(make_var)`
* The `commands` in each `target` is executed in a subshell. So changes to variables do not persist across commands. Unless...
* The `export` command makes newly created `make_var` accessible to subshells (e.g., if it invokes another file that requires this new variable)

```makefile
one=this will only work locally
export two=we can run subcommands with this

all: 
	@echo $(one)
	@echo $$one
	@echo $(two)
	@echo $$two
```

Running `make all` will return:
```
$ make all
this will only work locally

we can run subcommands with this
we can run subcommands with this
```

# The Template
```makefile
## ------------------------------------------------------------------------
## This is a header for the makefile
## All lines with ## is discoverable by the help command.
## The @ symbol at the beginning of a command in a Makefile suppresses the command echo.
## Long commands can be broken up with \
## Separate commands are denoted by &&
## ------------------------------------------------------------------------

# Include the .env file
-include .env

# Define shell to be bash shell. This will be used in the commands later.
SHELL := /bin/bash

# Set default variable values
my_makevar ?= default_value

# make DOCKER_TARGET_STAGE variable visible to all subprocesses
export DOCKER_TARGET_STAGE

help: ## Print this help message
	@echo "Available commands:"
	@egrep -h '##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?##"}; {printf "\033[36m %-15s\033[0m %s\n", $$1, $$2}'

build: ## Build the docker image. Options are based on your Dockerfile
	@echo "build"
	@$(SHELL) -c "\
	docker build \
	--build-arg X=$(X) \
	--target $(DOCKER_TARGET_STAGE) \
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

# Phony targets. Docker will think your dependencies are files unless they're marked with "PHONY"
.PHONY: help build logs start shell test stop rm clean redeploy
```
Note the usage of `clean` and `redeploy` & how they invoke previous commands.
# Alternatives
Modern alternatives to Make solves problems like syntax, readability, and documentation, but they usually require additional installations. On the other hand, `Make` comes pre-installed in Linux systems.

If you're not opposed to additional installations, you may enjoy these alternatives:
* [Just](https://github.com/casey/just) - A command runner as opposed to a build system. Inspired by Make, with improvements. Recipes can be written in Python or sh script.
* [xc](https://xcfile.dev/) - Make + readme documentation. Each xc task is defined in simple, human-readable Markdown. This means that even people without the xc tool installed can use the README.md (or whatever Markdown file contains the tasks) as a source of useful commands for the project. See [Motivation](https://blog.joe-davidson.co.uk/posts/introducing-the-xc-readme-task-runner/). (requires Go, and requires $GOBIN to be in your $PATH)
* [Task](https://taskfile.dev/) - Aims to simplify Make. Commands are written in YML schema. Task is written in Go.
* Bazel - by Google
* Buck - by Facebook

# Resources
* [Customizing](https://gist.github.com/prwhite/8168133) the help message
* [Makefile Tutorial](https://makefiletutorial.com/) 
* [Another tutoria with sh syntax explanations](https://gist.github.com/isaacs/62a2d1825d04437c6f08)