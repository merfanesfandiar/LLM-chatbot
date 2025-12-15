# --- Settings ---
APP = src/streamlit_app.py
VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
-include .env
export $(shell sed 's/=.*//' .env)

# Detect uv (exit code 0 if exists)
HAS_UV := $(shell command -v uv >/dev/null 2>&1 && echo 1 || echo 0)

# --- Helper messages ---
define MSG_UV
Using uv for environment & package management.
endef

define MSG_VENV
uv not found. Falling back to Python venv + pip.
endef

# --- Install dependencies ---
install:
ifeq ($(HAS_UV),1)
	@echo "$(MSG_UV)"
	uv pip install -r requirements.txt
else
	@echo "$(MSG_VENV)"
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
endif

# --- Run Streamlit ---
run:
ifeq ($(HAS_UV),1)
	
	uv run streamlit run $(APP) --client.toolbarMode=$(MODE)	
	
	
else
	$(PYTHON) -m streamlit run $(APP) --client.toolbarMode=$(MODE)
	
endif

ollama:
	ollama run $(OLLAMA_MODEL)

# --- Add a package ---
# Usage: make add pkg=requests
add:
ifeq ($(HAS_UV),1)
	uv add $(pkg)
else
	$(PIP) install $(pkg)
endif

# --- Remove a package ---
remove:
ifeq ($(HAS_UV),1)
	uv remove $(pkg)
else
	$(PIP) uninstall -y $(pkg)
endif

# --- Clean environment ---
clean:
ifeq ($(HAS_UV),1)
	uv clean
	rm -rf .uv
endif
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +

# --- Start = install + run ---
start: install run	ollama