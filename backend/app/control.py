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
from botocore.exceptions import ClientError, EndpointConnectionError

from app.config import Config

logger = logging.getLogger("handler_logger")
logger.setLevel(logging.DEBUG)

config = Config()

ROUTE_SEND_MESSAGE = "send_message"
ROUTE_CELL_NOTIFY = "cell_notify"


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        if isinstance(o, set):  # <---resolving sets as lists
            return list(o)
        return super(DecimalEncoder, self).default(o)


class Lock:
    KEY = "lock"

    def __init__(self, name: str) -> None:
        """Initialize the Lock class."""
        self.dynamodb = boto3.resource("dynamodb", region_name=config.region)
        self.table = self.dynamodb.Table(config.table)
        self.name = name

    @property
    def current_lock(self):
        """Get the current lock."""
        response = self.table.get_item(
            Key={
                "key": self.KEY,
                "type": self.name,
            }
        )
        return int(response.get("Item", {}).get("ttl", -1))

    def lock(self):
        """Acquire the lock."""
        if self.current_lock != -1:
            diff = self.current_lock - int(time.time())
            if diff < 0:
                logger.info("Breaking lock!!!!, diff: %s", diff)
                self.unlock()
            else:
                logger.info("Lock is still valid")
                return False
        try:
            self.table.put_item(
                Item={
                    "key": self.KEY,
                    "type": self.name,
                    "value": "locked",
                    "ttl": int(time.time()) + 60,
                },
                ConditionExpression="attribute_not_exists(#key)",
                ExpressionAttributeNames={
                    "#key": "key",
                },
            )
            logger.info("Lock acquired %s", self.name)
            return True
        except ClientError as e:
            if (
                str(e.response.get("Error", {}).get("Code", ""))
                != "ConditionalCheckFailedException"
            ):
                raise
            return False

    def unlock(self):
        """Release the lock."""
        self.table.delete_item(
            Key={
                "key": self.KEY,
                "type": self.name,
            },
        )
        logger.info("Lock released %s", self.name)


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

    def clear_active(self) -> None:
        """Clear all the active cells."""
        self.table.update_item(
            Key={
                "key": self.KEY,
                "type": self.TYPE,
            },
            UpdateExpression="set active_cells = :i",
            ExpressionAttributeValues={
                ":i": [],
            },
            ReturnValues="UPDATED_NEW",
        )

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
            return {}

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
            "x": int(cell.split(",")[0]),
            "y": int(cell.split(",")[1]),
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
        self.bcast = Broadcast()
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
            "clear_alert_boxes": self.action_clear_alert_boxes,
            "clear_backend_state": self.action_clear_backend_state,
        }

    def parse_message(self, message: Dict) -> None:
        """Parse the message and call the appropriate action."""
        self._set_by_connection_id()
        action = message.get("action")
        if action in self.action_map:
            res = self.action_map[action](message)
            if res:
                self.send_message(res)
        else:
            self.send_message(self._status_err(f"Unknown action {action}"))

    def action_hello(self, _: Dict):
        return {"action": "info", "message": "Hello World!"}

    def action_ping(self, _: Dict):
        return {"action": "info", "message": "pong!"}

    def action_clear_backend_state(self, _: Dict):
        """Clear the backend state."""
        self.state.clear_active()
        pl = self.action_send_all_active_cells(_)
        self.bcast.send_message(pl)

    def action_clear_alert_boxes(self, _: Dict):
        """Clear all the alert boxes."""
        self.table.update_item(
            Key={
                "key": "alert_box",
                "type": self.user,
            },
            UpdateExpression="set alert_boxes = :i",
            ExpressionAttributeValues={
                ":i": [],
            },
            ReturnValues="UPDATED_NEW",
        )
        return {"action": "alert_boxes", "message": []}

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
        except EndpointConnectionError:
            logger.info(f"Force removing connection id '{self.connectionId}'")
            self.delete_connection()


