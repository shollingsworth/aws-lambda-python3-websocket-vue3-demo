#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""config.py: Configuration for the application."""
import os


class Config:
    def __init__(self) -> None:
        self.is_offline = os.environ.get("IS_OFFLINE")
        self.stage = os.environ.get("STAGE", "")
        if not self.stage:
            raise ValueError("STAGE environment variable not set")
        self.prefix = os.environ.get("PREFIX", "")
        if not self.prefix:
            raise ValueError("PREFIX environment variable not set")
        self.sns_topic = os.environ.get("SNS_TOPIC", "")
        if not self.sns_topic:
            raise ValueError("SNS_TOPIC environment variable not set")
        self.region = os.environ.get("REGION", "")
        if not self.region:
            raise ValueError("REGION environment variable not set")
        self.table = os.environ.get("TABLE", "")
        if not self.table:
            raise ValueError("TABLE environment variable not set")
        self.userpool_id = os.environ.get("USERPOOL_ID", "")
        if not self.userpool_id:
            raise ValueError("USERPOOL_ID environment variable not set")
        self.app_client_id = os.environ.get("CLIENT_ID", "")
        if not self.app_client_id:
            raise ValueError("CLIENT_ID environment variable not set")
