VENV_DIR := .venv
PYTHON := python
VENV_PY := $(VENV_DIR)\Scripts\python.exe

.PHONY: venv install install-dev run clean enable-git-hooks init

init:
	@echo Initializing project...
	@$(MAKE) enable-git-hooks
	@$(MAKE) install-dev

venv:
	@if not exist "$(VENV_DIR)\Scripts\activate.bat" $(PYTHON) -m venv $(VENV_DIR)

install: venv
	@echo Installing production dependencies...
	@$(VENV_PY) -m pip install --upgrade pip
	@$(VENV_PY) -m pip install .

install-dev: venv
	@echo Installing development dependencies...
	@$(VENV_PY) -m pip install --upgrade pip
	@$(VENV_PY) -m pip install -e .[dev]

run:
	@echo Running Scrim Bot...
	@$(VENV_PY) src/main.py

clean:
	@echo Removing virtual environment...
	@if exist $(VENV_DIR) rmdir /S /Q $(VENV_DIR)

enable-git-hooks:
	git config --local core.hooksPath .githooks