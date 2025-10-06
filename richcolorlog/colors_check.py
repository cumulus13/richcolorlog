import os
import sys
import platform
import ctypes


class SafeDict(dict):
    """Dictionary yang mengembalikan string kosong untuk key yang tidak ada."""
    def __missing__(self, key):
        return ''


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
            import curses
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


class Colors:
    """Handler untuk color schemes dengan berbagai format output."""

    def __init__(self, color_type='ansi', show_background=False):
        self.color_type = color_type
        self.show_background = show_background

    def rich_color(self, show_background=False):
        """Mengembalikan color scheme dalam format Rich library."""
        if show_background:
            COLORS = {
                'debug': "#000000 on #FFAA00",
                'info': "#000000 on #00FF00",
                'warning': "black on #FFFF00",
                'error': "white on red",
                'critical': "bright_white on #0000FF",
                'fatal': "blue on #FF557F",
                'emergency': "bright_white on #AA00FF",
                'alert': "bright_white on #005500",
                'notice': "black on #00FFFF",
                'reset': '',
            }
        else:
            COLORS = {
                'debug': "#FFAA00",
                'info': "#00FF00",
                'warning': "#FFFF00",
                'error': "red",
                'critical': "#0000FF",
                'fatal': "#FF557F",
                'emergency': "#AA00FF",
                'alert': "#005500",
                'notice': "#00FFFF",
                'reset': '',
            }
        return COLORS

    def check(self):
        """Deteksi dan kembalikan color scheme sesuai terminal support."""
        COLORS = {}
        mode = Check()
        
        if mode == ColorSupport.TRUECOLOR:
            if self.color_type == 'ansi':
                if self.show_background:
                    COLORS = SafeDict({
                        'debug': "\x1b[38;2;0;0;0;48;2;255;170;0m",        # #000000 on #FFAA00
                        'info': "\x1b[38;2;0;0;0;48;2;0;255;0m",           # #000000 on #00FF00
                        'warning': "\x1b[38;2;0;0;0;48;2;255;255;0m",      # black on #FFFF00
                        # 'error': "\x1b[38;2;255;255;255;48;2;255;0;0m",    # white on red (RGB 24-bit) (Bugs)
                        'error': "\x1b[97;41m",                            # white on red
                        'critical': "\x1b[38;2;255;255;255;48;2;0;0;255m", # bright_white on #0000FF
                        'fatal': "\x1b[38;2;0;0;255;48;2;255;85;127m",     # blue on #FF557F
                        'emergency': "\x1b[38;2;255;255;255;48;2;170;0;255m", # bright_white on #AA00FF
                        'alert': "\x1b[38;2;255;255;255;48;2;0;85;0m",     # bright_white on #005500
                        'notice': "\x1b[38;2;0;0;0;48;2;0;255;255m",       # black on #00FFFF
                        'reset': "\x1b[0m"
                    })
                else:
                    COLORS = SafeDict({
                        'debug': "\x1b[38;2;255;170;0m",        # #FFAA00
                        'info': "\x1b[38;2;0;255;0m",           # #00FF00
                        'warning': "\x1b[38;2;255;255;0m",      # #FFFF00
                        'error': "\x1b[38;2;255;0;0m",          # red
                        'critical': "\x1b[38;2;0;0;255m",       # #0000FF
                        'fatal': "\x1b[38;2;255;85;127m",       # #FF557F
                        'emergency': "\x1b[38;2;170;0;255m",    # #AA00FF
                        'alert': "\x1b[38;2;0;85;0m",           # #005500
                        'notice': "\x1b[38;2;0;255;255m",       # #00FFFF
                        'reset': "\x1b[0m"
                    })
            elif self.color_type == 'rich':
                COLORS = self.rich_color(self.show_background)
                
        elif mode == ColorSupport.COLOR_256:
            if self.color_type == 'ansi':
                if self.show_background:
                    COLORS = SafeDict({
                        'debug': "\x1b[30;48;5;214m",      # black on orange
                        'info': "\x1b[30;48;5;46m",        # black on bright green
                        'warning': "\x1b[30;48;5;226m",    # black on yellow
                        'error': "\x1b[97;41m",            # white on red
                        'critical': "\x1b[97;44m",         # white on blue
                        'fatal': "\x1b[21;48;5;204m",      # blue on pink
                        'emergency': "\x1b[97;48;5;129m",  # white on purple
                        'alert': "\x1b[97;48;5;22m",       # white on dark green
                        'notice': "\x1b[30;48;5;51m",      # black on cyan
                        'reset': "\x1b[0m"
                    })
                else:
                    COLORS = SafeDict({
                        'debug': "\x1b[38;5;214m",      # orange
                        'info': "\x1b[38;5;46m",        # bright green
                        'warning': "\x1b[38;5;226m",    # yellow
                        'error': "\x1b[91m",            # red
                        'critical': "\x1b[38;5;21m",    # blue
                        'fatal': "\x1b[38;5;204m",      # pink
                        'emergency': "\x1b[38;5;129m",  # purple
                        'alert': "\x1b[38;5;22m",       # dark green
                        'notice': "\x1b[38;5;51m",      # cyan
                        'reset': "\x1b[0m"
                    })
            elif self.color_type == 'rich':
                COLORS = self.rich_color(self.show_background)
                
        elif mode == ColorSupport.BASIC:
            if self.color_type == 'ansi':
                if self.show_background:
                    COLORS = SafeDict({
                        'debug': "\x1b[30;43m",      # black on yellow
                        'info': "\x1b[30;42m",       # black on green
                        'warning': "\x1b[30;43m",    # black on yellow
                        'error': "\x1b[97;41m",      # white on red
                        'critical': "\x1b[97;44m",   # white on blue
                        'fatal': "\x1b[97;45m",      # white on magenta
                        'emergency': "\x1b[97;45m",  # white on magenta
                        'alert': "\x1b[97;42m",      # white on green
                        'notice': "\x1b[30;46m",     # black on cyan
                        'reset': "\x1b[0m"
                    })
                else:
                    COLORS = SafeDict({
                        'debug': "\x1b[33m",      # yellow
                        'info': "\x1b[32m",       # green
                        'warning': "\x1b[33m",    # yellow
                        'error': "\x1b[31m",      # red
                        'critical': "\x1b[34m",   # blue
                        'fatal': "\x1b[35m",      # magenta
                        'emergency': "\x1b[35m",  # magenta
                        'alert': "\x1b[32m",      # green
                        'notice': "\x1b[36m",     # cyan
                        'reset': "\x1b[0m"
                    })
            elif self.color_type == 'rich':
                # Untuk basic mode, tetap gunakan rich_color format
                COLORS = self.rich_color(self.show_background)
                
        elif mode == ColorSupport.NONE:
            COLORS = SafeDict({
                'debug': '',
                'info': '',
                'warning': '',
                'error': '',
                'critical': '',
                'fatal': '',
                'emergency': '',
                'alert': '',
                'notice': '',
                'reset': ''
            })
        
        return COLORS


