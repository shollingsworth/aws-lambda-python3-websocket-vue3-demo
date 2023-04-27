#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Websocket controller."""
import decimal
import json
import logging
import random
import time
from typing import Dict, List

import boto3
from botocore.client import logger
from botocore.exceptions import ClientError

from app.config import Config

logger = logging.getLogger("handler_logger")
logger.setLevel(logging.DEBUG)

config = Config()


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        if isinstance(o, set):  # <---resolving sets as lists
            return list(o)
        return super(DecimalEncoder, self).default(o)


class CellState:
    KEY = "state"
    TYPE = "active_cells"

    def __init__(self) -> None:
        """Initialize the ActiveCell class."""
        self.dynamodb = boto3.resource("dynamodb", region_name=config.region)
        self.table = self.dynamodb.Table(config.table)

    def _get_active(self) -> List[str]:
        """Get all the active cells."""
        response = self.table.get_item(
            Key={
                "key": self.KEY,
                "type": self.TYPE,
            }
        )
        res = response.get("Item", {}).get(self.TYPE, None)
        if res is None:
            self.table.put_item(
                Item={
                    "key": self.KEY,
                    "type": self.TYPE,
                    self.TYPE: [],
                }
            )
            return []
        return res

    def _get_random_cell(self):
        """Get a random cell."""
        # 50 x 50 grid
        active = self._get_active()
        cell = None
        while True:
            if len(active) == 2500:
                logger.info("All cells are active")
                break
            x = random.randint(0, 49)
            y = random.randint(0, 49)
            cell = f"{x},{y}"
            if cell not in active:
                break
        return cell

    def add_random_active(self):
        """Add an active cell."""
        cell = self._get_random_cell()
        if not cell:
            return {
                "action": "info",
                "message": "All cells are active",
            }

        self.table.update_item(
            Key={
                "key": self.KEY,
                "type": self.TYPE,
            },
            UpdateExpression="set active_cells = list_append(active_cells, :i)",
            ExpressionAttributeValues={
                ":i": [cell],
            },
            ReturnValues="UPDATED_NEW",
        )
        return {
            "action": "add_active_cell",
            "message": {
                "x": int(cell.split(",")[0]),
                "y": int(cell.split(",")[1]),
            },
        }

    def get_active_list(self):
        """Get the active cells as a dict."""
        active = self._get_active()
        payload = [
            {
                "x": int(cell.split(",")[0]),
                "y": int(cell.split(",")[1]),
            }
            for cell in active
        ]
        return payload


