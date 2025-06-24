#!/usr/bin/env python
"""
Rich Logger - A beautiful and feature-rich logging package using Rich library.
"""
import os
from pathlib import Path
import traceback

def get_version():
    """
    Get the version of the ddf module.
    Version is taken from the __version__.py file if it exists.
    The content of __version__.py should be:
    version = "0.33"
    """
    try:
        version_file = Path(__file__).parent / "__version__.py"
        if version_file.is_file():
            with open(version_file, "r") as f:
                for line in f:
                    if line.strip().startswith("version"):
                        parts = line.split("=")
                        if len(parts) == 2:
                            return parts[1].strip().strip('"').strip("'")
    except Exception as e:
        if os.getenv('TRACEBACK') and os.getenv('TRACEBACK') in ['1', 'true', 'True']:
            print(traceback.format_exc())
        else:
            print(f"ERROR: {e}")

    return "0.0.0"
    
__version__ = get_version()
__author__ = "Hadi Cahyadi"
__email__ = "cumulus13@gmail.com"

from .logger import (
    setup_logging,
    setup_logging_custom,
    get_def,
    CustomFormatter,
    CustomRichFormatter,
    _add_custom_level_method,
    EMERGENCY_LEVEL,
    FATAL_LEVEL,
    CRITICAL_LEVEL,
    ALERT_LEVEL,
    NOTICE_LEVEL,
    RICH_AVAILABLE,
    test
)

__all__ = [
    "setup_logging",
    "setup_logging_custom", 
    "get_def",
    "CustomFormatter",
    "CustomRichFormatter",
    "EMERGENCY_LEVEL",
    "FATAL_LEVEL", 
    "CRITICAL_LEVEL",
    "ALERT_LEVEL",
    "NOTICE_LEVEL"
    "RICH_AVAILABLE",
    "_add_custom_level_method",
    "test"
]