import logging
from getpass import getpass
import argparse
import configparser
import asyncio
import os
from pyindrav2h.connection import Connection
from pyindrav2h.v2hclient import v2hClient

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
    
    if (args.command == "device"):
        print(client.device.showDevice())
    elif (args.command == "statistics"):
        print(client.device.showStats())
    elif (args.command == "all"):
        print(client.device.showAll())
    elif (args.command == "loadmatch"):
        print(await client.device.load_match())
    elif (args.command == "idle"):
        print(await client.device.idle())
    elif (args.command == "schedule"):
        print(await client.device.schedule())

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
    subparsers.add_parser("schedule", help="return to scheuduled mode")

    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))