class Control:
    def __init__(self, connectionId: str) -> None:
        """Initialize the control class."""
        self.state = CellState()
        self.connectionId = connectionId
        self.stage = ""
        self.domain = ""
        self.user = ""
        self.dynamodb = boto3.resource("dynamodb", region_name=config.region)
        self.table = self.dynamodb.Table(config.table)
        self.action_map = {
            "hello": self.action_hello,
            "ping": self.action_ping,
            "save_alert_box": self.action_save_alert_box,
            "send_alert_boxes": self.action_send_alert_boxes,
            "send_all_active_cells": self.action_send_all_active_cells,
            "send_connection_id": self.action_send_connection_id,
        }

    def parse_message(self, message: Dict) -> None:
        """Parse the message and call the appropriate action."""
        self._set_by_connection_id()
        action = message.get("action")
        if action in self.action_map:
            res = self.action_map[action](message)
            self.send_message(res)
        else:
            self.send_message(self._status_err(f"Unknown action {action}"))

    def action_hello(self, _: Dict):
        return {"action": "info", "message": "Hello World!"}

    def action_ping(self, _: Dict):
        return {"action": "info", "message": "pong!"}

    def action_send_connection_id(self, _: Dict):
        return {"action": "connection_id", "message": self.connectionId}

    def action_send_all_active_cells(self, _: Dict):
        """Send the active cells to the user."""
        return {
            "action": "all_active_cells",
            "message": self.state.get_active_list(),
        }

    def action_send_alert_boxes(self, _: Dict):
        """Send the alert boxes to the user."""
        boxes = self._get_alert_boxes()
        return {
            "action": "alert_boxes",
            "message": self.to_dict(boxes),
        }

    def action_save_alert_box(self, data: Dict):
        """Save the alert box to the database."""
        print("action_save_alert_box", data)
        message = data.get("message", {})
        try:
            self.table.update_item(
                Key={
                    "key": "alert_box",
                    "type": self.user,
                },
                UpdateExpression="set alert_boxes = list_append(alert_boxes, :i)",
                ExpressionAttributeValues={
                    ":i": [
                        {
                            "x1": message.get("x1"),
                            "y1": message.get("y1"),
                            "x2": message.get("x2"),
                            "y2": message.get("y2"),
                        }
                    ]
                },
                ReturnValues="UPDATED_NEW",
            )
            return self.action_send_alert_boxes({})
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "ValidationException":
                self.table.put_item(
                    Item={
                        "key": "alert_box",
                        "type": self.user,
                        "alert_boxes": [
                            {
                                "x1": message.get("x1"),
                                "y1": message.get("y1"),
                                "x2": message.get("x2"),
                                "y2": message.get("y2"),
                            }
                        ],
                    }
                )
            return self.action_send_alert_boxes({})
        except Exception as e:
            logger.error(e)
            return self._status_err(str(e))

    def _status_ok(self, msg: str):
        """Send an OK message."""
        return {
            "action": "info",
            "message": msg,
        }

    def _status_err(self, msg: str):
        """Send an error message."""
        return {
            "action": "error",
            "message": msg,
        }

    def _status_alert(self, msg: str):
        """Send an alert message."""
        return {
            "action": "alert",
            "message": msg,
        }

    def _get_alert_boxes(self) -> List[Dict[str, int]]:
        """Get the alert boxes for the user."""
        item = self.table.get_item(
            Key={
                "key": "alert_box",
                "type": self.user,
            }
        )
        boxes = item.get("Item", {}).get("alert_boxes", [])
        return boxes
        # try:
        #  except ClientError as e:
        #      if e.response.get("Error", {}).get("Code") == "ResourceNotFoundException":
        #          return []
        #      raise e

    def _set_by_connection_id(self):
        response = self.table.get_item(
            Key={
                "key": "websocket",
                "type": self.connectionId,
            }
        )
        if "Item" in response:
            self.domain = response["Item"].get("domain")
            self.stage = response["Item"].get("stage")
            self.user = response["Item"].get("user")
            return True
        return False

    def delete_connection(self):
        self.table.delete_item(
            Key={
                "key": "websocket",
                "type": self.connectionId,
            }
        )

    def save_connection(
        self,
        domain: str,
        stage: str,
        user: str,
    ) -> None:
        """Save the connection to the database."""
        self.domain = domain
        self.stage = stage
        self.user = user
        self.table.put_item(
            Item={
                "key": "websocket",
                "type": self.connectionId,
                "domain": domain,
                "stage": stage,
                "user": user,
                "created": int(time.time()),
            }
        )

    def dump_json(self, data):
        return json.dumps(data, indent=4, cls=DecimalEncoder)

    def to_dict(self, data):
        return json.loads(json.dumps(data, cls=DecimalEncoder))

    def is_alert(self, cell: Dict[str, int]):
        """Check if the cell is in an alert box."""
        boxes = self._get_alert_boxes()
        for box in boxes:
            if (
                cell["x"] >= box["x1"]
                and cell["x"] < box["x2"]
                and cell["y"] >= box["y1"]
                and cell["y"] < box["y2"]
            ):
                return True
        return False

    def send_message(self, data):
        self._set_by_connection_id()
        if not self.domain:
            raise Exception(f"No domain set for connection '{self.connectionId}'")
        if config.is_offline or self.domain == "localhost":
            gwapi = boto3.client(
                "apigatewaymanagementapi",
                endpoint_url="http://localhost:3001",
            )
        else:
            gwapi = boto3.client(
                "apigatewaymanagementapi",
                endpoint_url=f"https://{self.domain}/{self.stage}",
            )
        try:
            return gwapi.post_to_connection(
                ConnectionId=self.connectionId, Data=json.dumps(data).encode("utf-8")
            )
        except ClientError as e:
            if "An error occurred (410)" in str(e):
                logger.info(f"Force removing connection id '{self.connectionId}'")
                self.delete_connection()


class Broadcast:
    def __init__(self) -> None:
        """Initialize the broadcast class."""
        self.dynamodb = boto3.resource("dynamodb", region_name=config.region)
        self.table = self.dynamodb.Table(config.table)

    def iterate_connection_ids(self):
        """Iterate over all connections."""
        response = self.table.scan()
        for item in response.get("Items", []):
            if item.get("key") == "websocket":
                yield item.get("type")

    def cell_notify(self, cell: Dict[str, int], is_new: bool, skip_local: bool = True):
        """Check if the cell is in an alert box."""
        for connection_id in self.iterate_connection_ids():
            control = Control(str(connection_id))
            control._set_by_connection_id()
            if skip_local and control.domain == "localhost":
                continue
            if not control.is_alert(cell):
                continue

            if control.is_alert(cell):
                if is_new:
                    self.send_message(
                        {
                            "action": "alert",
                            "message": f"Cell {cell['x']},{cell['y']} is in an alert box",
                        }
                    )
                else:
                    self.send_message(
                        {
                            "action": "alert_ok",
                            "message": f"Cell {cell['x']},{cell['y']} is clear",
                        }
                    )

    def send_message(self, data):
        """Send a message to all connections."""
        for connection_id in self.iterate_connection_ids():
            control = Control(str(connection_id))
            control.send_message(data)


def test_send_message():
    _id = """
0723d0d5-6407-4b63-94b8-7b9111117e90
    """.strip()

    control = Control(_id)
    control._set_by_connection_id()
    control.send_message(
        {
            "action": "info",
            "message": "test",
        }
    )


def test_random_active():
    cs = CellState()
    cs.add_random_active()


def test_broadcast():
    broadcast = Broadcast()
    broadcast.send_message(
        {
            "action": "info",
            "message": "broadcast test",
        }
    )


def test_broadcast_cell_alert():
    broadcast = Broadcast()
    broadcast.cell_notify(
        {
            "x": 1,
            "y": 1,
        },
        is_new=True,
        skip_local=False,
    )
    broadcast.cell_notify(
        {
            "x": 1,
            "y": 1,
        },
        is_new=False,
        skip_local=False,
    )


if __name__ == "__main__":
    test_broadcast_cell_alert()
    # test_broadcast()
    # test_send_message()
    # test_random_active()
