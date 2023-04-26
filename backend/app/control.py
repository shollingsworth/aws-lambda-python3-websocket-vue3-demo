#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Websocket controller."""
import decimal
import json
import time

import boto3
from botocore.client import logger
from botocore.exceptions import ClientError

from app.config import Config

config = Config()


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        if isinstance(o, set):  # <---resolving sets as lists
            return list(o)
        return super(DecimalEncoder, self).default(o)


class Control:
    def __init__(self, connectionId: str) -> None:
        """Initialize the control class."""
        self.connectionId = connectionId
        self.stage = ""
        self.domain = ""
        self.user = ""
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(config.table)
        print(self.table)
        self.action_map = {
            "hello": self.action_hello,
            "ping": self.action_ping,
            "save_alert_box": self.action_save_alert_box,
            "send_alert_boxes": self.action_send_alert_boxes,
        }

    def parse_message(self, message: dict) -> None:
        """Parse the message and call the appropriate action."""
        self._set_by_connection_id()
        action = message.get("action")
        if action in self.action_map:
            res = self.action_map[action](message)
            self.send_message(res)
        else:
            self.send_message(self._status_err(f"Unknown action {action}"))

    def action_hello(self, _: dict):
        return {"action": "info", "message": "Hello World!"}

    def action_ping(self, _: dict):
        return {"action": "info", "message": "pong!"}

    def action_send_alert_boxes(self, _: dict):
        """Send the alert boxes to the user."""
        boxes = self._get_alert_boxes()
        return {
            "action": "alert_boxes",
            "message": self.to_dict(boxes),
        }

    def action_save_alert_box(self, data: dict):
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

    def _get_alert_boxes(self):
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

    def send_message(self, data):
        if not self.domain:
            self._set_by_connection_id()
        if config.is_offline:
            gwapi = boto3.client(
                "apigatewaymanagementapi",
                endpoint_url="http://localhost:3001",
            )
        else:
            gwapi = boto3.client(
                "apigatewaymanagementapi",
                endpoint_url=f"https://{self.domain}/{self.stage}",
            )
        return gwapi.post_to_connection(
            ConnectionId=self.connectionId, Data=json.dumps(data).encode("utf-8")
        )


if __name__ == "__main__":
    control = Control("test")
    # control.save_connection("test", "test", "test")
    control._set_by_connection_id()
    control.action_save_alert_box(
        {
            "action": "save_alert_box",
            "x1": 1,
            "y1": 2,
            "x2": 3,
            "y2": 4,
        }
    )
    boxes = control._get_alert_boxes()
    print(control.dump_json(boxes))
