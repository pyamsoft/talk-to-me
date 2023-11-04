#!/usr/bin/env python3
from dataclasses import dataclass


@dataclass
class ChapterRange:
    start: int
    end: int


@dataclass
class BookInfo:
    title: str
    author: str


@dataclass
class Chapter:
    number: int
    title: str
    content: str
