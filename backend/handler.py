#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main Handler entrypoint for lambdas."""
import logging

from app.dynstream import ActiveCells
from app.websocket import WebSocketConnectHandler, WebSocketMessageHandler

logger = logging.getLogger("handler_logger")
logger.setLevel(logging.DEBUG)


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
    logger.info("Dynstream requested: %s", event)
    for record in event["Records"]:
        state_record = ActiveCells(record)
        state_record.send_alerts()
