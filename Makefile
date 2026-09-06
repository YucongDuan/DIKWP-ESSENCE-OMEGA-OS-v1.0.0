PYTHON ?= python

.PHONY: test demo suite verify zipapp dashboard release

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

demo:
	PYTHONPATH=src $(PYTHON) -m essence_omega_os demo --output outputs/demo

suite:
	PYTHONPATH=src $(PYTHON) -m essence_omega_os suite --examples examples --output outputs/reference

verify:
	PYTHONPATH=src $(PYTHON) scripts/verify_release.py

zipapp:
	$(PYTHON) scripts/build_zipapp.py

dashboard:
	$(PYTHON) scripts/build_offline_dashboard.py

release: test suite zipapp dashboard verify
