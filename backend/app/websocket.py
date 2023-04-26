#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main Handler entrypoint for lambdas."""
import json
import logging
import time

import boto3

from app.config import Config
from app.jwt import JwtToken

logger = logging.getLogger("handler_logger")
logger.setLevel(logging.DEBUG)
config = Config()

dynamodb = boto3.resource("dynamodb")


class WebSocketMessageHandler:
    """
    Handles messages sent to the websocket.

    Messages are sent to the websocket via the $connect route.
    """

    def __init__(self, event: dict) -> None:
        self.event = event
        self.body = self._get_body()
        self.connectionID = event.get("requestContext", {}).get("connectionId")
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

    def _get_response(self, status_code, body):
        if not isinstance(body, str):
            body = json.dumps(body)
        return {"statusCode": status_code, "body": body}

    def handle_message(self):
        logger.info("Message Event: {}".format(self.event))
        self.send_message(self.body)
        return self._get_response(200, "Event OK")

    def send_message(self, data):
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
            ConnectionId=self.connectionID, Data=json.dumps(data).encode("utf-8")
        )


class WebSocketConnectHandler:
    """
    Handles connecting and disconnecting for the Websocket.

    Connect verifes the passed in token, and if successful,
    adds the connectionID to the database.

    Disconnect removes the connectionID from the database.
    """

    def __init__(self, event: dict) -> None:
        #  # sts get caller identity
        #  sts = boto3.client("sts")
        #  self.account_id = sts.get_caller_identity()["Account"]
        #  logger.info("Account ID: {}".format(self.account_id))
        # get region
        self.event = event
        self.connectionID = event.get("requestContext", {}).get("connectionId")
        self.event_type = event.get("requestContext", {}).get("eventType")
        self.domain = event.get("requestContext", {}).get("domainName")
        self.stage = event.get("requestContext", {}).get("stage")
        self.token = event.get("queryStringParameters", {}).get("token")
        if self.token:
            self.tok = JwtToken(self.token)
        else:
            self.tok = None

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
            return self._get_response(500, msg)

    def _get_response(self, status_code, body):
        if not isinstance(body, str):
            body = json.dumps(body)
        return {"statusCode": status_code, "body": body}

    def _handle_connect(self):
        valid, status_code, msg = self._check_valid()
        if not valid:
            logger.error(msg)
            return self._get_response(status_code, msg)
        # Add connectionID to the database
        table = dynamodb.Table(config.table)
        table.put_item(
            Item={
                "key": "websocket",
                "type": self.connectionID,
                "domain": self.domain,
                "stage": self.stage,
                "created": int(time.time()),
            }
        )
        return self._get_response(200, "Connect successful.")

    def _handle_disconnect(self):
        logger.info("Disconnect requested (CID: {})".format(self.connectionID))
        # Ensure connectionID is set
        if not self.connectionID:
            logger.error("Failed: connectionId value not set.")
            return self._get_response(500, "connectionId value not set.")

        # Remove the connectionID from the database
        table = dynamodb.Table(config.table)
        table.delete_item(
            Key={
                "key": "websocket",
                "type": self.connectionID,
            }
        )
        return self._get_response(200, "Disconnect successful.")

    #  def _send_to_connection(self, data):
    #      gwapi = boto3.client(
    #          "apigatewaymanagementapi",
    #          endpoint_url=f"https://{self.domain}/{self.stage}",
    #      )
    #      return gwapi.post_to_connection(
    #          ConnectionId=self.connectionID, Data=json.dumps(data).encode("utf-8")
    #      )


#  def default_message(event, _):
#      """
#      Send back error when unrecognized WebSocket action is received.
#      """
#      logger.info(f"Unrecognized WebSocket action received. {event}")
#      return _get_response(400, "Unrecognized WebSocket action.")


#  def get_recent_messages(event, _):
#      """
#      Return the 10 most recent chat messages.
#      """
#      connectionID = event["requestContext"].get("connectionId")
#      logger.info("Retrieving most recent messages for CID '{}'".format(connectionID))
#
#      # Ensure connectionID is set
#      if not connectionID:
#          logger.error("Failed: connectionId value not set.")
#          return _get_response(500, "connectionId value not set.")
#
#      # Get the 10 most recent chat messages
#      table = dynamodb.Table("serverless-chat_Messages")
#      response = table.query(
#          KeyConditionExpression="Room = :room",
#          ExpressionAttributeValues={":room": "general"},
#          Limit=10,
#          ScanIndexForward=False,
#      )
#      items = response.get("Items", [])
#
#      # Extract the relevant data and order chronologically
#      messages = [{"username": x["Username"], "content": x["Content"]} for x in items]
#      messages.reverse()
#
#      # Send them to the client who asked for it
#      data = {"messages": messages}
#      _send_to_connection(connectionID, data, event)
#
#      return _get_response(200, "Sent recent messages to '{}'.".format(connectionID))


#  def send_message(event, _):
#      """
#      When a message is sent on the socket, verify the passed in token,
#      and forward it to all connections if successful.
#      """
#      logger.info("Message sent on WebSocket.")
#
#      # Ensure all required fields were provided
#      body = _get_body(event)
#      if not isinstance(body, dict):
#          logger.debug("Failed: message body not in dict format.")
#          return _get_response(400, "Message body not in dict format.")
#      for attribute in ["token", "content"]:
#          if attribute not in body:
#              logger.debug("Failed: '{}' not in message dict.".format(attribute))
#              return _get_response(400, "'{}' not in message dict".format(attribute))
#
#      # Verify the token
#      tok = JwtToken(body["token"])
#      if not tok.valid:
#          msg = f"Failed: Token verification failed. {tok.status}"
#          logger.debug(msg)
#          return _get_response(400, msg)
#      logger.info("Verified JWT for '{}'".format(tok.username))
#
#      # Get the next message index
#      # (Note: there is technically a race condition where two
#      # users post at the same time and use the same index, but
#      # accounting for that is outside the scope of this project)
#      table = dynamodb.Table("serverless-chat_Messages")
#      response = table.query(
#          KeyConditionExpression="Room = :room",
#          ExpressionAttributeValues={":room": "general"},
#          Limit=1,
#          ScanIndexForward=False,
#      )
#      items = response.get("Items", [])
#      index = items[0]["Index"] + 1 if len(items) > 0 else 0
#
#      # Add the new message to the database
#      timestamp = int(time.time())
#      content = body["content"]
#      table.put_item(
#          Item={
#              "Room": "general",
#              "Index": index,
#              "Timestamp": timestamp,
#              "Username": username,
#              "Content": content,
#          }
#      )
#
#      # Get all current connections
#      table = dynamodb.Table("serverless-chat_Connections")
#      response = table.scan(ProjectionExpression="ConnectionID")
#      items = response.get("Items", [])
#      connections = [x["ConnectionID"] for x in items if "ConnectionID" in x]
#
#      # Send the message data to all connections
#      message = {"username": username, "content": content}
#      logger.debug("Broadcasting message: {}".format(message))
#      data = {"messages": [message]}
#      for connectionID in connections:
#          _send_to_connection(connectionID, data, event)
#      return _get_response(
#          200, "Message sent to {} connections.".format(len(connections))
#      )


#  def ping(event, _):
#      """
#      Sanity check endpoint that echoes back 'PONG' to the sender.
#      """
#      logger.info(f"Ping requested. {event}")
#      return _get_response(200, "PONG!")
