#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main Handler entrypoint for lambdas."""
import logging
import time

from app.control import Broadcast, CellState, Lock, SnsRecordHandler
from app.dynstream import ActiveCells
from app.websocket import WebSocketConnectHandler, WebSocketMessageHandler

logger = logging.getLogger("handler_logger")
logger.setLevel(logging.DEBUG)

RAND_WAIT = 1


def connect(event, _):
    """Handle a connection event."""
    logger.info("Connect requested")
    return WebSocketConnectHandler(event).handle_connection()


def message(event, _):
    """Handle a message event."""
    logger.info("Message requested")
    return WebSocketMessageHandler(event).handle_message()


def dynstream(event, _):
    """Handle a dynmodbstream."""
    logger.info("Dynstream requested: %s", str(event)[:100])
    for record in event["Records"]:
        state_record = ActiveCells(record)
        state_record.send_alerts()


def schedule_random(event, _):
    """Handle a scheduled event."""
    logger.info("Scheduled event requested: %s", event)
    start = time.time()
    cs = CellState()
    bc = Broadcast()
    lock = Lock("schedule_random")
    is_locked = lock.lock()
    if not is_locked:
        logger.info("Lock is already in use, exiting")
        return
    # loop for 60 seconds
    while time.time() - start < 55:
        res = cs.add_random_active()
        if res:
            pl = {
                "action": "add_active_cell",
                "message": {
                    "x": res["x"],
                    "y": res["y"],
                },
            }
            bc.send_message(pl)
        else:
            # if no more cells are available, clear the board
            cs.clear_active()
            bc.send_message(
                {
                    "action": "board_cleared",
                }
            )
        time.sleep(RAND_WAIT)
    logger.info("Unlocking")
    lock.unlock()


def sns(event, _):
    """Handle an sns event."""
    logger.info("SNS event requested: %s", event)
    for record in event["Records"]:
        SnsRecordHandler(record).handle_message()
        #  {
        #      "Records": [
        #          {
        #              "EventSource": "aws:sns",
        #              "EventVersion": "1.0",
        #              "EventSubscriptionArn": "arn:aws:sns:us-east-2:668805947503:sh-ws-demo-dev20230427145206341500000003:f17bc7f6-50e5-499b-bc78-1071a7e83737",
        #              "Sns": {
        #                  "Type": "Notification",
        #                  "MessageId": "d8dc1647-9a1a-50da-8b72-4a8315ff3e71",
        #                  "TopicArn": "arn:aws:sns:us-east-2:668805947503:sh-ws-demo-dev20230427145206341500000003",
        #                  "Subject": None,
        #                  "Message": '{"foo": "bar"}',
        #                  "Timestamp": "2023-04-27T14:58:45.860Z",
        #                  "SignatureVersion": "1",
        #                  "Signature": "09Zh4d9XlNtLgnOscWaQHSO/YgrqF4JKPe50vNQmIticQK8Qxbd6MnL+LWFKhKQASLmgQT4MJuQVK6qqnyT/2fW5CBI+LA79KOLca6YrDSlfFAWBz9l6TY81zl8DyUfXI5a8gMQvg7k8G1d4eV1iySlJ6CnmVYIVJw3PxSMg9GloQtmDVrRZ+Cry09iYEZMsX0pFEDh0agRc9nvZRlrJGuRxXn6j6Z0X0ct7xT8zy1hK9wJNz8Ssu52tL4d45luQiXGyNdob6V3plWNXaUotaE0hWAQwNagWjfjL2XnLpRsDXt4/rKm9T9HOwVAXfFHVEac5ilB6WJep1w7E8kFV8w==",
        #                  "SigningCertUrl": "https://sns.us-east-2.amazonaws.com/SimpleNotificationService-56e67fcb41f6fec09b0196692625d385.pem",
        #                  "UnsubscribeUrl": "https://sns.us-east-2.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-2:668805947503:sh-ws-demo-dev20230427145206341500000003:f17bc7f6-50e5-499b-bc78-1071a7e83737",
        #                  "MessageAttributes": {},
        #              },
        #          }
        #      ]
        #  }
