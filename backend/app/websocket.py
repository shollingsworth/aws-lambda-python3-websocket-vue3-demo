#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main Handler entrypoint for lambdas."""
import json
import logging

from app.config import Config
from app.control import Control
from app.jwt import JwtToken

logger = logging.getLogger("handler_logger")
logger.setLevel(logging.DEBUG)
config = Config()


def _get_response(status_code, body):
    if not isinstance(body, str):
        body = json.dumps(body)
    return {"statusCode": status_code, "body": body}


class WebSocketMessageHandler:
    """
    Handles messages sent to the websocket.

    Messages are sent to the websocket via the $connect route.
    """

    def __init__(self, event: dict) -> None:
        self.connectionID = event.get("requestContext", {}).get("connectionId")
        self.control = Control(self.connectionID)
        self.event = event
        self.body = self._get_body()
        self.domain = event.get("requestContext", {}).get("domainName")
        self.stage = event.get("requestContext", {}).get("stage")
        logger.info(
            "Message received (CID: {}, Event: {})".format(
                self.connectionID,
                self.event,
            )
        )

    def _get_body(self):
        try:
            return json.loads(self.event.get("body", ""))
        except:
            logger.debug("event body could not be JSON decoded.")
            return {}

    def handle_message(self):
        logger.info("Message Event: {}".format(self.event))
        self.control.parse_message(self.body)
        return _get_response(200, "Event OK")


class WebSocketConnectHandler:
    """
    Handles connecting and disconnecting for the Websocket.

    Connect verifes the passed in token, and if successful,
    adds the connectionID to the database.

    Disconnect removes the connectionID from the database.
    """

    def __init__(self, event: dict) -> None:
        self.connectionID = event.get("requestContext", {}).get("connectionId")
        self.control = Control(self.connectionID)
        self.event = event
        self.event_type = event.get("requestContext", {}).get("eventType")
        self.domain = event.get("requestContext", {}).get("domainName")
        self.stage = event.get("requestContext", {}).get("stage")
        self.token = event.get("queryStringParameters", {}).get("token")
        if self.token:
            self.tok = JwtToken(self.token)
            self.username = self.tok.username
        else:
            self.tok = None
            self.username = ""

    def handle_connection(self) -> dict:
        if self.event_type == "CONNECT":
            return self._handle_connect()
        elif self.event_type == "DISCONNECT":
            return self._handle_disconnect()
        else:
            msg = "Connection manager received unrecognized eventType '{}'".format(
                self.event_type
            )
            logger.error(msg)
            return _get_response(500, msg)

    def _handle_connect(self):
        valid, status_code, msg = self._check_valid()
        if not valid:
            logger.error(msg)
            return _get_response(status_code, msg)
        # Add connectionID to the database
        self.control.save_connection(
            self.domain,
            self.stage,
            self.username,
        )
        return _get_response(200, "Connect successful.")

    def _handle_disconnect(self):
        logger.info("Disconnect requested (CID: {})".format(self.connectionID))
        # Ensure connectionID is set
        if not self.connectionID:
            logger.error("Failed: connectionId value not set.")
            return _get_response(500, "connectionId value not set.")

        # Remove the connectionID from the database
        self.control.delete_connection()
        return _get_response(200, "Disconnect successful.")

    def _check_valid(self):
        logger.info(
            "Message received (CID: {}, Event: {})".format(
                self.connectionID,
                self.event,
            )
        )
        if not self.connectionID:
            logger.error("Failed: connectionId value not set.")
            return False, 500, "connectionId value not set."

        # Ensure connectionID and token are set
        if not self.tok:
            logger.debug("Failed: token query parameter not provided.")
            return False, 400, "token query parameter not provided."

        # Verify the token
        if not self.tok.valid:
            msg = f"Failed: Token verification failed. {self.tok.status}"
            logger.debug(msg)
            return False, 400, msg
        return True, 200, "Valid"
