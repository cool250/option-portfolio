# Options Portfolio

Python Flask Web Framework to integrate with Broker. Currently supports TD Broker.
Run app.py to start Flask server.  The OAuth token is retrieved from Redis but can be changed to pick up from any persistent store including File.

## Features

1) Search for option income - Covered Calls and Secured Puts
2) Retrieves all your transaction based on Filter criteria - Date, Trade Type, Ticker, etc.
3) Shows the price for a ticker and other charting capabilities

<img width="1419" alt="Screen Shot 2021-03-21 at 11 36 38 AM" src="https://user-images.githubusercontent.com/5234229/111916848-29dcbb00-8a3a-11eb-80b2-281ad1377e29.png">

<img width="1390" alt="Screen Shot 2021-03-21 at 11 36 53 AM" src="https://user-images.githubusercontent.com/5234229/111916974-c30bd180-8a3a-11eb-9c8b-970823811d87.png">

<img width="1405" alt="Screen Shot 2021-03-21 at 11 37 31 AM" src="https://user-images.githubusercontent.com/5234229/111917001-e8004480-8a3a-11eb-806e-a983af1d9cfc.png">

<img width="1378" alt="Screen Shot 2021-03-21 at 11 38 22 AM" src="https://user-images.githubusercontent.com/5234229/111917008-f0f11600-8a3a-11eb-8a6c-7dda447270da.png">

## Local env setup

```shell
% brew install pyenv

% pyenv install 3.9.5

% pyenv local 3.9.5
```

Install latest poetry
```shell
% brew install poetry
```

Install just using brew
```shell
% brew install just
```

```shell
% just show-my-environment
which python
/Users/nishant/.pyenv/shims/python
python --version
Python 3.9.5
which poetry
/opt/homebrew/bin/poetry
poetry --version
Poetry (version 1.6.1)
poetry env info

Virtualenv
Python:         3.9.5
Implementation: CPython
Path:           /Users/nishant/code/2/option-portfolio/.venv
Executable:     /Users/nishant/code/2/option-portfolio/.venv/bin/python
Valid:          True

System
Platform:   darwin
OS:         posix
Python:     3.9.5
Path:       /Users/nishant/.pyenv/versions/3.9.5
Executable: /Users/nishant/.pyenv/versions/3.9.5/bin/python3.9
poetry run python --version
Python 3.9.5
poetry version --short
2023.10.1
```
