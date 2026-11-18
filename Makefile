PYTHON=python

data:
	@echo "Use: python src/download.py --months YYYY-MM YYYY-MM ..."
	$(PYTHON) src/build_panel.py

diagnostics:
	$(PYTHON) src/diagnostics.py

figures:
	$(PYTHON) src/visualize.py

test:
	pytest -q

all: data diagnostics figures test
