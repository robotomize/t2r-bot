import os


# Env configuration loader
class Config:
    def __init__(self):
        self.timeout = 5
        self.relays_number = 30
        self.telegram_token = ""
        self.debug = True

    def init_env(self):
        self.telegram_token = os.getenv("TOKEN")

        if os.getenv("DEBUG") is not None:
            if os.environ["DEBUG"] == "1" or os.environ["DEBUG"] == "true":
                self.debug = True
            else:
                self.debug = False

        if os.getenv("REQUEST_TIMEOUT") is not None:
            self.timeout = int(os.environ["REQUEST_TIMEOUT"])

        if os.getenv("RELAYS_NUMBER") is not None:
            self.relays_number = int(os.environ["RELAYS_NUMBER"])
