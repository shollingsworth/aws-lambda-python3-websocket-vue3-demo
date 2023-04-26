#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""config.py: Configuration for the application."""
import os


class Config:
    def __init__(self) -> None:
        self.is_offline = os.environ.get("IS_OFFLINE")
        self.stage = os.environ.get("STAGE", "dev")
        self.prefix = os.environ.get("PREFIX")
        self.table = f"{self.prefix}-{self.stage}"
