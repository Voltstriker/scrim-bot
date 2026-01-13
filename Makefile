VENV_DIR := .venv
PYTHON := python
VENV_PY := $(VENV_DIR)\Scripts\python.exe

.PHONY: venv install run clean enable-git-hooks init

init:
	@echo Initializing project...
	@$(MAKE) enable-git-hooks
	@if not exist requirements.txt echo "requirements.txt not found. Please create it." && exit 1
	@$(MAKE) install

venv:
	@if not exist "$(VENV_DIR)\Scripts\activate.bat" $(PYTHON) -m venv $(VENV_DIR)

install: venv
	@echo Installing requirements...
	@$(VENV_PY) -m pip install --upgrade pip
	@$(VENV_PY) -m pip install -r requirements.txt

run:
	@echo Running SoV Bot...
	@$(VENV_PY) bot.py

clean:
	@echo Removing virtual environment...
	@if exist $(VENV_DIR) rmdir /S /Q $(VENV_DIR)

enable-git-hooks:
	git config --local core.hooksPath .githooks