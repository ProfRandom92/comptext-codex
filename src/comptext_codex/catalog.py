"""Utilities to load the bundled CompText catalog."""

from __future__ import annotations

import csv
from importlib import resources
from typing import Iterable, List, Mapping

CATALOG_FILENAME = "CompText-Codex.csv"


def load_catalog() -> List[Mapping[str, str]]:
    """Load the command catalog shipped with the package."""

    with resources.files(__package__).joinpath("data").joinpath(CATALOG_FILENAME).open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def iter_catalog() -> Iterable[Mapping[str, str]]:
    for row in load_catalog():
        yield row
