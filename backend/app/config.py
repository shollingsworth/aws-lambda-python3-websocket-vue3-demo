#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""config.py: Configuration for the application."""
import os


class Config:
    def __init__(self) -> None:
        self.is_offline = os.environ.get("IS_OFFLINE")
        self.stage = os.environ.get("STAGE", "dev")
        self.prefix = os.environ.get("PREFIX", "sh-ws-demo")
        self.sns_topic = os.environ.get("SNS_TOPIC", "NOT SET")
        self.region = "us-east-2"
        self.table = f"{self.prefix}-{self.stage}" if not self.is_offline else f'{self.prefix}-dev'
