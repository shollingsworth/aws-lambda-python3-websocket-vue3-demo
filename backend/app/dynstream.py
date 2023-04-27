#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DynamoDB Stream Handler."""
import boto3

import logging
from app.config import Config
from app.control import Broadcast

config = Config()

logger = logging.getLogger("handler_logger")
logger.setLevel(logging.DEBUG)


class Record:
    """DynamoDB Stream Record."""

    def __init__(self, record):
        """Initialize Record."""
        self.record = record
        db = boto3.resource("dynamodb", region_name=config.region)
        self.table = db.Table(config.table)

    def __str__(self):
        """Return string representation."""
        return str(self.record)

    @property
    def event_name(self):
        """Return event name."""
        return self.record["eventName"]

    @property
    def dynamodb(self):
        """Return dynamodb."""
        return self.record["dynamodb"]

    @property
    def keys(self):
        """Return keys."""
        keys = self.dynamodb["Keys"]
        _type = keys.get("type", None)
        _key = keys.get("key", None)
        return (_type["S"], _key["S"])


class ActiveCells(Record):
    """DynamoDB Stream State Record."""

    def __init__(self, record):
        """Initialize StateRecord."""
        super().__init__(record)

    @property
    def is_state_record(self):
        """Return True if state record."""
        return self.keys == ("active_cells", "state")

    @property
    def new_image(self):
        """Return new image."""
        return self.dynamodb.get("NewImage", {})

    @property
    def old_image(self):
        """Return old image."""
        return self.dynamodb.get("OldImage", {})

    def _image_to_set(self, image):
        """Return image as dict."""
        return set([item["S"] for item in image.get("L", [])])

    @property
    def new_active_cells(self):
        old = self._image_to_set(self.old_image.get("active_cells", {}))
        new = self._image_to_set(self.new_image.get("active_cells", {}))
        return new - old

    #  @property
    #  def removed_active_cells(self):
    #      old = self._image_to_set(self.old_image.get("active_cells", {}))
    #      new = self._image_to_set(self.new_image.get("active_cells", {}))
    #      return old - new

    def send_alerts(self) -> None:
        """Return dict representation."""
        bcast = Broadcast()
        if not self.is_state_record:
            logger.info("Not a state record, exiting: %s", self.keys)
            return

        logger.info("New active cells: %s, sending broadcast", self.new_active_cells)
        for txt in self.new_active_cells:
            x, y = txt.split(",")
            bcast.cell_notify({"x": int(x), "y": int(y)})


def main():
    """Run main function."""
    demo = {
        "Records": [
            {
                "eventID": "ddc75468cbabe63148beb055aa33f112",
                "eventName": "REMOVE",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "us-east-2",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1682550222.0,
                    "Keys": {
                        "type": {"S": "04363e9b-cedc-4fb4-a07e-88f2ee38408b"},
                        "key": {"S": "websocket"},
                    },
                    "OldImage": {
                        "stage": {"S": "local"},
                        "created": {"N": "1682549398"},
                        "domain": {"S": "localhost"},
                        "type": {"S": "04363e9b-cedc-4fb4-a07e-88f2ee38408b"},
                        "user": {"S": "Google_117789969009555435433"},
                        "key": {"S": "websocket"},
                    },
                    "SequenceNumber": "7581700000000020340208852",
                    "SizeBytes": 174,
                    "StreamViewType": "NEW_AND_OLD_IMAGES",
                },
                "eventSourceARN": "arn:aws:dynamodb:us-east-2:668805947503:table/sh-ws-demo-dev/stream/2023-04-26T22:19:16.291",
            },
            {
                "eventID": "65c5b0efae5bec2836a6c1f0fde28539",
                "eventName": "INSERT",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "us-east-2",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1682550925.0,
                    "Keys": {"type": {"S": "active_cells"}, "key": {"S": "state"}},
                    "NewImage": {
                        "active_cells": {"L": []},
                        "type": {"S": "active_cells"},
                        "key": {"S": "state"},
                    },
                    "SequenceNumber": "7585600000000023689773852",
                    "SizeBytes": 63,
                    "StreamViewType": "NEW_AND_OLD_IMAGES",
                },
                "eventSourceARN": "arn:aws:dynamodb:us-east-2:668805947503:table/sh-ws-demo-dev/stream/2023-04-26T22:19:16.291",
            },
            {
                "eventID": "2c956070da78174bede841034c5a3182",
                "eventName": "MODIFY",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "us-east-2",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1682550925.0,
                    "Keys": {"type": {"S": "active_cells"}, "key": {"S": "state"}},
                    "NewImage": {
                        "active_cells": {"L": [{"S": "32,44"}]},
                        "type": {"S": "active_cells"},
                        "key": {"S": "state"},
                    },
                    "OldImage": {
                        "active_cells": {"L": []},
                        "type": {"S": "active_cells"},
                        "key": {"S": "state"},
                    },
                    "SequenceNumber": "7585700000000023689773945",
                    "SizeBytes": 108,
                    "StreamViewType": "NEW_AND_OLD_IMAGES",
                },
                "eventSourceARN": "arn:aws:dynamodb:us-east-2:668805947503:table/sh-ws-demo-dev/stream/2023-04-26T22:19:16.291",
            },
            {
                "eventID": "4f34b8aafb19364cd1cee267d72eddce",
                "eventName": "MODIFY",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "us-east-2",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1682554193.0,
                    "Keys": {"type": {"S": "active_cells"}, "key": {"S": "state"}},
                    "NewImage": {
                        "active_cells": {"L": [{"S": "32,44"}, {"S": "9,19"}]},
                        "type": {"S": "active_cells"},
                        "key": {"S": "state"},
                    },
                    "OldImage": {
                        "active_cells": {"L": [{"S": "32,44"}]},
                        "type": {"S": "active_cells"},
                        "key": {"S": "state"},
                    },
                    "SequenceNumber": "7585800000000023690800064",
                    "SizeBytes": 119,
                    "StreamViewType": "NEW_AND_OLD_IMAGES",
                },
                "eventSourceARN": "arn:aws:dynamodb:us-east-2:668805947503:table/sh-ws-demo-dev/stream/2023-04-26T22:19:16.291",
            },
            {
                "eventID": "8832fd8a1395eb2eac51dd2845eae5a8",
                "eventName": "REMOVE",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "us-east-2",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1682560306.0,
                    "Keys": {
                        "type": {"S": "21edc96d-bbdc-4736-a318-da661d0ba5d5"},
                        "key": {"S": "websocket"},
                    },
                    "OldImage": {
                        "stage": {"S": "local"},
                        "created": {"N": "1682559700"},
                        "domain": {"S": "localhost"},
                        "type": {"S": "21edc96d-bbdc-4736-a318-da661d0ba5d5"},
                        "user": {"S": "Google_117789969009555435433"},
                        "key": {"S": "websocket"},
                    },
                    "SequenceNumber": "7581600000000000155797526",
                    "SizeBytes": 173,
                    "StreamViewType": "NEW_AND_OLD_IMAGES",
                },
                "eventSourceARN": "arn:aws:dynamodb:us-east-2:668805947503:table/sh-ws-demo-dev/stream/2023-04-26T22:19:16.291",
            },
        ]
    }
    for record in demo["Records"]:
        state_record = ActiveCells(record)
        print(state_record.event_name)
        print(state_record.keys)
        print(state_record.new_active_cells)


if __name__ == "__main__":
    main()
