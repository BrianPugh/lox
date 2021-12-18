#!/usr/bin/env python
# content of conftest.py

import pytest


def pytest_addoption(parser):
    try:
        parser.addoption(
            "--visual",
            action="store_true",
            default=False,
            help="run interactive visual tests",
        )
    except ValueError:
        pass


def pytest_collection_modifyitems(config, items):
    if config.getoption("--visual"):
        # --visual given in cli: do not skip visual tests
        return
    skip_visual = pytest.mark.skip(reason="need --visual option to run")
    for item in items:
        if "visual" in item.keywords:
            item.add_marker(skip_visual)
