# t2r-bot
Telegram bot for fetching tor relays

## Usage

Docker

```shell
sudo docker-compose up
```

Python3.9

```shell
python3 -m venv env
pip3 install poetry
poetry install --no-dev
export TOKEN=<YOUR TELEGRAM TOKEN>
python3 app/main.py
```