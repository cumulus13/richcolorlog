
def test():
	from richcolorlog import setup_logging, AnsiLogHandler
	import os

	HAS_RICH=False
	try:
	    from rich.console import Console
	    from rich.panel import Panel
	    from rich.align import Align
	    console = Console()
	    HAS_RICH=True
	except:
	    # print("THIS TEST for 'rich' module installed !, please install first `pip install rich`")
	    # sys.exit()
	    pass

	if HAS_RICH:
	    console.print(Panel(Align("[bold #00FFFF]TEST LOGGING[/] with [bold #FFFF00]RichColorLog[/] [bold #AAAAFF](setup_logging)[/]", "center"), expand=True, border_style="green"))

	    console.rule(f"INFO: default")
	    logger= setup_logging()
	    logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    # console.rule("end")
	    console.rule("end")
	    console.print()

	    console.rule("INFO: show_path=False")
	    logger= setup_logging(show_path=False)
	    logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    console.rule("end")
	    console.print()

	    console.rule("INFO: show_icon=False")
	    logger= setup_logging(show_icon=False, show_path=False)
	    logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    console.rule("end")
	    console.print()

	    console.rule("INFO: icon_first=False")
	    logger= setup_logging(icon_first=False, show_path=False)
	    logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    console.rule("end")
	    console.print()

	    console.rule("ERROR: default, level_in_message=False")
	    logger= setup_logging(level_in_message=False)
	    logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    console.rule("end")
	    console.print()

	    console.rule("ERROR: show_path=False, level_in_message=False")
	    logger= setup_logging(show_path=False, level_in_message=False)
	    logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    console.rule("end")
	    console.print()

	    console.rule("ERROR: show_icon=False, level_in_message=False")
	    logger= setup_logging(show_icon=False, show_path=False, level_in_message=False)
	    logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    console.rule("end")
	    console.print()

	    console.rule("ERROR: icon_first=False, level_in_message=False")
	    logger= setup_logging(icon_first=False, show_path=False, level_in_message=False)
	    logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    console.rule("end")
	    console.print()

	    console.rule("show_path=False, level_in_message=False")
	    logger = setup_logging(show_path=False, level_in_message=False)
	            
	    logger.emergency("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.alert("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.critical("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.warning("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.notice("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.debug("This is a debug message - will RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.fatal("This is a debug message - will RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    console.rule("end")
	    console.print()

	    console.rule("show_background=False, show_path=False, level_in_message=False")
	    logger = setup_logging(show_background=False, show_path=False, level_in_message=False)

	    logger.emergency("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.alert("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.critical("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.warning("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.notice("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.debug("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.fatal("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

	    console.rule("end")
	    console.print()

	    console.rule("icon_first=False, show_path=False, level_in_message=False")
	    logger = setup_logging(show_path=False, icon_first=False)
	            
	    logger.emergency("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.alert("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.critical("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.warning("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.notice("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.debug("This is a debug message - will RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.fatal("This is a debug message - will RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    console.rule("end")
	    console.print()

	    console.rule("show_background=False, icon_first=False, show_path=False, level_in_message=False")
	    logger = setup_logging(show_background=False, show_path=False, icon_first=False)

	    logger.emergency("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.alert("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.critical("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.warning("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.notice("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.debug("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.fatal("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

	    console.rule("end")
	    console.print()

	    console.rule("show_background=False, icon_first=False, show_path=True, level_in_message=False")
	    logger = setup_logging(show_background=False, show_path=True, icon_first=False)

	    logger.emergency("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.alert("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.critical("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.warning("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.notice("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.debug("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.fatal("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

	    console.rule("end")
	    console.print()

	    console.rule("show_background=True, icon_first=False, show_path=True, level_in_message=True")
	    logger = setup_logging(show_background=True, show_path=True, icon_first=False, level_in_message=True)

	    logger.emergency("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.alert("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.critical("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.warning("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.notice("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.debug("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.fatal("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

	    console.rule("end")
	    console.print()

	    import logging
	    console.rule("⭐INHERITANCE⭐", characters="🦆")
	    console.print("\n\n")

	    logger = logging.getLogger("INHERITANCE")
	    from richcolorlog import RichColorLogHandler
	    handler = RichColorLogHandler()
	    logger.handlers.clear()
	    logger.addHandler(handler)
	    logger.propagate = False

	    logger.emergency("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.alert("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.critical("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.warning("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.notice("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.debug("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

	    console.rule("⭐INHERITANCE⭐ debug_color=#FFAA00", characters="🦆")
	    handler = RichColorLogHandler(debug_color="#FFAA00")
	    logger.handlers.clear()
	    logger.addHandler(handler)
	    logger.propagate = False
	    logger.debug("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

	    handler = RichColorLogHandler()
	    logger.handlers.clear()
	    logger.addHandler(handler)
	    logger.propagate = False
	    logger.fatal("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

	    console.rule("end")
	    console.print()

	    console.rule("⭐INHERITANCE⭐show_path=False, show_path=False", characters="🌽")
	    console.print("\n\n")

	    logger = logging.getLogger("INHERITANCE")
	    from richcolorlog import RichColorLogHandler
	    handler = RichColorLogHandler(show_path=False)
	    logger.handlers.clear()
	    logger.addHandler(handler)
	    logger.propagate = False

	    logger.emergency("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.alert("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.critical("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.warning("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.notice("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	    logger.debug("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

	    console.rule("⭐INHERITANCE⭐ debug_color=#FFAA00, show_path=False", characters="🌽")
	    handler = RichColorLogHandler(debug_color="#FFAA00", show_path=False)
	    logger.handlers.clear()
	    logger.addHandler(handler)
	    logger.propagate = False
	    logger.debug("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

	    handler = RichColorLogHandler(show_path=False)
	    logger.handlers.clear()
	    logger.addHandler(handler)
	    logger.propagate = False
	    logger.fatal("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

	#==========================================================================================
	if HAS_RICH:
		console.print(Panel(Align("[bold #00FFFF]TEST LOGGING[/] with [bold #FFFF00]AnsiLogHandler[/] [bold #AAAAFF](setup_logging)[/]", "center"), expand=True, border_style="green"))

		console.rule(f"INFO: default")
	else:
		print("TEST LOGGING with AnsiLogHandler (setup_logging)")
	logger= setup_logging(HANDLER=AnsiLogHandler)
	logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	# console.rule("end")
	if HAS_RICH:
		console.rule("end")
		console.print()
	else:
		print("--------------------------------------------------")
	

	if HAS_RICH: console.rule("INFO: show_path=False")
	logger= setup_logging(show_path=False, HANDLER=AnsiLogHandler)
	logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	if HAS_RICH:
		console.rule("end")
		console.print()

		console.rule("INFO: show_icon=False")
	else:
		print("-------------------------------------------------")
		print("TEST LOGGING with AnsiLogHandler (setup_logging)")
	logger= setup_logging(show_icon=False, show_path=False, HANDLER=AnsiLogHandler)
	logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	if HAS_RICH:
		console.rule("end")
		console.print()
	
		console.rule("INFO: icon_first=False")
	else:
		print("-------------------------------------------------")
		print("TEST LOGGING with AnsiLogHandler (setup_logging)")
  
	logger= setup_logging(icon_first=False, show_path=False, HANDLER=AnsiLogHandler)
	logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	if HAS_RICH:
		console.rule("end")
		console.print()

		console.rule("ERROR: default, level_in_message=False")
	else:
		print("-------------------------------------------------")
		print("TEST LOGGING with AnsiLogHandler (setup_logging)")
  
	logger= setup_logging(level_in_message=False, HANDLER=AnsiLogHandler)
	logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	if HAS_RICH:
		console.rule("end")
		console.print()

		console.rule("ERROR: show_path=False, level_in_message=False")
	else:
		print("-------------------------------------------------")
		print("TEST LOGGING with AnsiLogHandler (setup_logging)")
  
	logger= setup_logging(show_path=False, level_in_message=False, HANDLER=AnsiLogHandler)
	logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	if HAS_RICH:
		console.rule("end")
		console.print()
		console.rule("ERROR: show_icon=False, level_in_message=False")
	logger= setup_logging(show_icon=False, show_path=False, level_in_message=False, HANDLER=AnsiLogHandler)
	logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	if HAS_RICH:
		console.rule("end")
		console.print()

		console.rule("ERROR: icon_first=False, level_in_message=False")
	logger= setup_logging(icon_first=False, show_path=False, level_in_message=False, HANDLER=AnsiLogHandler)
	logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	if HAS_RICH:
		console.rule("end")
		console.print()

		console.rule("show_path=False, level_in_message=False")
	logger = setup_logging(show_path=False, level_in_message=False, HANDLER=AnsiLogHandler)
	        
	logger.emergency("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.alert("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.critical("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.warning("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.notice("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.debug("This is a debug message - will RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.fatal("This is a debug message - will RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	if HAS_RICH:
		console.rule("end")
		console.print()

		console.rule("show_background=False, show_path=False, level_in_message=False")
	logger = setup_logging(show_background=False, show_path=False, level_in_message=False, HANDLER=AnsiLogHandler)

	logger.emergency("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.alert("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.critical("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.warning("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.notice("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.debug("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.fatal("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

	if HAS_RICH:
		console.rule("end")
		console.print()

		console.rule("icon_first=False, show_path=False, level_in_message=False")
	logger = setup_logging(show_path=False, icon_first=False, HANDLER=AnsiLogHandler)
	        
	logger.emergency("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.alert("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.critical("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.warning("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.notice("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.debug("This is a debug message - will RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.fatal("This is a debug message - will RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	if HAS_RICH:
		console.rule("end")
		console.print()

		console.rule("show_background=False, icon_first=False, show_path=False, level_in_message=False")
	logger = setup_logging(show_background=False, show_path=False, icon_first=False, HANDLER=AnsiLogHandler)

	logger.emergency("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.alert("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.critical("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.warning("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.notice("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.debug("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.fatal("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

	if HAS_RICH:
		console.rule("end")
		console.print()

		console.rule("show_background=False, icon_first=False, show_path=True, level_in_message=False")
	logger = setup_logging(show_background=False, show_path=True, icon_first=False, HANDLER=AnsiLogHandler)

	logger.emergency("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.alert("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.critical("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.warning("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.notice("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.debug("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.fatal("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

	if HAS_RICH:
		console.rule("end")
		console.print()

		console.rule("show_background=True, icon_first=False, show_path=True, level_in_message=True")
	logger = setup_logging(show_background=True, show_path=True, icon_first=False, level_in_message=True, HANDLER=AnsiLogHandler)

	logger.emergency("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.alert("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.critical("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.warning("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.notice("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.info("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.debug("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.fatal("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

	if HAS_RICH:
		console.rule("end")
		console.print()

	import logging
	if HAS_RICH:
		console.rule("⭐INHERITANCE⭐", characters="🦆")
		console.print("\n\n")
	else:
		print("-------------------------------------------------")
		print("TEST LOGGING with AnsiLogHandler (INHERITANCE)")

	logger = logging.getLogger("INHERITANCE")
	from richcolorlog import AnsiLogHandler
	handler = AnsiLogHandler()
	logger.handlers.clear()
	logger.addHandler(handler)
	logger.propagate = False

	logger.emergency("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.alert("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.critical("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.warning("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.notice("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.debug("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

	if HAS_RICH:
		console.rule("⭐INHERITANCE⭐ debug_color=#FFAA00", characters="🦆")
	else:
		print("-------------------------------------------------")
		print("TEST LOGGING with AnsiLogHandler (INHERITANCE)")
  
	handler = AnsiLogHandler(debug_color="#FFAA00")
	logger.handlers.clear()
	logger.addHandler(handler)
	logger.propagate = False
	logger.debug("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

	handler = AnsiLogHandler()
	logger.handlers.clear()
	logger.addHandler(handler)
	logger.propagate = False
	logger.fatal("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

	if HAS_RICH:
		console.rule("end")
		console.print()

		console.rule("⭐INHERITANCE⭐show_path=False, show_path=False", characters="🌽")
		console.print("\n\n")
	else:
		print("-------------------------------------------------")
		print("TEST LOGGING with AnsiLogHandler (INHERITANCE)")

	logger = logging.getLogger("INHERITANCE")
	from richcolorlog import AnsiLogHandler
	handler = AnsiLogHandler(show_path=False)
	logger.handlers.clear()
	logger.addHandler(handler)
	logger.propagate = False

	logger.emergency("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.alert("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.critical("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.error("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.warning("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.notice("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")
	logger.debug("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

	if HAS_RICH:
		console.rule("⭐INHERITANCE⭐ debug_color='\x1b[38;2;255;170;0m', show_path=False", characters="🌽")
	else:
		print("-------------------------------------------------")
		print("TEST LOGGING with AnsiLogHandler (INHERITANCE)")
  
	handler = AnsiLogHandler(debug_color="\x1b[38;2;255;170;0m", show_path=False)
	logger.handlers.clear()
	logger.addHandler(handler)
	logger.propagate = False
	logger.debug("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")

	handler = AnsiLogHandler(show_path=False)
	logger.handlers.clear()
	logger.addHandler(handler)
	logger.propagate = False
	logger.fatal("RGBME v0.13.2 - 128x64 Matrix | 1x1 Chain | 12px per LED (REAL) | BrowserAdapter")


	# for ansi color easy use with make_colors.getSort() `pip install make_colors` (see README.)

if __name__ == '__main__':
	test()