# Contoh penggunaan
if __name__ == "__main__":
    colors_ansi = Colors(color_type='ansi', show_background=False).check()
    print(f"colors_ansi: {colors_ansi}")
    # # Test ANSI colors
    # print("=== Testing ANSI Colors ===")
    # colors_ansi = Colors(color_type='ansi', show_background=False)
    # ansi_scheme = colors_ansi.check()
    
    # for level, code in ansi_scheme.items():
    #     if level != 'reset':
    #         print(f"{code}{level.upper()}: This is a test message{ansi_scheme['reset']}")
    
    # print("\n=== Testing ANSI Colors with Background ===")
    # colors_ansi_bg = Colors(color_type='ansi', show_background=True)
    # ansi_bg_scheme = colors_ansi_bg.check()
    
    # for level, code in ansi_bg_scheme.items():
    #     if level != 'reset':
    #         print(f"{code}{level.upper()}: This is a test message{ansi_bg_scheme['reset']}")
    
    # # Test Rich colors (untuk digunakan dengan Rich library)
    # print("\n=== Testing Rich Color Format ===")
    # colors_rich = Colors(color_type='rich', show_background=False)
    # rich_scheme = colors_rich.check()
    
    # for level, style in rich_scheme.items():
    #     if level != 'reset':
    #         print(f"{level.upper()}: {style}")
    
    # # Deteksi mode terminal
    # print(f"\n=== Terminal Color Support: {Check()} ===")