#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main Handler entrypoint for lambdas."""
import logging

import boto3

from app.jwt import JwtToken
from app.websocket import WebSocketConnectHandler, WebSocketMessageHandler

logger = logging.getLogger("handler_logger")
logger.setLevel(logging.DEBUG)

dynamodb = boto3.resource("dynamodb")


def connect(event, _):
    """Handle a connection event."""
    logger.info("Connect requested")
    return WebSocketConnectHandler(event).handle_connection()


def message(event, _):
    """Handle a message event."""
    logger.info("Message requested")
    return WebSocketMessageHandler(event).handle_message()


def ping(event, _):
    """Handle a ping event."""
    logger.info("Ping requested: %s", event)
    return {"statusCode": 200, "body": "pong"}


if __name__ == "__main__":
    # the following is useful to make this script executable in both
    # AWS Lambda and any other local environments
    # for testing locally you can enter the JWT ID Token here
    token = """
eyJraWQiOiJ3VExGTzhmNkVrZ1R1V0wrMTJtNkNkd0JENXBhNVwvbFRDZHV4aSt6Yjlzcz0iLCJhbGciOiJSUzI1NiJ9.eyJhdF9oYXNoIjoiSjBuY2dJUzJSM3FwU1NKcnlhMEtPdyIsInN1YiI6IjBlZDg5OGNhLWVmNmQtNGU4Yy05MWE2LTFiNGY0YTJhNGI0NyIsImNvZ25pdG86Z3JvdXBzIjpbInVzLWVhc3QtMl95M01xMlNaNTRfR29vZ2xlIl0sImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMi5hbWF6b25hd3MuY29tXC91cy1lYXN0LTJfeTNNcTJTWjU0IiwiY29nbml0bzp1c2VybmFtZSI6Ikdvb2dsZV8xMTc3ODk5NjkwMDk1NTU0MzU0MzMiLCJvcmlnaW5fanRpIjoiNGM2MzgzNjYtZmE4Zi00NzhmLTgxMzYtY2IxZjVhNGNlM2RhIiwiYXVkIjoiMXRwbDg2ZGpoNGcydXNsdXJsamlpNjJzZ2QiLCJpZGVudGl0aWVzIjpbeyJ1c2VySWQiOiIxMTc3ODk5NjkwMDk1NTU0MzU0MzMiLCJwcm92aWRlck5hbWUiOiJHb29nbGUiLCJwcm92aWRlclR5cGUiOiJHb29nbGUiLCJpc3N1ZXIiOm51bGwsInByaW1hcnkiOiJ0cnVlIiwiZGF0ZUNyZWF0ZWQiOiIxNjgxOTI5NTMwOTkxIn1dLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTY4MjExOTI1NywiZXhwIjoxNjgyNDQ3NTk4LCJpYXQiOjE2ODI0NDM5OTgsImp0aSI6IjBhYWIzNDc2LTI3YmMtNGMwMy05ZDcwLTQxN2Q0OGRmNWYzZiIsImVtYWlsIjoiaG9sbGluZ3N3b3J0aC5zdGV2ZW5kQGdtYWlsLmNvbSJ9.g_WdwxGOWzKR54MRNxxKiDWJR1Wmo0Qazw9Z23VkmXiNXKvj-rERRsDGKYDuQYt5GJAQfD1Ubdi-QqoWnT5UXeGaIj5AlYuEELE0PLdDD9pt8dxCI8v3DzSr0uuF85F9azFiW9cu25k-amWxaM5Ae3zgcG-8JgWsmUd82PV6ugiwYzGZEi-RnBNddQ5L089-ot5j6ATdgvdVZJX-uoFoDwNCzZN4ji8lNBNuOB_lf9rzPKCzVYj8sEAARqbA9-dp8Tg4e11coMVAfF4Pn3VuZAReo8SsKFEvnPD3gxkW3ZR1JGv64snPYXPw77TVcaYOBxAK9z1LA9Ao2wtwft3P7Q
    """.strip()
    # event = {"token": token}
    # lambda_handler(event, None)
    tok = JwtToken(token)
    print(tok.to_dict())
