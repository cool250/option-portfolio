VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

run: install
	$(PYTHON) src/index.py


install: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip &&\
		$(PIP) install -r requirements.txt

clean:
	rm -rf __pycache__
	rm -rf $(VENV)

format:
	black src/*.py

lint:
	pylint src/index.py