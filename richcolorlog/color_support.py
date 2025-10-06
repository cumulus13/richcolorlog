#!/usr/bin/env python3
"""
color_support.py
----------------
Robust cross-platform terminal color detection for Python applications.

Detects if the current terminal supports:
 - truecolor (24-bit RGB)
 - 256 colors (8-bit)
 - basic ANSI (16 colors)
 - none (no color / redirected output)

Compatible with:
 - Linux, macOS, *BSD, and other UNIX-like systems
 - Windows 10+ (CMD, PowerShell, Windows Terminal)
"""

import os
import sys
import platform
import curses
import ctypes


__all__ = ["ColorSupport", "Check"]


class ColorSupport:
    TRUECOLOR = "truecolor"
    COLOR_256 = "256color"
    BASIC = "basic"
    NONE = "none"


class Check:
    """Auto-detect terminal color support across all major OS."""

    def __new__(cls, force: str | None = None):
        """Return detected color mode immediately (not an instance)."""
        return cls.detect_color_support(force)

    # --- Environment checks ---
    @staticmethod
    def _check_env_truecolor() -> bool:
        colorterm = (os.getenv("COLORTERM") or "").lower()
        if "truecolor" in colorterm or "24bit" in colorterm:
            return True
        if os.getenv("WT_SESSION"):  # Windows Terminal
            return True
        return False

    # --- curses terminfo (Unix-like only) ---
    @staticmethod
    def _curses_colors() -> int:
        try:
            curses.setupterm()
            n = curses.tigetnum("colors")
            if isinstance(n, int):
                return n
        except Exception:
            pass
        return -1

    # --- Windows ANSI Enable ---
    @staticmethod
    def enable_windows_ansi() -> bool:
        if platform.system() != "Windows":
            return False

        try:
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            if handle in (0, -1):
                return False

            mode = ctypes.c_uint()
            if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                return False

            ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            new_mode = mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
            if new_mode != mode.value:
                if not kernel32.SetConsoleMode(handle, new_mode):
                    return False
            return True
        except Exception:
            return False

    # --- Core detection logic ---
    @classmethod
    def detect_color_support(cls, force: str | None = None) -> str:
        if force in (
            ColorSupport.TRUECOLOR,
            ColorSupport.COLOR_256,
            ColorSupport.BASIC,
            ColorSupport.NONE,
        ):
            return force

        if not sys.stdout.isatty():
            return ColorSupport.NONE

        if cls._check_env_truecolor():
            return ColorSupport.TRUECOLOR

        term = (os.getenv("TERM") or "").lower()
        if "256color" in term:
            return ColorSupport.COLOR_256
        if "color" in term:
            return ColorSupport.BASIC

        colors = cls._curses_colors()
        if colors >= 16777216:
            return ColorSupport.TRUECOLOR
        if colors >= 256:
            return ColorSupport.COLOR_256
        if colors >= 8:
            return ColorSupport.BASIC

        if platform.system() == "Windows":
            if cls.enable_windows_ansi():
                if cls._check_env_truecolor() or sys.getwindowsversion().major >= 10:
                    return ColorSupport.TRUECOLOR
                return ColorSupport.BASIC
            return ColorSupport.NONE

        return ColorSupport.BASIC


# --- Example usage ---
if __name__ == "__main__":
    mode = Check()

    if mode == ColorSupport.TRUECOLOR:
        print("24-bit color detected 🎨")
    elif mode == ColorSupport.COLOR_256:
        print("256 colors supported 🟢")
    elif mode == ColorSupport.BASIC:
        print("Basic ANSI colors ⚪")
    else:
        print("No color support ❌")
