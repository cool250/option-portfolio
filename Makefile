VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

run: install
	$(PYTHON) index.py


install: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip &&\
		$(PIP) install -r requirements.txt

clean:
	rm -rf __pycache__
	rm -rf $(VENV)

format:
	black *.py

lint:
	pylint index.py