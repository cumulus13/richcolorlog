from richcolorlog import setup_logging
import os
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
console = Console()

console.print(Panel(Align("[bold #00FFFF]TEST LOGGING[/] with [bold #FFFF00]RichColorLog[/] [bold #AAAAFF](setup_logging)[/]", "center"), expand=True, border_style="green"))

console.rule(f"INFO: default")
logger= setup_logging(show_type=True)
logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")