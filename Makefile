VENV = .venv
ifeq ($(OS),Windows_NT)
    PYTHON_EXECUTABLE = python
    VENV_BIN = $(VENV)/Scripts
else
    PYTHON_EXECUTABLE = python
    VENV_BIN = $(VENV)/bin
endif

POETRY_VERSION=1.3.1
POETRY_RUN = $(VENV_BIN)/poetry run

# Manually define main variables

CLIENT_NAME = client
SERVER_NAME = server
ADMIN_NAME = admin

ifndef APP_PORT
override APP_PORT = 8000
endif

ifndef APP_HOST
override APP_HOST = 127.0.0.1
endif

args := $(wordlist 2, 100, $(MAKECMDGOALS))
ifndef args
MESSAGE = "No such command (or you pass two or many targets to ). List of possible commands: make help"
else
MESSAGE = "Done"
endif

CODE = $(CLIENT_NAME) $(SERVER_NAME) $(ADMIN_NAME)

# Commands

env:
	@$(eval SHELL:=/bin/bash)
	@cp .env.example .env


venv: ##@Environment Create virtual environment
	$(PYTHON_EXECUTABLE) -m venv $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade pip
	$(VENV_BIN)/python -m pip install poetry==$(POETRY_VERSION)
	$(VENV_BIN)/poetry config virtualenvs.create true
	$(VENV_BIN)/poetry config virtualenvs.in-project true
	$(VENV_BIN)/poetry install --no-interaction --no-ansi


install: ##@Code Install dependencies
	poetry install --no-interaction --no-ansi


up_client: ##@Application Up Client
	$(POETRY_RUN) python -m $(CLIENT_NAME)

up_admin: ##@Application Up Admin
	$(POETRY_RUN) python -m $(ADMIN_NAME)

up_server: ##@Application Up Server
	$(POETRY_RUN) python -m server

run: ##@Application Up App, Admin and Server
	$(POETRY_RUN) python -m $(CLIENT_NAME) & $(POETRY_RUN) python -m $(ADMIN_NAME) & $(POETRY_RUN) python -m $(SERVER_NAME)

format: ###@Code Formats all files
	$(POETRY_RUN) autoflake --recursive --in-place --remove-all-unused-imports $(CODE)
	$(POETRY_RUN) isort $(CODE)
	$(POETRY_RUN) black --line-length 79 --target-version py310 --skip-string-normalization $(CODE)
	$(POETRY_RUN) unify --in-place --recursive $(CODE)


lint: ###@Code Lint code
	$(POETRY_RUN) flake8 --jobs 4 --statistics --show-source $(CODE)
	$(POETRY_RUN) pylint $(CODE)
	$(POETRY_RUN) black --line-length 79 --target-version py310 --skip-string-normalization --check $(CODE)


check: format lint ###@Code Format and lint code
