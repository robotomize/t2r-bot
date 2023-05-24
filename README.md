# t2r-bot
Telegram bot for receiving a list of relays for use in the tor browser

## Usage

### Sh

```shell
python3 -m venv env
pip3 install poetry
poetry install --no-dev
export TOKEN=<YOUR TELEGRAM TOKEN>
python3 app/main.py
```

### Docker compose
```shell
sudo docker-compose up
```