class Broadcast:
    def __init__(self) -> None:
        """Initialize the broadcast class."""
        self.dynamodb = boto3.resource("dynamodb", region_name=config.region)
        self.table = self.dynamodb.Table(config.table)
        self.router = SnsRouter()

    def iterate_connection_ids(self):
        """Iterate over all connections."""
        response = self.table.scan()
        for item in response.get("Items", []):
            if item.get("key") == "websocket":
                dom = item.get("domain")
                if not dom == "localhost":
                    yield str(item.get("type"))

    def cell_notify(self, cell: Dict[str, int]):
        """Check if the cell is in an alert box."""
        for connection_id in self.iterate_connection_ids():
            pl = {
                "connection_id": connection_id,
                "data": {
                    "cell": cell,
                },
            }
            self.router.publish(ROUTE_CELL_NOTIFY, pl)

    def send_message(self, data):
        """Send a message to all connections."""
        for connection_id in self.iterate_connection_ids():
            pl = {
                "connection_id": connection_id,
                "data": data,
            }
            self.router.publish(ROUTE_SEND_MESSAGE, pl)

class SnsRouter:
    """Sns Router Handler for longer jobs."""

    def __init__(self):
        """Initialize the SnsRouter."""
        self.sns = boto3.client("sns", region_name=config.region)
        logger.info("Topic ARN: %s", config.sns_topic)

    def publish(self, action: str, message: Dict):
        """Send a message to the Sns topic."""
        self.sns.publish(
            Subject=action,
            TopicArn=config.sns_topic,
            Message=json.dumps(message),
        )


class SnsRecordHandler:
    """Sns Record Handler for longer jobs."""

    def __init__(self, record):
        """Initialize the SnsRecord."""
        self.record = record
        self.action = record["Sns"]["Subject"]
        self.message = json.loads(record["Sns"]["Message"])
        self.connection_id = self.message.get("connection_id")
        self.data = self.message.get("data", {})
        self.dynamodb = boto3.resource("dynamodb", region_name=config.region)
        self.table = self.dynamodb.Table(config.table)
        self.func_map = {
            ROUTE_SEND_MESSAGE: self.action_send_message,
            ROUTE_CELL_NOTIFY: self.action_cell_notify,
        }

    def action_cell_notify(self):
        if not all([self._check_valid_connection_id(), self._check_valid_data()]):
            return
        cell = self.data.get("cell")
        control = Control(self.connection_id)
        control._set_by_connection_id()
        if control.domain == "localhost":
            logger.info(f"Skipping localhost connection {self.connection_id}")
            return
        is_alert = control.is_alert(cell)
        if not is_alert:
            logger.info(f"Skipping non-alert connection {self.connection_id} / {cell}")
            return
        logger.info(f"Sending alert to {self.connection_id} / {cell}")
        message = {
            "action": "alert",
            "message": f"Cell {cell['x']},{cell['y']} is in an alert box",
        }
        control.send_message(message)

    def action_send_message(self):
        """Send a message to the websocket."""
        control = Control(self.message["connection_id"])
        if not all([self._check_valid_connection_id(), self._check_valid_data()]):
            return
        control.send_message(self.data)

    def handle_message(self):
        """Handle the message."""
        if self.action not in self.func_map:
            logger.error(f"Unknown action: {self.action}")
            return
        self.func_map[self.action]()

    def _check_valid_connection_id(self):
        """Check if the connection_id is valid."""
        if not self.connection_id:
            logger.error("No connection_id provided")
            return False
        return True

    def _check_valid_data(self):
        """Check if the data is valid."""
        if not self.data:
            logger.error("No data provided")
            return False
        return True


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
    )
    broadcast.cell_notify(
        {
            "x": 1,
            "y": 1,
        },
    )


if __name__ == "__main__":
    test_broadcast_cell_alert()
    # test_broadcast()
    # test_send_message()
    # test_random_active()
