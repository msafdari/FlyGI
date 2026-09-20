# FlyGI Milestones 0-1 developer and ARC-AGI-3 submission workflow.
PYTHON           ?= python3.12
UV               ?= uv
UV_RUN           := $(UV) run
FRAMEWORK_REPO   := https://github.com/arcprize/ARC-AGI-3-Agents.git
FRAMEWORK_COMMIT := 4743e7d0aaae0ded0d98a89a7e282e63564cd58b
FRAMEWORK_DIR    := vendor/ARC-AGI-3-Agents
COMP_SLUG        := arc-prize-2026-arc-agi-3
GAME             ?=
STEPS            ?= 200
BASELINE_SEEDS   ?= 0 1 2 3 4
BASELINE_ACTIONS ?= 80
BASELINE_GAMES   ?= all
BASELINE_OUTPUT  ?=
KAGGLE           := KAGGLE_API_TOKEN=$$(cat .kaggle/access_token) $(UV_RUN) kaggle

.PHONY: help setup test lint smoke play-local verify-local baseline-local list-games notebook submit status clean _check-kaggle

help:
	@awk 'BEGIN{FS=":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  %-15s %s\n",$$1,$$2}' $(MAKEFILE_LIST)

setup: ## Install locked dependencies and pin the official ARC agent framework
	$(UV) sync --extra arc --extra dev
	@if [ ! -d "$(FRAMEWORK_DIR)/.git" ]; then \
		mkdir -p vendor; \
		git clone --filter=blob:none $(FRAMEWORK_REPO) $(FRAMEWORK_DIR); \
	fi
	git -C $(FRAMEWORK_DIR) fetch --depth 1 origin $(FRAMEWORK_COMMIT)
	git -C $(FRAMEWORK_DIR) checkout --detach $(FRAMEWORK_COMMIT)
	$(UV_RUN) python scripts/slim_framework.py

test: ## Run the offline unit test suite
	$(UV_RUN) pytest

lint: ## Run static lint and formatting checks
	$(UV_RUN) ruff check .
	$(UV_RUN) ruff format --check .

smoke: ## Run offline Milestone 0-1 smoke validation
	$(UV_RUN) python scripts/smoke_test.py

play-local: ## Play all public games, or one with GAME=ls20
	$(UV_RUN) python scripts/play_local.py $(if $(GAME),--game $(GAME)) --max-steps $(STEPS)

verify-local: ## Official-style two-game random-agent smoke run
	$(UV_RUN) python scripts/play_local.py --game ls20,vc33 --max-steps 50

baseline-local: ## Run the strict-offline five-seed public random baseline
	MPLCONFIGDIR=/tmp/flygi-mpl-cache $(UV_RUN) python scripts/evaluate_random_baseline.py \
		--seeds $(BASELINE_SEEDS) --games $(BASELINE_GAMES) \
		--action-budget $(BASELINE_ACTIONS) $(if $(BASELINE_OUTPUT),--output $(BASELINE_OUTPUT))

list-games: ## List public ARC-AGI-3 games
	$(UV_RUN) python scripts/play_local.py --list

notebook: ## Build the internet-disabled Kaggle submission notebook
	$(UV_RUN) python scripts/build_notebook.py

_check-kaggle:
	@if [ ! -s .kaggle/access_token ]; then \
		echo "ERROR: .kaggle/access_token is missing or empty."; \
		echo "Create a token at https://www.kaggle.com/settings and save it there."; \
		exit 1; \
	fi

submit: notebook _check-kaggle ## Push the generated notebook to Kaggle (does not spend a submission)
	@grep -q REPLACE_WITH_YOUR_USERNAME notebooks/kernel-metadata.json && { \
		echo "ERROR: replace REPLACE_WITH_YOUR_USERNAME in notebooks/kernel-metadata.json"; \
		exit 1; } || true
	$(KAGGLE) kernels push -p notebooks/

status: _check-kaggle ## Show the latest Kaggle kernel status
	@KERNEL_ID=$$($(PYTHON) -c "import json; print(json.load(open('notebooks/kernel-metadata.json'))['id'])"); \
	$(KAGGLE) kernels status $$KERNEL_ID

clean: ## Remove only generated local artifacts
	$(UV_RUN) python scripts/clean_generated.py
