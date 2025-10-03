# In Jupyter/IPython
from logger import getLogger
import os

logger = getLogger('myapp', show_icon=True, icon_first=True, show_background=True)

logger.critical("Critical message")      # ❌ Critical message
logger.debug("Debug message")      # 🐞 Debug message
logger.info("Info message")        # ℹ️ Info message
logger.notice("Notice message")    # 🔔 Notice message
logger.warning("Warning message")  # ⚠️ Warning message
logger.error("Error message")      # ❌ Error message
logger.emergency("Emergency message")      # ❌ Emergency message
logger.alert("Alert message")      # ❌ Alert message

print("="*os.get_terminal_size()[0])

logger = getLogger('myapp', show_icon=True, icon_first=True, show_background=False)

logger.critical("Critical message")      # ❌ Critical message
logger.debug("Debug message")      # 🐞 Debug message
logger.info("Info message")        # ℹ️ Info message
logger.notice("Notice message")    # 🔔 Notice message
logger.warning("Warning message")  # ⚠️ Warning message
logger.error("Error message")      # ❌ Error message
logger.emergency("Emergency message")      # ❌ Emergency message
logger.alert("Alert message")      # ❌ Alert message
