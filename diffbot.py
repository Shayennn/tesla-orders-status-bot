import json
import logging
import os
from datetime import datetime

from dictdiffer import diff
from dotenv import load_dotenv
from logger import setup_logger

from utils import get_new_token, get_order_status, notify

logger = setup_logger(__name__, logging.DEBUG)

load_dotenv()

line_token = os.getenv("LINE_TOKEN")
tesla_token = os.getenv("TESLA_TOKEN")
tesla_refresh_token = os.getenv("TESLA_REFRESH_TOKEN")


# test get_new_token

try:
    new_token = get_new_token(tesla_token, tesla_refresh_token)
except Exception as e:
    notify(f"Error in get_new_token \n\n{e}", line_token)
    logger.error(e)
    raise e

if new_token["access_token"] != tesla_token:
    logger.debug("New token is generated")

    # save new token to .env
    with open(".env", "w") as f:
        f.writelines(
            [
                "# Refresh on " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n",
                f"LINE_TOKEN={line_token}\n",
                "TESLA_TOKEN=" + new_token["access_token"] + "\n",
                "TESLA_REFRESH_TOKEN=" + new_token["refresh_token"] + "\n",
            ]
        )

    tesla_token = new_token["access_token"]

# get order status


# load old status from data/status.json if exists
old_status = {}
if os.path.exists("data/status.json"):
    with open("data/status.json", "r") as f:
        old_status = json.load(f)

new_status = get_order_status(tesla_token)

# get diffwith dictdiffer

diffs = list(diff(old_status, new_status))

# Notify if there is any change

if diffs:
    logger.debug(diffs)

    change_msg = []
    for change in diffs:
        msg = ""
        change_pos = change[1]
        if not isinstance(change_pos, str):
            change_pos = ".".join([str(i) for i in change_pos])
        if change_pos == "":
            change_pos = "root"

        if change[0] == "add":
            msg += f"New Value At: {change_pos}\n"
            msg += f"Value: {change[2]}\n"
        elif change[0] == "change":
            msg += f"Change At: {change_pos}\n"
            msg += f"Old value: {change[2][0]}\n"
            msg += f"New value: {change[2][1]}\n"
        elif change[0] == "remove":
            msg += f"Remove: {change_pos}\n"
        change_msg += [msg]

    out_msg = "There is a change in order status\n\n"
    out_msg += f'\n{"*"*10}\n\n'.join(change_msg)
    logger.info(out_msg)
    notify(out_msg, line_token)
else:
    logger.info("No change")

# save new status to data/status.json
with open("data/status.json", "w") as f:
    json.dump(new_status, f, indent=2)
