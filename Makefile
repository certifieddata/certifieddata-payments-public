# CertifiedData Agent Commerce — developer Makefile
# One-command local orchestration for the demo suite.

SHELL := /bin/bash
PY    ?= python3
MOCK_PORT ?= 3456
LISTENER_PORT ?= 4567

export CDAC_BASE_URL ?= http://localhost:$(MOCK_PORT)
export CDAC_API_KEY  ?= cdp_test_any

.PHONY: help install mock stop demo demo-certified demo-denied demo-idempotency \
        demo-all webhooks listener verify-local clean

help:
	@echo "CertifiedData Agent Commerce — local targets"
	@echo ""
	@echo "  make install           install Python SDK + flask + cryptography"
	@echo "  make mock              start the local mock server (blocking)"
	@echo "  make demo              run the basic 5-phase demo against the mock"
	@echo "  make demo-certified    run the certified-artifact demo"
	@echo "  make demo-denied       run the governance/denied-path demo"
	@echo "  make demo-idempotency  run the idempotency-replay demo"
	@echo "  make demo-all          run every demo in sequence"
	@echo "  make listener          run the webhooks listener (blocking)"
	@echo "  make verify-local RID=<receipt_id>  verify a receipt via the mock"
	@echo "  make stop              kill any mock server listening on $(MOCK_PORT)"
	@echo ""
	@echo "Recommended workflow:"
	@echo "  terminal A:  make mock"
	@echo "  terminal B:  make listener"
	@echo "  terminal C:  make demo-all"

install:
	$(PY) -m pip install -e packages/python-sdk flask cryptography requests

mock:
	@echo "  Starting CDAC mock on :$(MOCK_PORT) — Ctrl-C to stop"
	$(PY) examples/claude-demo/mock_server.py

stop:
	-@lsof -ti :$(MOCK_PORT) | xargs -r kill || true

demo:
	$(PY) examples/claude-demo/demo.py

demo-certified:
	$(PY) examples/claude-demo/demo_certified.py

demo-denied:
	$(PY) examples/claude-demo/demo_denied.py

demo-idempotency:
	$(PY) examples/claude-demo/demo_idempotency.py

demo-all: demo demo-certified demo-denied demo-idempotency

listener:
	LISTENER_PORT=$(LISTENER_PORT) $(PY) examples/webhooks-listener/listener.py

verify-local:
	@if [ -z "$(RID)" ]; then echo "Usage: make verify-local RID=rcpt_…"; exit 2; fi
	@curl -s $(CDAC_BASE_URL)/api/payments/verify/$(RID) | $(PY) -m json.tool

clean:
	find . -name '__pycache__' -prune -exec rm -rf {} +
	find . -name '*.pyc' -delete
	-@rm -rf packages/*/dist node_modules
