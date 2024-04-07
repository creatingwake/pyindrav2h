import logging
from getpass import getpass
import argparse
import configparser
import asyncio
import os
from .connection import Connection
from .v2hclient import v2hClient
from . import V2H_MODES

logging.basicConfig()
logging.root.setLevel(logging.WARNING)

_LOGGER = logging.getLogger(__name__)

async def main(args):
    userEmail = args.email or input("Please enter your Indra login email: ")
    userPass = args.password or getpass(prompt="Indra password: ")

    if args.debug:
        logging.root.setLevel(logging.DEBUG)

    _LOGGER.debug(f"using {userEmail}, {userPass}")

    # create connection
    conn = Connection(userEmail, userPass)
    await conn.checkAPICreds()

    client = v2hClient(conn)

    # refresh device/stats data
    await client.refresh()

    if args.command == "schedule":
        args.command = "clear" # translate displayed mode commmand to endpoint command
    if (args.command == "device"):
        print(client.device.showDevice())
    elif (args.command == "statistics"):
        print(client.device.showStats())
    elif (args.command == "all"):
        print(client.device.showAll())
    elif (args.command in list(V2H_MODES.values())):
        for mode, command in V2H_MODES.items():
            if command == args.command:
                print(await client.device.select_charger_mode(mode))

def cli():
    config = configparser.ConfigParser()
    config["indra-account"] = {"email": "", "password": ""}
    config.read([".indra.cfg", os.path.expanduser("~/.indra.cfg")])
    parser = argparse.ArgumentParser(prog="indracli", description="Indra V2H CLI")
    parser.add_argument(
        "-u",
        "--email",
        dest="email",
        default=config.get("indra-account", "email"),
    )
    parser.add_argument(
        "-p",
        "--password",
        dest="password",
        default=config.get("indra-account", "password")
    )
    parser.add_argument("-d", "--debug", dest="debug", action="store_true")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("statistics", help="show device statistics")
    subparsers.add_parser("device", help="show device info")
    subparsers.add_parser("all", help="show all info")
    subparsers.add_parser("loadmatch", help="set mode to load matching")
    subparsers.add_parser("idle", help="set mode to IDLE")
    subparsers.add_parser("exportmatch", help="set mode to export matching")
    subparsers.add_parser("charge", help="set mode to CHARGE")
    subparsers.add_parser("discharge", help="set mode to discharge")
    subparsers.add_parser("schedule", help="return to scheuduled mode")

    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))