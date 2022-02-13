import logging
import random
import socket
import time
import typing

import requests
import telebot
from config import Config
from errors import FetchedError
from pyfiglet import Figlet

# URL for fetching relays
onion_url = (
    "https://onionoo.torproject.org/details?type=relay"
    "&running=true&fields=fingerprint,or_addresses"
)
# Custom user agent
user_agent = (
    "Mozilla/5.0 (Linux; Android 10; Android SDK built for x86) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36 "
)


# Checking a port for bad ports described below
def check_port(addr) -> bool:
    bad_ports = [
        1,
        7,
        9,
        11,
        13,
        15,
        17,
        19,
        20,
        21,
        22,
        23,
        25,
        37,
        42,
        43,
        53,
        69,
        77,
        79,
        87,
        95,
        101,
        102,
        103,
        104,
        109,
        110,
        111,
        113,
        115,
        117,
        119,
        123,
        135,
        137,
        139,
        143,
        161,
        179,
        389,
        427,
        465,
        512,
        513,
        514,
        515,
        526,
        530,
        531,
        532,
        540,
        548,
        554,
        556,
        563,
        587,
        601,
        636,
        989,
        990,
        993,
        995,
        1719,
        1720,
        1723,
        2049,
        3659,
        4045,
        5060,
        5061,
        6000,
        6566,
        6665,
        6666,
        6667,
        6668,
        6669,
        6697,
        10080,
    ]

    return int(addr.split(":")[1]) not in bad_ports


# Check remote port opened/closed(filtered)
def is_socket_open(addr: str = None) -> bool:
    if addr is None:
        return False

    addrs = addr.split(":")
    if len(addrs) < 2:
        return False

    try:
        # Trying open remote socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(2.0)
        result = sock.connect_ex((addrs[0], int(addrs[1])))
        sock.close()

        return result == 0
    except Exception as ex:
        logging.error(f"Unhandled is_socket_open {ex}")

    return False


# Fetching list of relays from tor website
def fetch_relays(
    relays_number: typing.Optional[int] = 30, timeout: typing.Optional[int] = 5
) -> str:
    random.seed(time.time(), 2)

    try:
        resp = requests.get(
            onion_url, timeout=timeout, headers={"User-Agent": user_agent}
        )
        if resp.status_code != 200:
            raise FetchedError(
                f"Fetching error, server response code is {resp.status_code}"
            )

        return parse_relays(resp.json(), relays_number)
    except requests.ConnectionError:
        raise FetchedError("Fetching error, server connection error")
    except Exception as e:
        raise FetchedError(e)


# Parse JSON list of relays
def parse_relays(json: dict, relays_number: typing.Optional[int] = 30) -> str:
    fetched_relays = json

    if "relays" not in fetched_relays:
        raise FetchedError("Fetching error, relays not found")

    filtered_relays = []

    # max relays number
    counter = len(fetched_relays["relays"])

    # Loop for filling validated relays list
    while counter > 0 and len(filtered_relays) < relays_number:
        rnd = random.randint(0, len(fetched_relays["relays"]) - 1)
        relay = fetched_relays["relays"][rnd]
        for addr in relay["or_addresses"]:
            if addr.find("[") == -1 and check_port(addr) and is_socket_open(addr):
                filtered_relays.append(addr + " " + relay["fingerprint"])
        counter -= 1

    return "\n".join(filtered_relays)


custom_fig = Figlet(font="graffiti")
print(custom_fig.renderText("tor2relays"))
print("t2r bot started")

config = Config()
config.init_env()

bot = telebot.TeleBot(config.telegram_token)

# Set logging level
if config.debug:
    logging.basicConfig(encoding="utf-8", level=logging.DEBUG)
    level = logging.DEBUG
else:
    logging.basicConfig(encoding="utf-8", level=logging.ERROR)
    level = logging.ERROR

print(f"logging level is {logging.getLevelName(level)}")


# Command /start /help for more information about bot
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(
        message,
        """
Hi, this is a bot giving a list of relays for tor. Below is a list of available commands.\n
/start - greeting, help on bot commands\n/help - alias for /start\n/relays - to get a text document with tor relays\n
        """,
    )


# Command /relays for fetching tor relays list
@bot.message_handler(commands=["relays"])
def relays(message):
    try:
        bot.send_message(chat_id=message.chat.id, text="Trying to get a list of relays")
    except Exception as send_message_error:
        logging.error("get relays send reply to user", exc_info=send_message_error)

    try:
        # Fetching relays
        output = fetch_relays(
            timeout=config.timeout, relays_number=config.relays_number
        )
        logging.debug("load relays successful")
    except FetchedError as fetched_error:
        logging.error("get relays fetched error", exc_info=fetched_error)
        bot.reply_to(message, """The list of relays is not available. Try later""")
        return
    except Exception as common_error:
        logging.error("get relays fetch relays:", exc_info=common_error)
        bot.reply_to(message, """The list of relays is not available. Try later""")
        return

    try:
        # Send text document with list of tor relays
        bot.send_document(
            caption=f"List of {config.relays_number} tor relays",
            chat_id=message.chat.id,
            document=output.encode("utf-8"),
        )
    except Exception as send_document_error:
        logging.error("get relays send reply to user", exc_info=send_document_error)


print("Listen telegram connections")
# Telegram infinity loop for fetching updates
bot.infinity_polling()
