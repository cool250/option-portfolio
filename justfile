default:
    just --list

show-my-environment:
    which python
    python --version
    which poetry
    poetry --version
    poetry env info
    poetry run python --version
    poetry version --short

clean-venv:
    rm -rf .venv

clean:
	rm -rf __pycache__

poetry-update:
    poetry update
    poetry install --no-root

poetry-venv:
    poetry install --no-root

run-app:
    poetry run python src/index.py

