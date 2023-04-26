#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Data Structures."""
from dataclasses import dataclass

@dataclass
class Cell:
    x: int
    y: int
    active: bool


@dataclass
class AlertBox:
    name: str
    x1: int
    y1: int
    x2: int
    y2: int
